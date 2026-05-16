from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import PromptTemplate

import os

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

  llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/v1",
    max_tokens=512
  )
  parser = CommaSeparatedListOutputParser()
  prompt = PromptTemplate(
    template="请列出5个:\n{subject}.\n{format_instructions}",
    input_variables= ["subject"]
  ).partial(
    format_instructions = parser.get_format_instructions()
  )

  input_text = prompt.format(subject="常用的JavaScript库")
  result = llm.invoke(input_text)
  l = parser.parse(result.content)
  print(l)

