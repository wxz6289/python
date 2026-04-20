from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

import os

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

chain = init_chat_model(
    model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0, api_key=deepseek_api_key
)

template = "请帮为{product}写一个广告语"
prompt = ChatPromptTemplate.from_template(template)

agent = prompt | chain

# result = agent.invoke({"product": "幸惠超市"})
result = agent.stream("幸惠超市")
for chunk in result:
  print(chunk.content, end="", flush=True)
