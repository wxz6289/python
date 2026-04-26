# LangChain 核心内容与最佳实践

LangChain 是一个面向 LLM 应用开发的框架，核心目标是把“模型调用、提示词、检索、工具、工作流编排、可观测性”组织成可维护、可扩展的工程体系。

---

## 1. LangChain 解决什么问题

只用“直接调用模型 API”通常会遇到这些问题：

- 提示词散落在代码里，难以复用和测试；
- 对话状态、上下文注入、结构化输出容易失控；
- RAG（检索增强生成）链路复杂，拼装成本高；
- Agent 调工具存在不稳定性，调试困难；
- 线上缺少可观测性（不知道模型为什么答错）。

LangChain 提供统一抽象，把这些能力模块化：

- **Model**：统一对接多种 LLM/Embedding 服务；
- **Prompt**：模板化管理提示词；
- **Chain / Runnable**：把步骤串成可组合工作流；
- **Retriever / VectorStore**：检索与知识库；
- **Memory / History**：对话历史管理；
- **Tool / Agent**：外部工具调用与决策；
- **Tracing**：调用链追踪与评估。

---

## 2. 核心组件（必须掌握）

## 2.1 Models（模型层）

- 职责：文本生成、函数调用、结构化输出、向量生成。
- 实践要点：
  - 封装统一模型入口，避免业务代码直接散调 SDK；
  - 按场景区分模型：路由模型（便宜快）与生成模型（质量高）；
  - 明确超参数（temperature、max_tokens、top_p）默认值并版本化。

## 2.2 Prompt Templates（提示词模板）

- 职责：把动态变量安全注入提示词。
- 实践要点：
  - 系统提示、开发者约束、用户输入分层；
  - 对关键提示词做版本标记（如 `v1`, `v2`）；
  - 在模板中明确输出格式，减少后处理成本。

## 2.3 Output Parser / Structured Output（结构化输出）

- 职责：将模型输出映射为 JSON/Pydantic 等结构。
- 实践要点：
  - 优先使用结构化输出而非自由文本；
  - 为解析失败设置重试与降级路径；
  - 对关键字段做 schema 校验（类型、枚举、必填）。

## 2.4 Runnable / Chain（工作流编排）

- 职责：将“提示词 -> 模型 -> 解析 -> 后处理”串成流水线。
- 实践要点：
  - 小链路可读性优先，复杂链路拆成可测试子步骤；
  - 把 I/O、LLM 调用、业务规则分层，便于 mock 和单测；
  - 为每个步骤附加 tracing 标签，方便问题定位。

## 2.5 Retriever + VectorStore（RAG 检索层）

- 职责：从知识库召回相关上下文供模型生成。
- 实践要点：
  - 优先“检索质量”而不是盲目增大上下文；
  - chunk 切分策略要与文档结构匹配（标题、段落、代码块）；
  - 检索返回后进行 rerank 或过滤，减少噪声上下文。

## 2.6 Tool / Agent（工具与代理）

- 职责：让模型调用外部系统（搜索、数据库、内部 API）。
- 实践要点：
  - 工具描述要清晰、入参 schema 严格；
  - 高风险工具必须加权限校验和参数白名单；
  - Agent 失败要可回退到固定链路，避免全流程不可控。

---

## 3. LangChain 典型架构

一个可落地的 LLM 应用常见分层：

1. **入口层**：HTTP/API/消息队列；
2. **编排层**：LangChain Runnable/Chain；
3. **能力层**：LLM、Retriever、Tools；
4. **数据层**：向量库、业务库、对象存储；
5. **观测层**：日志、Tracing、评估指标。

建议把“业务规则”放在编排层或独立服务，不要全部塞进提示词。

---

## 4. RAG 核心方法论（重点）

RAG 质量通常由以下环节共同决定：

- 文档清洗质量；
- chunk 切分策略；
- embedding 模型与向量库参数；
- 检索策略（相似度、混合检索、过滤）；
- 召回后重排；
- 最终回答提示词（引用约束、拒答策略）。

### 4.1 推荐 RAG 流程

1. 文档预处理（去噪、结构化）；
2. 合理 chunk（长度、重叠、按语义边界）；
3. 建索引并保存 metadata（来源、时间、权限）；
4. 检索 + 过滤 + 重排；
5. 生成答案并附带引用片段；
6. 记录 query/召回/答案用于离线评估。

### 4.2 常见错误

- chunk 太大导致上下文浪费，太小导致语义断裂；
- 无 metadata 过滤，召回到错误租户/错误版本文档；
- 把检索失败当“模型能力差”，没有先看召回命中率；
- 不做引用溯源，无法判断幻觉来源。

---

## 5. Agent 核心方法论

Agent 强在“动态决策 + 工具调用”，弱在“稳定性和可预测性”。

适合 Agent 的场景：

- 任务路径不固定，需要动态选择工具；
- 需要多步推理和外部操作；
- 用户问题开放、流程难以完全预定义。

