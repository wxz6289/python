# LangChain PromptTemplate 用法总结

`PromptTemplate` 是 LangChain 中最基础的文本提示词模板类，用于把固定提示词和动态变量组合成最终传给模型的 prompt。

它适合处理普通文本模型或简单字符串提示词。如果是 Chat Model 多角色对话，通常优先使用 `ChatPromptTemplate`。

---

## 1. 基本作用

直接把用户输入拼接到字符串里容易出现这些问题：

- 提示词散落在代码中，不方便维护。
- 变量名不统一，容易漏传或传错。
- 不方便与 LCEL 链式组合。
- 不方便批量调用、流式调用和调试。

`PromptTemplate` 的作用是把提示词模板化：

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template("请用一句话介绍 {topic}")

text = prompt.format(topic="LangChain")
print(text)
```

输出：

```text
请用一句话介绍 LangChain
```

---

## 2. from_template：从字符串创建模板

`from_template` 是最常用的创建方式，它会自动识别 `{}` 中的变量。

```python
from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate.from_template(
    "请把下面的内容翻译成 {language}：\n{text}"
)

print(prompt.input_variables)
```

输出：

```python
["language", "text"]
```

调用时必须传入模板中需要的变量：

```python
result = prompt.format(
    language="英文",
    text="你好，世界",
)

print(result)
```

输出：

```text
请把下面的内容翻译成 英文：
你好，世界
```

注意：模板变量使用 Python 字符串格式化风格，变量名写在 `{}` 中。

---

## 3. format：生成普通字符串

`format` 会把变量填入模板，并返回一个普通字符串。

```python
prompt = PromptTemplate.from_template(
    "你是一个{role}，请用{style}风格回答：{question}"
)

text = prompt.format(
    role="Python 老师",
    style="简洁",
    question="什么是装饰器？",
)

print(text)
```

`format` 适合这些场景：

- 只想得到最终 prompt 字符串。
- 调试提示词内容。
- 手动把 prompt 传给其他 SDK。

如果缺少变量，会报错：

```python
prompt.format(role="Python 老师")
```

因为缺少 `style` 和 `question`。

---

## 4. invoke：作为 Runnable 调用

新版 LangChain 中，`PromptTemplate` 也是一个 `Runnable`，因此可以直接调用 `invoke`。

```python
prompt = PromptTemplate.from_template("请解释 {concept}")

result = prompt.invoke({"concept": "LCEL"})

print(result)
```

`invoke` 返回的不是普通字符串，而是 `StringPromptValue`，它表示一个可传给模型的 PromptValue。

如果想拿到字符串，可以使用：

```python
prompt_value = prompt.invoke({"concept": "LCEL"})

print(prompt_value.to_string())
```

输出：

```text
请解释 LCEL
```

`format` 和 `invoke` 的区别：

| 方法 | 入参 | 返回值 | 典型用途 |
| --- | --- | --- | --- |
| `format` | 关键字参数 | `str` | 调试、手动生成 prompt 字符串 |
| `invoke` | 字典 | `PromptValue` | LCEL 链式调用、与模型组合 |

---

## 5. 与模型组成 LCEL 链

`PromptTemplate` 最常见的新版写法是和模型、解析器组成链：

```python
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

load_dotenv()

llm = init_chat_model(
    model="gpt-4o-mini",
    api_key=os.getenv("CLOSEAI_API_KEY"),
    base_url=os.getenv("CLOSEAI_BASE_URL"),
)

prompt = PromptTemplate.from_template(
    "请用三句话解释 {topic}，要求通俗易懂。"
)

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"topic": "向量数据库"})
print(result)
```

执行流程：

```text
输入字典 -> PromptTemplate 填充变量 -> LLM 生成回复 -> StrOutputParser 转成字符串
```

---

## 6. partial：预先固定部分变量

如果某些变量在多个调用中都一样，可以使用 `partial` 固定。

```python
prompt = PromptTemplate.from_template(
    "你是一个{role}，请回答：{question}"
)

teacher_prompt = prompt.partial(role="Python 老师")

text = teacher_prompt.format(question="什么是生成器？")
print(text)
```

输出：

```text
你是一个Python 老师，请回答：什么是生成器？
```

适合场景：

- 固定角色设定。
- 固定输出语言。
- 固定回答风格。
- 多个链复用同一模板。

---

## 7. input_variables：查看模板变量

可以通过 `input_variables` 查看模板需要哪些变量。

```python
prompt = PromptTemplate.from_template(
    "请把 {text} 总结成 {words} 字以内"
)

print(prompt.input_variables)
```

输出：

```python
["text", "words"]
```

这在调试复杂模板时很有用。

---

## 8. 模板中的大括号转义

如果提示词中需要出现真正的大括号，需要使用双大括号转义。

```python
prompt = PromptTemplate.from_template(
    "请输出 JSON，格式如下：{{\"name\": \"...\", \"age\": 18}}。用户信息：{info}"
)

