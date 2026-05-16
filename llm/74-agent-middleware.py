import os
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import wrap_tool_call
from pydantic import StrictStr
from langchain_core.tools import tool
from dotenv import load_dotenv

load_dotenv()

@tool
def calculate_multiply(a: int, b: int) -> int:
  """计算两个数的乘积"""
  return a * b

call_count = [0]  # Use list to allow modification in nested function

@wrap_tool_call
def log_tool_calls(request, handler):
  """Intercept and log every tool call - demonstrates cross-cutting concern."""
  call_count[0] += 1
  tool_name = request.name if hasattr(request, 'name') else str(request)

  print(f"[Middleware] Tool call #{call_count[0]}: {tool_name}")
  print(f"[Middleware] Arguments: {request.args if hasattr(request, 'args') else 'N/A'}")

  # Execute the tool call
  result = handler(request)

  # Log the result
  print(f"[Middleware] Tool call #{call_count[0]} completed")

  return result

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
    middleware=[log_tool_calls],
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
