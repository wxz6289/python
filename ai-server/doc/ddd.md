# 领域驱动设计（DDD）总结与最佳实践

**领域驱动设计**（Domain-Driven Design，Eric Evans 2003，后续由 Vaughn Vernon 等补充）是一种以**业务领域**为中心的设计方法：让软件结构反映业务语言与业务规则，而不是被数据库表、框架 API 或技术细节牵着走。

本文梳理 DDD 的**战略设计**与**战术设计**核心概念，给出工程最佳实践，并结合本仓库 [ai-server](../README.md)（FastAPI + RBAC/ACL + LangChain）说明如何在 Python Web 项目中落地。

相关文档：[FastAPI 核心内容](./fastapi.md) · [依赖注入](./dependon.md) · [ORM 总结](./orm.md)

---

## 1. DDD 解决什么问题

```
┌─────────────────────────────────────────────────────────────┐
│                    业务领域（Domain）                         │
│   用户 · 角色 · 权限 · 对话会话 · 订单 · 库存 …              │
├─────────────────────────────────────────────────────────────┤
│                   领域模型（Domain Model）                    │
│   实体 · 值对象 · 聚合 · 领域服务 · 领域事件                  │
├─────────────────────────────────────────────────────────────┤
│                 应用层（Application Layer）                   │
│   用例编排 · 事务边界 · DTO 转换 · 权限门面                   │
├─────────────────────────────────────────────────────────────┤
│              基础设施层（Infrastructure）                     │
│   ORM · 数据库 · Redis · HTTP · 消息队列 · LLM 客户端         │
├─────────────────────────────────────────────────────────────┤
│                 接口层（Interface / Delivery）                │
│   FastAPI 路由 · WebSocket · CLI · 定时任务                   │
└─────────────────────────────────────────────────────────────┘
```

| 问题 | 无 DDD 时常见症状 | DDD 的应对 |
|------|-------------------|------------|
| 业务逻辑散落 | 路由、CRUD、模板里到处是 `if/else` | 聚合根、领域服务承载不变量 |
| 沟通成本高 | 开发说「表/接口」，产品说「订单/权限」 | **统一语言**（Ubiquitous Language） |
| 模块边界模糊 | 改用户影响订单、改权限影响聊天 | **限界上下文**（Bounded Context） |
| 模型被 DB 绑架 | 贫血模型 + 巨型 Service | 富领域模型 + 分层/六边形架构 |
| 复杂度失控 | 所有功能堆在一个「大单体服务」 | 核心域优先、子域分类、上下文映射 |

**重要前提**：DDD 不是「必须上微服务」或「必须事件驱动」；它首先是**建模与边界**的方法论，单体应用同样可以受益。

---

## 2. 战略设计（Strategic Design）

战略设计回答：**系统划几块、每块负责什么、块之间如何协作**。

### 2.1 统一语言（Ubiquitous Language）

团队（产品、开发、测试）在**代码、文档、口头交流**中使用同一套术语。

| 坏例子 | 好例子（本仓库 auth 域） |
|--------|---------------------------|
| `check_table_user_role` | `user_has_permission` |
| `token_valid_flag` | `authenticate` / `authorize` |
| `chat_tbl_row` | `ChatSession`（对话会话） |

**实践**：

- 类名、方法名、API 字段名与产品文档一致
- 拒绝「技术翻译层」：不要在领域层出现 `dict_row`、`orm_obj` 这类无语义命名
- 新需求先对齐词汇表，再写代码

### 2.2 子域分类（Subdomain）

按业务价值将系统拆成子域：

| 类型 | 说明 | 投入策略 |
|------|------|----------|
| **核心域**（Core Domain） | 差异化竞争力，必须自建精耕 | 最好的人才、最清晰的模型 |
| **支撑域**（Supporting Subdomain） | 业务需要但非差异化 | 可自建简化版或适度外包 |
| **通用域**（Generic Subdomain） | 行业通用能力 | 优先买/用开源（认证框架、支付网关） |

以 ai-server 为例（示意）：

| 子域 | 可能分类 | 说明 |
|------|----------|------|
| RBAC + ACL 授权 | 核心域 / 支撑域 | 若多租户、细粒度策略是卖点 → 核心域 |
| LangChain 对话 | 核心域 | AI 命理对话是产品价值 |
| 用户注册登录 | 通用域 | OAuth2/JWT 模式成熟，可标准化 |
| 统一 API 响应包装 | 通用域 | 横切技术能力，非业务 |

