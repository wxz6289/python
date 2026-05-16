from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, field_validator
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

import os

class Joke(BaseModel):
  setup: str = Field(description="设置笑话的主题")
  punchline: str = Field(description="笑话的内容")

  @field_validator("setup")
  @classmethod
  def question_mark(cls, v):
    if v[-1] != "?":
      raise ValueError("询问格式错误!")
    return v


if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY.")

  llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.1,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
    max_tokens=512
  )
  parser = PydanticOutputParser(pydantic_object=Joke)

  # prompt = PromptTemplate(
  #   template="回答用户的询问:\n{format_instructions}\n{query}",
  #   input_variables=["query"],
  #   partial_variables={"format_instructions": parser.get_format_instructions() }
  # )

  prompt = PromptTemplate(
    template="回答用户的询问:\n{format_instructions}\n{query}"
  ).partial(
    format_instructions = parser.get_format_instructions()
  )

  prompt_model = prompt | llm
  result = prompt_model.invoke({ "query": "请给我讲一个笑话"})
  print(result.content, end="", flush=True)

