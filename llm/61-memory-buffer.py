import os
from typing import Dict

from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from model import create_model

store: Dict[str, InMemoryChatMessageHistory] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
  if session_id not in store:
    store[session_id] = InMemoryChatMessageHistory()
  return store[session_id]


if __name__ == "__main__":
  # api_key = os.getenv("DASHSCOPE_API_KEY")
  # if not api_key:
  #   raise ValueError("请先设置环境变量 DASHSCOPE_API_KEY")
  #
  # llm = ChatOpenAI(
  #   model= os.getenv("DASHSCOPE_MODEL"),
  #   api_key=api_key,
  #   base_url= os.getenv("DASHSCOPE_BASE_URL"),
  #   temperature=0.2,
  # )
  llm = create_model("qwen", "qwen3.6-plus")

  prompt = ChatPromptTemplate.from_messages(
    [
      ("system", "你是一个有上下文记忆的助手，回答要简洁。"),
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

  session_config = {"configurable": {"session_id": "user-001"}}

  session_config2 = {"configurable": {"session_id": "user-002"}}

  r1 = chain_with_memory.invoke({"input": "我叫小明，是一名 Python 开发者。"}, config=session_config)
  print("第1轮:", r1.content)

  r2 = chain_with_memory.invoke({"input": "你还记得我是谁吗？"}, config=session_config)
  print("第2轮:", r2.content)

  r3 = chain_with_memory.invoke({"input": "我做什么开发？请一句话回答。"}, config=session_config)
  print("第3轮:", r3.content)

  r4 = chain_with_memory.invoke({"input": "你记住我的开发技能了吗？"}, config=session_config2)
  print("第4轮:", r4.content)