**最佳实践**：资源有限时，**只在核心域做完整 DDD**；通用域用成熟方案，避免过度设计。

### 2.3 限界上下文（Bounded Context）

**限界上下文** = 一个语义边界内的模型是自洽的。同一词在不同上下文里可以有**不同含义**。

经典例子：

- **销售上下文**的 `Customer`：信用额度、收货地址
- **物流上下文**的 `Customer`：配送偏好、签收记录

本仓库可识别的上下文（逻辑划分，非强制微服务）：

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Identity &  │     │ Authorization│     │   Chat / AI  │
│   Access     │────▶│   (RBAC/ACL) │────▶│   Context    │
│  (用户/Token)│     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

- `app/auth/`：用户、角色、权限、ACL、ChatSession —— 一个上下文内的模型
- `app/services/master.py`：LLM 对话 —— 另一个上下文
- `app/routers/items.py`：演示用商品 —— 可与真实「商品域」分离

**规则**：一个聚合只属于一个限界上下文；跨上下文通过 **ID 引用** 或 **集成事件**，不要共享同一个 ORM 实体类到处改。

### 2.4 上下文映射（Context Map）

描述上下文之间的协作关系：

| 关系 | 含义 | 典型实现 |
|------|------|----------|
| **Partnership** | 两边共同演进 | 同一团队维护两个模块 |
| **Shared Kernel** | 共享一小部分模型/库 | 公共 `UserId` 类型、共享事件 schema |
| **Customer-Supplier** | 上游供下游消费 | auth 提供 `authorize()` 给 chat 用 |
| **Conformist** | 下游完全服从上游模型 | chat 直接使用 auth 的 `UserRead` |
| **Anti-Corruption Layer（ACL）** | 翻译层，隔离外部模型 | 对接第三方支付、外部用户中心 |
| **Open Host Service** | 对外暴露稳定 API | `/auth/check` 作为权限门面 |
| **Published Language** | 公共交换格式 | JSON Schema、Protobuf |

本仓库中，`AuthorizationService.authorize()` 相当于 auth 上下文对 chat 上下文提供的**应用服务门面**；chat 路由不直接查 ACL 表，避免 chat 域被 auth 表结构污染 —— 这是轻量级的防腐层思想。

---

## 3. 战术设计（Tactical Design）

战术设计回答：**在一个限界上下文内部，对象怎么建模**。

### 3.1 实体（Entity）

有**唯一标识**，生命周期内属性可变，同一 ID 即同一事物。

```python
# 概念示例 — 用户实体
class User:
    def __init__(self, user_id: int, username: str, status: int) -> None:
        self.id = user_id
        self.username = username
        self.status = status

    def deactivate(self) -> None:
        if self.status != 1:
            raise DomainError("User already inactive")
        self.status = 0
```

本仓库 `app/auth/models.py` 中的 `User`、`Role` 是 **SQLAlchemy 持久化模型**。严格 DDD 中，领域实体与 ORM 映射可以分离；中小项目常合并，但业务规则仍应逐步从路由挪到实体/领域服务。

### 3.2 值对象（Value Object）

**无独立 ID**，由属性定义相等性，通常**不可变**，可替换。

| 实体 vs 值对象 | 实体 | 值对象 |
|----------------|------|--------|
| 标识 | 有 ID | 无 ID，值相等即相等 |
| 可变性 | 可变 | 倾向不可变 |
| 示例 | User、Order | Money、Email、DateRange、Address |

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int   # 分
    currency: str = "CNY"

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")
        return Money(self.amount + other.amount, self.currency)
```

**最佳实践**：能用值对象表达的就不要用裸 `float`、`str` 满天飞（金额、邮箱、权限动作 `Action("read")`）。

### 3.3 聚合与聚合根（Aggregate & Aggregate Root）

**聚合**是一组相关对象的一致性边界；**聚合根**是外部访问聚合的唯一入口。

```
        ┌─────────────────────────────────┐
        │         Order (聚合根)           │
        │  order_no, status, customer_id  │
        ├─────────────────────────────────┤
        │  OrderLine (实体，聚合内)        │
        │  OrderLine (实体，聚合内)        │
        └─────────────────────────────────┘
```

**不变量（Invariants）** 在聚合根内维护，例如：

- 订单总价 = 各行小计之和
- 已取消订单不能追加行项
- 库存扣减与订单创建在同一事务

**规则**：

1. 外部只能通过**聚合根 ID** 引用聚合（`order_id`，不要持有 `OrderLine` 引用到处改）
2. 一个事务只修改**一个聚合**（大聚合可拆）
3. 跨聚合用**领域事件**或**应用服务编排** + 最终一致性

### 3.4 仓储（Repository）

仓储封装持久化，对领域层表现为「集合式」接口：

```python
class UserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> User | None: ...
    async def save(self, user: User) -> None: ...
