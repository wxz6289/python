from langchain_openai import ChatOpenAI
from pydantic import SecretStr

import os

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

  chain = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=SecretStr(deepseek_api_key),
    base_url="https://api.deepseek.com/v1",
  )

  try:
    result = chain.invoke([
      ("system", "你是我的学习助手"),
      ("human", "请帮我总结最近React常见的面试题")
    ])
    print(result.content)
  except Exception as e:
    print("opps!")
    print(e)
