from langchain.chat_models import init_chat_model

model = init_chat_model(model="deepseek-chat")
response = model.invoke("什么是大模型?")
print(response.content, end="", flush=True)


