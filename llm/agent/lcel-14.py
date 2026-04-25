from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr

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


class SkillOutput(BaseModel):
  name: str = Field(description="助手名称")
  role: str = Field(description="助手角色介绍")
  skills: list[str] = Field(description="助手掌握的技能列表")


parser = JsonOutputParser(pydantic_object=SkillOutput)

prompt = PromptTemplate(
  template=(
    "{input}\n"
    "请按照以下格式要求输出 JSON，不要输出 Markdown 代码块或额外解释。\n"
    "{format_instructions}"
  ),
  input_variables=["input"],
  partial_variables={"format_instructions": parser.get_format_instructions()},
)

chain = prompt | llm | parser


if __name__ == "__main__":
  result = chain.invoke({"input": "你是谁？你会什么技能？"})
  print(json.dumps(result, ensure_ascii=False, indent=2))
