import os
from pprint import pprint
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, \
  ModelResponse
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic

load_dotenv('.env')

deepseek_model = init_chat_model(
  model=os.getenv('DEEPSEEK_MODEL'),
  api_key=os.getenv('DEEPSEEK_API_KEY'),
  base_url=os.getenv('DEEPSEEK_BASE_URL'),
  temperature=0.0)

anthropic_model = ChatAnthropic(
  model_name="claude-haiku-4-5",
  api_key=os.getenv('ANTHROPIC_API_KEY'),
  base_url=os.getenv('ANTHROPIC_BASE_URL'),
  temperature=0.0)

claude_model = init_chat_model(
  model="claude-haiku-4-5",
  api_key=os.getenv('ANTHROPIC_API_KEY'),
  base_url=os.getenv('ANTHROPIC_BASE_URL'),
  temperature=0.0)

gpt_model = init_chat_model(
  model="gpt-5-nano",
  api_key=os.getenv('CLOSEAI_API_KEY'),
  base_url=os.getenv('CLOSEAI_BASE_URL'),
  temperature=0.0)

@wrap_model_call
def dynamic_model_selector(request: ModelRequest, handler) -> ModelResponse:
  """根据对话动态切换语言模型"""
  print(type(request))
  pprint(request)
  pprint(request.state["messages"])
  print(type(request))
  pprint(request)
  pprint(request.state["messages"])
  message_count = len(request.state["messages"])
  if message_count >= 3:
    model = deepseek_model
  else:
    model = gpt_model
  return handler(request.override(model=model))

agent = create_agent(
  model=deepseek_model,
  middleware=[dynamic_model_selector],
)

if __name__ == "__main__":
  response = agent.invoke(
    {
      "messages":
        [HumanMessage( content= "最新的langchain有哪些核心内容?")]
    }
  )
  print( response)
