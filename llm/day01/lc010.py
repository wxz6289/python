from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.messages import HumanMessage

if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )
  agent = create_agent(model=model)
  message = HumanMessage([
    { "type": "text", "text": "请给我介绍langchain" },
    { "type": "image", "url": "https://langchain.com/images/logo.png" }
  ])
  result = agent.stream(
    {
      "messages": [message],
    },
    stream_mode="messages",
  )

  for token, metadata in result:
    if isinstance(token, str):
      print(token, end="", flush=True)
    else:
      token.pretty_print()
