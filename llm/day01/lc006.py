from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
import os

if __name__ == "__main__":
  model = init_chat_model(
    model="qwen-max",
    model_provider="openai",
    temperature=1.5,
    top_p=0.95,
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
  )
  agent = create_agent(model=model)
  result = agent.invoke({
    "messages": [
      {"role": "user", "content": "请给我介绍create_agent"}
      ]
    })
  print(result)
