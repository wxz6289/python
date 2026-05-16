import os
from typing import Dict

from pydantic import SecretStr
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

store: Dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
  if session_id not in store:
    store[session_id] = InMemoryChatMessageHistory()
  return store[session_id]


if __name__ == "__main__":
  api_key = os.getenv("DEEPSEEK_API_KEY")
  if not api_key:
    raise ValueError("请先设置环境变量 DEEPSEEK_API_KEY")

  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=SecretStr(api_key),
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
  )

  prompt = ChatPromptTemplate.from_messages(
    [
      ("system", "你是一个有短时记忆的助手，回答简洁。"),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{input}"),
    ]
  )

  chain = prompt | llm

  # 纯 LCEL 记忆写法：等价于 ConversationBufferMemory 的“完整历史缓存”行为
  chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
  )

  config: RunnableConfig = {"configurable": {"session_id": "demo-user-001"}}

  questions = [
    "我叫小明，在做后端开发。",
    "我还在学习 LangChain。",
    "你还记得我的名字和方向吗？",
  ]

  for i, q in enumerate(questions, start=1):
    resp = chain_with_memory.invoke({"input": q}, config=config)
    print(f"第{i}轮 用户: {q}")
    print(f"第{i}轮 助手: {resp.content}\n")

  history = get_session_history("demo-user-001")
  print("===== 当前会话历史条数 =====")
  print(len(history.messages))
