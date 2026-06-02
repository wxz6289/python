import os
from langchain.chat_models import init_chat_model
import requests
from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

# override=True：避免 shell 中旧的 DEEPSEEK_API_KEY 覆盖 .env
load_dotenv(".env", override=True)


def create_deepseek() -> ChatDeepSeek:
  api_key = os.getenv("DEEPSEEK_API_KEY")
  if not api_key:
    raise EnvironmentError("请设置 DEEPSEEK_API_KEY")

  base_url = os.getenv("DEEPSEEK_BASE_URL")
  return init_chat_model(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=SecretStr(api_key),
    api_base=base_url,
    temperature=0,
    max_tokens=1000,
  )

  # return ChatDeepSeek(
  #   model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
  #   api_key=SecretStr(api_key),
  #   api_base=base_url,
  #   temperature=0,
  #   max_tokens=1000,
  # )


WTTR_HEADERS = {"User-Agent": "curl/7.68.0"}


@tool
def get_weather(city: str) -> dict:
  """根据城市名称获取实时天气信息（wttr.in，无需 API Key）"""
  response = requests.get(
    f"https://wttr.in/{city}",
    params={"format": "j1", "lang": "zh"},
    headers=WTTR_HEADERS,
    timeout=20,
  )
  response.raise_for_status()
  data = response.json()

  current = data["current_condition"][0]
  area = data["nearest_area"][0]
  weather_desc = current.get("lang_zh") or current.get("weatherDesc") or [{"value": "未知"}]

  return {
    "city": area["areaName"][0]["value"],
    "region": area.get("region", [{}])[0].get("value"),
    "country": area["country"][0]["value"],
    "weather": weather_desc[0]["value"],
    "temperature": f"{current.get('temp_C')}°C",
    "feels_like": f"{current.get('FeelsLikeC')}°C",
    "humidity": f"{current.get('humidity')}%",
    "wind": f"{current.get('winddir16Point')} {current.get('windspeedKmph')} km/h",
    "observation_time": current.get("observation_time"),
  }


def main() -> None:
  model = create_deepseek()

  deep_agent = create_deep_agent(
    model=model,
    tools=[get_weather],
    system_prompt="你是一个天气助手，可以调用工具查询城市天气。",
  )

  response = deep_agent.invoke({
    "messages": [
      {"role": "user", "content": "杭州今天的天气怎样?"},
    ],
  })

  last_msg = response["messages"][-1]
  print(getattr(last_msg, "content", last_msg))


if __name__ == "__main__":
  main()
