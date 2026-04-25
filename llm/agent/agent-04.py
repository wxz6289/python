import os

import numexpr
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SHARED_MEMORY: dict[str, dict[str, str]] = {}
CURRENT_THREAD_ID = "king-shared-memory-demo"


def get_thread_memory() -> dict[str, str]:
  """返回当前会话共享记忆，Agent 调用的工具都会读写这份数据。"""
  return SHARED_MEMORY.setdefault(CURRENT_THREAD_ID, {})


@tool
def save_memory(key: str, value: str) -> str:
  """把一条信息保存到当前会话的共享记忆中。"""
  memory = get_thread_memory()
  memory[key] = value
  return f"已保存记忆: {key}={value}"


@tool
def read_memory(key: str) -> str:
  """从当前会话的共享记忆中读取指定 key。"""
  memory = get_thread_memory()
  if key not in memory:
    return f"没有找到 key={key} 的记忆。"
  return f"{key}={memory[key]}"


@tool
def list_memory() -> str:
  """列出当前会话中的全部共享记忆。"""
  memory = get_thread_memory()
  if not memory:
    return "当前共享记忆为空。"
  return "\n".join(f"{key}={value}" for key, value in memory.items())


@tool
def llm_math(expression: str) -> str:
  """执行数学表达式计算。"""
  try:
    return str(numexpr.evaluate(expression))
  except Exception as exc:
    return f"计算失败: {exc}"


def print_last_message(result: dict) -> None:
  messages = result.get("messages", [])
  if not messages:
    print(result)
    return

  last_message = messages[-1]
  if hasattr(last_message, "pretty_print"):
    last_message.pretty_print()
  else:
    print(last_message)


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

  checkpointer = InMemorySaver()

  agent = create_agent(
    model=llm,
    tools=[save_memory, read_memory, list_memory, llm_math],
    checkpointer=checkpointer,
    system_prompt=(
      "你是一个演示共享记忆能力的工具 Agent。"
      "请根据工具描述自主选择是否调用工具。"
      "当用户要求你记住信息时，必须调用 save_memory 保存；"
      "当用户询问已经记住的信息时，必须调用 read_memory 或 list_memory 查询；"
      "遇到数学计算优先调用 llm_math。"
      "同一个 thread_id 下，Agent 的对话历史由 checkpointer 保存，"
      "工具读写的数据保存在 SHARED_MEMORY 中。"
      "最终回答请简洁，并给出关键依据。"
    ),
  )

  config = {"configurable": {"thread_id": CURRENT_THREAD_ID}}

  first_question = "请使用工具记住：name=King，topic=新版 LangChain Agent。"
  first_result = agent.invoke(
    {"messages": [HumanMessage(content=first_question)]},
    config=config,
  )

  print("\n===== 第一轮回答 =====")
  print_last_message(first_result)
  print("\n===== Tool 共享记忆 =====")
  print(SHARED_MEMORY)

  second_question = "请从共享记忆里查一下我的名字，并计算 2**11 + 99。"
  second_result = agent.invoke(
    {"messages": [HumanMessage(content=second_question)]},
    config=config,
  )

  print("\n===== 第二轮回答（带记忆）=====")
  print_last_message(second_result)
  print("\n===== Tool 共享记忆 =====")
  print(SHARED_MEMORY)

  third_question = "请列出当前共享记忆中的全部内容。"
  third_result = agent.invoke(
    {"messages": [HumanMessage(content=third_question)]},
    config=config,
  )

  print("\n===== 第三轮回答（带记忆）=====")
  print_last_message(third_result)
  print("\n===== Tool 共享记忆 =====")
  print(SHARED_MEMORY)

  fourth_question = "请使用工具记住：name=Jack，topic=Python语法。"
  fourth_result = agent.invoke(
    {"messages": [HumanMessage(content=fourth_question)]},
    config=config,
  )

  print("\n===== 第四轮回答（带记忆）=====")
  print_last_message(fourth_result)
  print("\n===== Tool 共享记忆 =====")
  print(SHARED_MEMORY)
