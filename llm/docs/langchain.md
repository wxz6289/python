SpringAI/Langchain
Dify/RAG Flow/DB-GPT/MaxKB

RAG
Agent

大模型问题

- 知识冻结
- 幻觉

Fine-tuned model 精调/微调

宵

除草必加
消烟秀去津

核心组件

- Components
-

Transformer
RLHF
MoE Mixture of Experts，专家混合 委员会模型  通才模型（稠密模型）
通过一种“分而治之”的架构，巧妙地解决了模型规模扩大带来的计算成本爆炸性增长问题，是实现**万亿参数级别模型**的关键。

LLM

### **1. 核心定义**

- **参数量巨大**：通常指千亿（100B+）级别参数，例如GPT-3（1750亿参数）、GPT-4（约1.8万亿）、PaLM（5400亿）等。
- **预训练+微调范式**：先在无标注海量文本上学习通用语言规律（预训练），再通过指令微调、人类反馈强化学习（RLHF）等对齐人类需求。

---

### **2. 关键技术特点**

- **涌现能力**：当参数规模超过临界点（如100亿）时，模型会“涌现”出小模型不具备的能力，如复杂推理、代码生成、跨领域知识整合等。
- **上下文学习**：无需额外训练，仅通过提示（Prompt）中的示例就能学习新任务。
- **多模态扩展**：新一代大模型可处理文本、图像、音频等多模态输入（如GPT-4V、Gemini）。

---

### **3. 典型应用场景**

- **生成与创作**：文本生成、代码编写、剧本创作等。
- **知识问答**：基于训练时学习的知识回答复杂问题（需注意时效性）。
- **工具调用**：通过API连接计算器、搜索引擎、专业软件（如ChatGPT的插件系统）。
- **智能体（Agent）**：能规划任务、调用工具完成复杂目标（如AutoGPT）。

- **Transformer架构**：基于自注意力机制，支持并行训练，成为大模型的基础。
- **Scaling Law（缩放定律）**：模型性能随参数、数据、计算量增加而可预测提升。
- **对齐（Alignment）**：通过RLHF等技术使模型输出符合人类价值观。
- **开源vs闭源**：
  - 闭源：GPT-4、Claude（商业化，能力强但透明度低）。
  - 开源：Llama、ChatGLM、Qwen（可定制、可私有部署）。

## LangChain 新版预制链与 Memory 总结

### 1) 预制文档链（Document Combine Chains）

新版 LangChain 在文档处理里常用三种组合策略，核心区别是“怎么把多段文档喂给模型”。

| 策略 | 典型函数 | 适用场景 | 优点 | 风险/代价 |
| --- | --- | --- | --- | --- |
| Stuff | `create_stuff_documents_chain` | 文档总量较小、上下文放得下 | 实现最简单、速度快 | 容易超上下文长度 |
| Map-Reduce | `create_map_reduce_documents_chain` | 文档很多、单次放不下 | 可扩展到长文档 | 多次调用模型，成本更高 |
| Refine | `create_refine_documents_chain` | 需要逐步迭代提炼答案 | 对细节保留较好 | 顺序依赖强、延迟高 |

实践建议：

- 小文档优先 `stuff`，简单直接。
- 长文档优先 `map_reduce`，稳定且容易并行。
- 对答案质量要求高、可接受更高延迟时用 `refine`。

---

### 2) 新版 Memory 主路径（LCEL）

新版更推荐“LCEL + Message History”组合，而不是依赖旧链式 Memory 类。

核心组件：

- `RunnableWithMessageHistory`：给任意 LCEL 链注入会话历史。
- `InMemoryChatMessageHistory`：进程内存储会话消息（简单演示常用）。
- `MessagesPlaceholder`：在 Prompt 中显式插入历史消息。

典型模式：

1. 用 `ChatPromptTemplate` 定义 `system/history/input` 结构。
2. 用 `RunnableWithMessageHistory` 包装链。
3. 通过 `session_id` 区分用户会话。

---

### 3) 常见记忆策略（从短时到长时）

#### A. 全量对话缓存（Buffer）

- 思路：保存全部历史对话并每轮都注入。
- 优点：实现最简单。
- 缺点：上下文会持续增长，最终超模型限制。

