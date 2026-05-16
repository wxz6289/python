from langchain_openai import ChatOpenAI
from pydantic import SecretStr

import os

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY")

  chain = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL"),
    temperature=0,
    api_key=SecretStr(deepseek_api_key),
    base_url=os.getenv("DEEPSEEK_BASE_URL"),
    timeout=30,
    max_retries=2
  )

  try:
    result = chain.invoke("你好，请给我倒水。")
    print(result.content)
  except Exception as e:
    print("opps!")
    print(e)
