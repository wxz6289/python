import os
from typing import Dict, List

from pydantic import BaseModel, Field, SecretStr
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI


class EntityItem(BaseModel):
  name: str = Field(description="实体名，例如 小明、LangChain、可乐")
  category: str = Field(description="实体类别，例如 人名/职业/技能/宠物/地点/组织")
  value: str = Field(description="实体对应信息或描述")


class EntityExtractionResult(BaseModel):
  entities: List[EntityItem] = Field(default_factory=list)


store: Dict[str, InMemoryChatMessageHistory] = {}
entity_store: Dict[str, Dict[str, str]] = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
  if session_id not in store:
    store[session_id] = InMemoryChatMessageHistory()
  return store[session_id]


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

  extractor_parser = PydanticOutputParser(pydantic_object=EntityExtractionResult)
  extractor_prompt = ChatPromptTemplate.from_template(
    """你是信息抽取器。请从用户输入中提取可长期记忆的实体信息。

用户输入:
{input}

请按以下格式返回:
{format_instructions}
"""
  )
  extractor_chain = extractor_prompt | llm | extractor_parser

  prompt = ChatPromptTemplate.from_messages(
    [
      (
        "system",
        "你是一个有实体记忆的助手。优先基于“实体清单”和历史对话回答，回答简洁。",
      ),
      ("system", "当前实体清单:\n{entity_memory}"),
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
  entity_store.setdefault(session_id, {})

  questions = [
    "我叫小明，在做后端开发。",
    "我还在学习 LangChain。",
    "我家猫叫可乐。",
    "你还记得我的名字、职业和猫的名字吗？",
  ]

  for i, q in enumerate(questions, start=1):
    extracted = extractor_chain.invoke(
      {
        "input": q,
        "format_instructions": extractor_parser.get_format_instructions(),
      }
    )
    for item in extracted.entities:
      key = f"{item.category}:{item.name}"
      entity_store[session_id][key] = item.value

    entity_memory_text = "\n".join(
      [f"- {k} = {v}" for k, v in entity_store[session_id].items()]
    ) or "（暂无）"

    resp = chain_with_memory.invoke(
      {"input": q, "entity_memory": entity_memory_text},
      config=config,
    )
    print(f"第{i}轮 用户: {q}")
    print(f"第{i}轮 助手: {resp.content}\n")

  history = get_session_history(session_id)
  print("===== 当前会话历史条数 =====")
  print(len(history.messages))
  print("\n===== 实体记忆清单 =====")
  for k, v in entity_store[session_id].items():
    print(f"{k} -> {v}")
