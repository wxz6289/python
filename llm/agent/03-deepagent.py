import os
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from tavily import TavilyClient
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def internet_search(
  query: str,
  topic: Literal["web", "general", "news", "finance", "books", "patents"] = "web",
  num_results: int = 5,
  include_raw_content: bool = False
) -> str:
  """使用 Tavily 进行网络搜索"""
  return tavily.search(query, topic=topic, include_raw_content=include_raw_content, max_results=num_results)

def main() -> None:
  api_key = os.getenv("OPENAI_API_KEY") or os.getenv("CLOSEAI_API_KEY")
  if not api_key:
    raise EnvironmentError("请设置 OPENAI_API_KEY 或 CLOSEAI_API_KEY。")
  base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL")

  model = init_chat_model(
    model="gpt-5-nano",
    api_key=api_key,
    **({"base_url": base_url} if base_url else {}),
    use_responses_api=True,
  )

  research_instructions = """
  你是一个资深技术人员，你的工作是关注前沿技术发展趋势，收集新兴技术发展形成报告。
  你可以使用网络搜索工具收集相关信息并进行深度总结
  ## `internet_search`
  使用它可以进行网络搜索返回你查询的内容
  """

  agent = create_deep_agent(
    model=model,
    tools=[
      internet_search,
    ],
    system_prompt= research_instructions
  )

  result = agent.invoke({
    "messages": [
      {"role": "user", "content": "deepagent核心内容有哪些？"},
    ],
  })

  last_msg = result["messages"][-1]
  print(getattr(last_msg, "content", last_msg))


if __name__ == "__main__":
  main()
