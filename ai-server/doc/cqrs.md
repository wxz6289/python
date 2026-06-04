# CQRS（命令查询职责分离）总结与最佳实践

**CQRS**（Command Query Responsibility Segregation，命令查询职责分离）由 **Greg Young** 等推广，核心思想极其简单：**改变系统状态**的操作（Command）与**读取系统状态**的操作（Query）在模型、路径甚至存储上分开设计。

它与 DDD 常配合使用，但 CQRS **不是 DDD 的子集**，也不是「必须上 Event Sourcing / 微服务」的前置条件。本文梳理 CQRS 的核心概念、分层形态、与相关模式的关系，给出工程最佳实践，并结合本仓库 [ai-server](../README.md) 说明在 Python / FastAPI 项目中的落地方式。

相关文档：[领域驱动设计](./ddd.md) · [依赖注入](./dependon.md) · [ORM 总结](./orm.md)

---

## 1. CQRS 解决什么问题

传统 CRUD 架构里，**同一张表、同一个实体类**既负责写入（创建订单、扣库存）又负责展示（列表页、详情页、报表）。随着业务变复杂，会出现：

| 问题 | 典型症状 |
|------|----------|
| **读写需求冲突** | 写模型要维护不变量、小聚合；读模型要宽表、多表 JOIN、分页排序 |
| **性能瓶颈** | 复杂查询拖慢 OLTP 写入；为读优化加的索引反过来伤害写 |
| **模型膨胀** | 一个 `Order` 实体塞满展示字段、统计字段、状态机逻辑 |
| **扩展困难** | 读流量是写流量的 100 倍，却无法独立扩容读侧 |
| **职责模糊** | `update()` 既改业务状态又顺带更新展示字段，难以测试与审计 |

CQRS 的应对：**写侧专注业务规则与一致性，读侧专注查询效率与展示形态**，允许两边演化速度、数据结构、甚至技术栈不同。

```
                    ┌─────────────────────────────────────┐
                    │           客户端 / API 网关           │
                    └──────────────┬──────────────────────┘
                                   │
              ┌────────────────────┴────────────────────┐
              │                                         │
              ▼                                         ▼
    ┌──────────────────┐                    ┌──────────────────┐
    │   Command 侧      │                    │    Query 侧       │
    │  改变状态 · 有副作用  │                    │  只读 · 无副作用    │
    │  POST/PUT/PATCH   │                    │  GET / 报表 / 搜索  │
    └─────────┬─────────┘                    └─────────┬─────────┘
              │                                         │
              ▼                                         ▼
    ┌──────────────────┐                    ┌──────────────────┐
    │  写模型 / 聚合根    │                    │  读模型 / 投影 DTO  │
    │  领域不变量 · 事务   │                    │  宽表 · 视图 · ES   │
    └─────────┬─────────┘                    └─────────┬─────────┘
              │                                         │
              ▼                                         ▼
    ┌──────────────────┐         同步/异步          ┌──────────────────┐
    │   写库（OLTP）      │ ──────────────────────▶ │   读库 / 缓存       │
    └──────────────────┘         投影 / 事件         └──────────────────┘
```

**CQRS 第一原则**（Bertrand Meyer / CQS 思想）：**命令改变状态但不返回值（业务意义下的「结果对象」）；查询返回值但不改变状态。** HTTP 层面仍会有 201/204 等状态码，指的是传输语义，不是把「查询结果 DTO」混进写操作。

---

## 2. 核心概念

### 2.1 Command（命令）

命令表示**意图**：「创建会话」「授予权限」「提交订单」。它是**现在时**的业务动作，携带执行所需的最小数据。

| 特征 | 说明 |
|------|------|
| **命名** | 用动词或动宾短语：`CreateChatSession`、`GrantPermission`，避免 `ChatSessionDTO` |
| **语义** | 表达「要做什么」，不是「数据库一行长什么样」 |
| **校验** | 基本格式校验在接口层；**业务不变量在写模型 / 领域层** |
| **返回值** | 通常返回 `command_id`、新资源 id，或空（204）；**不要**返回复杂聚合图供前端展示 |
| **幂等** | 关键命令应设计幂等键（`Idempotency-Key`、业务唯一号），防止重复提交 |

