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

router_prompt = ChatPromptTemplate.from_template("""
请判断下面问题属于哪一类：
- tech
- translate

问题：{input}
只返回类别名称
""")

router_chain = router_prompt | model

def smart_router(x):
  category = router_chain.invoke(x).content.strip()

  if category == "translate":
    return translate_chain
  return tech_chain

chain = RunnableLambda(smart_router)

resoult = chain.invoke({"input": "请解释POP是什么意思"})
print(resoult.content, end="")
