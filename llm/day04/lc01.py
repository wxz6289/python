from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
import numexpr

@tool
def calculator(expr: str) -> str:
  """执行数学表达式计算，例如: 2**8 或 (10 + 5) / 3。"""
  return str(numexpr.evaluate(expr))


if __name__ == "__main__":
  system_prompt = """
  你是一个数学助手。
  当用户提出数学问题时，优先使用 calculator 工具进行精确计算，再返回简洁答案。
  """

  agent = create_agent(
    model="deepseek-chat",
    tools=[calculator],
    system_prompt=system_prompt,
  )

  message = HumanMessage("2**8 等于多少")
  response = agent.invoke({"messages": [message]})

  for msg in response.get("messages", []):
    if hasattr(msg, "pretty_print"):
      msg.pretty_print()
    else:
      print(msg)
