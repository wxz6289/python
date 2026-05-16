import datetime

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, \
  SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
  AIMessagePromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import os

load_dotenv()

class Person(BaseModel):
  name: str = Field(..., description="你的名字")
  age: int = Field(..., description="你的年龄")
  birthday: datetime.date = Field(..., description="你的生日")

if __name__ == "__main__":
  parser = PydanticOutputParser(pydantic_object=Person)
  model = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "deepseek-r1:8b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
  )
  
  template = """
  你是一个数据Mock助手，专注生成指定格式的数据 
  
  {format_instruction}
  
  """
  prompt = ChatPromptTemplate.from_template(
    template,
    partial_variables={"format_instruction": parser.get_format_instructions()}
  )

  chain = prompt | model
  
  response = chain.stream({"input": "请生成指定格式的JSON数据"})
  for chunk in response:
    print(chunk.content, end="", flush=True)
