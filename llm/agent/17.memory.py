from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os
import requests
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

@tool
def get_user_info(username: str) -> str:
  """获取用户信息"""
  headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
    "User-Agent": "llm-agent"
  }
  url = f"https://api.github.com/users/{username}"
  response = requests.get(url, headers=headers, timeout=5)
  print(response)
  if response.status_code == 200:
    return response.json()
  else:
    return "用户不存在"



with PostgresSaver.from_conn_string(os.getenv("DB_URI")) as saver:
  saver.setup()
  agent = create_agent(
    model=os.getenv("DEEPSEEK_MODEL"),
    # model_kwargs = { "thinking": False},
    tools= [get_user_info],
    checkpointer= saver,
  )
  response = agent.invoke(
    {"messages": [{ "role": "user", "content":"请获取用户 wxz6289 的信息"}]},
    { "configurable": { "thread_id": "1"}}
  )

  print(response)
