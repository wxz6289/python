from langchain.agents import create_agent

if __name__ == "__main__":
  agent = create_agent(model="deepseek-chat")
  messages = agent.stream(
    {
      "messages": [
      {"role": "user", "content": "请给我介绍流式调用"}
      ]
      },
      stream_mode="messages",
    )

  for token, metadata in messages:
    if isinstance(token, str):
      if token:
        print(token, end="", flush=True)
      continue

    content = getattr(token, "content", "")
    if isinstance(content, str) and content:
      print(content, end="", flush=True)
