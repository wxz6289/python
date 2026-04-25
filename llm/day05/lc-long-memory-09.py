import os
import re
from typing import Dict, List, TypedDict

from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class SessionState(TypedDict):
  summary: str
  recent_turns: List[str]


MAX_RECENT_TURNS = 4
TOKEN_REFRESH_THRESHOLD = 100
memory_store: Dict[str, SessionState] = {}


class SummaryMemory:
  """
  ConversationSummaryMemory 的 LCEL 等价实现：
  - 长期摘要: summary
  - 短期窗口: recent_turns
  """

  def __init__(self, summary_chain, max_recent_turns: int = 4, token_refresh_threshold: int = 220):
    self.summary_chain = summary_chain
    self.max_recent_turns = max_recent_turns
    self.token_refresh_threshold = token_refresh_threshold
    self.store: Dict[str, SessionState] = {}

  def _estimate_tokens(self, text: str) -> int:
    """
    轻量 token 估算：
    - 英文/数字按词计数
    - 中文按字符计数
    """
    en_terms = re.findall(r"\w+", text)
    zh_chars = re.findall(r"[\u4e00-\u9fff]", text)
    return len(en_terms) + len(zh_chars)

  def _buffer_token_size(self, turns: List[str]) -> int:
    return self._estimate_tokens("\n".join(turns))

  def _get_state(self, session_id: str) -> SessionState:
    if session_id not in self.store:
      self.store[session_id] = {"summary": "", "recent_turns": []}
    return self.store[session_id]

  def load_memory_variables(self, session_id: str) -> Dict[str, str]:
    state = self._get_state(session_id)
    return {
      "summary": state["summary"] or "（暂无长期摘要）",
      "recent_turns": "\n".join(state["recent_turns"]) or "（暂无）",
    }

  def save_context(self, session_id: str, user_input: str, assistant_output: str) -> None:
    state = self._get_state(session_id)
    new_turn = f"用户: {user_input}\n助手: {assistant_output}"
    state["recent_turns"].append(new_turn)

    # 刷新时机由 token 长度决定：超过阈值才把缓冲对话压缩进长期摘要
    if self._buffer_token_size(state["recent_turns"]) >= self.token_refresh_threshold:
      updated_summary = self.summary_chain.invoke(
        {
          "summary": state["summary"] or "（暂无）",
          "new_turn": "\n\n".join(state["recent_turns"]),
        }
      )
      state["summary"] = (
        updated_summary.content if hasattr(updated_summary, "content") else str(updated_summary)
      )
      state["recent_turns"] = []
    elif len(state["recent_turns"]) > self.max_recent_turns:
      # 未触发刷新时仍限制最近轮数，避免无界增长
      state["recent_turns"] = state["recent_turns"][-self.max_recent_turns:]


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

  # 回答链：使用“长期摘要 + 最近原始对话”
  answer_prompt = ChatPromptTemplate.from_template(
    """你是一个有长期记忆的助手，请基于以下记忆回答用户问题。

长期记忆摘要:
{summary}

最近对话:
{recent_turns}

用户当前问题:
{input}
"""
  )
  answer_chain = answer_prompt | llm

  # 摘要更新链：把最新一轮对话压缩进长期摘要
  summary_prompt = ChatPromptTemplate.from_template(
    """你是记忆压缩器。请把“已有摘要”和“一批新对话”整合成更新后的摘要。
要求:
1. 保留稳定事实（如姓名、职业、偏好、地点、宠物等）
2. 删除重复和无关细节
3. 摘要尽量精炼（建议 6-10 条）

已有摘要:
{summary}

一批新对话:
{new_turn}
"""
  )
  summary_chain = summary_prompt | llm

  session_id = "demo-user-001"
  summary_memory = SummaryMemory(
    summary_chain=summary_chain,
    max_recent_turns=MAX_RECENT_TURNS,
    token_refresh_threshold=TOKEN_REFRESH_THRESHOLD,
  )

  user_inputs = [
    "我叫小明，是后端开发。",
    "我住在杭州，喜欢骑行。",
    "我最近在学 LangChain 和记忆系统设计。",
    "我养了一只猫，叫可乐。",
    "你还记得我的基本信息吗？",
    "请结合我们的长期对话，给我一个学习建议。",
  ]

  for i, user_input in enumerate(user_inputs, start=1):
    memory_vars = summary_memory.load_memory_variables(session_id)
    answer = answer_chain.invoke(
      {
        "summary": memory_vars["summary"],
        "recent_turns": memory_vars["recent_turns"],
        "input": user_input,
      }
    )
    assistant_text = answer.content if hasattr(answer, "content") else str(answer)
    summary_memory.save_context(session_id, user_input, assistant_text)

    print(f"\n第{i}轮 用户: {user_input}")
    print(f"第{i}轮 助手: {assistant_text}")

  final_memory = summary_memory.load_memory_variables(session_id)
  print("\n===== 长时记忆摘要 =====\n")
  print(final_memory["summary"])
  print("\n===== 当前未刷新的最近对话缓冲 =====\n")
  print(final_memory["recent_turns"])