print(prompt.format(info="张三，18岁"))
```

否则 LangChain 会把 `{name}`、`{age}` 当成模板变量。

---

## 9. 常见错误

### 9.1 变量名不一致

```python
prompt = PromptTemplate.from_template("介绍 {topic}")
prompt.format(name="LangChain")
```

错误原因：模板需要 `topic`，但传入的是 `name`。

正确写法：

```python
prompt.format(topic="LangChain")
```

### 9.2 把 format 写成 formate

正确方法名是 `format`，不是 `formate`。

```python
prompt.format(topic="LangChain")
```

### 9.3 用 PromptTemplate 写多角色对话

`PromptTemplate` 只适合普通文本模板。如果需要系统消息、用户消息、历史消息，建议使用 `ChatPromptTemplate`。

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业助手。"),
    ("user", "{question}"),
])
```

---

## 10. ChatPromptTemplate 用法

`ChatPromptTemplate` 是面向 Chat Model 的提示词模板。它不是生成一整段普通字符串，而是生成一组带角色的消息，例如 `system`、`human`、`ai`。

相比 `PromptTemplate`，它更适合现代大模型对话场景：

- 可以区分系统指令和用户输入。
- 可以保留多轮对话结构。
- 可以插入历史消息。
- 可以和 tool calling、Agent、结构化输出等能力更好配合。

### 10.1 from_messages：创建多角色模板

最常用方式是 `ChatPromptTemplate.from_messages`。

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的 Python 老师，回答要简洁。"),
    ("human", "请解释 {topic}"),
])
```

这里的每一项都是一条消息：

| 角色 | 含义 |
| --- | --- |
| `system` | 系统提示词，用于定义角色、规则、边界 |
| `human` / `user` | 用户输入 |
| `ai` / `assistant` | AI 历史回复，常用于 few-shot 或上下文 |
| `placeholder` | 消息占位符，常用于插入历史消息 |

### 10.2 format_messages：生成消息列表

`format_messages` 会把模板变量填入，并返回消息对象列表。

```python
messages = prompt.format_messages(topic="装饰器")

for message in messages:
    print(message.type, message.content)
```

输出类似：

```text
system 你是一个专业的 Python 老师，回答要简洁。
human 请解释 装饰器
```

`format_messages` 适合调试 Chat Prompt 最终会变成什么消息。

### 10.3 invoke：作为 Runnable 调用

`ChatPromptTemplate` 也是 `Runnable`，可以直接调用 `invoke`。

```python
prompt_value = prompt.invoke({"topic": "生成器"})

print(prompt_value)
print(prompt_value.to_messages())
```

`invoke` 返回的是 `ChatPromptValue`，它可以继续传给 Chat Model。

如果只想看字符串形式：

```python
print(prompt_value.to_string())
```

### 10.4 与模型组成链

新版 LangChain 中常用 LCEL 写法：

```python
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

llm = init_chat_model(
    model="gpt-4o-mini",
    api_key=os.getenv("CLOSEAI_API_KEY"),
    base_url=os.getenv("CLOSEAI_BASE_URL"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业助手，回答必须使用中文。"),
    ("human", "{question}"),
])

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"question": "什么是 LangChain？"})
print(result)
```

执行流程：

```text
输入字典 -> ChatPromptTemplate 生成消息列表 -> Chat Model 生成回复 -> 解析为字符串
```

### 10.5 few-shot 示例

可以在模板中写入少量示例，帮助模型学习回答风格。

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个成语解释助手，回答要短。"),
    ("human", "解释：画蛇添足"),
    ("ai", "比喻做了多余的事，反而坏事。"),
    ("human", "解释：{idiom}"),
])

result = prompt.invoke({"idiom": "亡羊补牢"})
print(result.to_string())
```

这里的 `ai` 消息不是模型实时生成的，而是放在 prompt 里的示例答案。

### 10.6 部分变量固定

`ChatPromptTemplate` 也支持 `partial`。

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个{role}，回答风格是{style}。"),
    ("human", "{question}"),
])

teacher_prompt = prompt.partial(role="Python 老师", style="简洁清晰")

messages = teacher_prompt.format_messages(question="什么是闭包？")
```

适合复用固定角色、语言、风格和输出约束。

---

## 11. MessagesPlaceholder 用法

它表示“这里先空着，运行时再插入一组消息”。
最常见的用途是插入聊天历史。

### 11.1 基础示例

```python
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有上下文记忆的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])

history = [
    HumanMessage(content="我叫小明。"),
    AIMessage(content="好的，我记住了，你叫小明。"),
]