#### B. 窗口记忆（Window）

- 思路：仅保留最近 N 轮（或最近 M 条消息）。
- 优点：稳定控制上下文长度。
- 缺点：较早信息容易丢失。

#### C. 相关性检索记忆（Relevance-based）

- 思路：从历史中筛选与当前问题最相关的片段，再注入模型。
- 优点：在有限上下文里提升信息密度。
- 缺点：检索策略不好会漏关键信息。

#### D. 实体记忆（Entity Memory）

- 思路：抽取结构化实体（如姓名、职业、地点、宠物）并存储为键值或对象。
- 优点：稳定事实不会随对话窗口丢失。
- 缺点：需要额外抽取步骤与冲突更新逻辑。

#### E. 知识图谱记忆（KG Memory）

- 思路：把记忆组织为三元组 `(subject, relation, object)`，按问题检索相关关系。
- 优点：适合“关系型记忆”和可解释推理。
- 缺点：构图和检索复杂度更高。

#### F. 摘要记忆（Summary Memory）

- 思路：将旧对话压缩成“长期摘要”，只保留最近原文窗口。
- 优点：压缩率高，适合长会话。
- 缺点：摘要质量决定记忆质量，可能引入信息损失。

#### G. Token 阈值触发刷新

- 思路：不是按轮数，而是按 token 长度触发摘要/裁剪。
- 优点：更贴合模型上下文上限。
- 缺点：需要 token 估算或 tokenizer 支持。

#### H. 向量数据库长时记忆

- 思路：将历史对话/摘要向量化存入向量库（FAISS/Chroma 等），按语义检索。
- 优点：可扩展、跨会话复用、语义检索能力强。
- 缺点：引入嵌入模型、索引维护和检索误召回问题。

---

### 4) 旧版 Memory 类与新版替代关系

旧教程中常见：

- `ConversationBufferMemory`
- `ConversationBufferWindowMemory`
- `ConversationSummaryMemory`
- `ConversationKGMemory`

新版迁移建议：

- 使用 `RunnableWithMessageHistory` 替代“黑盒 Memory 注入”。
- 将“窗口/摘要/实体/KG/向量检索”作为显式策略实现到业务代码。
- 通过 LCEL 组合链路，减少版本升级时的 API 断裂风险。

---

### 5) 选型建议（实战）

- 首选组合：`短窗口 + 摘要 + 向量检索`（兼顾时效、长度、召回）。
- 如果是强事实场景（CRM/客服）：叠加“实体记忆”。
- 如果是关系推理场景（人物关系、事件链）：叠加“知识图谱记忆”。
- 若成本敏感：先窗口策略，再按需加摘要与向量库。

---

### 6) LCEL（LangChain Expression Language）

LCEL 是新版 LangChain 推荐的链路编排方式。
它把 Prompt、Model、Parser、Retriever、Tool 等组件都抽象成 `Runnable`，再用管道符 `|` 组合起来。

#### 核心思想

- **一切皆 Runnable**：Prompt、模型、解析器、函数包装器都可以作为链路节点。
- **用 `|` 表示顺序执行**：前一个节点的输出会作为后一个节点的输入。
- **链路是显式的**：每一步怎么处理输入、怎么传递输出都更清楚。
- **天然支持 invoke/batch/stream**：同一条链可以单次调用、批量调用、流式输出。

最小示例：

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template("请用一句话介绍 {topic}")
chain = prompt | llm | StrOutputParser()

