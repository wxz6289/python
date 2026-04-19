from langchain_community.chat_models import ChatTongyi
from langchain.agents import create_agent
from langchain.messages import HumanMessage
# from ipywidgets import FileUpload
# from IPython.display import display
import base64


if __name__ == "__main__":
  model = ChatTongyi(
    model="qwen-max",
  )
  # file_upload = FileUpload()
  # uploaded_file = file_upload.value[0]
  with open("../example/index.png", "rb") as f:
    image_data = f.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")
    print(base64_image)

  agent = create_agent(model=model)
  message = HumanMessage([
    { "type": "text", "text": "请给我分析这张图片内容" },
    { "type": "image", "base64": base64_image, "mime_type": "image/png" }
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
