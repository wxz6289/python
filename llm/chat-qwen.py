from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage,SystemMessage

import os

if __name__ == "__main__":
  api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not api_key:
    raise EnvironmentError("Please set DASHSCOPE_API_KEY (or OPENAI_API_KEY).")

  llm = ChatOpenAI(
    model="qwen3.6-plus",
    temperature=0.8,
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
  )

  messages = [
    SystemMessage(content="你好，我是小智!"),
    HumanMessage(content="你好，今天杭州天气怎样？")
  ]

  try:
    # llm.invoke(messages)
    for chunk in llm.stream(messages):
      print(chunk.content, end="", flush=True)
  except Exception as e:
    print("opps!")
    print(e)
