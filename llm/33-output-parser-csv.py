from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
from langchain_core.output_parsers import CommaSeparatedListOutputParser
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

parser = CommaSeparatedListOutputParser()

prompt = PromptTemplate.from_template("""
{input}
{format_instructions}
""")
prompt = prompt.partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser
result = chain.invoke({
  "input": "请给出一个csv格式的数据,包含以下字段: name,age,gender",
})
print(result)
