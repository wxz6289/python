import os

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

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

outline_prompt = PromptTemplate.from_template(
  """
请为主题《{topic}》生成一个简洁大纲。
要求：
- 只输出 3 个要点
- 每个要点不超过 20 个字
"""
)

article_prompt = PromptTemplate.from_template(
  """
请根据下面的大纲写一段中文短文。

主题：
{topic}

大纲：
{outline}

要求：
- 150 字以内
- 语言通俗
"""
)

summary_prompt = PromptTemplate.from_template(
  """
请根据下面的短文生成标题和一句话摘要。

短文：
{article}

输出格式：
标题：...
摘要：...
"""
)

text_parser = StrOutputParser()

outline_chain = outline_prompt | llm | text_parser
article_chain = article_prompt | llm | text_parser
summary_chain = summary_prompt | llm | text_parser


def show_steps(data: dict) -> dict:
  print("\n===== 第一步：大纲 =====")
  print(data["outline"])
  print("\n===== 第二步：正文 =====")
  print(data["article"])
  print("\n===== 第三步：标题与摘要 =====")
  print(data["summary"])
  return data


chain = (
  RunnablePassthrough.assign(outline=outline_chain)
  .assign(article=article_chain)
  .assign(summary=summary_chain)
  | RunnableLambda(show_steps)
)

if __name__ == "__main__":
  chain.invoke({"topic": "LCEL 多 Prompt 链式顺序调用"})
