from langchain_community.chat_models import ChatTongyi

if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )
  result = model.stream("请给我介绍langchain")
  for chunk in result:
    print(chunk.content, end="", flush=True)
