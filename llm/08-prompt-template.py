from langchain_core.prompts import ChatPromptTemplate, \
  AIMessagePromptTemplate

chat_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一个起名大师，你的名字叫{name}"),
        ("human", "你好{name},感觉如何?"),
        ("ai", "你好，我状态很好"),
        ("human", "{user_input}"),
    ]
)

prompt = chat_template.format_messages(name="高启明", user_input="你叫什么名字?")
print(prompt)

chat_template = ChatPromptTemplate.from_template(role="ai", template="我是{name}的助理")
chat_message = chat_template.format(name="你")
print(chat_message)

ai_template = AIMessagePromptTemplate.from_template("愿{name}与你同在")
ai_message= ai_template.format(name="主")
print(ai_message)
