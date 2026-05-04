import os
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from pydantic import StrictStr
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def calculate_multiply(a: int, b: int) -> int:
  """计算两个数的乘积"""
  return a * b


def main() -> None:
  api_key = os.getenv("OPENAI_API_KEY") or os.getenv("CLOSEAI_API_KEY")
  if not api_key:
    raise EnvironmentError("请设置 OPENAI_API_KEY 或 CLOSEAI_API_KEY。")
  base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL")

  model = ChatOpenAI(
    model="gpt-5-nano",
    api_key=StrictStr(api_key),
    **({"base_url": base_url} if base_url else {}),
    use_responses_api=True,
  )

  agent = create_deep_agent(
    model=model,
    tools=[
      calculate_multiply,
    ],
    system_prompt="""
  你是一个数学助手，请帮助用户计算乘积。
  """
  )

  result = agent.invoke({
    "messages": [
      {"role": "user", "content": "请计算 11 * (17 + 42)"},
    ],
  })

  last_msg = result["messages"][-1]
  print(getattr(last_msg, "content", last_msg))

if __name__ == "__main__":
  main()