prompt_value = prompt.invoke({
    "history": history,
    "question": "你还记得我叫什么吗？",
})

print(prompt_value.to_string())
```

最终消息顺序是：

```text
system: 你是一个有上下文记忆的助手。
human: 我叫小明。
ai: 好的，我记住了，你叫小明。
human: 你还记得我叫什么吗？
```

### 11.2 与 RunnableWithMessageHistory 结合

`MessagesPlaceholder` 经常配合 `RunnableWithMessageHistory` 自动管理历史消息。

```python
from typing import Dict
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

store: Dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有记忆的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | llm

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

config = {"configurable": {"session_id": "user-001"}}

chain_with_history.invoke({"input": "我叫小明"}, config=config)
chain_with_history.invoke({"input": "我叫什么？"}, config=config)
```

关键点：

- `MessagesPlaceholder(variable_name="history")` 负责在 prompt 中预留历史消息位置。
- `history_messages_key="history"` 必须和占位符变量名一致。
- `input_messages_key="input"` 表示当前用户输入字段。
- `session_id` 用于区分不同用户或不同会话。

### 11.3 与 Redis 聊天历史结合

生产环境中通常不用进程内字典保存历史，而是用 Redis、数据库等外部存储。

```python
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

def get_session_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(
        session_id=session_id,
        url="redis://localhost:6379/0",
        key_prefix="chat:",
        ttl=60 * 60 * 24,
    )

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有长期会话记忆的助手。"),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain_with_history = RunnableWithMessageHistory(
    prompt | llm,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

result = chain_with_history.invoke(
    {"input": "我正在学习 LangChain。"},
    config={"configurable": {"session_id": "redis-user-001"}},
)
```

这样同一个 `session_id` 的聊天历史会保存在 Redis 中，下一次请求可以继续使用。

### 11.4 optional 参数

如果某些调用没有历史消息，可以设置 `optional=True`。

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手。"),
    MessagesPlaceholder(variable_name="history", optional=True),
    ("human", "{question}"),
])

prompt.invoke({"question": "你好"})
```

如果不设置 `optional=True`，调用时缺少 `history` 可能会报错。

### 11.5 n_messages：限制历史数量

可以用 `n_messages` 限制插入最近多少条消息，避免上下文太长。

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手。"),
    MessagesPlaceholder(variable_name="history", n_messages=4),
    ("human", "{question}"),
])
```

这表示只插入最近 4 条历史消息。

注意：`n_messages` 是按消息条数计算，不是按对话轮数计算。一轮对话通常包括一条 `HumanMessage` 和一条 `AIMessage`。

### 11.6 常见错误

变量名不一致：

```python
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain_with_history = RunnableWithMessageHistory(
    prompt | llm,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)
```

这里占位符叫 `history`，但 `history_messages_key` 写成了 `chat_history`，运行时会导致历史消息无法正确注入。

正确写法：

```python
history_messages_key="history"
```

传入字符串而不是消息列表：

```python
prompt.invoke({
    "history": "用户之前说过他叫小明",
    "question": "他叫什么？",
})
```

`MessagesPlaceholder` 需要的是消息列表，例如 `HumanMessage`、`AIMessage`，不是普通字符串。

---

## 12. Chat Message 消息类型

LangChain 的 Chat Model 并不是只接收一段字符串，而是接收一组消息对象。每条消息都有自己的角色、内容和附加信息。

常见消息类型都在 `langchain_core.messages` 中：

```python
from langchain_core.messages import (
    AIMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
```

### 12.1 主要消息类型对比

| 消息类型 | 对应角色 | 主要用途 |
| --- | --- | --- |
| `SystemMessage` | `system` | 定义模型角色、规则、边界、输出要求 |
| `HumanMessage` | `human` / `user` | 表示用户输入 |
| `AIMessage` | `ai` / `assistant` | 表示模型回复，也可承载 tool calls |
| `ChatMessage` | 自定义 role | 需要自定义角色名时使用 |
| `ToolMessage` | `tool` | 表示工具执行结果，通常用于 tool calling / Agent |

### 12.2 SystemMessage：系统指令

`SystemMessage` 用于放置最高层级的行为约束，例如角色、边界、输出格式。

```python
from langchain_core.messages import SystemMessage

message = SystemMessage(
    content="你是一个专业的 Python 老师，回答要简洁、准确。"
)
```

典型用途：

- 定义助手身份。
- 规定回答语言。
- 规定输出格式。
- 设置安全边界。
- 说明不能做什么。

在 `ChatPromptTemplate` 中，下面两种写法含义接近：

```python
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="你是一个专业助手。"),
    ("human", "{question}"),
])
```

或：

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业助手。"),
    ("human", "{question}"),
])
```

### 12.3 HumanMessage：用户消息

