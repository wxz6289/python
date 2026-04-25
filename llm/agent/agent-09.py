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


def init_demo_db(db_path: str) -> None:
  os.makedirs(os.path.dirname(db_path), exist_ok=True)
  with sqlite3.connect(db_path) as conn:
    conn.executescript(
      """
      DROP TABLE IF EXISTS students;
      DROP TABLE IF EXISTS courses;
      DROP TABLE IF EXISTS scores;
      DROP TABLE IF EXISTS teachers;

      CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        city TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        title TEXT NOT NULL
      );

      CREATE TABLE courses (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        teacher_id INTEGER NOT NULL,
        FOREIGN KEY(teacher_id) REFERENCES teachers(id)
      );

      CREATE TABLE scores (
        student_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        score INTEGER NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id),
        FOREIGN KEY(course_id) REFERENCES courses(id)
      );
      """
    )
    conn.executemany(
      "INSERT INTO students (id, name, age, gender, city) VALUES (?, ?, ?, ?, ?)",
      [
        (1, "King", 18, "男", "Shanghai"),
        (2, "Alice", 19, "女", "Beijing"),
        (3, "Bob", 20, "男", "Shenzhen"),
      ],
    )
    conn.executemany(
      "INSERT INTO teachers (id, name, age, gender, title) VALUES (?, ?, ?, ?, ?)",
      [
        (1, "陈老师", 36, "男", "讲师"),
        (2, "王老师", 42, "女", "教授"),
      ],
    )
    conn.executemany(
      "INSERT INTO courses (id, name, teacher_id) VALUES (?, ?, ?)",
      [
        (1, "Python", 1),
        (2, "LangChain", 2),
      ],
    )
    conn.executemany(
      "INSERT INTO scores (student_id, course_id, score) VALUES (?, ?, ?)",
      [
        (1, 1, 95),
        (1, 2, 98),
        (2, 1, 88),
        (2, 2, 91),
        (3, 1, 76),
        (3, 2, 84),
      ],
    )
    conn.commit()


def build_llm() -> ChatOpenAI:
  api_key = (
    os.getenv("CLOSEAI_API_KEY")
    or os.getenv("OPENAI_API_KEY")
    or os.getenv("DEEPSEEK_API_KEY")
  )
  if not api_key:
    raise EnvironmentError("请先设置 CLOSEAI_API_KEY、OPENAI_API_KEY 或 DEEPSEEK_API_KEY")

  base_url = os.getenv("OPENAI_BASE_URL")
  model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
  if os.getenv("DEEPSEEK_API_KEY") and not base_url:
    base_url = "https://api.deepseek.com/v1"
    model = os.getenv("OPENAI_MODEL", "deepseek-chat")

  return ChatOpenAI(
    model=model,
    temperature=0,
    api_key=SecretStr(api_key),
    base_url=base_url,
  )


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


def execute_sql(db_path: str, sql: str) -> str:
  allowed_prefixes = ("select", "insert", "update", "delete")
  outputs = []

  with sqlite3.connect(db_path) as conn:
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


def build_sql_qa_chain(llm: ChatOpenAI, db: SQLDatabase):
  sql_prompt = PromptTemplate.from_template(
    """
你是 SQLite 专家。请根据表结构为用户问题生成 SQL。

要求:
- 只输出 SQL，不要输出解释。
- 可以使用 SELECT、INSERT、UPDATE、DELETE 查询。
- 如果用户要求修改数据，请生成必要的 INSERT/UPDATE/DELETE 语句，并在最后追加一条 SELECT 查询用于验证结果。
- 如果用户要求插入关联数据，请先插入父表数据，再插入子表数据。
- 如果需要排序或限制数量，请使用 SQLite 语法。
- 禁止输出 DROP、CREATE、ALTER、TRUNCATE、PRAGMA 等管理类语句。

表结构:
{table_info}

用户问题:
{question}

SQL:
"""
  )
  answer_prompt = PromptTemplate.from_template(
    """
你是一个 SQL 数据分析助手。请根据用户问题、生成的 SQL 和 SQL 执行结果，用中文回答。

用户问题:
{question}

SQL:
{query}

SQL 执行结果:
{result}

请给出简洁答案:
"""
  )
  write_query = sql_prompt | llm | StrOutputParser() | RunnableLambda(clean_sql)

  return (
    RunnablePassthrough.assign(table_info=lambda _: db.get_table_info())
    .assign(query=write_query)
    .assign(result=lambda x: execute_sql(DB_PATH, x["query"]))
    | answer_prompt
    | llm
    | StrOutputParser()
  )


if __name__ == "__main__":
  init_demo_db(DB_PATH)
  db = SQLDatabase.from_uri(f"sqlite:///{DB_PATH}")
  llm = build_llm()
  chain = build_sql_qa_chain(llm, db)

  questions = [
    "LangChain 课程成绩最高的学生是谁？分数是多少？",
    "请插入一名学生：姓名李四，年龄20，性别女，城市杭州；再给她插入 LangChain 课程成绩99分，并查询 LangChain 课程最高分学生。",
    "请把 King 的 Python 成绩更新为100分，并查询 King 的所有课程成绩。",
    "请删除 Bob 的所有成绩记录，并查询当前还有成绩记录的学生姓名。",
  ]

  for question in questions:
    answer = chain.invoke({"question": question})
    print(f"\n问题: {question}")
    print(f"回答: {answer}")
