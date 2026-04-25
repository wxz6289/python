import os
import re
from typing import Dict, List, Set, TypedDict

from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class Turn(TypedDict):
  user: str
  assistant: str



TOP_K_RELEVANT_TURNS = 3
session_turn_store: Dict[str, List[Turn]] = {}


def tokenize(text: str) -> Set[str]:
  """
  轻量分词：提取英文词、数字和中文片段，用于相关性打分。
  不依赖向量库，适合教学演示“相关历史筛选”思路。
  """
  tokens = re.findall(r"\w+|[\u4e00-\u9fff]{1,4}", text.lower())
  return set(tokens)


def select_relevant_turns(query: str, turns: List[Turn], top_k: int) -> List[Turn]:
  query_terms = tokenize(query)
  scored: List[tuple[int, int, Turn]] = []

  for idx, turn in enumerate(turns):
    turn_text = f"{turn['user']} {turn['assistant']}"
    score = len(query_terms & tokenize(turn_text))
    # 次排序用 idx，让较新的对话在同分下优先
    scored.append((score, idx, turn))

  ranked = sorted(scored, key=lambda x: (x[0], x[1]), reverse=True)
  return [turn for score, _, turn in ranked if score > 0][:top_k]


if __name__ == "__main__":
  api_key = os.getenv("DEEPSEEK_API_KEY")
  if not api_key:
    raise ValueError("请先设置环境变量 DEEPSEEK_API_KEY")

  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=SecretStr(api_key),
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
  )

  prompt = ChatPromptTemplate.from_messages(
    [
      (
        "system",
        "你是一个有记忆的助手。请优先依据“相关历史对话”回答，"
        "如果历史不足则明确说明并给出合理回答。",
      ),
      ("human", "相关历史对话:\n{relevant_history}\n\n当前问题:\n{input}"),
    ]
  )

  chain = prompt | llm

  session_id = "user-001"
  session_turn_store.setdefault(session_id, [])

  demo_questions = [
    "我叫小明，是一名 Python 开发者。",
    "我最近在学 LangChain 和记忆机制。",
    "我还养了一只叫可乐的猫。",
    "你还记得我是谁吗？",
    "我在学什么技术？",
    "我的猫叫什么？",
  ]

  for i, user_input in enumerate(demo_questions, start=1):
    turns = session_turn_store[session_id]
    relevant_turns = select_relevant_turns(
      query=user_input,
      turns=turns,
      top_k=TOP_K_RELEVANT_TURNS,
    )
    relevant_history = "\n".join(
      [
        f"- 用户: {turn['user']}\n  助手: {turn['assistant']}"
        for turn in relevant_turns
      ]
    ) or "（无相关历史）"

    response = chain.invoke({"input": user_input, "relevant_history": relevant_history})
    assistant_text = response.content if hasattr(response, "content") else str(response)

    session_turn_store[session_id].append(
      {"user": user_input, "assistant": assistant_text}
    )

    print(f"\n第{i}轮 用户: {user_input}")
    print(f"第{i}轮 助手: {assistant_text}")
