from langchain_ollama import ChatOllama

if __name__ == "__main__":
  model = ChatOllama(model="deepseek-r1:8b")
  result = model.invoke("请总结Vue核心要点")
  print(result)
