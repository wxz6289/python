import os
from pprint import pprint
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field

load_dotenv('.env')

deepseek_model = init_chat_model(
  model=os.getenv('DEEPSEEK_MODEL'),
  api_key=os.getenv('DEEPSEEK_API_KEY'),
  base_url=os.getenv('DEEPSEEK_BASE_URL'),
  temperature=0.0)
gpt_model = init_chat_model(
  model="gpt-5-nano",
  api_key=os.getenv('CLOSEAI_API_KEY'),
  base_url=os.getenv('CLOSEAI_BASE_URL'),
  temperature=0.0)
agent = create_agent(
  model=deepseek_model,
)

class Movie(BaseModel):
  title: str = Field(description="电影名称")
  year: int = Field(description="电影上映年份")
  director: str = Field(description="电影导演")
  rating: float = Field(description="电影评分")

model_with_structure = gpt_model.with_structured_output(Movie)

response = model_with_structure.invoke("请提供电影 泰坦尼克号 的相关信息")
pprint(response)
print(type(response))