```python
# 命令对象（示意）—— 只含写操作需要的字段
class CreateChatSessionCommand:
    session_id: str
    owner_id: int
    department: str | None = None
```

### 2.2 Query（查询）

查询表示**问题**：「某用户有哪些角色？」「会话列表（分页）？」。**绝不修改状态**。

| 特征 | 说明 |
|------|------|
| **命名** | `GetChatSession`、`ListUserPermissions` |
| **参数** | 过滤、排序、分页、投影字段 |
| **返回值** | **读模型 DTO**（Read Model），面向 UI/报表优化 |
| **缓存** | 读侧是缓存、CDN、只读副本的主要受益者 |
| **授权** | 仍要做鉴权，但通常比写侧轻（只读 ACL 检查） |

```python
# 读模型 DTO（示意）—— 可包含展示专用字段，不必与写表一一对应
class ChatSessionListItem:
    session_id: str
    owner_name: str      # 读侧 JOIN 或投影时已 denormalize
    last_message_at: datetime | None
    message_count: int
```

### 2.3 Command Handler / Query Handler

**Handler** 是 CQRS 的入口：一个命令对应一个 Handler（或一组相关命令对应一个服务方法），**不**用巨型 `Service.update_everything()`。

```
Command  →  CommandHandler.handle(cmd)  →  加载聚合  →  执行业务  →  持久化  →  （可选）发布事件
Query    →  QueryHandler.handle(qry)     →  读库/投影/缓存  →  返回 DTO（无写操作）
```

| 组件 | 职责 |
|------|------|
| **CommandHandler** | 编排事务边界、加载聚合、调用领域逻辑、提交、发布领域事件 |
| **QueryHandler** | 只读访问读模型；**禁止**注入写仓储或调用会改状态的方法 |
| **Bus（可选）** | `CommandBus` / `QueryBus` 统一 dispatch，路由到对应 Handler |

### 2.4 写模型 vs 读模型

| 维度 | 写模型（Write Model） | 读模型（Read Model） |
|------|----------------------|----------------------|
| **目的** | 维护业务不变量、记录真实状态 | 高效回答查询、适配 UI |
| **结构** | 聚合根、值对象、小实体图 | 宽表、物化视图、文档、搜索引擎索引 |
| **一致性** | 强一致（单事务内） | 往往**最终一致**（投影延迟毫秒～秒级） |
| **演化** | 随领域规则变 | 随页面/报表变，可多个读模型对应同一写模型 |
| **典型存储** | 规范化 OLTP 表 | SQL 视图、Redis、Elasticsearch、ClickHouse |

**关键认知**：读模型是**可丢弃的**—— 只要写模型与事件流在，可以重建投影。这也是 CQRS 与 Event Sourcing 常结对出现的原因。

---

## 3. CQRS 的三种成熟度

不必一步到位；多数团队从 **Level 1** 开始即可。

### 3.1 Level 1：逻辑分离（同一数据库）

- Command / Query **类与 Handler 分开**，路由分开
- **共用一套表**，但写走聚合+仓储，读走专用 Query 与 DTO
- **本仓库 auth / chat 域接近此级别**：`AuthorizationService` 承担写侧编排，`UserRead` 等 schema 服务读侧展示

```
app/auth/
├── application/
│   └── authorization_service.py   # 写：authorize、ensure_chat_session
├── interface/
│   ├── router.py                  # HTTP 入口
│   └── schemas.py                 # UserRead 等读 DTO
└── infrastructure/
    └── acl_repository.py          # 持久化
```

**适用**：中小型 API、团队刚引入 DDD、读写表结构尚未分化。

### 3.2 Level 2：物理分离读库（读写库同构或读库为副本）

- 写库主库 + **只读副本** 或 **专用读表（投影表）**
- 写成功后通过**同步双写**或**异步消费者**更新读表
- 读 Handler **只**访问读库/投影

**适用**：读多写少、列表/搜索慢、需要独立扩展读节点。

### 3.3 Level 3：异构读写存储 + 事件驱动

- 写：PostgreSQL + 聚合
- 读：Elasticsearch（搜索）、Redis（热点）、ClickHouse（分析）
- 通过**领域事件**或 **CDC** 同步

