from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

api_key = os.getenv("CLOSEAI_API_KEY")
if not api_key:
  raise EnvironmentError("CLOSEAI_API_KEY is not set")

base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("OPENAI_BASE_URL is not set")

if __name__ == "__main__":
  model = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=api_key,
    base_url=base_url,
    temperature=0,
  )

  prompt = ChatPromptTemplate.from_template("请根据以下信息回答问题: {info} \n {question}")
  chain = prompt | model | StrOutputParser()
  result = chain.invoke({"info": "你好，我是AI助手，很高兴认识你。", "question": "学习AI Agent是否有前途?"})
  print(result)