不适合 Agent 的场景：

- 固定业务流程（推荐使用 Chain）；
- 强一致性、高审计要求流程（建议显式编排）；
- 高并发低延迟核心链路（Agent 成本高、波动大）。

### 5.1 新版 LangChain Agent 主要类型对比

新版 LangChain 的重点已经不是通过 `AgentType` 枚举选择大量内置 Agent，而是推荐用 `create_agent` 构建标准 Agent，并在复杂场景下下沉到 LangGraph 自定义执行图。

| 类型 | 典型 API / 方式 | 核心特点 | 适合场景 | 优点 | 注意点 |
| --- | --- | --- | --- | --- | --- |
| 标准工具调用 Agent | `create_agent(model, tools, system_prompt=...)` | 模型根据问题自动选择工具，执行工具后把结果放回上下文，再继续生成 | 搜索、查数据库、调用内部 API、执行计算等通用工具型任务 | 新版首选；接口简单；底层基于 LangGraph，支持流式、状态、持久化和中断 | 工具描述和参数 schema 必须清晰，否则容易误调用 |
| ReAct 风格 Agent | 新版通常通过 `create_agent` 的工具循环实现；旧版常见 `ZERO_SHOT_REACT_DESCRIPTION` | 按“思考 -> 行动 -> 观察 -> 再思考”的模式循环调用工具 | 需要多步推理、多工具协作、路径不固定的任务 | 可解释性较好，便于观察工具调用链路 | 推理链路长，成本和延迟更高；要限制最大轮数 |
| 结构化输出 Agent | `create_agent(..., response_format=Schema)` | Agent 最终输出符合 Pydantic / JSON Schema 等结构 | 表单抽取、任务分类、生成可落库结果、需要稳定字段的场景 | 比自由文本更容易进入业务系统；便于校验和重试 | 结构复杂时要处理解析失败和模型不完全遵循 schema 的情况 |
| 带记忆 / 持久化 Agent | `create_agent(..., checkpointer=..., store=...)` 或 LangGraph persistence | 把会话状态、工具结果、长期记忆保存到外部存储 | 多轮对话、用户画像、长期任务、跨请求恢复 | 支持中断恢复；上下文不依赖单次进程内存 | 要区分短期聊天历史和长期记忆；敏感信息需要脱敏和过期策略 |
| 带中间件 Agent | `create_agent(..., middleware=[...])` | 通过 middleware 在模型调用、工具调用、上下文管理前后插入逻辑 | 需要审计、脱敏、摘要、人工确认、动态模型选择的生产应用 | 横切能力可复用；比在业务代码里硬编码更清晰 | middleware 过多会增加调试复杂度，需要 tracing |
| Human-in-the-loop Agent | `HumanInTheLoopMiddleware`、`interrupt_before/after` | 在敏感工具调用前后暂停，等待人工批准或补充信息 | 支付、发邮件、删数据、改配置、执行生产操作 | 降低高风险自动化操作的事故概率 | 需要设计审批 UI、超时策略和幂等机制 |
| 自定义 LangGraph Agent | `StateGraph` / LangGraph 节点和边 | 把 Agent 拆成显式图：模型节点、工具节点、审核节点、路由节点等 | 复杂业务流、多阶段审批、多 Agent 协作、强可控流程 | 可控性最高；适合生产级复杂编排 | 开发成本高于 `create_agent`，需要先设计状态结构 |
| 多 Agent 协作 | 通常基于 LangGraph 自定义 supervisor / worker / handoff 流程 | 多个角色 Agent 分工协作，由主管 Agent 路由或汇总 | 复杂研究、代码生成、数据分析、任务拆解 | 角色职责清晰，可并行或分阶段处理复杂任务 | 容易放大成本和不确定性；需要明确停止条件和结果合并规则 |

### 5.2 旧版 AgentType 对比与迁移建议

旧版 LangChain 常通过 `initialize_agent(..., agent=AgentType.xxx)` 选择 Agent 类型，这类方式在新版中不再是首选。新项目建议优先使用 `create_agent` 或 LangGraph。

