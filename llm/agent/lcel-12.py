from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("CLOSEAI_API_KEY")
if not api_key:
  raise EnvironmentError("CLOSEAI_API_KEY is not set")

base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("OPENAI_BASE_URL is not set")

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  api_key=api_key,
  base_url=base_url,
)

prompt = PromptTemplate.from_template("{input}")

chain = prompt | llm
# llm.bind(stop = ["\n"])

result = chain.invoke({"input": '你是谁？你会什么技能？'})
print(result.content)
