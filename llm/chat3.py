from langchain_openai import ChatOpenAI

import os

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

  chain = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
    timeout=30,
    max_retries=2,
    response_format= { "type": "json_object"}
  )

  try:
    result = chain.invoke("你好，请给我倒水。")
    print(result.content)
  except Exception as e:
    print("opps!")
    print(e)