`HumanMessage` 表示用户输入。

```python
from langchain_core.messages import HumanMessage

message = HumanMessage(content="请解释什么是 LangChain")
```

直接调用 Chat Model 时可以这样传入：

```python
messages = [
    SystemMessage(content="你是一个专业助手。"),
    HumanMessage(content="请解释什么是 LangChain"),
]

response = llm.invoke(messages)
print(response.content)
```

在模板中也可以用元组简写：

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业助手。"),
    ("human", "{question}"),
])
```

### 12.4 AIMessage：模型回复

`AIMessage` 表示模型已经给出的回复，常用于构造历史对话或 few-shot 示例。

```python
from langchain_core.messages import AIMessage, HumanMessage

history = [
    HumanMessage(content="我叫小明。"),
    AIMessage(content="好的，我记住了，你叫小明。"),
    HumanMessage(content="我叫什么？"),
]
```

`AIMessage` 还可能包含工具调用信息，例如支持 tool calling 的模型返回时，常见字段包括：

```python
response = llm_with_tools.invoke("现在几点？")

print(response.content)
print(response.tool_calls)
```

其中 `tool_calls` 表示模型希望调用哪些工具。普通文本回复则主要读取 `response.content`。

### 12.5 ChatMessage：自定义角色消息

`ChatMessage` 可以手动指定 `role`，适合需要非标准角色名的场景。

```python
from langchain_core.messages import ChatMessage

message = ChatMessage(
    role="critic",
    content="这个回答缺少示例，需要补充代码。"
)
```

一般情况下，不建议滥用自定义 role。主流模型对 `system`、`user`、`assistant`、`tool` 这些标准角色支持更稳定。

适合使用 `ChatMessage` 的场景：

- 某些模型或网关支持自定义 role。
- 内部评审、改写、打分流程需要区分特殊角色。
- 构造多 Agent 协作上下文时，需要保留角色来源。

### 12.6 ToolMessage：工具结果消息

`ToolMessage` 表示工具执行后的结果，通常和 `AIMessage.tool_calls` 配合使用。

```python
from langchain_core.messages import ToolMessage

tool_message = ToolMessage(
    content="北京今天晴，气温 22°C。",
    tool_call_id="call_123",
)
```

典型流程：

1. 用户提问。
2. 模型返回 `AIMessage`，其中包含 `tool_calls`。
3. 程序执行工具。
4. 将工具结果包装成 `ToolMessage`。
5. 再把消息列表传回模型，让模型基于工具结果生成最终回答。

简化示例：

```python
messages = [HumanMessage(content="北京今天天气怎么样？")]

ai_message = llm_with_tools.invoke(messages)
messages.append(ai_message)

for tool_call in ai_message.tool_calls:
    tool_result = run_tool(tool_call)
    messages.append(
        ToolMessage(
            content=tool_result,
            tool_call_id=tool_call["id"],
        )
    )

final_response = llm_with_tools.invoke(messages)
print(final_response.content)
```

在日常开发中，如果使用 `create_agent`，这些工具消息通常由 Agent 框架自动管理；手写工具调用循环时才需要直接构造 `ToolMessage`。

### 12.7 消息列表与 ChatPromptTemplate 的关系

`ChatPromptTemplate` 的最终产物就是消息列表。

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个助手。"),
    ("human", "{question}"),
])

prompt_value = prompt.invoke({"question": "你好"})

messages = prompt_value.to_messages()
print(messages)
```

输出的 `messages` 中通常包含：

```python
[
    SystemMessage(content="你是一个助手。"),
    HumanMessage(content="你好"),
]
```

所以这两种方式都可以传给 Chat Model：

```python
# 方式一：使用模板
chain = prompt | llm
chain.invoke({"question": "你好"})

# 方式二：手动构造消息
llm.invoke([
    SystemMessage(content="你是一个助手。"),
    HumanMessage(content="你好"),
])
```

### 12.8 使用建议

- 固定规则和角色设定放在 `SystemMessage`。
- 用户输入放在 `HumanMessage`。
- 历史模型回复用 `AIMessage`。
- 工具执行结果用 `ToolMessage`。
- 不确定时优先使用标准角色，不要随意使用 `ChatMessage` 自定义 role。
- 多轮历史要保持消息顺序：`HumanMessage` 和 `AIMessage` 应按真实对话顺序排列。

---

## 13. Few-shot Prompt 模板

Few-shot prompting 指在提示词中提供少量高质量示例，让模型学习回答格式、推理方式、语气风格或分类标准。

LangChain 中常见两类 Few-shot 模板：

- `FewShotPromptTemplate`：用于普通文本 prompt。
- `FewShotChatMessagePromptTemplate`：用于 Chat Model 的多消息 prompt。

### 13.1 什么时候需要 Few-shot

