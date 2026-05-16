from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage,SystemMessage

import os

if __name__ == "__main__":
  api_key = os.getenv("DASHSCOPE_API_KEY")
  if not api_key:
    raise EnvironmentError("Please set DASHSCOPE_API_KEY.")

  llm = ChatOpenAI(
    model=os.getenv("DASHSCOPE_MODEL", "qwen3.6-plus"),
    temperature=0.8,
    api_key=api_key,
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
    streaming=True
  )

  messages = [
    SystemMessage(content="你是一个智能助手，名字叫小智，请使用中文回答。"),
    HumanMessage(content="请介绍一下Python中的asyncio")
  ]

  try:
    for chunk in llm.stream(messages):
      if not chunk.content:
        continue
      print(chunk.content, end="", flush=True)
  except Exception as e:
    print(e)
