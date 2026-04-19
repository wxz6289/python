from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.messages import HumanMessage


if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )
  system_prompt = """
  你是一个数据模拟助手，请帮助用户生成用户要求的数据。
  示例：
  user: 生成10条用户信息数据
  assistant: 请按照以下格式生成10条用户信息数据：
  （{user_id}, {user_name}, {user_age}, {user_gender}, {user_email}）

  请按照以下SQL语句生成10条用户信息数据：
  sql：
  INSERT INTO users (id, name, age, gender, email) VALUES (%s, %s, %s, %s, %s)
  """

  agent = create_agent(model=model)
  message = HumanMessage("请生成10条用户数据")
  result = agent.stream(
    {
      "messages": [message],
    },
    system_prompt= system_prompt,
    stream_mode="messages",
  )

  for token, metadata in result:
    if isinstance(token, str):
      print(token, end="", flush=True)
    else:
      token.pretty_print()
