import json
import math
import os
from typing import List, Literal

import requests
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import tool
from langchain_deepseek import ChatDeepSeek
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

search_tool = TavilySearch(
  max_results=5,
  topic = "general"
)

class WeatherInput(BaseModel):
  location: str = Field(description="城市名称")
  unit: Literal["metric", "imperial"] = Field(description="温度单位", default="metric")
  include_forecast: bool = Field(description="是否包含未来天气预报", default=False)
  exclude: str = Field(description="排除的天气数据，多个数据用逗号分隔", default="hourly,daily")

def get_coordinates(city: str):
    """根据城市名称获取经纬度"""
    api_key = os.getenv("WEATHER_API_KEY")

    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city,
        "limit": 1,   # 只取一个结果
        "appid": api_key
    }

    res = requests.get(url, params=params)
    if res.status_code != 200:
      return f"查询 {city} 经纬度失败：{res.status_code}"
    payload = json.loads(res.text)
    return payload[0]["lat"], payload[0]["lon"]

@tool
def get_weather(input: WeatherInput) -> str:
  """获取城市天气信息"""
  api_key = os.getenv("WEATHER_API_KEY")
  if not api_key:
    raise ValueError("WEATHER_API_KEY is not set")

  lat, lon = get_coordinates(input.location)
  if isinstance(lat, str) or isinstance(lon, str):
    return lat

  url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&exclude={input.exclude}&appid={api_key}&lang=zh_cn"
  print(url)
  res = requests.get(url)
  print(res.status_code)
  print(res.text)
  if res.status_code != 200:
    return f"查询 {input.location} 天气失败：{res.status_code}"
  payload = json.loads(res.text)
  return f"{input.location} 当前天气：{payload.get('weather', [{}])[0].get('description', '未知')}, 气温 {payload.get('main', {}).get('temp', 0)}°{input.unit}"

@tool("square", description="计算x的平方")
def square(x: int) -> int:
  return x ** 2

@tool
def log(x: int) -> float:
  """
  计算x的以10为底的对数
  Args:
    x: 要计算的数
  Returns:
    x的以10为底的对数
  """
  return math.log(x, 10)

@tool
def web_search(query: str) -> str:
  """搜索相关资料"""
  return search_tool.invoke(query)


class Reference(BaseModel):
  title: str = Field(description="参考资料的标题")
  url: str = Field(description="参考资料的URL")

class Answer(BaseModel):
  references: List[Reference] = Field(description="参考资料")
  answer: str = Field(description="回答")

def router(query: str) -> str:
  if any(k in query for k in ["计算", "平方", "对数", "天气"]):
    return "agent"
  elif any(k in query for k in ["生成", "数据", "JSON"]):
    return "structured"
  else:
    return "agent"

def run(query: str, agent, llm) -> str:
  route = router(query)
  match route:
    case "structured":
      return llm.with_structured_output(Answer).invoke( [HumanMessage(query)])
    case _:
      return agent.invoke({"messages": [HumanMessage(query)]})

if __name__ == "__main__":
  system_prompt = """
  你是全能助手，优先调用工具获取真实信息，如果工具返回失败，则使用模型生成信息。 工具包括get_weather、square、log。
  示例：
  user: 查询北京天气
  assistant: 北京 当前天气：晴，气温 20°C

  user: 计算2的平方
  assistant: 2**2 = 4

  user: 计算20的平方后再计算以10为底的对数
  assistant: 20**2 = 400, log10(400) = 2.6020599913279623

  """
  deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY")
  llm = ChatDeepSeek(model="deepseek-chat",
                     base_url="https://api.deepseek.com/v1",
                     api_key=deepseek_api_key)
  agent = create_agent(model=llm,
                       tools = [get_weather, square, log, search_tool],
                       system_prompt=system_prompt)
  response = run("蒸蚌是什么梗? 请搜索相关资料并生成JSON数据", agent, llm)

  for message in response:
    if hasattr(message, "pretty_print"):
      message.pretty_print()
    else:
      print(message, end="", flush=True)