**适用**：复杂搜索、实时大屏、多维度报表；**复杂度和运维成本最高**。

| 级别 | 分离程度 | 典型成本 | 何时选 |
|------|----------|----------|--------|
| Level 1 | 代码/类分离 | 低 | 默认起点；CRUD + 若干复杂用例 |
| Level 2 | 读库/投影 | 中 | 读性能成为瓶颈、报表拖垮 OLTP |
| Level 3 | 异构 + 事件 | 高 | 搜索/分析/多读模型是核心需求 |

---

## 4. 与相关模式的关系

### 4.1 CQRS vs CQS（命令查询分离）

| | CQS | CQRS |
|---|-----|------|
| **粒度** | 函数/方法级：setter 无返回，getter 无副作用 | 架构级：整条链路、模型、存储可分离 |
| **范围** | 代码纪律 | 系统设计模式 |
| **关系** | CQRS 可看作 CQS 在分布式/DDD 中的扩展 |

在 Python 中即使不做「完整 CQRS」，也应遵守：**查询函数不 commit；命令函数不返回复杂查询结果**。

### 4.2 CQRS + DDD

| DDD 概念 | 在 CQRS 中的位置 |
|----------|------------------|
| **聚合根** | 写模型的核心，Command 的加载与持久化单元 |
| **领域事件** | 写侧提交后通知读侧更新投影 |
| **仓储** | 写仓储只服务 CommandHandler |
| **应用服务** | 常演化为 CommandHandler；或薄编排层调用 Handler |
| **限界上下文** | 每个上下文可有独立的 CQRS 读写模型 |

本仓库按 DDD 分层后，**自然演进 CQRS 的路径**：

1. 将 `AuthorizationService` 中纯读方法（如 `get_user_context`）抽到 `UserQueryService`
2. 写方法（`authorize`、`ensure_chat_session`）保留在 Command 侧
3. 路由层：`GET` 调 QueryHandler，`POST/PUT/DELETE` 调 CommandHandler

### 4.3 CQRS + Event Sourcing（ES）

| 模式 | 存储什么 | 与 CQRS 关系 |
|------|----------|--------------|
| **传统 CQRS** | 写库存当前状态；读库存投影 | 可独立使用 |
| **ES** | 存事件流；当前状态由 replay 得出 | 常与 CQRS 写侧结合 |
| **CQRS + ES** | 写侧 append-only 事件；读侧多种投影 | 强审计、回放、复杂协作 |