Few-shot 适合这些场景：

- 输出格式要求严格，但又不想只靠文字描述。
- 分类、抽取、改写、评分等任务需要示例约束。
- 希望模型模仿固定回答风格。
- 用户输入差异较大，需要用示例说明边界。
- 零样本提示词效果不稳定，需要用样例增强一致性。

不适合这些场景：

- 任务非常简单，一个清晰指令就足够。
- 示例会占用大量上下文，影响长文输入。
- 业务规则强约束，应该用代码或结构化校验实现。
- 示例质量不稳定，可能把模型带偏。

---

## 14. FewShotPromptTemplate

`FewShotPromptTemplate` 用于构造普通文本形式的 few-shot prompt。它会把多个示例按指定格式拼接起来，再加上前置说明和用户输入。

### 14.1 基本组成

一个 `FewShotPromptTemplate` 通常包含：

| 参数 | 作用 |
| --- | --- |
| `examples` | 示例数据列表 |
| `example_prompt` | 每个示例如何格式化 |
| `prefix` | 示例前面的总体说明 |
| `suffix` | 示例后面的用户输入模板 |
| `input_variables` | 用户调用时需要传入的变量 |
| `example_separator` | 示例之间的分隔符 |

### 14.2 基础用法

```python
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

examples = [
    {
        "word": "开心",
        "antonym": "难过",
    },
    {
        "word": "高",
        "antonym": "矮",
    },
]

example_prompt = PromptTemplate.from_template(
    "词语：{word}\n反义词：{antonym}"
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请根据示例，写出给定词语的反义词。",
    suffix="词语：{input}\n反义词：",
    input_variables=["input"],
    example_separator="\n\n",
)

text = prompt.format(input="热")
print(text)
```

输出类似：

```text
请根据示例，写出给定词语的反义词。

词语：开心
反义词：难过

词语：高
反义词：矮

词语：热
反义词：
```

### 14.3 与模型组成链

```python
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser

llm = init_chat_model(model="gpt-4o-mini")

chain = prompt | llm | StrOutputParser()

result = chain.invoke({"input": "热"})
print(result)
```

虽然 `FewShotPromptTemplate` 生成的是文本 prompt，但也可以传给 Chat Model。模型会把它作为一条用户消息或文本输入处理。

### 14.4 分类任务示例

Few-shot 很适合分类，因为示例可以明确标签边界。

```python
examples = [
    {"text": "这个产品太好用了，下次还买", "label": "正面"},
    {"text": "物流太慢了，包装也破了", "label": "负面"},
    {"text": "已经收到，暂时还没使用", "label": "中性"},
]

example_prompt = PromptTemplate.from_template(
    "文本：{text}\n分类：{label}"
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请判断用户评论的情感分类，只能输出：正面、负面、中性。",
    suffix="文本：{input}\n分类：",
    input_variables=["input"],
    example_separator="\n\n",
)
```

这里示例的价值在于：模型不仅知道有哪些标签，还能看到每个标签对应的典型表达。

### 14.5 输出格式示例

如果希望模型输出固定格式，也可以用示例约束。

```python
examples = [
    {
        "question": "Python 是什么？",
        "answer": "结论：Python 是一种编程语言。\n解释：它语法简洁，常用于 Web、数据分析和 AI。",
    },
    {
        "question": "Redis 是什么？",
        "answer": "结论：Redis 是一种内存数据库。\n解释：它常用于缓存、计数器、排行榜和消息队列。",
    },
]

example_prompt = PromptTemplate.from_template(
    "问题：{question}\n回答：{answer}"
)

prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请按示例格式回答问题。",
    suffix="问题：{input}\n回答：",
    input_variables=["input"],
)
```

注意：如果格式必须被程序解析，仍然建议结合 `JsonOutputParser`、Pydantic 或结构化输出能力，不要只依赖 few-shot。

---

## 15. FewShotChatMessagePromptTemplate

`FewShotChatMessagePromptTemplate` 用于 Chat Model。它不会把示例简单拼成一整段文本，而是把每个示例组织成多条 chat message。

这比普通文本 few-shot 更适合对话模型，因为它保留了 `human` 和 `ai` 的角色结构。

### 15.1 基础用法

```python
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)

examples = [
    {
        "input": "解释：画蛇添足",
        "output": "比喻做了多余的事，反而坏事。",
    },
    {
        "input": "解释：亡羊补牢",
        "output": "比喻出了问题后及时补救，还不算晚。",
    },
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个成语解释助手，回答要简洁。"),
    few_shot_prompt,
    ("human", "{input}"),
])

prompt_value = prompt.invoke({"input": "解释：刻舟求剑"})
print(prompt_value.to_messages())
```

最终消息大致是：

