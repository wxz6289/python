from langchain_community.chat_models import ChatTongyi

if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )
  result = model.invoke("请给我介绍langchain-community")
  print(result.content)
