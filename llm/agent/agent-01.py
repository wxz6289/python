import os

import numexpr
import requests
from pydantic import SecretStr
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_openai import ChatOpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


@tool
def serpapi_search(query: str) -> str:
  """使用 SerpAPI 搜索互联网信息并返回前几条结果摘要。"""
  api_key = os.getenv("SERPAPI_API_KEY")
  if not api_key:
    return "缺少 SERPAPI_API_KEY，无法执行联网搜索。"

  response = requests.get(
    "https://serpapi.com/search.json",
    params={
      "q": query,
      "api_key": api_key,
      "engine": "google",
      "hl": "zh-cn",
      "num": 5,
    },
    timeout=20,
  )
  response.raise_for_status()
  payload = response.json()

  organic = payload.get("organic_results", [])[:5]
  if not organic:
    return "未检索到有效结果。"

  lines = []
  for i, item in enumerate(organic, start=1):
    title = item.get("title", "无标题")
    link = item.get("link", "")
    snippet = item.get("snippet", "")
    lines.append(f"{i}. {title}\n链接: {link}\n摘要: {snippet}")

  return "\n\n".join(lines)


@tool
def llm_math(expression: str) -> str:
  """执行数学表达式计算，例如: 2**10、(128 + 64) / 3。"""
  try:
    return str(numexpr.evaluate(expression))
  except Exception as exc:
    return f"计算失败: {exc}"


if __name__ == "__main__":
  deepseek_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_key:
    raise ValueError("请先设置环境变量 DEEPSEEK_API_KEY")

  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=SecretStr(deepseek_key),
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
  )

  agent = create_agent(
    model=llm,
    tools=[serpapi_search, llm_math],
    system_prompt=(
      "你是一个可联网搜索的问答助手。"
      "遇到需要最新信息的问题时，优先调用 serpapi_search；"
      "遇到数学计算时，优先调用 llm_math。"
      "回答时请先给结论，再给 2-4 条依据。"
    ),
  )

  user_question = "帮我算 2**10 + 23 的值, 并告诉我毛爷爷的生日是哪天?"
  result = agent.invoke({"messages": [HumanMessage(content=user_question)]})

  for msg in result.get("messages", []):
    if hasattr(msg, "pretty_print"):
      msg.pretty_print()
    else:
      print(msg)