```text
system: 你是一个成语解释助手，回答要简洁。
human: 解释：画蛇添足
ai: 比喻做了多余的事，反而坏事。
human: 解释：亡羊补牢
ai: 比喻出了问题后及时补救，还不算晚。
human: 解释：刻舟求剑
```

### 15.2 与模型组成链

```python
chain = prompt | llm | StrOutputParser()

result = chain.invoke({"input": "解释：刻舟求剑"})
print(result)
```

这种写法适合所有 Chat Model 场景，尤其适合需要模型模仿“用户问、助手答”的任务。

### 15.3 对话风格示例

`FewShotChatMessagePromptTemplate` 不只是约束答案格式，也可以约束语气。

```python
examples = [
    {
        "input": "我总是学不会递归。",
        "output": "别急，递归的关键是先相信函数已经能解决小问题。我们从最简单的阶乘例子开始。",
    },
    {
        "input": "闭包到底有什么用？",
        "output": "可以把闭包理解成函数带着一份记忆。它常用于装饰器、回调和封装状态。",
    },
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个耐心的 Python 老师。"),
    few_shot_prompt,
    ("human", "{question}"),
])
```

模型会更容易模仿示例中的耐心、解释方式和回答长度。

### 15.4 与 MessagesPlaceholder 搭配

Few-shot 示例和真实历史消息可以同时存在，但要注意顺序。

```python
from langchain_core.prompts import MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个客服助手。"),
    few_shot_prompt,
    MessagesPlaceholder(variable_name="history", optional=True),
    ("human", "{input}"),
])
```

常见顺序是：

```text
系统规则 -> few-shot 示例 -> 真实历史消息 -> 当前用户输入
```

这样模型先看到稳定示例，再看到当前会话上下文。

### 15.5 示例选择器

当示例很多时，不应该把所有示例都塞进 prompt。示例选择器负责根据当前输入，动态挑选最合适的一小部分示例。

核心原则：**不是示例越多越好，而是越相关、越稳定、越能覆盖当前问题越好**。

常见选择策略：

| 策略 | 典型类 | 选择依据 | 适合场景 |
| --- | --- | --- | --- |
| 固定示例 | 直接传 `examples` | 人工挑选固定样例 | 示例少、任务稳定、格式演示 |
| 长度限制 | `LengthBasedExampleSelector` | 根据 prompt 长度控制示例数量 | 输入长度变化大、需要控制 token |
| 语义相似度 | `SemanticSimilarityExampleSelector` | 根据 embedding 相似度选择最相关示例 | 问答、分类、抽取、意图识别 |
| MMR 多样性选择 | `MaxMarginalRelevanceExampleSelector` | 兼顾相关性和多样性 | 容易选出重复示例的场景 |
| N-Gram 重叠 | `NGramOverlapExampleSelector` | 根据词面重叠选择示例 | 短文本、固定表达、无 embedding 环境 |
| 自定义选择 | 自定义 `BaseExampleSelector` | 业务规则、标签、难度、租户等 | 需要强业务控制的生产系统 |

### 15.6 固定示例选择

最简单的方式是直接传入 `examples`。

```python
few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)
```

适合：

- 示例数量少。
- 示例非常经典。
- 任务输入差异不大。
- 主要目的是演示固定输出格式。

注意：固定示例不关心当前输入是否相关。如果示例和当前问题差异很大，可能会误导模型。

### 15.7 LengthBasedExampleSelector：按长度选择

`LengthBasedExampleSelector` 会根据示例格式化后的长度，尽量选择能放入 `max_length` 范围内的示例。

```python
from langchain_core.example_selectors import LengthBasedExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate

examples = [
    {"question": "Python 是什么？", "answer": "Python 是一种编程语言。"},
    {"question": "Redis 是什么？", "answer": "Redis 是一种内存数据库，常用于缓存。"},
    {"question": "LangChain 是什么？", "answer": "LangChain 是用于构建 LLM 应用的框架。"},
]

example_prompt = PromptTemplate.from_template(
    "问题：{question}\n回答：{answer}"
)

example_selector = LengthBasedExampleSelector(
    examples=examples,
    example_prompt=example_prompt,
    max_length=100,
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="请参考示例回答问题。",
    suffix="问题：{input}\n回答：",
    input_variables=["input"],
)
```

适合：

- 用户输入长短差异很大。
- 需要避免 prompt 超过上下文窗口。
- 示例格式比较固定。

注意：

- 它主要按长度控制，不保证语义最相关。
- `max_length` 不是严格 token 数，通常用于近似控制。
- 如果示例质量差，长度选择也无法改善效果。

### 15.8 SemanticSimilarityExampleSelector：按语义相似度选择

`SemanticSimilarityExampleSelector` 会把示例向量化，根据当前输入选择语义最相近的示例。

