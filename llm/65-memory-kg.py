import os
from typing import List
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from langchain_neo4j import Neo4jChatMessageHistory, Neo4jGraph  # pyright: ignore[reportMissingImports]
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(dotenv_path="../.env")

api_key = os.getenv("CLOSEAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
  raise EnvironmentError("Please set CLOSEAI_API_KEY (or OPENAI_API_KEY).")

base_url = os.getenv("CLOSEAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("Please set CLOSEAI_BASE_URL (or OPENAI_BASE_URL).")

neo4j_url = os.getenv("NEO4J_URL", "bolt://localhost:7687")
neo4j_username = os.getenv("NEO4J_USERNAME", "neo4j")
neo4j_password = os.getenv("NEO4J_PASSWORD")
neo4j_database = os.getenv("NEO4J_DATABASE", "neo4j")
if not neo4j_password:
  raise EnvironmentError("Please set NEO4J_PASSWORD.")

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

neo4j_graph = Neo4jGraph(
  url=neo4j_url,
  username=neo4j_username,
  password=neo4j_password,
  database=neo4j_database,
  # 关闭 schema 刷新，避免在某些 Neo4j 环境中触发 APOC 依赖。
  refresh_schema=False,
)

prompt = ChatPromptTemplate.from_messages([
  ("system", "你是一个简洁的中文助手，优先利用历史上下文回答。"),
  MessagesPlaceholder(variable_name="history"),
  ("human", "{input}"),
])
chat_chain = prompt | llm | StrOutputParser()


def get_session_history(session_id: str) -> Neo4jChatMessageHistory:
  return Neo4jChatMessageHistory(
    session_id=session_id,
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password,
    database=neo4j_database,
    node_label="LangChainSession",
    window=6,
  )


chain_with_memory = RunnableWithMessageHistory(
  chat_chain,
  get_session_history=get_session_history,
  input_messages_key="input",
  history_messages_key="history",
)

triple_prompt = ChatPromptTemplate.from_messages([
  (
    "system",
    "请从输入中提取事实三元组，按每行 subject|predicate|object 输出。"
    "如果没有可提取事实，输出 NONE。不要输出解释。",
  ),
  ("human", "{text}"),
])
triple_chain = triple_prompt | llm | StrOutputParser()


def extract_triples(text: str) -> List[tuple[str, str, str]]:
  content = triple_chain.invoke({"text": text}).strip()
  if content.upper() == "NONE":
    return []
  triples: List[tuple[str, str, str]] = []
  for line in content.splitlines():
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 3:
      continue
    if all(parts):
      triples.append((parts[0], parts[1], parts[2]))
  return triples


def save_triples_to_neo4j(triples: List[tuple[str, str, str]]) -> None:
  for subject, predicate, object_ in triples:
    neo4j_graph.query(
      """
      // 纯 Cypher 写法，不依赖 APOC
      MERGE (s:Entity {name: $subject})
      MERGE (o:Entity {name: $object})
      MERGE (s)-[r:FACT {predicate: $predicate}]->(o)
      """,
      params={"subject": subject, "predicate": predicate, "object": object_},
    )


def ask(session_id: str, user_input: str) -> str:
  triples = extract_triples(user_input)
  save_triples_to_neo4j(triples)
  return chain_with_memory.invoke(
    {"input": user_input},
    config={"configurable": {"session_id": session_id}},
  )


session_id = "kg-demo-user-001"

print("Q1:", "我叫King，我是前端工程师，正在学习TypeScript。")
print("A1:", ask(session_id, "我叫King，我是前端工程师，正在学习TypeScript。"))
print()

print("Q2:", "我现在在杭州工作，公司使用React和Next.js。")
print("A2:", ask(session_id, "我现在在杭州工作，公司使用React和Next.js。"))
print()

print("Q3:", "你还记得我是谁、在哪里工作、在学什么吗？")
print("A3:", ask(session_id, "你还记得我是谁、在哪里工作、在学什么吗？"))
print()

rows = neo4j_graph.query(
  """
  MATCH (s:Entity)-[r:FACT]->(o:Entity)
  RETURN s.name AS subject, r.predicate AS predicate, o.name AS object
  ORDER BY subject, predicate, object
  """
)
print("triples in neo4j:")
for row in rows:
  print(f"({row['subject']}, {row['predicate']}, {row['object']})")
