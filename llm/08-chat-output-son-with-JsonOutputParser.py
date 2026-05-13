from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import SecretStr
import os


if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

  llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key= SecretStr(deepseek_api_key),
    base_url="https://api.deepseek.com/v1",
    timeout=30,
    max_retries=2,
  )

  parser = JsonOutputParser()

  try:
    prompt = PromptTemplate.from_template(
      "请输出JSON:\n{input}\n{format_instructions}"
    ).partial(format_instructions=parser.get_format_instructions())

    chain = prompt | llm | parser
    res = chain.invoke({"input": "帮我倒水"})
    print(res)
  except Exception as e:
    print("opps!")
    print(e)
