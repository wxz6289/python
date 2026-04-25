import os
from typing import Dict, Sequence

from pydantic import SecretStr
from langchain_core.messages import BaseMessage
from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI

WINDOW_TURNS = 1
MAX_MESSAGES = WINDOW_TURNS * 2
store: Dict[str, "WindowedChatMessageHistory"] = {}


class WindowedChatMessageHistory(InMemoryChatMessageHistory):
  """只保留最近 max_messages 条消息，避免上下文无限增长。"""

  max_messages: int = MAX_MESSAGES

  def add_messages(self, messages: Sequence[BaseMessage]) -> None:
    super().add_messages(messages)
    if len(self.messages) > self.max_messages:
      del self.messages[:-self.max_messages]


def get_session_history(session_id: str) -> BaseChatMessageHistory:
  if session_id not in store:
    store[session_id] = WindowedChatMessageHistory(max_messages=MAX_MESSAGES)
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

  session_config: RunnableConfig = {"configurable": {"session_id": "user-001"}}

  r1 = chain_with_memory.invoke({"input": "我叫小明，是一名 Python 开发者。"}, config=session_config)
  print("第1轮:", r1.content)

  r2 = chain_with_memory.invoke({"input": "你还记得我是谁吗？"}, config=session_config)
  print("第2轮:", r2.content)

  r3 = chain_with_memory.invoke({"input": "我做什么开发？请一句话回答。"}, config=session_config)
  print("第3轮:", r3.content)

  r4 = chain_with_memory.invoke({"input": "我叫什么？"}, config=session_config)
  print("第4轮:", r4.content)
