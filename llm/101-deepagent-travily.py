import os
import sys
from typing import Literal

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import AIMessage, BaseMessage
from langchain_deepseek import ChatDeepSeek
from langgraph.types import Overwrite
from pydantic import SecretStr
from tavily import TavilyClient

load_dotenv(".env", override=True)

VALID_TOPICS = {"software development", "ai", "business"}

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
  raise EnvironmentError("请设置 TAVILY_API_KEY")

tavily_client = TavilyClient(api_key=tavily_api_key)


def message_text(message: BaseMessage) -> str:
  content = getattr(message, "content", "")
  if isinstance(content, str):
    return content.strip()
  if isinstance(content, list):
    parts: list[str] = []
    for block in content:
      if isinstance(block, str):
        parts.append(block)
      elif isinstance(block, dict) and block.get("type") == "text":
        parts.append(str(block.get("text", "")))
    return "".join(parts).strip()
  return str(content).strip()


def last_ai_text(messages: list[BaseMessage]) -> str:
  for message in reversed(messages):
    if isinstance(message, AIMessage):
      text = message_text(message)
      if text:
        return text
  return ""


@tool
def search_web(
  query: str,
  max_results: int = 5,
  topic: Literal["general", "news", "finance"] = "general",
  include_raw_content: bool = False,
) -> dict:
  """Search the web for information on a given query."""
  safe_topic = topic if topic in VALID_TOPICS else "general"
  try:
    return tavily_client.search(
      query,
      max_results=max_results,
      include_raw_content=include_raw_content,
      topic=safe_topic,
    )
  except Exception as exc:
    return {"error": str(exc), "query": query, "topic": safe_topic}


def create_model() -> ChatDeepSeek:
  api_key = os.getenv("DEEPSEEK_API_KEY")
  if not api_key:
    raise EnvironmentError("请设置 DEEPSEEK_API_KEY")

  return ChatDeepSeek(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=SecretStr(api_key),
    api_base=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0,
    max_tokens=8192,
  )


def main() -> None:
  model = create_model()
  research_prompt = """You are an expert researcher that can search the web for information.
Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `search_web`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
The topic must be one of: software development, ai, business.
"""
  deep_agent = create_deep_agent(
    model=model,
    tools=[search_web],
    system_prompt=research_prompt,
  )
  agent_input = {
    "messages": [
      {
        "role": "user",
        "content": (
          "2026年前端开发、后端开发、全栈开发、AI工程师的招聘现状以及就业情况,"
          "AI对这些开发岗位的影响,写一份详细真实的研究报告"
        ),
      },
    ],
  }

  final_text = ""
  print("开始研究，请稍候...", flush=True)
  for chunk in deep_agent.stream(
    agent_input,
    stream_mode="updates",
    config={"recursion_limit": 50},
  ):
    for update in chunk.values():
      if not update or not (messages := update.get("messages")):
        continue
      message_list = messages.value if isinstance(messages, Overwrite) else messages
      for message in message_list:
        text = message_text(message)
        if text:
          final_text = text

  if not final_text:
    response = deep_agent.invoke(
      agent_input,
      config={"recursion_limit": 50},
    )
    final_text = last_ai_text(response["messages"])

  if final_text:
    print(final_text, flush=True)
  else:
    print("未生成研究报告，请检查 Tavily API 或模型配置。", file=sys.stderr, flush=True)
    sys.exit(1)


if __name__ == "__main__":
  main()
