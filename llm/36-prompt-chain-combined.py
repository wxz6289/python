from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

import os

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

model = init_chat_model(
    model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0, api_key=deepseek_api_key
)

prompt_1 = ChatPromptTemplate.from_template("请帮为为{product}写一条广告语")
prompt_2 = ChatPromptTemplate.from_template(
  "请把这句广告语改得更有冲击力：{text}"
)

agent1 = prompt_1 | model
agent2 = prompt_2 | model

chain = (
  prompt_1
  | model
  | (lambda x: {"text": x.content})
  | prompt_2
  | model
)

result = chain.stream("幸惠超市")
for chunk in result:
  print(chunk.content, end="", flush=True)
