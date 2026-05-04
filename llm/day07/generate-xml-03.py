from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
from langchain_core.output_parsers import XMLOutputParser
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
import os

load_dotenv()

api_key = os.getenv("CLOSEAI_API_KEY")
if not api_key:
  raise EnvironmentError("Please set CLOSEAI_API_KEY.")

base_url = os.getenv("CLOSEAI_BASE_URL")
if not base_url:
  raise EnvironmentError("Please set CLOSEAI_BASE_URL.")

model = ChatAnthropic(
  model="claude-haiku-4-5",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

parser = XMLOutputParser()

prompt = PromptTemplate.from_template("""
{input}
{format_instructions}
""").partial(format_instructions=parser.get_format_instructions())

chain = prompt | model
result = chain.invoke({
  "input": "杭州有几个区? 各个区的名字是什么?",
})
print(result.content)