```

本仓库当前更接近 **Active Record / CRUD** 风格（`app/auth/rbac.py`、`app/crud.py` 直接操作 ORM）。演进方向：

- 路由 → 应用服务 → **仓储接口** → SQLAlchemy 实现
- 领域层不 import `AsyncSession`

### 3.5 领域服务（Domain Service）

当某个操作**不属于任何一个实体**，但属于领域逻辑时，用领域服务：

- 跨多个聚合的纯领域规则
- 无状态的领域计算

```python
# 概念示例
class PricingService:
    def calculate_discount(self, order: Order, customer: Customer) -> Money:
        ...
```

与 **应用服务** 的区别见 [§4.2](#42-应用服务-vs-领域服务)。

本仓库 `app/auth/acl.py` 中的 `evaluate_acl_entries` 接近**领域服务**：纯函数式 ACL 求值，不依赖 HTTP。

### 3.6 领域事件（Domain Event）

聚合内发生的重要业务事实，用过去式命名：

- `OrderPlaced`
- `UserRegistered`
- `ChatSessionCreated`

```python
@dataclass(frozen=True)
class UserRegistered:
    user_id: int
    username: str
    occurred_at: datetime
```

用于：

- 解耦上下文（发事件，别的上下文订阅）
- 审计、通知、读模型投影（CQRS）

中小 API 不必一上来就上事件总线；**先在核心域识别事件**即可。

### 3.7 工厂（Factory）

创建复杂聚合或确保创建时满足不变量：

```python
class OrderFactory:
    @staticmethod
    def create(order_no: str, lines: list[OrderLineDraft]) -> Order:
        if not lines:
            raise DomainError("Order must have at least one line")
        return Order(...)
```

避免在路由里 `Order(...)` 拼半天。

---

## 4. 分层架构

### 4.1 经典四层

| 层 | 职责 | 本仓库对应（现状 / 目标） |
|----|------|---------------------------|
| **接口层** | HTTP、DTO、鉴权入口 | `app/routers/`、`app/auth/dependencies.py` |
| **应用层** | 用例编排、事务、DTO 转换 | `AuthorizationService`（部分应用+领域混合） |
| **领域层** | 实体、值对象、领域服务、仓储接口 | `app/auth/acl.py`（部分）；可抽 `domain/` |
| **基础设施层** | ORM、DB、Redis、LLM | `app/db/`、`app/auth/models.py`、`services/master.py` |

依赖方向：**外层依赖内层**，领域层不依赖 FastAPI / SQLAlchemy。

```
Interface  →  Application  →  Domain  ←  Infrastructure
   (路由)        (用例)         (规则)      (实现仓储接口)
```

### 4.2 应用服务 vs 领域服务

| | 应用服务 | 领域服务 |
|---|----------|----------|
| **例子** | `AuthorizationService.authorize()` | `evaluate_acl_entries()` |
| **职责** | 编排：取用户 → 查 RBAC → 查 ACL → 返回结果 | 纯规则：给定 entries + context → allow/deny |
| **依赖** | 可调仓储、领域服务、发事件 | 尽量不依赖基础设施 |
| **事务** | 常在此划定事务边界 | 无 |

本仓库 `AuthorizationService` 同时做了编排与持久化访问，是 pragmatic 做法；若 auth 域继续膨胀，应把 `evaluate_acl_entries` 留在领域层，Service 只做协调。

### 4.3 六边形架构 / 整洁架构

与四层本质相同，强调**端口与适配器**：

- **端口**：领域定义的接口（`UserRepository`、`LLMClient`）
- **适配器**：FastAPI 路由、SQLAlchemy 仓储、`Master` 调 LangChain

```
         [ FastAPI Router ]     [ CLI ]
                │                    │
                └────────┬───────────┘
                         ▼
                  [ Application ]
                         ▼
                   [ Domain ]
                         ▲
                ┌────────┴────────┐
         [ SQLAlchemy Repo ]  [ LangChain Adapter ]
