import os
from typing import Dict
from pydantic import SecretStr
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI
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
      ("system", "你是一个有记忆的助手。"),
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
  config: RunnableConfig = {"configurable": {"session_id": "demo-user-001"}}

  q1 = "我叫小明，是一名后端开发。"
  a1 = chain_with_memory.invoke({"input": q1}, config=config)
  print("第1轮:", a1.content)

  q2 = "我做什么岗位？"
  a2 = chain_with_memory.invoke({"input": q2}, config=config)
  print("第2轮:", a2.content)

  q3 = "请一句话复述你记住了我哪些信息。"
  a3 = chain_with_memory.invoke({"input": q3}, config=config)
  print("第3轮:", a3.content)

  print("\n===== 当前 Memory Buffer =====\n")
  history = get_session_history("demo-user-001")
  for msg in history.messages:
    role = type(msg).__name__.replace("Message", "")
    print(f"{role}: {msg.content}")
