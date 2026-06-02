from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
import os
from dotenv import load_dotenv

load_dotenv(".env", override=True)

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY.")

  llm = ChatOpenAI(
    model= os.getenv("DEEPSEEK_MODEL"),
    api_key= SecretStr(deepseek_api_key),
    base_url= os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0,
  )

  parser = JsonOutputParser()

  try:
    prompt = PromptTemplate.from_template(
      "\n{query}\n{format_instructions}"
    ).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm | parser
    res = chain.invoke({"query": "请输出一个JSON对象列表，包含name和age两个字段，以当前流行的网红信息为例，列表长度为3。"})
    print(res)
  except Exception as e:
    print(e)
