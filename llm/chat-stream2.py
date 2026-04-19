from langchain_openai import OpenAI
import os

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

  llm = OpenAI(
    model="deepseek-chat",
    temperature=0,
    api_key=deepseek_api_key,
    base_url="https://api.deepseek.com/beta",
  )

  try:
    for chunk in llm.stream("请写一首春天的诗"):
      print(chunk, end="", flush=True)
  except Exception as e:
    print("opps!")
    print(e)
