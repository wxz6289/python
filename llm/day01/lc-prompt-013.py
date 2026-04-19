from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.messages import HumanMessage


if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )
  system_prompt = """
  你是一个编程助手，请帮助用户解决在编程过程中遇到的问题。
  示例：
  user: 如何安装Python？
  assistant: 请按照以下步骤安装Python：
  1. 下载Python安装包
  2. 运行安装包
  3. 安装完成后，输入python --version命令，查看Python版本

  user: 如何安装Pandas？
  assistant: 请按照以下步骤安装Pandas：
  1. 打开终端，输入python -m pip install pandas命令，安装Pandas
  2. 安装完成后，输入python -c "import pandas as pd; print(pd.__version__)"命令，查看Pandas版本
  """

  agent = create_agent(model=model)
  message = HumanMessage("如何使用最新的langchainGraph？")
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
