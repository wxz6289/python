from langchain_openai import ChatOpenAI
from pydantic import SecretStr
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
  print(openai_api_key)
  print(base_url)
  print(SecretStr(openai_api_key))
  model = ChatOpenAI(
    model="gpt-5.4-nano-2026-03-17",
    temperature=0,
    api_key=SecretStr(openai_api_key),
    base_url=base_url,
  )
  result = model.invoke("你好，请给我倒水。")
  print(result.content)
