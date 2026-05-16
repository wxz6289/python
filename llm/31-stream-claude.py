from langchain_openai import OpenAI
import os

if __name__ == "__main__":
  claude_api_key = os.getenv("CLAUDE_API_KEY")
  llm = OpenAI(
    model="claude-3-5-haiku-20241022",
    temperature=0,
    api_key=claude_api_key,
    base_url="https://api.mcxhm.cn"
  )

  try:
    for chunk in llm.stream("请写一首春天的诗"):
      print(chunk, end="", flush=True)
  except Exception as e:
    print("opps!")
    print(e)
