from pprint import pprint
from langchain_core.tools.structured import StructuredTool
from pydantic import BaseModel, Field


class SearchInput(BaseModel):
  query: str = Field(description="The query to search for")

class SearchOutput(BaseModel):
  result: str = Field(description="The result of the search")

def search(query: str) -> str:
  """Search the web for information"""
  return "I found some information for you."

search_tool = StructuredTool.from_function(
  func=search,
  name="search tool",
  description="Search the web for information",
  return_direct=True,
  args_schema=SearchInput,
  return_schema=SearchOutput,
)

print(search_tool.name)
print(search_tool.description)
print(search_tool.args_schema)
print(search_tool.func)
print(search_tool.args)
print(search_tool.return_direct)

result = search_tool.invoke("What is the capital of France?")
print(result)