result = chain.invoke({"topic": "LCEL"})
```

#### 常见调用方式

| 方法 | 含义 | 适用场景 |
| --- | --- | --- |
| `invoke(input)` | 单次调用 | 普通问答、单条任务 |
| `batch(inputs)` | 批量调用 | 多条文本分类、批处理 |
| `stream(input)` | 流式输出 | 聊天机器人、实时生成 |
| `ainvoke(input)` | 异步单次调用 | async 应用 |
| `abatch(inputs)` | 异步批量调用 | 高并发批处理 |

#### 常用组件

- `PromptTemplate` / `ChatPromptTemplate`：把变量格式化成 prompt 或 messages。
- `ChatOpenAI` / 其他模型：负责模型调用。
- `StrOutputParser`：把模型输出转成字符串。
- `JsonOutputParser` / Pydantic parser：把模型输出转成结构化数据。
- `RunnableLambda`：把普通 Python 函数包装进链路。
- `RunnablePassthrough`：保留原始输入，并追加中间字段。

#### 管道符组合

```python
chain = prompt | llm | StrOutputParser()
```

执行流程：

1. `prompt` 接收字典输入，生成 PromptValue。
2. `llm` 接收 PromptValue，返回模型消息。
3. `StrOutputParser` 提取文本内容。

#### RunnableLambda

当链路中需要插入普通 Python 逻辑时，可以使用 `RunnableLambda`。

```python
from langchain_core.runnables import RunnableLambda

def clean_text(text: str) -> str:
    return text.strip()

chain = prompt | llm | StrOutputParser() | RunnableLambda(clean_text)
```

#### RunnablePassthrough.assign

`RunnablePassthrough.assign(...)` 常用于保留原始输入，同时增加中间结果。

```python
from langchain_core.runnables import RunnablePassthrough

chain = (
    RunnablePassthrough.assign(query=write_query_chain)
    .assign(result=lambda x: db.run(x["query"]))
    | answer_prompt
    | llm
    | StrOutputParser()
)
```

这个模式很适合 SQL / RAG：

- 原始问题保留在 `question`。
- 中间生成的 SQL 存到 `query`。
- SQL 执行结果存到 `result`。
- 最后一起交给模型生成答案。

#### 并行输入

LCEL 可以用字典把多个 Runnable 并行执行，再合并结果。

```python
chain = {
    "context": retriever,
    "question": RunnablePassthrough(),
} | prompt | llm | StrOutputParser()
```

常见于 RAG：

- `retriever` 根据问题检索上下文。
- `RunnablePassthrough()` 保留原始问题。
- `prompt` 同时接收 `context` 和 `question`。

#### 与旧 Chain 的区别

| 旧式 Chain | LCEL |
| --- | --- |
| 封装较重，内部步骤不够显式 | 每一步组合关系清楚 |
| 版本升级时类名容易变化 | 基于 `Runnable` 统一抽象 |
| 自定义中间逻辑较麻烦 | 可用 `RunnableLambda` 灵活插入 |
| 调试依赖具体 Chain 类 | 可逐段 invoke 调试 |

#### 实战建议

- 新项目优先使用 LCEL：`prompt | model | parser`。
- 复杂链路先拆成小链，再组合成大链。
- 对关键中间结果使用 `assign` 命名，方便调试。
- RAG、SQL、Memory 这类多步骤流程，优先用 LCEL 显式表达。
- 如果流程变成复杂状态机、多分支、多循环，再考虑升级到 LangGraph。

---

### 7) 对话模型 vs 非对话模型（新版 LangChain 视角）

#### 基本定义

- **对话模型（Chat Model）**：输入是消息序列（system/user/assistant/tool），输出是一条消息。
  在 LangChain 中通常用 `ChatOpenAI` 一类接口。
- **非对话模型（Text/Completion Model）**：输入是单段文本 prompt，输出是文本补全。
  在 LangChain 中通常用 `LLM` 类接口。

#### 输入输出形式对比

| 维度 | 对话模型 | 非对话模型 |
| --- | --- | --- |
| 输入 | 多消息结构（role + content） | 单文本字符串 |
| 输出 | `AIMessage`（可带 tool calls 等结构） | 文本字符串 |
| 上下文组织 | 天然支持多轮对话 | 需手动拼接历史 |
| 工具调用 | 原生更友好（函数/工具调用） | 需额外解析与约束 |

#### 在 LangChain 中的常用组件

- 对话模型常配：
  - `ChatPromptTemplate`
  - `MessagesPlaceholder`
  - `RunnableWithMessageHistory`
  - `create_agent`（工具调用/Agent）
- 非对话模型常配：
  - `PromptTemplate`
  - 纯文本生成链（`prompt | llm | parser`）

#### 适用场景

- **优先用对话模型**：
  - 聊天机器人、Copilot、Agent
  - 需要工具调用、结构化对话、会话记忆
  - 多轮上下文管理复杂的系统
- **可用非对话模型**：
  - 单轮文本改写、摘要、分类、抽取
  - 固定模板批处理任务
  - 不需要对话状态与工具调用的离线任务

#### 成本与复杂度

- 对话模型：
  - 优点：语义更稳定、对多轮和工具更友好；
  - 代价：消息结构更复杂，调试时要关注 role 与历史注入方式。
- 非对话模型：
  - 优点：接口简单、适合流水线批处理；
  - 代价：需要自己处理历史拼接、工具协议和状态管理。

#### 迁移建议（老代码到新版）

- 如果你在做 Agent / Chat / Memory，建议统一迁移到：
  - `ChatPromptTemplate + ChatModel + RunnableWithMessageHistory`
- 如果你在做离线文本处理，可继续保留文本 LLM 链，但建议：
  - 显式模板化输入
  - 统一输出解析器
  - 需要多轮时再升级到 Chat 模型

#### 一句话选型

- **默认优先对话模型**（尤其是 LangChain 新版 Agent 与 Memory 场景）。
- **只有在任务明确是单轮纯文本补全时**，再考虑非对话模型。

### 8) 消息类型（Message Types）速览

在 LangChain 的对话链路里，模型输入不是一整段字符串，而是“消息列表”。
每条消息都带有类型（可理解为 role）和内容，模型会按顺序读取。

#### 常用消息类型

- `SystemMessage`：
  - 用于定义全局行为、身份和边界（例如“你是一个严谨的 Python 助手”）。
  - 通常放在消息列表最前面，影响整轮对话风格与规则。
- `HumanMessage`：
  - 表示用户输入的问题或指令。
  - 在多轮场景中会不断追加，构成用户侧历史。
- `AIMessage`：
  - 表示模型历史回复。
  - 可包含普通文本，也可包含工具调用元数据（不同模型字段可能不同）。
- `ToolMessage`：
  - 表示工具执行结果回传给模型的消息。
  - 常用于 Agent 流程，让模型基于工具结果继续推理和回答。

#### 与 role 的对应关系（便于理解）

| LangChain 消息类 | 常见 role 概念 | 主要用途 |
| --- | --- | --- |
| `SystemMessage` | `system` | 设定规则/身份/风格 |
| `HumanMessage` | `user` | 用户问题与指令 |
| `AIMessage` | `assistant` | 模型回复与工具调用意图 |
| `ToolMessage` | `tool` | 工具执行结果回填 |

#### 最小示例（消息列表）

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="你是一个简洁的 Python 助手。"),
    HumanMessage(content="解释一下列表推导式。"),
]
```

