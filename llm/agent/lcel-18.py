import os
import sqlite3

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))
DB_PATH = os.path.join(BASE_DIR, "resources", "school.db")

api_key = os.getenv("CLOSEAI_API_KEY")
if not api_key:
  raise EnvironmentError("CLOSEAI_API_KEY is not set")

base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("OPENAI_BASE_URL is not set")

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

text_parser = StrOutputParser()


def clean_sql(text: str) -> str:
  sql = text.strip()
  if sql.startswith("```"):
    lines = sql.splitlines()
    if lines and lines[0].startswith("```"):
      lines = lines[1:]
    if lines and lines[-1].strip() == "```":
      lines = lines[:-1]
    sql = "\n".join(lines).strip()
  if sql.lower().startswith("sql"):
    sql = sql[3:].strip()
  return sql.rstrip(";")


def split_sql_statements(sql: str) -> list[str]:
  return [statement.strip() for statement in sql.split(";") if statement.strip()]


def execute_sql(sql: str) -> str:
  allowed_prefixes = ("select", "insert", "update", "delete")
  outputs = []

  with sqlite3.connect(DB_PATH) as conn:
    conn.row_factory = sqlite3.Row
    for statement in split_sql_statements(sql):
      normalized = statement.lstrip().lower()
      if not normalized.startswith(allowed_prefixes):
        raise ValueError(f"只允许执行 SELECT/INSERT/UPDATE/DELETE，当前 SQL: {statement}")

      cursor = conn.execute(statement)
      if normalized.startswith("select"):
        rows = [dict(row) for row in cursor.fetchall()]
        outputs.append(f"SQL: {statement}\n结果: {rows}")
      else:
        outputs.append(f"SQL: {statement}\n影响行数: {cursor.rowcount}")
    conn.commit()

  return "\n\n".join(outputs)


def show_sql(data: dict) -> dict:
  print("\n===== 生成的 SQL =====")
  print(data["sql"])
  print("\n===== SQL 执行结果 =====")
  print(data["result"])
  return data


if not os.path.exists(DB_PATH):
  raise FileNotFoundError(f"没有找到数据库文件: {DB_PATH}")

db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")

sql_prompt = PromptTemplate.from_template(
  """
你是 SQLite 专家。请根据数据库表结构，把用户的自然语言问题转换成 SQL。

要求：
- 只输出 SQL，不要输出解释。
- 可以使用 SELECT、INSERT、UPDATE、DELETE。
- 如果用户要求修改数据，请在修改语句后追加一条 SELECT 语句验证结果。
- 如果只是查询，请只生成 SELECT。
- 禁止输出 DROP、CREATE、ALTER、TRUNCATE、PRAGMA 等管理类语句。
- 如果需要排序或限制数量，请使用 SQLite 语法。

数据库表结构：
{table_info}

用户问题：
{question}

SQL：
"""
)

answer_prompt = PromptTemplate.from_template(
  """
你是一个数据库助手。请根据用户问题、生成的 SQL 和 SQL 执行结果，用中文回答。

用户问题：
{question}

生成的 SQL：
{sql}

SQL 执行结果：
{result}

请给出简洁回答：
"""
)

sql_chain = sql_prompt | llm | text_parser | RunnableLambda(clean_sql)

chain = (
  RunnablePassthrough.assign(table_info=lambda _: db.get_table_info())
  .assign(sql=sql_chain)
  .assign(result=lambda x: execute_sql(x["sql"]))
  | RunnableLambda(show_sql)
  | answer_prompt
  | llm
  | text_parser
)


if __name__ == "__main__":
  question = "LangChain 课程成绩最高的学生是谁？分数是多少？"
  answer = chain.invoke({"question": question})
  print("\n===== 最终回答 =====")
  print(answer)
