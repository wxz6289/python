from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate, \
  ChatPromptTemplate

prompt = ChatPromptTemplate([
  SystemMessage("你是顶级的文档助手"),
  HumanMessagePromptTemplate.from_template("{input}")
])

model = init_chat_model(model="deepseek-chat")
chain = prompt | model
response = chain.invoke({"input": "请详细介绍LLM中的MoE"})
print(response.content, end="", flush=True)


