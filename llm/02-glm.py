from zai import ZhipuAiClient
from dotenv import load_dotenv
import os

load_dotenv()

if __name__ == "__main__":
  client = ZhipuAiClient(
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL")
  )

  response = client.chat.completions.create(
    model= os.getenv("GLM_MODEL"),
    messages=[
      {"role": "system", "content": "你是一个助手"},
      {"role": "user", "content": "请介绍一下你自己"}
    ],
    temperature=0.5
  )

  print(response.choices[0].message.content)
