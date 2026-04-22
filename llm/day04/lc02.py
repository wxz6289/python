import os

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_tavily import TavilySearch
import numexpr


@tool
def calculator(expr: str) -> str:
  """执行数学表达式计算，例如: 2**10 或 (128 + 64) / 2。"""
  return str(numexpr.evaluate(expr))


if __name__ == "__main__":
  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0,
  )

  search_tool = TavilySearch(max_results=3)
  tools = [calculator, search_tool]

  system_prompt = """
  你是一个工具增强助手。
  - 涉及数学运算时，优先使用 calculator 获取精确结果。
  - 涉及实时信息时，使用 Tavily 搜索后再回答。
  - 最终答案请简洁清晰。
  """

  agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
  )

  message = HumanMessage("帮我算 2**10 + 当前新加坡人口是多少")
  response = agent.invoke({"messages": [message]})

  for msg in response.get("messages", []):
    if hasattr(msg, "pretty_print"):
      msg.pretty_print()
    else:
      print(msg)
