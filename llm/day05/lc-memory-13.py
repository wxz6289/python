import os
from typing import Dict
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory

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
      ("system", "你是一个有会话记忆的助手，回答简洁。"),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{input}"),
    ]
  )

  chain = prompt | llm
  chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
  )

  # 同一个 session_id 会自动复用历史，实现“会话自动记忆”
  config: RunnableConfig = {"configurable": {"session_id": "demo-user-001"}}

  q1 = "我叫小明，是后端开发。"
  r1 = chain_with_memory.invoke({"input": q1}, config=config)
  print("第1轮:", r1.content)

  q2 = "你还记得我是谁、做什么吗？"
  r2 = chain_with_memory.invoke({"input": q2}, config=config)
  print("第2轮:", r2.content)

  q3 = "请用一句话总结你记住了我的哪些信息?"
  r3 = chain_with_memory.invoke({"input": q3}, config=config)
  print("第3轮:", r3.content)
