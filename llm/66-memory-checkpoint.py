from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage

if __name__ == "__main__":
  config = { "configurable": { "thread_id": "test" } }

  agent = create_agent(
    "deepseek-chat",
    checkpointer=InMemorySaver()
    )

  result = agent.invoke(
    {"messages": [
      HumanMessage(content="你好，我是King, 请给我介绍React相关的知识"),
      HumanMessage(content="你好，我是谁？")
    ]},
    config=config)

  for message in result.get("messages", []):
    if hasattr(message, "pretty_print"):
      message.pretty_print()
    else:
      print(message.content, end="", flush=True)
