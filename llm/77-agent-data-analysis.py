import os
from typing import Literal
from deepagents import create_deep_agent
from langchain_openai import ChatOpenAI
from langchain.agents.middleware import wrap_tool_call
from pydantic import StrictStr
from langchain_core.tools import tool
from langchain_core.utils.uuid import uuid7
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from tavily import TavilyClient
from daytona import Daytona, DaytonaConfig
from langchain_daytona import DaytonaSandbox
from langchain.tools import tool
from slack_sdk import WebClient
import csv
import io

load_dotenv()

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

daytona_api_key = os.getenv("DAYTONA_API_KEY")

config = DaytonaConfig(
  api_key=daytona_api_key,
)
sandbox = Daytona(config).create()
backend = DaytonaSandbox(sandbox=sandbox)
result = backend.execute("echo ready!")
print( result )

data = [
  ["Date", "Product", "Units Sold", "Revenue"],
  ["2025-08-01", "Widget A", 10, 250],
  ["2025-08-02", "Widget B", 5, 125],
  ["2025-08-03", "Widget A", 7, 175],
  ["2025-08-04", "Widget C", 3, 90],
  ["2025-08-05", "Widget B", 8, 200],
]

# Convert to CSV bytes
text_buf = io.StringIO()
writer = csv.writer(text_buf)
writer.writerows(data)
csv_bytes = text_buf.getvalue().encode("utf-8")
text_buf.close()

# Upload to backend
backend.upload_files([("/home/daytona/data/sales_data.csv", csv_bytes)])

slack_token = os.environ["SLACK_USER_TOKEN"]
slack_client = WebClient(token=slack_token)

@tool(parse_docstring=True)
def slack_send_message(text: str, file_path: str | None = None) -> str:
  """Send message, optionally including attachments such as images.

  Args:
      text: (str) text content of the message
      file_path: (str) file path of attachment in the filesystem.
  """
  if not file_path:
    slack_client.chat_postMessage(channel=channel, text=text)
  else:
    fp = backend.download_files([file_path])
    slack_client.files_upload_v2(
      channel="C0123456ABC",  # specify your own channel here
      content=fp[0].content,
      initial_comment=text,
    )

  return "Message sent."


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
  checkpointer = InMemorySaver()
  agent = create_deep_agent(
    model=model,
    tools=[slack_send_message],
    backend=backend,
    checkpointer=checkpointer,
    middleware=[log_tool_calls],
  )

  thread_id = str(uuid7())
  config = {
    "configurable": {
      "thread_id": thread_id,
    }
  }

  input_message = {
    "role": "user",
    "content": (
      "Analyze ./data/sales_data.csv in the current dir and generate a beautiful plot. "
      "When finished, send your analysis and the plot to Slack using the tool."
    ),
  }

  for step in agent.stream(
    {"messages": [input_message]},
    config,
    stream_mode="updates",
  ):
    for _, update in step.items():
      if update and (messages := update.get("messages")) and isinstance(messages, list):
        for message in messages:
          message.pretty_print()

if __name__ == "__main__":
  main()
