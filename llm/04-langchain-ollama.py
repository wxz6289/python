from dotenv import load_dotenv
from langchain_ollama import ChatOllama
import os

load_dotenv()

if __name__ == "__main__":
  model = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "deepseek-r1:8b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
  )

  response = model.invoke(
    input=[
      {"role": "system", "content": "你是一个助手"},
      {"role": "user", "content": "请介绍一下你自己"}
    ]
  )
  print(response.content)
