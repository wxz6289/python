from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
from dotenv import load_dotenv
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


prompt = PromptTemplate.from_template("""
{input}
请按照以下XML格式输出,不要输出任何其他内容:
<city><counter>count</counter><regions><region>name1</region><region>name2</region>...</regions></city>
""")

chain = prompt | model
result = chain.invoke({
  "input": "杭州有几个区? 各个区的名字是什么?",
})
print(result.content)

