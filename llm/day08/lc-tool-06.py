from pprint import pprint
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.chat_history import  BaseChatMessageHistory
from pydantic import SecretStr
from langchain_tavily import TavilySearch
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
import os

load_dotenv(dotenv_path="../.env")

api_key = os.getenv("CLOSEAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not api_key:
  raise EnvironmentError("Please set CLOSEAI_API_KEY (or OPENAI_API_KEY).")

base_url = os.getenv("CLOSEAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("Please set CLOSEAI_BASE_URL (or OPENAI_BASE_URL).")

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
  raise EnvironmentError("Please set TAVILY_API_KEY.")


tavily_search_tool = TavilySearch(
  max_results=5,
  topic="general",
  api_key=SecretStr(tavily_api_key),
)

history = BaseChatMessageHistory()

model = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

agent = create_agent(
  model=model,
  tools=[tavily_search_tool]
)

result = agent.invoke({
  "messages": [
    HumanMessage(content="What is the capital of France?")
  ]
})
for message in result.get("messages", []):
  if isinstance(message, str):
    print(message)
  else:
    message.pretty_print()