```

---

## 5. 与 FastAPI / Python 项目的映射

### 5.1 常见目录结构（演进路径）

**阶段 1 — 按技术分层（本仓库现状）**

```
app/
├── routers/          # 接口
├── auth/
│   ├── models.py     # ORM
│   ├── schemas.py    # Pydantic DTO
│   ├── service.py    # 服务
│   └── rbac.py       # 数据访问
├── services/
└── db/
```

**阶段 2 — 按限界上下文 + 层**

```
app/
├── auth/
│   ├── domain/
│   │   ├── entities.py
│   │   ├── value_objects.py
│   │   ├── services.py      # evaluate_acl_entries
│   │   └── repositories.py  # Protocol
│   ├── application/
│   │   └── authorization_service.py
│   ├── infrastructure/
│   │   └── sqlalchemy_user_repo.py
│   └── interface/
│       ├── router.py
│       └── schemas.py
├── chat/
│   └── ...
```

不必一次到位；**当单个模块超过 ~10 个用例且规则复杂时再拆**。

### 5.2 Pydantic Schema 的角色

| 类型 | DDD 角色 |
|------|----------|
| `UserCreate` / `UserRead` | **DTO**（接口层 / 应用层边界） |
| SQLAlchemy `User` | **持久化模型**（基础设施） |
| 纯 Python `@dataclass` User | **领域实体**（可选，大项目推荐分离） |

**最佳实践**：

- 路由入参/出参用 Pydantic，不直接把 ORM 模型当 API 响应
- `model_config = {"from_attributes": True}` 用于 ORM → DTO 映射（本仓库 `UserRead` 已如此）

### 5.3 依赖注入与 DDD

FastAPI `Depends` 负责**组装应用服务**（注入 session、配置），不应承载领域规则：

```python
# 好：依赖注入组装
async def get_auth_service(session: AsyncSession = Depends(get_db_session)):
    return AuthorizationService(session)

# 差：在 Depends 里写 ACL 业务规则
```

详见 [依赖注入文档](./dependon.md)。

---

## 6. CQRS 与事件溯源（进阶，选用）

| 模式 | 说明 | 何时考虑 |
|------|------|----------|
| **CQRS** | 读写模型分离（写模型走聚合，读模型走投影表/ES） | 读多写多、报表复杂、读写性能差异大 |
| **Event Sourcing** | 存事件流而非当前状态 | 强审计、金融、需要时光回溯 |

大多数 CRUD + 若干复杂用例的 API **不需要** CQRS/ES。先用聚合 + 仓储 + 必要时领域事件即可。

---

## 7. 最佳实践清单

### 7.1 推荐做法

| 实践 | 说明 |
|------|------|
| **从核心域开始** | 先对最复杂、最有价值的子域建模，不要全项目一刀切 |
| **统一语言落地到代码** | 类名/方法名与产品一致，PR review 检查术语 |
| **小聚合** | 聚合尽量小，减少锁与并发冲突 |
| **一个事务一个聚合** | 跨聚合用事件或 Saga，避免大事务 |
| **路由薄、领域厚** | 路由：参数 + 调应用服务 + 返回 DTO |
| **仓储抽象持久化** | 领域层不感知 SQL/Redis |
| **显式不变量** | 在聚合根方法里校验，不要靠「记得在路由里检查」 |
| **防腐层对接外部系统** | 第三方 API、遗留系统通过 ACL 翻译 |
| **测试领域逻辑** | 领域服务/实体单元测试不启动 FastAPI |
| **渐进式采用** | 新功能按 DDD 写，旧代码按需重构 |

### 7.2 反模式（避免）

| 反模式 | 问题 |
|--------|------|
| **贫血领域模型** | 实体只有 getter/setter，逻辑全在 `XxxService` 巨型类 |
| **上帝 Service** | 一个 Service 几千行，管所有用例 |
| **跨上下文共享 ORM 实体** | chat 直接改 `User.roles`，边界崩溃 |
| **聚合过大** | 把整个「订单+用户+库存」当一个聚合 |
| **过早微服务** | 上下文边界没理清就拆服务，分布式复杂度暴增 |
| **伪 DDD** | 文件夹叫 `domain/` 但没有不变量、没有聚合边界 |
| **CRUD 冒充 DDD** | `create/update/delete` 镜像数据库，无业务语义 |
| **过度事件驱动** | 简单同步调用硬拆成事件，调试困难 |

### 7.3 何时用 / 不用 DDD

**适合**：

- 业务规则复杂、变化频繁
- 多团队协作、需要清晰边界
- 生命周期长、维护成本高的系统

**不必强上**：

- 简单 CRUD、管理后台
- 原型 / MVP 验证阶段
- 只读报表、ETL 管道

---

## 8. 本仓库 DDD 视角速览

| 模块 | 上下文 | 现状 | 可演进方向 |
|------|--------|------|------------|
| `app/auth/` | Identity & Authorization | Service + ORM + ACL 纯函数 | 抽 `domain/`，仓储接口化 |
| `app/routers/chat.py` | Chat | 路由 + `prepare_chat_access` + `Master` | Chat 聚合（Session、Message） |
| `app/routers/items.py` | Catalog（演示） | 路由内 mock | 若业务化：Item 聚合 + 应用服务 |
| `app/crud.py` | — | 贫血 CRUD | 按上下文拆入各域仓储 |
| `app/schemas/` | 跨层 DTO | Pydantic 模型 | 保持，按上下文分子包 |

**已有良好实践**：

- auth 与 chat 通过 `AuthorizationService.authorize()` 协作，而非 chat 直接查权限表
- `evaluate_acl_entries` 作为可单测的领域规则
- Pydantic DTO 与 ORM 分离（`UserRead` vs `User`）

**可改进点（按需）**：

- 将「用户禁用」「角色变更」等规则收拢到实体或领域服务
- 为 `ChatSession` 定义聚合根行为（创建、归属校验）
- 路由仅保留 HTTP  concern，业务进 application layer

---

## 9. 建模工作流（推荐步骤）

1. **事件风暴 / 需求梳理**：列出领域事件、命令、参与者
2. **识别子域**：核心 / 支撑 / 通用，决定投入
3. **划定限界上下文**：画上下文地图，定义集成方式
4. **统一语言词汇表**：名词、动词、禁止混用语
5. **找聚合**：从不变量出发，画聚合边界
6. **定义仓储与应用服务**：一个用例 = 一个应用服务方法
7. **接口层适配**：FastAPI 路由 + Pydantic DTO
8. **测试**：领域单元测试 + 接口集成测试

---

## 10. 测试策略

| 层级 | 测什么 | 工具 |
|------|--------|------|
| **领域层** | 不变量、ACL 求值、价格计算 | pytest，纯函数，无 DB |
| **应用层** | 用例编排、事务行为 | mock 仓储 |
| **接口层** | HTTP 契约、鉴权 | `TestClient`，`dependency_overrides` |
| **集成** | 仓储 + 真 DB | testcontainers / docker compose |

```python
# 领域层测试示例 — 无需 FastAPI
def test_deny_overrides_allow():
    entries = [allow_entry, deny_entry]
    assert evaluate_acl_entries(entries, ctx) is False
