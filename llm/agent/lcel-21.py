from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6380/0")

llm = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=os.getenv("CLOSEAI_API_KEY"),
  base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL"),
)

prompt = ChatPromptTemplate.from_messages([
  (
    "system",
    "你是一个有 Redis 聊天记忆的助手。请基于上文回答用户问题，回答简洁。",
  ),
  MessagesPlaceholder(variable_name="history"),
  ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()

def get_session_history(session_id: str) -> RedisChatMessageHistory:
  return RedisChatMessageHistory(
    session_id=session_id,
    url=REDIS_URL,
    key_prefix="lc-chat-history:",
    ttl=60 * 60 * 24,
  )

chain_with_redis_memory = RunnableWithMessageHistory(
  chain,
  get_session_history=get_session_history,
  input_messages_key="input",
  history_messages_key="history",
)

config: RunnableConfig = {"configurable": {"session_id": "redis-demo-user-001"}}

result1 = chain_with_redis_memory.invoke(
  {"input": "我叫小明，是一名后端开发，正在学习 LangChain。"},
  config=config,
)
print("第1轮:", result1)

result2 = chain_with_redis_memory.invoke(
  {"input": "你还记得我叫什么、在学习什么吗？"},
  config=config,
)
print("第2轮:", result2)

result3 = chain_with_redis_memory.invoke(
  {"input": "我是干什么工作的？"},
  config=config,
)
print("第3轮:", result3)

