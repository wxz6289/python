from langchain_openai import ChatOpenAI
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

print(api_key, base_url)

model = ChatAnthropic(
  model="claude-haiku-4-5",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)

xml_data = """
<book>
  <title>The Great Gatsby</title>
  <author>F. Scott Fitzgerald</author>
  <year>1925</year>
</book>
"""

parser = XMLOutputParser()

prompt = PromptTemplate.from_template(
  """
You are an XML parsing assistant.
Parse the XML input and normalize it to a clean XML output.

{format_instructions}

Input XML:
{input}

IMPORTANT:
- Output XML only.
- Do not include markdown fences.
- Do not include any explanation.
  """)

chain = prompt | model | parser
result = chain.invoke({
  "input": xml_data,
  "format_instructions": parser.get_format_instructions(),
})

print(result)
