from langchain_openai import ChatOpenAI
from langchain_core.callbacks import get_usage_metadata_callback

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

  with get_usage_metadata_callback() as cb:
    result = llm.invoke("请总结Vue核心要点")
    print(result.content, end="", flush=True)
    print(cb)