```python
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

examples = [
    {"input": "订单一直没发货", "category": "物流问题"},
    {"input": "我要申请退款", "category": "售后退款"},
    {"input": "怎么修改收货地址", "category": "订单修改"},
    {"input": "优惠券为什么不能用", "category": "营销活动"},
]

example_prompt = PromptTemplate.from_template(
    "用户问题：{input}\n分类：{category}"
)

example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=examples,
    embeddings=OpenAIEmbeddings(),
    vectorstore_cls=FAISS,
    k=2,
)

prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="请判断用户问题分类，只能输出示例中的分类名称。",
    suffix="用户问题：{input}\n分类：",
    input_variables=["input"],
)
```

适合：

- 用户表达变化大，但语义相近。
- 示例库较多。
- 分类、意图识别、问答、抽取任务。

注意：

- 需要 embedding 模型和向量库。
- 示例文本应包含用于匹配的关键字段，例如 `input`。
- 相似示例过多时，可能选出内容重复的样例。
- 生产环境要关注 embedding 成本、缓存和向量库更新。

### 15.9 MaxMarginalRelevanceExampleSelector：相关且多样

`MaxMarginalRelevanceExampleSelector` 使用 MMR 策略，既考虑与当前输入的相似度，也避免选出的示例彼此过于重复。

```python
from langchain_core.example_selectors import MaxMarginalRelevanceExampleSelector
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
    examples=examples,
    embeddings=OpenAIEmbeddings(),
    vectorstore_cls=FAISS,
    k=3,
    fetch_k=10,
)
```

参数含义：

- `k`：最终选择多少个示例。
- `fetch_k`：先召回多少个候选示例，再从中做多样性选择。

适合：

- 示例库里有大量相似样例。
- 希望覆盖多个角度。
- 单纯相似度选择总是选出重复示例。

注意：

- MMR 不一定选择“最相似”的前几个示例，而是兼顾多样性。
- 如果任务只需要最接近的标准答案，相似度选择可能更直接。

### 15.10 NGramOverlapExampleSelector：按词面重叠选择

`NGramOverlapExampleSelector` 根据输入和示例之间的 n-gram 词面重叠选择示例，不依赖 embedding。

```python
from langchain_community.example_selectors import NGramOverlapExampleSelector

example_selector = NGramOverlapExampleSelector(
    examples=examples,
    example_prompt=example_prompt,
    threshold=0.0,
)
```

适合：

- 没有 embedding 环境。
- 输入和示例有明显关键词重叠。
- 短文本、固定表达、命令式输入。

注意：

- 对同义改写不敏感。
- 中文场景可能受分词和字面匹配影响。
- 更适合作为轻量策略，不适合作为复杂语义匹配方案。

### 15.11 自定义示例选择策略

生产环境中，经常需要按业务规则选择示例，例如：

- 按业务线选择：电商、教育、金融。
- 按用户类型选择：新用户、老用户、VIP 用户。
- 按任务类型选择：分类、摘要、抽取、改写。
- 按语言选择：中文、英文、日文。
- 按风险等级选择：普通问答、高风险操作、合规审查。

可以自定义一个选择函数，在构造 prompt 前先筛选示例。

```python
def select_examples(input_text: str, task_type: str, limit: int = 3) -> list[dict]:
    matched = [
        example
        for example in examples
        if example["task_type"] == task_type
    ]
    return matched[:limit]

selected_examples = select_examples(
    input_text="我要申请退款",
    task_type="售后",
)

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=selected_examples,
    example_prompt=example_prompt,
)
```

如果需要接入 LangChain 标准接口，可以继承 `BaseExampleSelector`。

```python
from langchain_core.example_selectors import BaseExampleSelector

class TaskTypeExampleSelector(BaseExampleSelector):
    def __init__(self, examples: list[dict]):
        self.examples = examples

    def add_example(self, example: dict) -> None:
        self.examples.append(example)

    def select_examples(self, input_variables: dict) -> list[dict]:
        task_type = input_variables.get("task_type")
        return [
            example
            for example in self.examples
            if example.get("task_type") == task_type
        ][:3]
```

适合：

- 示例选择必须遵守业务规则。
- 示例需要按租户、权限、地区隔离。
- 需要可解释地控制为什么选中某些示例。

### 15.12 示例选择策略建议

- **示例少且稳定**：直接使用固定 `examples`。
- **输入长度变化大**：使用 `LengthBasedExampleSelector` 控制上下文。
- **表达方式变化大**：使用 `SemanticSimilarityExampleSelector`。
- **相似示例太多**：使用 `MaxMarginalRelevanceExampleSelector`。
- **没有 embedding 依赖**：可以尝试 `NGramOverlapExampleSelector`。
- **有明确业务标签**：优先用自定义规则先过滤，再做相似度选择。
- **生产环境**：建议记录每次选中的示例，便于调试和评估。

