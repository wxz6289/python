from pprint import pprint
from langchain_core.tools.structured import StructuredTool
from langchain_core.messages import ToolMessage
from pydantic import BaseModel, Field, SecretStr
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


class SearchInput(BaseModel):
  query: str = Field(description="The query to search for")

def search(query: str) -> str:
  """Search the web for information"""
  if "capital of france" in query.lower():
    return "Paris is the capital of France."
  return f"No mocked result for query: {query}"

search_tool = StructuredTool.from_function(
  func=search,
  name="search_tool",
  description="Search the web for information",
  args_schema=SearchInput,
)

model = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

llm_with_tools = model.bind_tools([search_tool])

question = "What is the capital of France?"
ai_msg = llm_with_tools.invoke(question)

print("tool calls:")
pprint(ai_msg.tool_calls)

messages = [("human", question), ai_msg]
for tool_call in ai_msg.tool_calls:
  if tool_call["name"] != search_tool.name:
    continue
  tool_result = search_tool.invoke(tool_call["args"])
  messages.append(
    ToolMessage(
      content=tool_result,
      tool_call_id=tool_call["id"],
    )
  )

final_answer = llm_with_tools.invoke(messages)
print("final answer:")
print(final_answer.content)
