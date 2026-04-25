import os

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
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

advantages_prompt = PromptTemplate.from_template(
  """
请分析主题《{topic}》的主要优势。
要求：
- 输出 3 条
- 每条不超过 25 个字
"""
)

risks_prompt = PromptTemplate.from_template(
  """
请分析主题《{topic}》可能遇到的风险或挑战。
要求：
- 输出 3 条
- 每条不超过 25 个字
"""
)

learning_plan_prompt = PromptTemplate.from_template(
  """
请为主题《{topic}》给出一个学习计划。
要求：
- 输出 3 个步骤
- 每个步骤不超过 30 个字
"""
)

merge_prompt = PromptTemplate.from_template(
  """
请把下面 3 条并行链路的结果合并成一份简洁总结。

主题：
{topic}

优势分析：
{advantages}

风险分析：
{risks}

学习计划：
{learning_plan}

输出格式：
1. 综合结论：
2. 关键优势：
3. 主要风险：
4. 下一步行动：
"""
)

text_parser = StrOutputParser()

advantages_chain = advantages_prompt | llm | text_parser
risks_chain = risks_prompt | llm | text_parser
learning_plan_chain = learning_plan_prompt | llm | text_parser


def show_parallel_results(data: dict) -> dict:
  print("\n===== 并行链 1：优势分析 =====")
  print(data["advantages"])
  print("\n===== 并行链 2：风险分析 =====")
  print(data["risks"])
  print("\n===== 并行链 3：学习计划 =====")
  print(data["learning_plan"])
  return data


chain = (
  RunnableParallel(
    topic=RunnableLambda(lambda x: x["topic"]),
    advantages=advantages_chain,
    risks=risks_chain,
    learning_plan=learning_plan_chain,
  )
  | RunnableLambda(show_parallel_results)
  | merge_prompt
  | llm
  | text_parser
)


if __name__ == "__main__":
  result = chain.invoke({"topic": "LCEL 多链并行调用"})
  print("\n===== 最终合并结果 =====")
  print(result)
