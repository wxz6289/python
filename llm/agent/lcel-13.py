from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from pydantic import SecretStr

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

api_key = os.getenv("CLOSEAI_API_KEY")
if not api_key:
  raise EnvironmentError("CLOSEAI_API_KEY is not set")

base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("OPENAI_BASE_URL is not set")

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

prompt = PromptTemplate.from_template(
  "{input}\n请调用 get_skills 工具，并把你会的技能放到 skills 数组中。"
)

tools = [{
  "type": "function",
  "function": {
    "name": "get_skills",
    "description": "获取技能",
    "parameters": {
      "type": "object",
      "properties": {
        "skills": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["skills"]
    },
  },
}]

chain = prompt | llm.bind_tools(
  tools,
  tool_choice={"type": "function", "function": {"name": "get_skills"}},
)


if __name__ == "__main__":
  result = chain.invoke({"input": "你是谁？你会什么技能？"})
  print(result)
  print(result.tool_calls)
