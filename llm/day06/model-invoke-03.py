from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain.messages import HumanMessage
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "../.env"))


openai_api_key = os.getenv("CLOSEAI_API_KEY")
if not openai_api_key:
    raise EnvironmentError("Please set CLOSEAI_API_KEY.")
base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
    raise EnvironmentError("Please set OPENAI_BASE_URL.")


if __name__ == "__main__":
  model = ChatOpenAI(
    model="gpt-5.4-nano-2026-03-17",
    temperature=0,
    api_key=SecretStr(openai_api_key),
    base_url=base_url,
  )
  message = HumanMessage(content="请介绍langchain中的model的调用方式。")
  result = model.invoke([message])
  print(result.content)
