from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

llm = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=os.getenv("CLOSEAI_API_KEY"),
  base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL"),
)

prompt = ChatPromptTemplate.from_messages([
  (
    "system",
    "你是一个 SQL 查询助手。请根据上文表结构和用户问题生成 SQL，并给用户一个清晰回复。\n"
    "回复格式：\n"
    "SQL：<SQL语句>\n"
    "说明：<这条 SQL 查询了什么>",
  ),
  MessagesPlaceholder(variable_name="messages"),
  ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()

messages = [
  HumanMessage(content="数据库里有一张 users 表，字段包括 id、username、age、city。"),
  AIMessage(content="好的，我会基于 users 表结构生成 SQL。"),
  HumanMessage(content="请回答时同时给出 SQL 和简短说明。"),
  AIMessage(content="明白，我会同时给出 SQL 和说明。"),
]

result = chain.invoke({
  "messages": messages,
  "input": "请查询用户名为张三的用户信息",
})

print(result)
