import os
import math
import re
from collections import Counter
from typing import Dict, List
from pydantic import SecretStr
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

try:
  from langchain_community.vectorstores import FAISS
except ImportError:
  FAISS = None


class SimpleKeywordEmbeddings(Embeddings):
  """
  轻量本地 Embeddings（无外部依赖）：
  - 将文本映射到固定维度稀疏向量
  - 仅用于演示“向量数据库长时记忆”流程
  """

  def __init__(self, dim: int = 256):
    self.dim = dim

  def _tokenize(self, text: str) -> List[str]:
    return re.findall(r"\w+|[\u4e00-\u9fff]{1,4}", text.lower())

  def _embed(self, text: str) -> List[float]:
    vec = [0.0] * self.dim
    counts = Counter(self._tokenize(text))
    if not counts:
      return vec

    for token, freq in counts.items():
      idx = hash(token) % self.dim
      vec[idx] += float(freq)

    # L2 normalize
    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0:
      vec = [v / norm for v in vec]
    return vec

  def embed_query(self, text: str) -> List[float]:
    return self._embed(text)

  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    return [self._embed(t) for t in texts]


class VectorLongMemory:
  def __init__(self, embeddings: Embeddings, top_k: int = 4):
    self.embeddings = embeddings
    self.vectorstore = None
    self.top_k = top_k
    self.turn_idx = 0

  def save_turn(self, session_id: str, user_input: str, assistant_output: str) -> None:
    self.turn_idx += 1
    text = f"用户: {user_input}\n助手: {assistant_output}"
    doc = Document(
      page_content=text,
      metadata={"session_id": session_id, "turn": self.turn_idx},
    )
    if self.vectorstore is None:
      self.vectorstore = FAISS.from_documents([doc], self.embeddings)
    else:
      self.vectorstore.add_documents([doc])

  def load_relevant_memory(self, session_id: str, query: str) -> str:
    if self.vectorstore is None:
      return "（暂无相关长时记忆）"

    docs = self.vectorstore.similarity_search(query, k=self.top_k)
    session_docs = [d for d in docs if d.metadata.get("session_id") == session_id]
    if not session_docs:
      return "（暂无相关长时记忆）"
    return "\n\n".join(d.page_content for d in session_docs)


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
  if FAISS is None:
    raise ImportError("未安装 FAISS 依赖，请先安装: pip install faiss-cpu langchain-community")

  embeddings = SimpleKeywordEmbeddings(dim=256)
  long_memory = VectorLongMemory(embeddings=embeddings, top_k=4)

  # 回答链：使用“长期摘要 + 最近原始对话”
  answer_prompt = ChatPromptTemplate.from_template(
    """你是一个有长时记忆的助手。请优先依据“检索出的历史记忆”回答。
如果历史记忆不足，请明确说明并给出合理回答。

检索出的历史记忆:
{retrieved_memory}

用户当前问题:
{input}
"""
  )
  answer_chain = answer_prompt | llm

  session_id = "demo-user-001"

  user_inputs = [
    "我叫小明，是后端开发。",
    "我住在杭州，喜欢骑行。",
    "我最近在学 LangChain 和记忆系统设计。",
    "我养了一只猫，叫可乐。",
    "你还记得我的基本信息吗？",
    "请结合我们的长期对话，给我一个学习建议。",
  ]

  for i, user_input in enumerate(user_inputs, start=1):
    retrieved_memory = long_memory.load_relevant_memory(session_id, user_input)
    answer = answer_chain.invoke(
      {
        "retrieved_memory": retrieved_memory,
        "input": user_input,
      }
    )
    assistant_text = answer.content if hasattr(answer, "content") else str(answer)
    long_memory.save_turn(session_id, user_input, assistant_text)

    print(f"\n第{i}轮 用户: {user_input}")
    print(f"第{i}轮 助手: {assistant_text}")
    print("---- 检索记忆 ----")
    print(retrieved_memory)
