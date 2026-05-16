from langchain.agents import create_agent
from langchain.tools import tool
from langchain.messages import HumanMessage
import json
from urllib.parse import quote
from urllib.request import urlopen

@tool
def get_weather(city: str) -> str:
  """Get the weather of a city"""
  city = city.strip()
  if not city:
    return "城市名不能为空。"

  try:
    # wttr.in 提供免费天气查询接口，适合教学和快速验证。
    url = f"https://wttr.in/{quote(city)}?format=j1"
    with urlopen(url, timeout=8) as resp:
      payload = json.loads(resp.read().decode("utf-8"))

    current = payload.get("current_condition", [{}])[0]
    temp_c = current.get("temp_C", "未知")
    humidity = current.get("humidity", "未知")
    wind_kmph = current.get("windspeedKmph", "未知")
    desc_list = current.get("weatherDesc", [])
    desc = desc_list[0].get("value", "未知") if desc_list else "未知"
    return (
      f"{city} 当前天气：{desc}，气温 {temp_c}°C，"
      f"湿度 {humidity}%，风速 {wind_kmph} km/h。"
    )
  except Exception as exc:
    return f"查询 {city} 天气失败：{exc}"

if __name__ == "__main__":
  agent = create_agent(model="deepseek-chat", tools=[get_weather])

  response = agent.invoke({
      "messages": [
        HumanMessage(content="请给我查询杭州天气"),
      ]
    })

  messages = response.get("messages", []) if isinstance(response, dict) else getattr(response, "messages", [])
  for message in messages:
    message.pretty_print()