```

本仓库 `tests/test_acl_unit.py` 即符合「领域逻辑单测」思路。

---

## 11. 与相关方法论的关系

| 方法论 | 与 DDD 关系 |
|--------|-------------|
| **微服务** | 限界上下文常成为服务边界，但 DDD 不要求微服务 |
| **Clean Architecture** | 分层与依赖方向一致，可结合使用 |
| **Event Storming** | DDD 战略设计的协作式建模 workshop |
| **CRUD API** | 可共存；非核心域保持简单 CRUD 即可 |
| **ORM** | 持久化细节，应在基础设施层；见 [ORM 文档](./orm.md) |

---

## 12. 常见问题

| 问题 | 答案 |
|------|------|
| DDD 一定要分离领域实体和 ORM 吗？ | 小项目可合并；规则变复杂时再分离 |
| 聚合多大合适？ | 能在一个事务内保证一致性的最小集合；通常 1~3 个实体 |
| Service 和 Repository 的区别？ | Repository 像集合，管存取；Service 管无归属实体上的领域逻辑或应用编排 |
| Python 适合 DDD 吗？ | 适合；dataclass、`Protocol`、类型注解足够表达模式 |
| 和「三层架构」冲突吗？ | 不冲突；DDD 的接口/应用/领域/基础设施是三层架构的细化 |

---

## 13. 小结

**DDD 核心 = 统一语言 + 限界上下文 + 聚合一致性 + 分层依赖向内。**

落地时记住四句话：

1. **战略上**先划上下文与子域，别急着拆微服务  
2. **战术上**用聚合根守住不变量，别搞贫血 CRUD  
3. **工程上**路由薄、应用编排、领域纯、基础设施可替换  
4. **节奏上**核心域深度建模，通用域用现成方案，渐进演进  

结合本仓库：auth 域已具备上下文雏形（RBAC + ACL + Service 门面）；下一步若业务增长，优先在 **auth** 与 **chat** 内完善聚合与仓储抽象，而不是在全项目强行引入完整 DDD 目录结构。