#### 实战建议

- 在 Agent/工具调用场景，优先使用标准消息类型，避免手写 role 字符串导致格式不一致。
- 让 `system` 约束稳定、简短、可测试；把变化需求放到 `human` 消息里。
- 配合 `MessagesPlaceholder("history")` 管理历史，避免把历史手工拼成大字符串。

### 9) Toolkit（工具包）介绍

在 LangChain 中，`Tool` 是 Agent 可以调用的单个能力；`Toolkit` 是一组相关工具的集合。
简单理解：**Tool 是一个函数能力，Toolkit 是一组函数能力的打包方案**。

#### Tool vs Toolkit

| 概念 | 含义 | 示例 |
| --- | --- | --- |
| `Tool` | 单个可调用工具 | 查询天气、执行 SQL、搜索网页 |
| `Toolkit` | 多个相关 Tool 的集合 | SQL 工具包、文件系统工具包、检索工具包 |

使用 Toolkit 的好处：

- 把同一类能力统一封装，减少手动拼工具列表。
- 适合 Agent 场景，Agent 可以根据工具描述自动选择调用哪个工具。
- 便于复用，比如多个 Agent 都可以共享同一套数据库工具或文件工具。

#### 常见 Toolkit 类型

- **SQL Toolkit**：
  - 用于让 Agent 查询数据库。
  - 常见能力包括列出表、查看表结构、执行 SQL 查询等。
  - 适合“自然语言问数据库”的场景。
