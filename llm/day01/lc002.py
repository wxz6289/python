import os
from langchain.chat_models import init_chat_model

if __name__ == "__main__":
  model = init_chat_model(
    model="qwen-max",
    model_provider="openai",
    temperature=1.5,
    top_p=0.95,
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
  )
  print(type(model))
  print(model.invoke("你好，今天杭州天气怎样？"))
