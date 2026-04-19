from langchain.agents import create_agent

if __name__ == "__main__":
  agent = create_agent(model="deepseek-chat")
  result = agent.invoke({
    "messages": [
      {"role": "user", "content": "请给我介绍deepseek-chat"}
      ]
    })
  print(result)