- **Retriever Toolkit**：
  - 把检索器包装成工具，让 Agent 可以主动检索文档。
  - 常用于 RAG。
- **File System Toolkit**：
  - 让 Agent 读取、写入或搜索本地文件。
  - 使用时要注意权限边界，避免误删或覆盖重要文件。
- **API Toolkit**：
  - 把外部 API 封装成一组工具。
  - 适合 CRM、工单系统、天气、搜索、GraphQL 等接口调用。
- **自定义 Toolkit**：
  - 当多个工具属于同一个业务域时，可以自己封装成 toolkit。
  - 例如“订单工具包”：查询订单、创建退款、更新物流状态。

#### 基本使用思路

Toolkit 通常会暴露一个 `get_tools()` 方法，把内部工具列表交给 Agent。

```python
tools = toolkit.get_tools()

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个可以使用工具完成任务的助手。",
)
```

如果不使用 Toolkit，也可以直接传入手写工具：

```python
agent = create_agent(
    model=llm,
    tools=[search_tool, sql_tool, calculator_tool],
)
```

#### SQL Toolkit 场景理解

SQL Toolkit 本质上是把数据库操作拆成多个工具，例如：

- 查看有哪些表。
- 查看某张表的字段结构。
- 检查 SQL 是否合理。
- 执行 SQL 查询。

Agent 收到“哪个学生 LangChain 成绩最高？”这类问题时，大致流程是：

1. 先查看数据库表结构。
2. 判断需要关联哪些表。
3. 生成 SQL。
4. 执行 SQL。
5. 根据结果组织自然语言回答。

#### 实战建议

- 简单任务：直接用 `@tool` 定义少量工具即可。
- 工具数量变多、属于同一业务域时：考虑封装成 Toolkit。
- 涉及数据库、文件、外部系统时：工具描述要写清楚输入、输出和限制。
- 对高风险工具（删除、转账、发邮件等）：建议增加人工确认或权限校验。
- 新版 LangChain / LangGraph 场景中，Toolkit 仍然是“组织工具”的方式，最终交给 Agent 的通常还是 `tools` 列表。

## 1）通用 LLM 应用/链路编排框架

- **LlamaIndex**：偏 RAG/数据摄取与索引（把文档/数据变成可检索结构），也支持工具与工作流。
- **Haystack**：偏企业级搜索与问答（RAG 为主），也支持工作流编排与组件化。
- **DSPy**：以“声明式/优化”思路做提示与推理链的自动优化，适合做研究型或需要持续改进的系统。
- **Semantic Kernel（SK）**：微软生态相关，强调“skill（技能）”与插件式能力编排。
- **CrewAI**：更偏“多智能体协作/角色分工”的编排框架。
- **AutoGen**：更偏“多智能体对话/协作”的框架（偏研究与实验风格）。
- **LangGraph**（LangChain 官方子项目）：如果你只是想要更强的状态机/有向图工作流能力，它是同生态的替代/增强路线。

## 2）面向多智能体/对话编排的框架

- **Microsoft AutoGen**：多智能体对话、协同。
- **CrewAI**：多角色、多任务流程编排。
- **Flowise / LangFlow**：偏可视化拖拽构建（也是“编排框架”的一种形态），可以快速搭建链/工作流。

## 3）RAG/检索增强相关框架

- **LlamaIndex**：RAG 生态很强（数据索引/检索管线）。
- **Haystack**：RAG 组件化（Retriever、Reader、Pipeline 等）。
- **RAG 相关的通用工程平台**（不完全等同 LangChain，但常用于 RAG 落地）：
  - **OpenAI Cookbook / 示例体系**（偏工程模板）
  - **RAGflow**（偏产品化/平台化）
  - **Dify**（偏平台化：工作流 + RAG + 部署）

## 4）平台化“可搭建”的方案（接近低代码/工程平台）

- **Dify**：工作流 + 知识库（RAG）+ 应用发布。
- **Flowise / LangFlow**：可视化拖拽构建链/工作流（常用于原型和快速交付）。
- **LangChain 用在平台上**：有些平台底层用别的框架，但使用体验类似。

Dall-E 文到图的模型
eleven labs Text2Speech tts合成声音
closeai <www.closeai-asia.com>
