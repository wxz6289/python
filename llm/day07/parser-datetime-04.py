from langchain_anthropic import ChatAnthropic  # pyright: ignore[reportMissingImports]
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
from pydantic import BaseModel, Field
from datetime import datetime
from langchain_core.output_parsers import PydanticOutputParser
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

class DateTimeResult(BaseModel):
  value: datetime = Field(description="Normalized datetime")


parser = PydanticOutputParser[DateTimeResult](pydantic_object=DateTimeResult)

prompt = PromptTemplate.from_template("""
你是一个日期时间解析助手。
请将用户输入中的日期时间标准化后输出为结构化结果。

{format_instructions}

用户输入:
{input}

要求:
- 只输出日期时间结果
- 不要输出解释
- 不要输出多余文本
""")

prompt = prompt.partial(format_instructions=parser.get_format_instructions())

print(parser.get_format_instructions())

chain = prompt | model | parser
result = chain.invoke({
  "input": "请给出2026/04/27 10:20:12的日期时间",
})
print(result.value.isoformat())
