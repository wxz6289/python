# LangChain 内置 Chain 核心总结

## 1) Chain 是什么

- `Chain` 用于把多个步骤串起来，形成可复用的调用流程（如：提示词 -> 模型 -> 输出解析）。
- 在新版本中，官方更推荐基于 `Runnable` / `LCEL`（LangChain Expression Language）来表达链式流程。
- 可以把 `Chain` 理解为“业务流程模板”，把模型调用、工具调用、检索等组合在一起。



## 2) 新版主线：Runnable + LCEL

- 核心接口：`Runnable`
  - 支持 `invoke`（单次调用）、`batch`（批量）、`stream`（流式）、`ainvoke`（异步）。
- 组合操作常用：
  - `|`：顺序串联（最常用）
  - `RunnableParallel`：并行分支
  - `RunnablePassthrough`：透传原始输入，便于和中间结果合并
  - `assign`：在字典上下文中追加字段
- 常见标准链结构：
  - `ChatPromptTemplate | ChatModel | StrOutputParser`

## 3) 常见内置 Chain（重点）

### 3.1 `LLMChain`（经典，仍常见）

- 功能：`PromptTemplate + LLM` 的封装。
- 场景：简单问答、改写、分类、抽取。
- 说明：很多示例仍在使用，但新项目优先用 LCEL 的 Runnable 写法。

### 3.2 `ConversationChain

- 功能：带记忆（Memory）的对话链。
- 场景：多轮上下文聊天。
- 说明：新版更推荐使用消息历史相关 Runnable 方案（更灵活）。

- ConversationBufferWindowMemory

- ConversationTokenBufferMemory
- ConversatiionSummaryMemory
- ConversatiionSummaryBufferMemory
- ConversationEntityMemory
- ConversationKGMemory
- VectorStoreRetrieverMemory

### 3.3 `SequentialChain` / `SimpleSequentialChain`

- 功能：多个子链按顺序执行，前一步输出作为后一步输入。
- 场景：多步加工（先摘要，再生成标题，再翻译）。
- 风险：步骤多时调试复杂，建议配合 LangSmith 观测。

### 3.4 路由链：`RouterChain` / `MultiPromptChain`（历史常见）

- 功能：根据输入把请求路由到不同子链。
- 场景：多任务分流（代码问题走代码提示词，写作问题走写作提示词）。
- 新趋势：推荐用 LCEL 自定义路由逻辑（可维护性更高）。

### 3.5 问答与检索链（RAG 方向）

- 常见构建函数：
  - `create_stuff_documents_chain`
  - `create_retrieval_chain`
- 旧版常见：`RetrievalQA`
- 场景：文档问答、知识库助手。
- 核心流程：`Retriever -> (文档拼接/压缩) -> Prompt -> LLM -> Parser`。

## 4) 实战中最常见的 3 类链模板

### 模板 A：基础生成链

- `Prompt -> ChatModel -> StrOutputParser`
- 用途：通用文本生成与改写。

### 模板 B：结构化输出链

- `Prompt -> ChatModel.with_structured_output(...)`
- 用途：稳定返回 JSON / Pydantic 结构，便于程序消费。

### 模板 C：检索增强链（RAG）

- `Query -> Retriever -> Documents -> Prompt -> ChatModel`
- 用途：让答案绑定私有知识，降低幻觉。

## 5) 选型建议（简版）

- 新项目：优先 `LCEL/Runnable`，不要过度依赖老式 `Chain` 类。
- 简单流程：直接 `prompt | model | parser`。
- 多分支或并行：`RunnableParallel + assign + passthrough`。
- 生产环境：务必加上日志、追踪与评估（如 LangSmith）。

## 6) 易错点

- 输入输出 key 不一致：多链拼接时最常见。
- 上下文过长：RAG 需要控制检索数量与 chunk 大小。
- 结构化输出不稳定：优先 schema 约束和重试机制。
- 只看最终答案不看中间步骤：排障效率会很低。

## 7) 一句话理解

- LangChain 的“内置 Chain”正在从“预定义类”演进到“Runnable 可组合流程”，核心目标是：更灵活地搭建、观测、复用 LLM 工作流。
