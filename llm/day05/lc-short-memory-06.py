import os
from typing import Dict, List, Set
import re
from pydantic import BaseModel, Field, SecretStr
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


class KnowledgeTriple(BaseModel):
  subject: str = Field(description="主语实体，例如 小明")
  relation: str = Field(description="关系，例如 职业是/学习/养了")
  obj: str = Field(description="宾语实体或值，例如 后端开发/LangChain/可乐")


class TripleExtractionResult(BaseModel):
  triples: List[KnowledgeTriple] = Field(default_factory=list)


store: Dict[str, InMemoryChatMessageHistory] = {}
kg_store: Dict[str, List[KnowledgeTriple]] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
  if session_id not in store:
    store[session_id] = InMemoryChatMessageHistory()
  return store[session_id]


def tokenize(text: str) -> Set[str]:
  terms = re.findall(r"\w+|[\u4e00-\u9fff]{1,4}", text.lower())
  return set(terms)


def select_relevant_triples(query: str, triples: List[KnowledgeTriple], top_k: int = 6) -> List[KnowledgeTriple]:
  q_terms = tokenize(query)
  scored = []
  for i, triple in enumerate(triples):
    triple_text = f"{triple.subject} {triple.relation} {triple.obj}"
    score = len(q_terms & tokenize(triple_text))
    scored.append((score, i, triple))
  ranked = sorted(scored, key=lambda x: (x[0], x[1]), reverse=True)
  return [t for s, _, t in ranked if s > 0][:top_k]


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

  triple_parser = PydanticOutputParser(pydantic_object=TripleExtractionResult)
  triple_extractor_prompt = ChatPromptTemplate.from_template(
    """你是知识图谱抽取器。请从用户输入中提取可长期记忆的知识三元组 (subject, relation, obj)。
如果没有可抽取事实，返回空数组。

用户输入:
{input}

请按以下格式返回:
{format_instructions}
"""
  )
  triple_extractor_chain = triple_extractor_prompt | llm | triple_parser

  prompt = ChatPromptTemplate.from_messages(
    [
      (
        "system",
        "你是一个有知识图谱记忆的助手。请优先依据“相关知识图谱”和历史对话回答，回答简洁。",
      ),
      ("system", "当前相关知识图谱:\n{kg_context}"),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{input}"),
    ]
  )

  chain = prompt | llm

  chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history",
  )

  config: RunnableConfig = {"configurable": {"session_id": "demo-user-001"}}
  session_id = "demo-user-001"
  kg_store.setdefault(session_id, [])

  questions = [
    "我叫小明，在做后端开发。",
    "我还在学习 LangChain。",
    "我家猫叫可乐。",
    "我住在杭州。",
    "你还记得我的名字、职业和猫的名字吗？",
    "我住在哪个城市？",
  ]

  for i, q in enumerate(questions, start=1):
    extracted = triple_extractor_chain.invoke(
      {
        "input": q,
        "format_instructions": triple_parser.get_format_instructions(),
      }
    )
    kg_store[session_id].extend(extracted.triples)

    related = select_relevant_triples(q, kg_store[session_id], top_k=6)
    kg_context = "\n".join(
      [f"- ({t.subject}, {t.relation}, {t.obj})" for t in related]
    ) or "（暂无相关知识）"

    resp = chain_with_memory.invoke(
      {"input": q, "kg_context": kg_context},
      config=config,
    )
    print(f"第{i}轮 用户: {q}")
    print(f"第{i}轮 助手: {resp.content}\n")

  history = get_session_history(session_id)
  print("===== 当前会话历史条数 =====")
  print(len(history.messages))
  print("\n===== 知识图谱记忆(全部三元组) =====")
  for t in kg_store[session_id]:
    print(f"({t.subject}, {t.relation}, {t.obj})")