实践中常用组合策略：

```text
业务过滤 -> 语义召回 -> 多样性去重 -> 长度截断 -> 拼入 prompt
```

示例选择的最终目标不是“选出看起来最像的样例”，而是“选出最能帮助模型稳定完成当前任务的样例”。

---

## 16. Few-shot 应用场景

### 16.1 分类与标签判断

示例可以帮助模型理解分类边界。

适合：

- 情感分类。
- 工单分类。
- 风险等级判断。
- 用户意图识别。

注意：分类标签必须稳定，最好在 prompt 中明确“只能输出这些标签”。

### 16.2 信息抽取

示例可以告诉模型从文本中抽取哪些字段。

适合：

- 从简历抽取姓名、年限、技能。
- 从订单文本抽取商品、数量、地址。
- 从报错日志抽取错误类型、原因、建议。

注意：抽取结果如果要进入系统，建议使用结构化输出和字段校验。

### 16.3 格式约束

示例可以强化固定回答格式。

适合：

- 结论 + 原因 + 建议。
- 摘要 + 关键词。
- 问题分析 + 解决步骤。
- SQL + 说明。

注意：few-shot 只能提高概率，不能保证 100% 符合格式。

### 16.4 风格模仿

示例可以让模型学习语气、长度和表达方式。

适合：

- 客服话术。
- 教学风格。
- 产品文案。
- 古风、幽默、严谨等特定表达。

注意：不要提供相互冲突的风格示例。

### 16.5 复杂推理模式

示例可以展示解题步骤或判断路径。

适合：

- 数学题解题格式。
- 代码审查流程。
- SQL 生成流程。
- 多条件业务判断。

注意：不要要求模型暴露冗长隐式推理过程。更推荐让模型输出简洁的“依据、结论、校验结果”。

---

## 17. Few-shot 注意事项

### 17.1 示例质量比数量重要

优先选择少量、高质量、覆盖边界的示例。

不建议：

- 示例太多。
- 示例重复。
- 示例互相矛盾。
- 示例格式不一致。

### 17.2 示例要覆盖边界情况

如果任务有容易混淆的类别，示例应覆盖这些边界。

例如情感分类中，“还行”“一般般”“暂时没用”可能不是正面，也不是负面，更接近中性。

### 17.3 控制上下文长度

few-shot 会占用 token。示例越多，留给用户输入、检索内容和模型输出的空间越少。

建议：

- 先从 2 到 5 个示例开始。
- 优先保留最有代表性的示例。
- 长输入任务要减少示例数量。
- 示例很多时使用 example selector。

### 17.4 保持格式完全一致

模型会模仿示例格式。如果示例格式不一致，输出也容易不稳定。

好的示例：

```text
问题：...
结论：...
原因：...
```

坏的示例：

```text
问题：...
答案：...

Q: ...
A: ...
```

### 17.5 不要把业务强约束只交给 few-shot

few-shot 是概率性引导，不是硬规则。

如果要求很严格，例如：

- JSON 必须可解析。
- 字段必须完整。
- 分类标签必须属于枚举。
- 数字范围必须合法。

应结合：

- `JsonOutputParser`
- Pydantic
- 结构化输出
- 后置校验
- 失败重试

### 17.6 注意数据安全

示例中不要放真实敏感数据。

避免包含：

- 手机号、身份证号、地址。
- API Key、Token。
- 真实客户信息。
- 公司内部敏感业务规则。

### 17.7 Few-shot 与 RAG 的区别

Few-shot 示例教模型“怎么答”，RAG 检索内容告诉模型“根据什么答”。

| 能力 | 作用 |
| --- | --- |
| Few-shot | 约束格式、风格、分类标准、解题方式 |
| RAG | 提供外部知识、事实依据、文档内容 |

两者可以结合：

```text
系统规则 -> few-shot 示例 -> 检索到的上下文 -> 用户问题
```

---

## 18. 选择建议

- 简单文本提示词：使用 `PromptTemplate`。
- 多角色 Chat 提示词：使用 `ChatPromptTemplate`。
- 需要对话历史：使用 `ChatPromptTemplate` + `MessagesPlaceholder`。
- 普通文本 few-shot：使用 `FewShotPromptTemplate`。
- Chat Model few-shot：使用 `FewShotChatMessagePromptTemplate`。
- 新版链式调用：优先使用 `prompt | llm | parser`。
- 调试最终提示词：使用 `format` 或 `invoke(...).to_string()`。

一句话总结：`PromptTemplate` 负责把变量安全、清晰地填入提示词；`format` 用来得到字符串，`invoke` 用来参与新版 LangChain 的 Runnable 链式编排。
