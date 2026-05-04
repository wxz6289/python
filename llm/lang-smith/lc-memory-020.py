from langchain.agents import create_agent
import sqlite3
from langgraph_checkpoint_sqlite import SqliteSaver
from langchain.messages import HumanMessage
import os

if __name__ == "__main__":
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  DB_PATH = os.path.join(BASE_DIR, "resources", "checkpoint.db")
  with sqlite3.connect(DB_PATH, check_same_thread=False) as connection:
    checkpointer = SqliteSaver(connection)
    checkpointer.setup()

    agent = create_agent("deepseek-chat", checkpointer=checkpointer)
    result = agent.invoke({"messages": [HumanMessage(content="我是谁? 你是谁?")]},
                          config={"configurable": {"thread_id": "user_king-001"}})

  for message in result.get("messages", []):
    if hasattr(message, "pretty_print"):
      message.pretty_print()
    else:
      print(message.content, end="", flush=True)
