from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

import os

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

model = init_chat_model(
    model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0, api_key=deepseek_api_key
)

tech_chain = ChatPromptTemplate.from_template("你是技术专家，请回答: {input}") | model
translate_chain = ChatPromptTemplate.from_template("请翻译：{input}") | model

def router(x):
  text = x["input"]
  if "翻译" in text:
    return translate_chain
  return tech_chain

chain = RunnableLambda(router)

resoult = chain.invoke({"input": "hello world"})
print(resoult.content, end="")
