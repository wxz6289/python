from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.messages import HumanMessage


if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )

  agent = create_agent(model=model)
  message = HumanMessage("我是谁？")
  result = agent.stream(
    {
      "messages": [message],
    },
    system_prompt="你是一个智能助手，请回答用户的问题。",
    stream_mode="messages",
  )

  for token, metadata in result:
    if isinstance(token, str):
      print(token, end="", flush=True)
    else:
      token.pretty_print()
