import os
from pprint import pprint

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv('.env')

gpt_model = init_chat_model(
  model="gpt-5-nano",
  api_key=os.getenv('CLOSEAI_API_KEY'),
  base_url=os.getenv('CLOSEAI_BASE_URL'),
  temperature=0.0)

json_scheme = {
  "title": "Movie",
  "description": "电影详细信息",
  "type": "object",
  "properties": {
    "title": {
      "type": "string",
      "description": "电影名称"
    },
    "year": {
      "type": "string",
      "description": "电影上映年份"
    },
    "director": {
      "type": "string",
      "description": "电影导演"
    },
    "rating": {
      "type": "number",
      "description": "电影评分"
    }
  },
  "required": [
    "title",
    "year",
    "director",
    "rating"
  ]
}

model_with_structure = gpt_model.with_structured_output(json_scheme, method="json_schema", include_raw= True)

response = model_with_structure.invoke("请提供电影 小男孩 的相关信息")
pprint(response)
print(type(response))