| 旧版类型 | 主要用途 | 新版建议 |
| --- | --- | --- |
| `ZERO_SHOT_REACT_DESCRIPTION` | 经典 ReAct Agent，根据工具描述零样本选择工具 | 用 `create_agent(model, tools)` 替代 |
| `STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION` | 支持多参数工具的结构化 Chat Agent | 用带 schema 的 tool + `create_agent` 替代 |
| `OPENAI_FUNCTIONS` | 基于 OpenAI function calling 的 Agent | 用支持 tool calling 的模型 + `create_agent` 替代 |
| `OPENAI_MULTI_FUNCTIONS` | 一次调用中可能选择多个 OpenAI function | 用现代 tool calling 模型和显式工具循环替代 |
| `CONVERSATIONAL_REACT_DESCRIPTION` | 带对话记忆的 ReAct Agent | 用 `create_agent` + `checkpointer` / message history 替代 |
| `CHAT_ZERO_SHOT_REACT_DESCRIPTION` | 面向 Chat Model 的零样本 ReAct Agent | 用 `create_agent` 替代 |
| `CHAT_CONVERSATIONAL_REACT_DESCRIPTION` | 面向 Chat Model 且带对话历史的 ReAct Agent | 用 `create_agent` + 持久化状态替代 |
| `SELF_ASK_WITH_SEARCH` | 通过搜索工具拆解问题并逐步回答 | 用搜索 tool + `create_agent`，或显式 LCEL / LangGraph 流程替代 |
| `REACT_DOCSTORE` | 面向文档库问答的 ReAct Agent | 多数场景改用 RAG Chain；复杂检索再接 Agent |

### 5.3 选择建议

- **优先选 Chain / Runnable**：流程固定、可预测、对稳定性要求高。
- **优先选 `create_agent`**：任务路径不固定，但主要是“模型 + 工具调用”的常规 Agent。
- **优先选结构化输出 Agent**：最终结果要进入数据库、接口或自动化流程。
- **优先选带 checkpointer 的 Agent**：需要多轮对话恢复、任务暂停继续、跨请求保存状态。
- **优先选 LangGraph 自定义 Agent**：需要复杂状态机、人工审批、多 Agent 协作或强可控流程。
- **谨慎使用多 Agent**：只有当任务天然可拆分为多个专业角色时再引入，否则会显著增加成本和不确定性。

### 5.4 Agent 最佳实践

- 限制可用工具数量，降低误调用概率；
- 工具入参严格 schema 化，避免自由文本直透后端；
- 设置 `max_iterations` 与超时，防止无限循环；
- 为每次工具调用落日志（输入、输出、耗时、错误）；
- 对关键操作使用“人审/二次确认”。

---

## 6. 生产最佳实践（工程视角）

## 6.1 提示词工程

- 提示词要“短、明确、可执行”，避免冗长背景；
- 显式定义边界：不知道就说不知道，禁止编造；
- 对结构化输出给出严格 JSON schema 示例；
- 使用 few-shot 时优先高质量少样本，不盲目堆样本。

## 6.2 可靠性与降级

- 设计超时、重试（指数退避）、熔断；
- 配置模型 fallback（高质量模型失败后退到低成本模型）；
- 对关键接口做幂等设计，避免重试导致副作用；
- 当检索失败时返回“可解释的失败信息”，而非强行作答。

## 6.3 成本与性能优化

- 监控 token 使用量（输入/输出分开）；
- 缓存稳定结果（如 embedding、常见问答）；
- 采用分层模型策略：分类/路由用小模型，最终生成用大模型；
- 控制上下文长度，优先提升召回质量而不是堆 token。

## 6.4 安全与合规

- 对用户输入做注入防护（Prompt Injection 防御）；
- 工具执行层做权限隔离和参数校验；
- 对敏感数据脱敏，日志中避免记录明文隐私；
- 多租户场景必须做 metadata 权限过滤。

## 6.5 可观测性与评估

- 全链路 tracing：请求 ID、模型、提示词版本、工具调用；
- 构建离线评估集（准确性、引用正确率、拒答准确率）；
- 建立线上反馈回路（用户评分 + 人工抽检）；
- 每次提示词/模型升级都要做 A/B 或回归测试。

---

## 7. 测试策略（强烈建议）

- **单元测试**：对解析器、工具封装、路由逻辑做 deterministic 测试；
- **集成测试**：覆盖“检索 -> 生成 -> 解析”完整链路；
- **回归测试**：固定一批高价值问题集，比较版本结果；
- **故障注入**：模拟模型超时、向量库异常、工具失败；
- **人工评审**：对关键业务答案做定期抽样。

---

## 8. 参考项目模板（建议）

推荐目录结构：

```text
app/
  chains/        # 可复用工作流
  prompts/       # 提示词模板（按版本管理）
  retrievers/    # 检索封装
  tools/         # 工具定义和参数 schema
  parsers/       # 输出解析与校验
  services/      # 业务服务层
  api/           # 接口层
tests/
  unit/
  integration/
```

这类结构的目标是：提示词、模型调用、业务逻辑、基础设施解耦，便于团队协作与演进。

---

## 9. 快速落地清单（Checklist）

- 明确单一业务目标，不要一开始就做“全能助手”；
- 先做非 Agent 版本（检索 + 生成）验证价值；
- 结构化输出 + schema 校验先落地；
- 接入 tracing 与 token 成本监控；
- 配置超时、重试、fallback；
- 建立评估集并持续回归；
- 最后再引入 Agent 扩展复杂任务。

---

## 10. 一句话结论

LangChain 的核心价值不是“把模型接上就能跑”，而是把 LLM 应用变成可工程化系统：可组合、可测试、可观测、可迭代。
