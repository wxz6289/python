from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains.router import MultiPromptChain

import os

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

model = init_chat_model(
    model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0, api_key=deepseek_api_key
)

prompt_infos = [
  {
    "name": "tech",
    "description": "回答技术问题",
    "prompt_template": "你是技术专家：{input}"
  },
  {
    "name": "translate",
    "description": "做翻译",
    "prompt_template": "请翻译：{input}"
  },
]

chain = MultiPromptChain.from_prompts(
  llm = model,
  prompt_infos= prompt_infos,
  default_chain= None
)

resoult = chain.invoke("请解释什么是TCP协议")
print(resoult)
