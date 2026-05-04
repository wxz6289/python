from langchain.agents import create_agent
from langchain.messages import HumanMessage
from pydantic import BaseModel
import json

class User(BaseModel):
  id: int
  name: str
  age: int
  gender: str
  email: str

class UserList(BaseModel):
  users: list[User]

if __name__ == "__main__":
  system_prompt = """
  你是一个数据模拟助手，请帮助用户生成用户要求的数据。
  示例：
  user: 生成10条用户信息数据
  assistant: 请按照以下JSON格式生成10条用户信息数据：
  请按照以下JSON格式生成10条用户信息数据：
  [
    {
      "id": 1,
      "name": "张曼玉",
      "age": 20,
      "gender": "女",
      "email": "zhangmanyu@gmail.com"
    },
    {
      "id": 2,
      "name": "王菲",
      "age": 50,
      "gender": "女",
      "email": "wangfei@gmail.com"
    },
    ...
    {
      "id": 10,
      "name": "刘德华",
      "age": 60,
      "gender": "男",
      "email": "liudehua@gmail.com"
    }
  ]
  注意: 无需输出任何其他内容，直接输出JSON格式数据。
  """

  agent = create_agent(model="deepseek-chat",
                       response_format=UserList,
                       system_prompt=system_prompt)

  message = HumanMessage("请生成10条用户数据,以json格式输出")
  response = agent.invoke({"messages": [message]})

  messages = response.get("messages", []) if isinstance(response, dict) else response.messages
  print(json.dumps(messages, indent=2, ensure_ascii=False))