**ES 不是 CQRS 的前提**。大多数项目 **不需要 ES**；见 [DDD 文档 §6](./ddd.md#6-cqrs-与事件溯源进阶选用)。

### 4.4 CQRS vs CRUD

| CRUD | CQRS |
|------|------|
| `Create/Read/Update/Delete` 对称 | `Command` 与 `Query` 不对称、语义化 |
| 一个 `Order` 实体包打天下 | `PlaceOrder` 命令 + `OrderSummary` 读模型 |
| 简单直接 | 边界清晰、可扩展，但文件与概念更多 |

**不要为了 CQRS 而 CQRS**：简单资源管理（如 demo 里的 `Item` CRUD）保持 CRUD 即可。

---

## 5. 请求生命周期（FastAPI 视角）

### 5.1 写路径（Command）

```
HTTP POST /chat/sessions
    → 路由解析 Body → CreateChatSessionCommand
    → Depends: 鉴权、DbSession
    → CreateChatSessionHandler.handle(cmd)
        → ChatSessionAggregate.create(...)
        → ChatSessionRepository.save(aggregate)
        → session.commit()
        → （可选）event_bus.publish(ChatSessionCreated)
    → 201 + { "session_id": "..." }   # 简短确认，非完整读模型
```

### 5.2 读路径（Query）

```
HTTP GET /chat/sessions?page=1
    → ListChatSessionsQuery(page=1, user_id=...)
    → Depends: 鉴权（如 prepare_chat_access 的只读版）
    → ListChatSessionsHandler.handle(query)
        → 只读 session / 读库 / Redis
        → 返回 list[ChatSessionListItem]
    → 200 + JSON
```

### 5.3 与依赖注入的配合

| 依赖 | 写侧 | 读侧 |
|------|------|------|
| `AsyncSession` | 读写主库，有 `commit` | **只读** session 或 `session.execute(select...)` 不 commit |
| 鉴权 | `get_current_user` + 写权限 | 同等或更轻的读权限 |
| Handler 注册 | `Depends(get_create_session_handler)` | `Depends(get_list_sessions_handler)` |

**反模式**：一个 `ChatService` 同时暴露 `create_session()` 和 `list_sessions()`，内部共用会修改状态的缓存字典—— 读写耦合，难以独立测试与扩展。

---

## 6. 读模型投影与最终一致

当读写存储分离时，读模型通过**投影**（Projection）更新：

```
写侧事务提交
    → 发布领域事件（内存 / 消息队列 / Outbox）
        → Projector 消费事件
            → UPSERT 读表 / 更新 ES 文档 / 失效 Redis 缓存
```

| 策略 | 说明 | 一致性 |
|------|------|--------|
| **同步投影** | 同一进程、同一请求内更新读表 | 近强一致；写路径变长 |
| **异步投影** | 消息队列 + Worker | 最终一致；写路径短 |
| **Transactional Outbox** | 业务表与 outbox 同事务；独立进程投递 | 可靠、生产常用 |

**产品层面**必须接受：用户创建后立刻列表**可能**短暂看不到（或看到旧数据），需 UI 策略（乐观展示、轮询、WebSocket 推送）。

---

## 7. 最佳实践

### 7.1 推荐做法

| 实践 | 说明 |
|------|------|
| **从逻辑分离开始** | 先分 Command/Query 类与 Handler，不急于拆库 |
| **命令用业务语言命名** | `GrantRole` 而非 `UpdateUserRoleTable` |
| **读模型为 UI 设计** | 一个页面可对应一个 Query + 一个 DTO，允许冗余字段 |
| **写侧保持小聚合** | Command 只加载必要聚合，避免「一次写全库」 |
| **查询不走聚合根** | 列表/统计直接查读模型或 SQL，**不要** `load 10000 个聚合再 map` |
| **显式事务边界** | 一个 Command = 一个事务；跨聚合用 Saga / 事件 |
| **读侧无领域事件副作用** | QueryHandler 内禁止 `publish` 或 `save` |
| **幂等与去重** | 支付、下单、创建资源类命令带幂等键 |
| **版本化读 API** | 读模型字段常变，DTO 与 API 版本一起演进 |
| **可观测** | 分别监控写延迟、投影滞后（lag）、读 QPS |

### 7.2 反模式（避免）

| 反模式 | 问题 |
|--------|------|
| **伪 CQRS** | 仅把文件夹改名 `commands/`，内部仍是 CRUD Service |
| **查询里改状态** | `GET /users` 顺带更新 `last_seen_at` — 破坏 Query 语义 |
| **命令返回 fat DTO** | `POST` 返回整个聚合图，读侧逻辑渗入写路径 |
| **读侧调用写仓储** | QueryHandler 加载聚合根做展示 — 性能与耦合双输 |
| **过早拆库** | 无性能证据就上 ES + Kafka + 三库 |
| **忽略投影失败** | 读模型永久落后；需死信队列、重放、对账任务 |
| **一个 Handler 包打天下** | `OrderCommandHandler` 两千行 — 应按用例拆分 |
| **全局 CQRS 一刀切** | demo、配置、健康检查仍用简单 CRUD |

### 7.3 何时用 / 不用 CQRS

| 适合 CQRS（至少 Level 1） | 不必 CQRS |
|---------------------------|-----------|
| 读写模型差异大（订单写 vs 订单大屏读） | 简单 CRUD、管理后台 |
| 读流量远大于写，需独立扩展 | 原型、内部工具 |
| 复杂搜索、报表、多维度聚合 | 单一实体、字段少于 10 个 |
| 多团队：写域与读 API 不同步发布 | 强一致要求「写后读必见」且不能接受投影 |
| 需审计每条状态变更（+ ES） | 团队无 DDD/CQRS 经验且交付紧 |

**经验法则**：若你说不清「读模型和写模型有什么不同」，先不要拆库；若只能说「读很多」，先试只读副本 + 缓存，再考虑 Level 2。

---

## 8. 在本仓库中的落地建议

当前 ai-server 已具备 DDD 分层（`auth` / `chat` / `catalog`），可按子域**渐进**引入 CQRS：

### 8.1 auth 域（示意）

| 类型 | 示例 | 现有 / 建议 |
|------|------|-------------|
| **Command** | `RegisterUser`、`AssignRole`、`UpsertChatSession` | `ensure_chat_session` → 显式 Command |
| **Query** | `GetCurrentUser`、`ListPermissions`、`GetChatSession` | `get_user_context`、`UserRead` |
| **Handler 位置** | `auth/application/commands/` · `auth/application/queries/` | 从 `AuthorizationService` 拆分 |

### 8.2 chat 域（示意）

| 类型 | 示例 | 说明 |
|------|------|------|
| **Command** | `SendMessage`（若持久化会话） | 写侧调 LLM 前可先落库 |
| **Query** | `GetChatHistory` | 读侧分页；与 LangChain memory 解耦 |
| **访问控制** | `prepare_chat_access` | 读/写路由均可复用，属横切关注点 |

### 8.3 catalog 域

`Item` 资源若仅为 demo CRUD，**保持 CRUD**，不必强行 Command/Query 分包。

### 8.4 目录结构参考（Level 1）

```
app/chat/
├── application/
│   ├── commands/
│   │   ├── create_session.py      # CreateChatSessionCommand + Handler
│   │   └── send_message.py
│   └── queries/
│       ├── get_session.py
│       └── list_sessions.py
├── domain/
│   └── ...                          # 聚合、不变量（写侧）
├── infrastructure/
│   ├── write_repository.py
│   └── read_repository.py         # 初期可指向同库不同 SQL
└── interface/
    ├── router.py                  # POST → commands, GET → queries
    └── schemas.py                 # Command DTO / Read DTO 分离
```

---

## 9. 测试策略

| 层级 | Command | Query |
|------|---------|-------|
| **单元测试** | 聚合 + Handler 逻辑，mock 仓储 | QueryHandler + 固定读数据 fixture |
| **集成测试** | 写库 commit 后断言行状态 | 只读查询结果；**断言无写 SQL** |
| **投影测试** | 发布事件 → 等待 projector → 读模型断言 | 测最终一致延迟边界 |
| **契约测试** | 命令 schema 与 OpenAPI 一致 | 读 DTO 字段与前端约定一致 |

```python
# 查询侧：确保 handler 不提交写事务（示意）
async def test_list_sessions_is_read_only(session, handler):
    await handler.handle(ListChatSessionsQuery(user_id=1))
    assert not session.dirty  # 或 spy：repository.save 未被调用
```

---

## 10.  checklist 速查

**设计阶段**

- [ ] 能否列出至少 3 个「写意图」Command 与 3 个「读问题」Query？
- [ ] 读模型 DTO 是否与写表结构解耦？
- [ ] 是否接受最终一致（若拆读库）？

**实现阶段**

- [ ] Command / Query 类分离；Handler 单一职责
- [ ] Query 路径无 `commit` / `save` / 领域事件发布
- [ ] 路由 HTTP 方法语义正确：GET 不写，POST/PUT/PATCH/DELETE 不返回 fat 读模型
- [ ] 关键 Command 有幂等设计

**运维阶段**

- [ ] 监控投影 lag 与读库延迟
- [ ] 投影失败可重放；定期对账写库与读库

---

## 11. 延伸阅读

| 资料 | 说明 |
|------|------|
| Greg Young — CQRS Documents | 模式原典与术语 |
| Martin Fowler — CQRS | 何时需要、何时过度 |
| *Implementing Domain-Driven Design*（Vaughn Vernon） | DDD 与 CQRS 结合 |
| Microsoft — CQRS pattern | 云架构视角的读写分离 |
| 本仓库 [DDD 文档 §6](./ddd.md#6-cqrs-与事件溯源进阶选用) | 与 ES 的简要对比 |

---

**总结**：CQRS 的价值在于**让写路径专注正确性、读路径专注效率**，通过显式分离避免单一模型被读写两种需求撕裂。从 **Level 1 逻辑分离** 起步，在真实性能与复杂度压力下再考虑读库与事件投影；与 ai-server 已有的 DDD 分层天然契合，但 **catalog 级简单 CRUD 不必强行套用**。
