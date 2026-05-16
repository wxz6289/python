import os
from pprint import pprint

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from typing_extensions import Annotated, TypedDict

load_dotenv('.env')

gpt_model = init_chat_model(
  model="gpt-5-nano",
  api_key=os.getenv('CLOSEAI_API_KEY'),
  base_url=os.getenv('CLOSEAI_BASE_URL'),
  temperature=0.0)

class Actor(TypedDict):
  name: str
  role: str

class MovieDetails(TypedDict):
  title: Annotated[str, ..., "电影名称"]
  year: Annotated[str, ..., "电影上映年份"]
  director: Annotated[str, ...,"电影导演"]
  rating: Annotated[float, ...,"电影评分"]
  actors: list[Actor]
  genres: list[str]

model_with_structure = gpt_model.with_structured_output(MovieDetails)

response = model_with_structure.invoke("请提供电影 泰坦尼克号 的相关信息")
pprint(response)
print(type(response))
