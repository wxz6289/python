import os
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


def normalize_input(data: Dict[str, Any]) -> Dict[str, Any]:
  """把原始输入标准化，作为自定义链的前置步骤。"""
  topic = str(data.get("topic", "")).strip()
  style = str(data.get("style", "简洁")).strip()
  return {"topic": topic, "style": style}


def wrap_output(text: str) -> Dict[str, str]:
  """把模型输出包装成结构化结果，作为自定义链的后置步骤。"""
  return {"answer": text.strip()}


if __name__ == "__main__":
  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
  )

  prompt = ChatPromptTemplate.from_messages(
    [
      ("system", "你是一个教学助手，请用{style}风格解释概念。"),
      ("human", "请解释：{topic}"),
    ]
  )

  # 最新 LCEL 风格：把自定义步骤与标准组件串起来
  custom_chain = (
    RunnableLambda(normalize_input)
    | prompt
    | llm
    | StrOutputParser()
    | RunnableLambda(wrap_output)
  )

  result = custom_chain.invoke({"topic": "什么是自定义链", "style": "通俗易懂"})
  print(result["answer"])
