from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,SystemMessage
import os
from pydantic import SecretStr
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env"))

openai_api_key = os.getenv("CLOSEAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError("Please set CLOSEAI_API_KEY.")
base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
    raise EnvironmentError("Please set OPENAI_BASE_URL.")

llm = ChatOpenAI(
  model="gpt-5.4-nano-2026-03-17",
  temperature=0,
  api_key=SecretStr(openai_api_key),
  base_url=base_url,
)

messages1 = [
  SystemMessage(content="你是一个中文助手。"),
  HumanMessage(content="写一段100字的诗。")
]
messages2 = [
  SystemMessage(content="你是一个英文助手。"),
  HumanMessage(content="Write a 100-word poem in English.")
]
messages3 = [
  SystemMessage(content="你是一个日文助手。"),
  HumanMessage(content="日本語で100字の詩を書いてください。")
]

messages = [messages1, messages2, messages3]

# for message in messages:
#   resp = llm.invoke(message)
#   print(resp.content)
result = llm.batch(messages)
for resp in result:
  print(resp.content)
  print("-" * 60)
