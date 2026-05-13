from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import os

load_dotenv()

if __name__ == "__main__":
  model = init_chat_model(
    model_provider="openai",
    model=os.getenv("GLM_MODEL"),
    api_key=os.getenv("GLM_API_KEY"),
    base_url=os.getenv("GLM_BASE_URL")
  )

  response = model.invoke(
    input=[
      {"role": "system", "content": "你是一个助手"},
      {"role": "user", "content": "请介绍一下你自己"}
    ]
  )
  print(response.content)
