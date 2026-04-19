from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
import math

@tool
def square(x: int) -> int:
  """计算x的平方"""
  return x ** 2

@tool
def log(x: int) -> float:
  """计算x的以10为底的对数"""
  return math.log(x, 10)

if __name__ == "__main__":
  system_prompt = """
  你是一个计算助手，请帮助用户计算x的平方或以10为底的对数。
  示例：
  user: 计算2的平方
  assistant: 2**2 = 4

  user: 计算100的平方后再计算以10为底的对数
  assistant: 10**2 = 100, log10(100) = 2
  """

  agent = create_agent(model="deepseek-chat",
                       tools = [square, log],
                       system_prompt=system_prompt)

  message = HumanMessage("请计算20的平方后再计算以10为底的对数")
  response = agent.invoke({"messages": [message]})

  for message in response.get("messages", []):
    if isinstance(message, str):
      print(message)
    else:
      message.pretty_print()
