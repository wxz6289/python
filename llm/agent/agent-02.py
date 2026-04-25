import os
import numexpr
import requests
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain.agents import create_react_agent, load_tools, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StrOutputParser


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


@tool
def serpapi_search(query: str) -> str:
  """使用 SerpAPI 搜索互联网信息并返回摘要结果。"""
  api_key = os.getenv("SERPAPI_API_KEY")
  if not api_key:
    return "缺少 SERPAPI_API_KEY，无法执行联网搜索。"

  response = requests.get(
    "https://serpapi.com/search.json",
    params={
      "q": query,
      "api_key": api_key,
      "engine": "google",
      "hl": "zh-cn",
      "num": 5,
    },
    timeout=20,
  )
  response.raise_for_status()
  payload = response.json()
  organic = payload.get("organic_results", [])[:5]

  if not organic:
    return "未检索到有效结果。"

  lines = []
  for i, item in enumerate(organic, start=1):
    title = item.get("title", "无标题")
    link = item.get("link", "")
    snippet = item.get("snippet", "")
    lines.append(f"{i}. {title}\n链接: {link}\n摘要: {snippet}")
  return "\n\n".join(lines)


@tool
def llm_math(expression: str) -> str:
  """执行数学表达式计算。"""
  try:
    return str(numexpr.evaluate(expression))
  except Exception as exc:
    return f"计算失败: {exc}"


if __name__ == "__main__":
  deepseek_key = os.getenv("DEEPSEEK_API_KEY")
  if not deepseek_key:
    raise ValueError("请先设置环境变量 DEEPSEEK_API_KEY")

  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=SecretStr(deepseek_key),
    base_url="https://api.deepseek.com/v1",
    temperature=0,
  )

  agent = create_agent(
    model=llm,
    tools=[serpapi_search, llm_math],
    system_prompt=(
      "你是一个 zero-shot-react-description 风格的工具 Agent。"
      "请根据工具描述自主选择是否调用工具。"
      "遇到最新信息问题优先调用 serpapi_search；"
      "遇到数学计算优先调用 llm_math。"
      "最终回答请简洁，并给出关键依据。"
    ),
  )

  question = "请先计算 2**11 + 99, 再告诉我关于LangChain的最新动态。"
  result = agent.invoke({"messages": [{"role": "user", "content": question}]})

  print("\n===== 最终回答 =====")
  for msg in result.get("messages", []):
    if hasattr(msg, "pretty_print"):
      msg.pretty_print()
    else:
      print(msg)
