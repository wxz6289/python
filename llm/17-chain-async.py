from langchain_openai import ChatOpenAI
import asyncio
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

async def main():
    resp = await llm.ainvoke([
        ("system", "你是一个中文助手。"),
        ("user", "写一段100字的诗。")
    ])
    print(resp.content)

asyncio.run(main())
