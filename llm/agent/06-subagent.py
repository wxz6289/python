import os
from typing import Literal
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import wrap_tool_call
from pydantic import StrictStr
from langchain_core.tools import tool
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def internet_search(
  query: str,
  topic: Literal["web", "general", "news", "javascript", "react", "vue"] = "web",
  num_results: int = 5,
  include_raw_content: bool = False
) -> str:
  """使用 Tavily 进行网络搜索"""
  return tavily.search(query, topic=topic, include_raw_content=include_raw_content, max_results=num_results)

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

  research_subagent = {
    "name": "research-agent",
    "description": "Used to research more in depth questions",
    "system_prompt": "You are a great researcher",
    "tools": [internet_search],
    "model": "openai:gpt-5-nano",  # Optional override, defaults to main agent model
  }
  subagents = [research_subagent]

  agent = create_deep_agent(
    model=model,
    subagents=subagents,
    middleware=[log_tool_calls],
  )

  result = agent.invoke({
    "messages": [
      {"role": "user", "content": "请查询Vue和React的最新动态"},
    ],
  })

  last_msg = result["messages"][-1]
  print(getattr(last_msg, "content", last_msg))

if __name__ == "__main__":
  main()
