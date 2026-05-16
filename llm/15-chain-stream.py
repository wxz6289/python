import os

from langchain.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY.")

  llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
  )

  messages = [
    SystemMessage(content="你好，我是小智!"),
    HumanMessage(content="你好，请给我倒水。")
  ]

  try:
    # llm.invoke(messages)
    for chunk in llm.stream(messages):
      print(chunk.content, end="", flush=True)
  except Exception as e:
    print("opps!")
    print(e)
