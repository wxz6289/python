# import os
from langchain_community.chat_models import ChatTongyi

if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
    # api_key=os.getenv("TONGYI_API_KEY"),
    # base_url=os.getenv("TONGYI_BASE_URL"),
  )
  print(type(model))
  print(model.invoke("你好，今天杭州天气怎样？"))
