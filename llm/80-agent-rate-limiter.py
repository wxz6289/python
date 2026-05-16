import os
from pprint import pprint

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter

load_dotenv('.env')

rate_limiter = InMemoryRateLimiter(
  requests_per_second=.1,
  check_every_n_seconds=0.1,
  max_bucket_size=10
)

gpt_model = init_chat_model(
  model="gpt-5-nano",
  api_key=os.getenv('CLOSEAI_API_KEY'),
  base_url=os.getenv('CLOSEAI_BASE_URL'),
  rate_limiter=rate_limiter,
  temperature=0.0)

tool = {"type": "web_search"}
model_with_tool = gpt_model.bind_tools([tool])


response = model_with_tool.invoke("今天中国有什么重大新闻?")
pprint(response.content_blocks)
