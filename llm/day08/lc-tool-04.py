from pprint import pprint
from langchain_core.tools.structured import StructuredTool
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field, SecretStr
from langchain_core.prompts import ChatPromptTemplate
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

model = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

llm_with_tools = model.bind_tools([tavily_search_tool])

prompt_template = ChatPromptTemplate(
  [
    ("system", "You are a helpful assistant that can search the web for information."),
    ("human", "{input}"),
  ]
)

prompt = prompt_template.format_messages(
  input ="What is the capital of France?"
)
ai_msg = llm_with_tools.invoke(prompt)
pprint(ai_msg)
