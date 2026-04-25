from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

if __name__ == "__main__":
  messages = [
    SystemMessage(content="你是一个智能助手，请回答用户的问题。"),
    HumanMessage(content="你好，我是谁？"),
    AIMessage(content="你好，我是小智。"),
  ]

  sym = SystemMessage(content="你是一个智能助手，请回答用户的问题。", additional_kwargs={"tool": "hello"})
  print(sym)
  print(sym.additional_kwargs)
  sym.pretty_print()
  hum = HumanMessage(content="你好，我是谁？")
  print(hum)
  ai = AIMessage(content="你好，我是小智。")
  print(ai)
