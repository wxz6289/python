# Model Context Protocol（MCP）协议总结与最佳实践

[MCP](https://modelcontextprotocol.io/)（Model Context Protocol）是一套**开放标准**，用于把 AI 应用（宿主）与**外部系统**连接起来：数据源（文件、数据库）、可执行能力（工具、API）、以及可复用的交互模板（提示词）等。协议**只规范「上下文如何交换」**，不规定宿主内部如何用 LLM 或如何编排 Agent。

- **官方介绍**：[What is MCP?](https://modelcontextprotocol.io/docs/getting-started/intro.md)
- **规范索引**：[Specification（以站点 `latest` 为准）](https://modelcontextprotocol.io/specification/latest)
- **机器可读文档目录**：[llms.txt](https://modelcontextprotocol.io/llms.txt)

下文术语与分层与官方 [Architecture overview](https://modelcontextprotocol.io/docs/learn/architecture.md) 一致；传输与安全细节以规范 **2025-11-25** 文档为主（版本会演进，实现时请以你对接的 `protocolVersion` 为准）。

---

## 目录

1. [角色与架构](#1-角色与架构)
2. [协议分层：传输层与数据层](#2-协议分层传输层与数据层)
3. [消息模型：JSON-RPC 2.0](#3-消息模型json-rpc-20)
4. [生命周期与能力协商](#4-生命周期与能力协商)
5. [服务端原语：Tools / Resources / Prompts](#5-服务端原语tools--resources--prompts)
6. [客户端原语：Sampling / Elicitation / Roots / Logging](#6-客户端原语sampling--elicitation--roots--logging)
7. [横切能力](#7-横切能力)
8. [传输：stdio 与 Streamable HTTP](#8-传输stdio-与-streamable-http)
9. [授权与安全](#9-授权与安全)
10. [JSON Schema 与 `_meta`](#10-json-schema-与-_meta)
11. [扩展与生态](#11-扩展与生态)
12. [最佳实践（服务端）](#12-最佳实践服务端)
13. [最佳实践（客户端 / Host）](#13-最佳实践客户端--host)
14. [调试与交付](#14-调试与交付)
15. [参考链接](#15-参考链接)

---

## 1. 角色与架构

| 角色 | 职责 |
|------|------|
| **MCP Host** | 面向用户的 AI 应用（如 IDE、桌面客户端），负责协调一个或多个 **MCP Client** |
| **MCP Client** | 与**某一个** MCP Server 维持一条连接，替 Host 取回上下文、执行工具调用等 |
| **MCP Server** | 对外提供 Tools / Resources / Prompts 等能力；可本地进程，也可远程服务 |

要点：**一个 Server 对应一个 Client 连接**；Host 连多个 Server 时会实例化多个 Client。本地 **stdio** 型 Server 常为单客户端进程；远程 **Streamable HTTP** 型 Server 通常服务多客户端。

---

## 2. 协议分层：传输层与数据层

| 层次 | 内容 |
|------|------|
| **数据层** | 基于 **JSON-RPC 2.0** 的请求/响应/通知；生命周期、能力声明；Tools / Resources / Prompts 等原语语义 |
| **传输层** | 建连、帧格式、字节编码（UTF-8）、鉴权（尤其 HTTP）；对上层屏蔽「消息如何送达」 |

同一套 JSON-RPC 消息可跑在不同传输上，便于「实现一次协议、换传输不换语义」。

---

## 3. 消息模型：JSON-RPC 2.0

规范要求所有消息符合 [JSON-RPC 2.0](https://www.jsonrpc.org/specification)。MCP 在细节上比「最小 JSON-RPC」更严，例如：

- **Request**：必须带 **`id`**（字符串或整数），且 **`id` 不得为 `null`**；同一会话内发送方不得复用已用过的 `id`
- **Response**：成功时必须有 **`result`**；失败时为 **`error`**（含整数 **`code`** 与 **`message`**）
- **Notification**：**不得**带 `id`；单向、不期待响应

实现时需区分：**传输失败**（网络、HTTP 状态）与 **JSON-RPC 层错误**（例如工具业务失败可能仍以 200 + RPC 结果字段表达，视具体方法定义而定）。工具错误在规范中有 **`isError`** 等约定（见 [Tools - Error handling](https://modelcontextprotocol.io/specification/latest/server/tools)）。

---

## 4. 生命周期与能力协商

MCP 是**有状态**协议：连接建立后通过 **`initialize` / `initialized`** 等完成**协议版本**与 **capabilities** 协商。

- **`protocolVersion`**：双方必须协商到**共同支持的版本**，否则应终止连接
- **capabilities**：声明本端是否支持 tools、resources、sampling、elicitation 等；对端仅可依赖已协商的能力

详细状态机见规范：[Lifecycle](https://modelcontextprotocol.io/specification/latest/basic/lifecycle)。

---

## 5. 服务端原语：Tools / Resources / Prompts

这是多数 Server 开发者最关心的「对外暴露什么」。

| 原语 | 典型用途 | 发现 / 调用模式（概念上） |
|------|----------|---------------------------|
| **Tools** | 可执行动作：查库、调 API、改状态机等 | `tools/list` 发现；`tools/call` 执行（可带输入 JSON Schema） |
| **Resources** | 上下文数据：文件片段、文档、结构化记录等 | `resources/list` / `resources/read` 等（以规范为准） |
| **Prompts** | 可复用提示模板（含参数），便于客户端插入对话 | `prompts/list`；`prompts/get` 取模板与参数说明 |

设计意图：**列表可动态变化**；Server 可通过 **notification** 告知工具列表变更（如 `tools/listChanged`），Client 应刷新索引。

**Tools 与安全**：规范强调工具描述与实现可能被滥用（诱导模型调用危险操作等），Server 应在实现层做权限校验与审计，而不是仅依赖模型「自觉」。见 [Tools - Security considerations](https://modelcontextprotocol.io/specification/latest/server/tools)。

---

## 6. 客户端原语：Sampling / Elicitation / Roots / Logging

这些能力由 **Client（Host 侧）** 实现，使 Server 可以：

| 原语 | 作用 |
|------|------|
| **Sampling** | Server 向 Host 请求 **LLM 补全**（`sampling/createMessage`），避免 Server 自己绑模型 SDK，保持模型无关 |
| **Elicitation** | Server 向用户**索取信息或确认**（人机在环） |
| **Roots** | 声明/约束 Client 侧「根目录」等上下文边界（常与文件类工具有关） |
| **Logging** | Server 向 Client 输出结构化日志，便于宿主展示与排障 |

---

## 7. 横切能力

规范还提供跨原语的能力（具体以 `latest` 为准），常见包括：

- **Progress**：长任务进度上报
- **Ping**：存活检测
- **Cancellation**：取消进行中的请求
- **Pagination**：列表类结果分页
- **Tasks（实验性）**：可延迟取结果、跟踪状态的长任务包装

---

## 8. 传输：stdio 与 Streamable HTTP

### 8.1 stdio（标准输入输出）

- Client **拉起** Server 子进程；**一行一条** JSON-RPC 消息（**消息体内不得含未转义的换行**）
- Server **仅**向 **stdout** 写入合法 MCP 消息；**stderr** 可用于日志（Client 不应默认把 stderr 当「一定出错」）
- 规范建议：**只要条件允许，Client 应支持 stdio**

适用于本地、低延迟、无网络暴露场景。

### 8.2 Streamable HTTP（推荐用于远程）

取代旧版 **HTTP + SSE** 组合（协议 **2024-11-05** 中的旧传输；新版本见 [Transports](https://modelcontextprotocol.io/specification/latest/basic/transports)）。

要点摘要：

- 单一 **MCP 端点**同时支持 **POST** 与 **GET**
- Client 对 Server 的 JSON-RPC 消息主要用 **POST**；`Accept` 需同时声明 **`application/json`** 与 **`text/event-stream`**
- Server 对 POST 中的 **request** 可返回 **JSON 单对象** 或 **`text/event-stream`** 开启 SSE，以流式下发多条消息直至最终 **response**
- **GET** 可用于 Client 监听 Server 下行消息（若 Server 不支持则返回 **405**）
- **会话**：Server 可在初始化响应中返回 **`MCP-Session-Id`**，后续请求 Client **必须**带上；404 时 Client 应重新 `initialize`
- **协议版本头**：Client 应在后续 HTTP 请求中带 **`MCP-Protocol-Version`**（值为协商好的版本）

#### Streamable HTTP 安全警告（规范原文要求）

1. Server **必须**校验 **`Origin`**，防范 **DNS 重绑定**；非法 `Origin` 应 **403**
2. 本地监听宜 **仅绑定 localhost**，避免 `0.0.0.0` 暴露
3. 应对所有连接做**适当鉴权**

缺少这些时，恶意网页可能通过 DNS 重绑定访问用户机器上的本地 MCP Server。

### 8.3 自定义传输

允许自定义传输，但必须仍满足 JSON-RPC 与生命周期要求，并在文档中说明建连与消息边界。

---

## 9. 授权与安全

### 9.1 授权框架（HTTP）

- 使用 **HTTP 类传输**的实现**宜**遵循规范中的 [Authorization](https://modelcontextprotocol.io/specification/latest/basic/authorization)（OAuth 等）
- **stdio** 传输**不应**照搬 HTTP OAuth 流程；凭据宜来自**环境变量**等 Host 控制的面

教程与威胁模型见：

- [Understanding Authorization in MCP](https://modelcontextprotocol.io/docs/tutorials/security/authorization.md)
- [Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices.md)

### 9.2 典型风险（实现时要有对策）

| 风险 | 说明 |
|------|------|
| **DNS 重绑定** | 本地 HTTP Server 被恶意网页滥用；见上文 `Origin` 与绑定地址 |
| **Confused Deputy（OAuth 代理）** | MCP 作为「代理」对接第三方 IdP 时，静态 client_id、动态注册与第三方 consent cookie 组合不当，可导致**跳过用户同意**把授权码换给攻击者；代理型 Server 必须做**按客户端的同意与 redirect 校验** |
| **会话劫持** | `MCP-Session-Id` 需高熵、防泄露；HTTPS、Cookie 安全属性、服务端失效策略要完整 |
| **工具与提示注入** | 不可信数据进入 tool 参数或 resource 内容时，可能操纵模型行为；需输入校验、权限最小化、敏感操作二次确认 |
| **跨 Server 数据流** | 「代码模式」或多工具编排时，一个 Server 的输出是另一个 Server 的不可信输入 |

---

## 10. JSON Schema 与 `_meta`

### 10.1 JSON Schema

- 工具入参、elicitation 等广泛使用 **JSON Schema**
- 未写 `$schema` 时，默认方言为 **[JSON Schema 2020-12](https://json-schema.org/draft/2020-12/schema)**；实现**必须**支持 2020-12，并**应**文档化额外支持的方言

### 10.2 `_meta`

协议为扩展保留 **`_meta`** 字段：键名规则、反向 DNS 风格前缀、以及 `*.modelcontextprotocol.*` / `*.mcp.*` 等保留命名空间见规范 [General fields - `_meta`](https://modelcontextprotocol.io/specification/latest/basic/index#general-fields)。

### 10.3 `icons`（若实现 UI）

规范对 **icons** 的 URI 方案、禁止不安全的 scheme、防跟踪与 SVG 风险等有明确要求；Client 拉取图标时应**不带凭据**并做类型与大小限制（见规范 **icons** 小节）。

---

## 11. 扩展与生态

- **Extensions**：可选扩展集合见 [Extensions overview](https://modelcontextprotocol.io/extensions/overview.md)
- **MCP Registry**：发布与发现 Server 的流程见 [Registry](https://modelcontextprotocol.io/registry/about.md)
- **SEPs**：协议演进以 [Specification Enhancement Proposals](https://modelcontextprotocol.io/seps/index.md) 为线索

---

## 12. 最佳实践（服务端）

1. **工具设计**
   - 名称清晰、稳定；描述写清**副作用**与**权限范围**（规范对 tool 命名格式有 SEP 讨论，实现前查最新 SEP/规范）
   - 为工具提供严谨的 **`inputSchema`**；尽量提供 **`outputSchema`**，便于 Host 做类型化封装与校验
2. **错误语义**
   - 区分「参数不合法」「权限不足」「下游 API 失败」；与规范中 **tool 错误** 表达方式对齐，便于 Client 以异常或 `isError` 处理
3. **幂等与审计**
   - 写操作尽量幂等或带 idempotency key；记录 **request id / 会话** 便于排障
4. **资源与提示**
   - Resources：控制体积与分页；大文本优先摘要 + 按需 read
   - Prompts：参数默认值与边界写清楚，避免模型猜
5. **动态列表**
   - 工具增减时发 **list_changed** 类通知（若已声明支持），避免 Client 缓存过期
6. **远程部署**
   - 必做 TLS、鉴权、`Origin` 校验、仅本地则绑定 127.0.0.1；敏感操作走 OAuth 与最小 scope

---

## 13. 最佳实践（客户端 / Host）

官方 [Client Best Practices](https://modelcontextprotocol.io/docs/develop/clients/client-best-practices.md) 针对「多 Server、成百上千工具」的场景，核心建议如下。

### 13.1 渐进式工具发现（Progressive discovery）

- 不要每次会话开始时把**全部** `tools/list` 塞进模型上下文
- 当工具定义预计占上下文 **约 1%～5%**（可按产品调整）时，改为：
  - 提供轻量 **`search_tools`**（或等价元工具），只返回**名称 + 一行描述**
  - 需要时再 **`get_tool_details`** 拉取**单个**工具的完整 schema
- 监听 **`notifications/tools/list_changed`**，失效本地检索索引
- **按 Server 分组**展示工具，便于模型推理依赖关系

### 13.2 与「提示缓存」的交互

频繁增删工具定义会导致前缀缓存失效、费用上升。可：

- 新工具**追加在列表末尾**而非整体重排，或
- 对外只暴露稳定的 **`call_tool({ name, args })`** 元工具，使对外「工具列表」不变

### 13.3 程序化工具调用（Code mode / 沙箱）

让模型在**沙箱代码**里调用生成的 API，**中间结果不经过模型上下文**，仅返回摘要：

- 沙箱**无直连网络**；所有外呼经 Host **broker** 转发并带鉴权
- 对沙箱内发起的每一次 `tools/call` 仍要做**授权与确认策略**（批准脚本 ≠ 批准任意副作用）
- 设超时、内存上限；对 `console.log` 等回传做**截断与过滤**
- 将 MCP 的 **`isError: true`** 映射为可捕获异常，便于模型自我修复

### 13.4 动态 Server 管理

维护 Server **目录与描述**，按需 `enable_server` / `disable_server`，减少常驻连接与无关工具污染。

---

## 14. 调试与交付

- 使用 [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector.md) 对 Server 做交互式验证
- 阅读 [Debugging](https://modelcontextprotocol.io/docs/tools/debugging.md) 系统排错
- 发布到 Registry 或对内交付时，写清 **支持的 `protocolVersion`、传输方式、环境变量、OAuth 配置**

---

## 15. 参考链接

| 主题 | 链接 |
|------|------|
| 架构概览 | https://modelcontextprotocol.io/docs/learn/architecture.md |
| 规范首页（版本化） | https://modelcontextprotocol.io/specification/latest |
| 传输层 | https://modelcontextprotocol.io/specification/latest/basic/transports |
| 生命周期 | https://modelcontextprotocol.io/specification/latest/basic/lifecycle |
| 工具 | https://modelcontextprotocol.io/specification/latest/server/tools |
| 资源 | https://modelcontextprotocol.io/specification/latest/server/resources |
| 提示 | https://modelcontextprotocol.io/specification/latest/server/prompts |
| 客户端能力（Sampling 等） | https://modelcontextprotocol.io/specification/latest/client/ |
| 安全最佳实践 | https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices.md |
| 客户端最佳实践 | https://modelcontextprotocol.io/docs/develop/clients/client-best-practices.md |
| 官方 SDK 列表 | https://modelcontextprotocol.io/docs/sdk.md |

---

## 一句话总结

**MCP 用 JSON-RPC 在 Host–Client–Server 之间协商能力并交换 Tools / Resources / Prompts 等上下文；stdio 适合本地，远程用 Streamable HTTP 并务必处理 Origin、会话与 OAuth；Host 侧应对多工具做渐进发现或代码化编排，Server 侧应强 schema、强鉴权、清晰的错误与审计。**
