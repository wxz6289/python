from langchain_openai import OpenAI
import os

if __name__ == "__main__":
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY") or "sk-cf1wIjsmF8Hkuk2lCX3I9Nl6WuDMDk1iKrU7jq205jlyZwDx"
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")
  claude_api_key = "sk-jbr415mhVuzLsDZ8aquxyr9EfzpKKUZqG4q51P7NYhysUYns"
  llm = OpenAI(
    model="claude-3-5-haiku-20241022",
    temperature=0,
    api_key=claude_api_key,
    base_url="https://api.mcxhm.cn"
    # base_url="https://api.deepseek.com/beta",
  )

  try:
    for chunk in llm.stream("请写一首春天的诗"):
      print(chunk, end="", flush=True)
  except Exception as e:
    print("opps!")
    print(e)
