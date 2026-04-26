import ast
import operator
import os
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage
from langchain_core.prompts.chat import SystemMessagePromptTemplate
from langchain_core.tools import tool
from langsmith import Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

llm = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=os.getenv("CLOSEAI_API_KEY"),
  base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL"),
)

HUB_PROMPT = os.getenv("LANGCHAIN_HUB_PROMPT", "hwchase17/openai-functions-agent")
DEFAULT_SYSTEM_PROMPT = "你是一个新版 LangChain Agent 示例助手。需要时主动调用工具，回答要简洁。"

OPERATORS = {
  ast.Add: operator.add,
  ast.Sub: operator.sub,
  ast.Mult: operator.mul,
  ast.Div: operator.truediv,
  ast.Pow: operator.pow,
  ast.USub: operator.neg,
}

def extract_system_prompt(prompt: Any) -> str:
  """从 Hub 拉取的 Prompt 中尽量提取 system prompt 文本。"""
  for message in getattr(prompt, "messages", []):
    if isinstance(message, BaseMessage) and message.type == "system":
      return str(message.content)
    if isinstance(message, SystemMessagePromptTemplate):
      prompt_template = getattr(message, "prompt", None)
      template = getattr(prompt_template, "template", None)
      if template:
        return str(template)
  return DEFAULT_SYSTEM_PROMPT


def load_system_prompt_from_hub() -> str:
  try:
    client = Client()
    prompt = client.pull_prompt(HUB_PROMPT)
    print(prompt)
    return extract_system_prompt(prompt)
  except Exception as exc:
    print(f"Hub 提示词拉取失败，使用本地默认提示词：{exc}")
    return DEFAULT_SYSTEM_PROMPT


def safe_eval(node: ast.AST) -> float:
  if isinstance(node, ast.Expression):
    return safe_eval(node.body)
  if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
    return float(node.value)
  if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
    return OPERATORS[type(node.op)](safe_eval(node.left), safe_eval(node.right))
  if isinstance(node, ast.UnaryOp) and type(node.op) in OPERATORS:
    return OPERATORS[type(node.op)](safe_eval(node.operand))
  raise ValueError("仅支持数字和 +、-、*、/、** 运算。")


@tool
def calculator(expression: str) -> str:
  """计算一个简单的数学表达式，例如：2 * (3 + 4)。"""
  try:
    tree = ast.parse(expression, mode="eval")
    return str(safe_eval(tree))
  except Exception as exc:
    return f"计算失败：{exc}"


@tool
def get_weather(city: str) -> str:
  """查询指定城市的天气示例数据。"""
  demo_weather = {
    "tokyo": "东京今天多云，气温约 18°C。",
    "beijing": "北京今天晴，气温约 22°C。",
    "shanghai": "上海今天小雨，气温约 20°C。",
  }
  return demo_weather.get(city.lower(), f"暂时没有 {city} 的天气数据。")


agent = create_agent(
  model=llm,
  tools=[calculator, get_weather],
  system_prompt=load_system_prompt_from_hub(),
)

result = agent.invoke({
  "messages": [
    {"role": "user", "content": "What is the weather in Tokyo? Also calculate 12 * (3 + 4)."},
  ]
})

last_message = result["messages"][-1]
if isinstance(last_message, AIMessage):
  print(last_message.content)
else:
  print(last_message)

