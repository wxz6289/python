from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class Task(BaseModel):
  action: str
  object: str

if __name__ == "__main__":
  api_key = os.getenv("CLOSEAI_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not api_key:
    raise EnvironmentError("Please set CLOSEAI_API_KEY (or OPENAI_API_KEY).")

  chain = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=SecretStr(api_key),
    base_url= os.getenv("OPENAI_BASE_URL"),
    timeout=30,
    max_retries=2,
  )

  structured_llm = chain.with_structured_output(Task)
  result = structured_llm.invoke("请将这句话转成任务JSON：'你好，请给我倒水。'")
  print(f"action={result.action}, object={result.object}")
