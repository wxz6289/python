# LangSmith 文档要点与最佳实践

以下内容依据 LangChain 官方文档站点当前结构整理（[LangSmith 主页](https://docs.langchain.com/langsmith/home)）。产品会持续演进，具体配额、定价与 UI 以官网为准。

---

## 1. LangSmith 是什么

LangSmith 被定位为 **与框架无关** 的一体化平台：在统一环境里完成 **追踪（Tracing）、评测（Evaluation）、提示词迭代（Prompt engineering）、部署（Deployment）** 以及 **平台与合规选型**，适用于各类 Agent 与 LLM 应用栈（不限于 LangChain）。

官方强调的串联路径：**从本地开发到生产**——观测 → 评测 → 部署 → 按基础设施需求选择云端 / 混合 / 自建（[Platform setup](https://docs.langchain.com/langsmith/platform-setup)）。

---

## 2. 文档体系中的核心模块

| 模块 | 作用摘要 |
|------|----------|
| **Observability（可观测性）** | 接入追踪、在 UI/API 中筛选与对比 Trace、仪表与告警、规则/Webhook/在线评测自动化、反馈与标注队列；内置 **Polly** 辅助分析 Trace（[Observability](https://docs.langchain.com/langsmith/observability)） |
| **Evaluation（评测）** | **离线评测**（上线前）与 **在线评测**（生产流量），数据集、评估器、实验与结果对比（[Evaluation](https://docs.langchain.com/langsmith/evaluation)） |
| **Deployment（部署）** | 以 **Agent Server** 为运行时：持久执行、流式输出、扩缩；用 **Deployment SDK**（`langgraph-sdk`）在代码里操作 Assistants / Threads / Runs / Cron；可与 Studio、RemoteGraph、MCP/A2A 等组合（见 §6；[Deployment](https://docs.langchain.com/langsmith/deployment)） |
| **Prompt engineering** | 提示词版本管理与协作迭代（首页「More ways to build」） |
| **Studio** | 连接本地或已部署的 Agent Server，可视化图、检查点、单步调试与分支探索（[Deployment 文档中的 Studio](https://docs.langchain.com/langsmith/deployment)） |
| **LangSmith CLI** | 在终端查询 Trace、数据集、实验等（首页说明） |
| **Fleet** | 可视化设计与部署 Agent（低代码方向，首页说明） |
| **Integrations** | 对接 OpenAI、Anthropic、LangChain/LangGraph、CrewAI、Vercel AI SDK、Pydantic AI 等（[integrations](https://docs.langchain.com/langsmith/integrations)） |

合规与部署形态：官方提及面向企业的 **HIPAA、SOC 2 Type 2、GDPR** 等（详见 Trust Center；商业方案需对接销售）。

---

## 3. 可观测性：数据模型（必读）

理解下面四层，后面所有筛选、评测与告警才有抓手（[Observability concepts](https://docs.langchain.com/langsmith/observability-concepts)）。

- **Project（项目）**：某一应用或服务的 Trace 容器；需将 Trace 打到指定项目（见 [Log traces to a project](https://docs.langchain.com/langsmith/log-traces-to-project)）。
- **Trace（追踪）**：**一次用户操作**对应一整条追踪；由多个 **Run** 组成，共享同一 trace id。可类比 OpenTelemetry 里「一次请求的一组 span」。
- **Run（运行）**：最小工作单元：一次 LLM 调用、一次检索、一次解析等；类比 **span**。
- **Thread（会话线程）**：多轮对话中，每一轮往往是一条 Trace，但通过同一标识串起来。文档约定可在 metadata 中使用 `session_id`、`thread_id` 或 `conversation_id`（[Threads](https://docs.langchain.com/langsmith/threads)）。

**限制**：单条 Trace 最多 **25,000** 个 Run；超出后该 Trace 上新增的 Run 会被拒绝—— Agent 或超长流水线需要控制拆分粒度或子 Trace 策略。

**数据保留（SaaS）**：Trace 自写入起约 **400 天** 后删除；超出保留期的用法之一是把重要样本加入 **Dataset**，数据集可长期保留（详见文档 [Data retention](https://docs.langchain.com/langsmith/observability-concepts#data-retention) 与计费说明）。

---

## 4. 如何产生 Trace：集成 vs 手动埋点

1. **集成（自动埋点）**  
   使用受支持的框架/SDK 时，通常只需配置环境变量等，即可采集输入输出与元数据（等价于广义上的 auto-instrumentation）。

2. **手动埋点**  
   任意代码可用：Python 的 `@traceable` / `traceable`、`trace` 上下文管理器，或 **RunTree** 等低级 API（[Annotate code](https://docs.langchain.com/langsmith/annotate-code)）。

**实践要点**：生产环境对「哪些路径必须带 Trace」要有清单；高流量路径可配合采样（见下文最佳实践）。

---

## 5. 评测体系：离线 vs 在线

### 5.1 离线评测（上线前）

典型流程（[Evaluation](https://docs.langchain.com/langsmith/evaluation)）：

1. **Dataset**：人工用例、历史生产 Trace、或合成数据构成样本集（[Manage datasets](https://docs.langchain.com/langsmith/manage-datasets)）。
2. **Evaluators（评估器）**：人工标注、**代码规则**、**LLM-as-judge**、**成对比较（Pairwise）** 等（[Evaluators 概念](https://docs.langchain.com/langsmith/evaluation-concepts#evaluators)）。
3. **Experiment（实验）**：在数据集上跑你的应用，形成可对比实验；可配置 **重复次数、并发、缓存** 等（[Experiment configuration](https://docs.langchain.com/langsmith/experiment-configuration)）。
4. **分析**：用于基准（benchmark）、单元测试、回归测试、回溯（backtesting）等场景（[Evaluation types](https://docs.langchain.com/langsmith/evaluation-types)）。

### 5.2 在线评测（生产）

- 每次真实交互产生 **Run**（通常无标准答案）。
- 配置 **在线评估器** 自动作用于生产 Trace：安全、格式、质量启发式、**无参考输出的 LLM 评判** 等。
- 使用 **过滤条件 + 采样率** 控制成本与覆盖面（文档：[Online evaluations](https://docs.langchain.com/langsmith/online-evaluations-llm-as-judge)）。
- 多轮场景可对 **Run** 或 **Thread** 做在线评测（[Multi-turn online evaluations](https://docs.langchain.com/langsmith/online-evaluations-multi-turn)）。

### 5.3 闭环

官方推荐路径：**把线上失败的 Trace 加入 Dataset → 针对性加/调 Evaluator → 离线实验验证修复 → 再发布**，形成持续改进回路。

---

## 6. 部署（LangSmith Deployment）

### 6.1 平台能力（与文档对齐）

- **定位**：面向 Agent 负载的 **编排与运行时**，支持持久执行、流式输出、水平扩展；**框架无关**，例如可部署 LangGraph 或其他框架构建的 Agent（[Deployment](https://docs.langchain.com/langsmith/deployment)）。
- **核心抽象**：**Agent Server**——底层能力包括 **Assistants**（助手配置）、**Threads**（跨轮次状态）、**Runs**（一次执行）等；文档中的部署形态与 Studio / CI/CD 仍适用前述章节。
- **Plus 计划**：文档写明 Deployment 需 **Plus 及以上**；BYOC 与高级支持需联系商务。
- **交付形态**：云端完全托管、混合（控制面托管 + 数据面在你方云）、完全自建；同一套运行时 API，差异在运维边界（[Platform setup](https://docs.langchain.com/langsmith/platform-setup)）。
- **生态连接**：**RemoteGraph**（远程调用已部署的图）、**MCP**、**A2A**、自定义路由/中间件/鉴权等（同 [Deployment](https://docs.langchain.com/langsmith/deployment)）。

### 6.2 Deployment SDK（重点：`langgraph-sdk`）

官方 Python 参考入口：[Deployment SDK](https://reference.langchain.com/python/langsmith/deployment-sdk)（文档注明 **Formerly LangGraph Platform**，实现包为 **`langgraph-sdk`**，与「LangSmith 上的已部署 Agent / LangGraph API」对话）。

| 要点 | 说明 |
|------|------|
| **包名** | PyPI：`langgraph-sdk`（与 Reference 中「完整 API 见 langgraph-sdk 包文档」一致） |
| **职责** | 提供 **异步 / 同步** 客户端，管理 **assistants、threads、runs、cron jobs**，以及 **认证相关工具** |
| **顶层入口** | `get_client()` → 返回 `LangGraphClient`（异步）；另有 **`SyncLangGraphClient`** 用于同步场景（见 Reference 同一页） |
| **客户端分层** | `LangGraphClient` 通过属性暴露子客户端，典型包括 **`assistants`、`threads`、`runs`、`crons`**，以及 **`store`**（与 Reference 总览一致） |
| **领域模型（Schema）** | `Assistant`、`Config`、`Interrupt`、`Checkpoint`、`StreamMode` 等：助手、单次调用配置、中断、检查点、流式模式（详见 [langgraph-sdk](https://pypi.org/project/langgraph-sdk/) 包内 API） |

#### `get_client()`：连接方式（可操作性）

参考：[get_client](https://reference.langchain.com/python/langgraph-sdk/_async/client/get_client)。

- **`url`**  
  - 传入部署的 **LangGraph / Agent Server 基地址**（示例：`http://localhost:8123`）→ **远程 HTTP** 访问。  
  - **`url=None`**：优先尝试 **进程内（in-process）** 连接（ASGI）；仅当你在 **Agent Server 进程内** 使用该客户端时才有意义，用于同进程内调用已注册的图（文档示例用 `client.runs.wait(...)` 调子 Agent）。
- **`api_key`**  
  - **默认**：从环境变量按顺序读取 **`LANGGRAPH_API_KEY` → `LANGSMITH_API_KEY` → `LANGCHAIN_API_KEY`**。  
  - 显式传入 **`api_key=None`**：关闭上述自动加载（适用于本地无密钥或自管网关）。
- **`headers` / `timeout`**：自定义鉴权头、控制超时（默认 read/write 偏长，适合长流式任务）。

#### 最小异步示例（远程服务）

```python
import asyncio
from langgraph_sdk import get_client

async def main() -> None:
    client = get_client(url="http://localhost:8123")  # 或云部署的 LangGraph API 根 URL
    # 子客户端：client.assistants | .threads | .runs | .crons | .store
    await client.assistants.get(assistant_id="YOUR_ASSISTANT_ID")
    # 接着：await client.threads.create(...) → client.runs.stream(...)

asyncio.run(main())
```

典型流程（需与你的部署上实际存在的 `assistant_id` 一致）：**创建 / 获取 Thread → 在 Thread 上发起 Run → `stream` 或 `wait` 取结果**。Threads 负责 **跨多次调用的状态持久**（与 §3 中「会话」概念一致：部署侧用 `thread_id` 维持续跑）。

#### 与同步代码

若业务线程不能使用 `asyncio`，使用 Reference 中的 **`SyncLangGraphClient`**，避免在同步视图里硬塞 `asyncio.run()` 导致嵌套事件循环问题。

#### 实践清单（部署 SDK）

1. **先定连接模式**：仅本地 sidecar / 本机开发 → 远程 `url`；在 Agent Server 内嵌二次调用 → 再考虑 `url=None` 进程内路径。  
2. **密钥**：生产用 **`LANGGRAPH_API_KEY`（或文档允许的等价变量）** 注入，勿写死在仓库；CI 用密钥仓注入同一变量名。  
3. **Thread 为先**：多轮对话必须先 **`threads.create()`（或复用已有 thread_id）**，再在 **`runs.stream` / `runs.wait`** 上挂输入，避免「每轮新建 thread」丢失状态。  
4. **流式 vs 阻塞**：对用户暴露 SSE/WebSocket 时用 **`runs.stream`**（结合 **`StreamMode`**）；批处理或后端编排可用 **`wait`** 简化错误处理。  
5. **Cron**：定时任务走 **`client.crons`**（Reference 与 Deployment 文档中的计划任务一致），与人工触发的 `runs` 分开监控。  
6. **人机回路**：关注 **`Interrupt`** 与检查点相关 API，与 Studio 里「暂停 / 恢复」路径对齐后再写客户端逻辑。  
7. **版本**：以 PyPI 当前 `langgraph-sdk` 与 [LangChain Reference](https://reference.langchain.com/python/langsmith/deployment-sdk) 为准升级，Breaking Change 常出现在子客户端方法名上。

---

## 7. 最佳实践（汇总）

### 7.1 可观测性

- **项目划分**：按环境（dev/staging/prod）或服务边界拆 Project，避免所有 Trace 混在一个项目里难以做权限与告警。
- **Thread 元数据**：多轮对话务必稳定传入 `session_id` / `thread_id` / `conversation_id` 之一，便于按会话排障与在线评测。
- **Tags 与 Metadata**：用 tag 做粗分类（如 `agent:v2`），metadata 放版本号、租户 id、模型名等可筛选字段（[add-metadata-tags](https://docs.langchain.com/langsmith/add-metadata-tags)）。
- **Run 数量**：注意单 Trace 25k Run 上限；超深 Agent 树或无限循环会触发拒绝，需在代码层限制深度与工具调用次数。
- **反馈（Feedback）**：对关键 Run 打结构化反馈（标签 + 分数），便于后续训练数据筛选与评估器对齐。
- **保留策略**：需要长期留存的用例 **写入 Dataset**，不要仅依赖 Trace 在线保留期。

### 7.2 评测

- **离线优先兜底**：核心路径至少有一份回归集 + CI 可跑的实验，避免仅靠线上抽样。
- **评估器分层**：廉价规则 / 代码检测先行，再对子集用 LLM-as-judge，平衡成本与覆盖率。
- **在线评测**：必须配 **采样率与过滤**（例如仅对新版本 tag、或仅含某工具的 Trace），避免全量 LLM 评判导致费用与延迟失控。
- **实验对比**：模型或 Prompt 变更用同一 Dataset、固定随机性与缓存策略，再对比实验指标（参考 [Experiment configuration](https://docs.langchain.com/langsmith/experiment-configuration)）。

### 7.3 安全与合规

- 向 Trace 写入内容前做 **PII/密钥脱敏**；metadata 中避免明文密钥。
- 有合规要求时优先查阅官方 **Trust / Platform setup**，评估自建或混合部署。

### 7.4 与开发流程结合

- 将「Dataset + 离线实验」纳入发布门禁；线上告警与在线评测结果再反哺 Dataset。
- 使用 **Studio** 调试 Agent Server 与检查点，缩短「本地可跑、线上行为不一致」的定位时间。

### 7.5 调用已部署 Agent（Deployment SDK）

- **同一套 API 键习惯**：运维给网关的 key 与 `get_client` 读取顺序一致，避免本地能跑、线上因变量名不同 401。  
- **超时**：生产对 `timeout` 分级——交互读路径略短、批处理/长 Agent 链保持默认或单独客户端实例。  
- **可观测**：业务侧打 **`assistant_id` / `thread_id` / `run_id`** 日志，与 LangSmith Trace、Deployment 控制台三方对照排障。  
- **不要把 Deployment SDK 与「Tracing SDK」混为一谈**：前者管 **远程运行图**，后者管 **把本地调用的 span 送上 LangSmith**；一个服务可以两者同时用。

---

## 8. 官方入口速查

| 主题 | 链接 |
|------|------|
| 总览 | https://docs.langchain.com/langsmith/home |
| 可观测性 | https://docs.langchain.com/langsmith/observability |
| 概念（Project / Trace / Run / Thread） | https://docs.langchain.com/langsmith/observability-concepts |
| 评测总览 | https://docs.langchain.com/langsmith/evaluation |
| 部署 | https://docs.langchain.com/langsmith/deployment |
| **Deployment SDK（Python Reference）** | https://reference.langchain.com/python/langsmith/deployment-sdk |
| **get_client（langgraph-sdk）** | https://reference.langchain.com/python/langgraph-sdk/_async/client/get_client |
| 集成列表 | https://docs.langchain.com/langsmith/integrations |
| 全文档索引（llms.txt） | https://docs.langchain.com/llms.txt |

---

## 9. 文档维护说明

LangSmith 功能面宽（观测、评测、部署、提示词、CLI、Fleet 等），且商业能力与保留策略会更新。**以 [LangSmith 官方文档](https://docs.langchain.com/langsmith/home) 与控制台说明为准**；若你发现本文与官网不一致，应以官网为准并酌情更新本页。
