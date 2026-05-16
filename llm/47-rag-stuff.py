import os

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

def create_stuff_chain(llm, prompt):
  def format_inputs(inputs):
    return {
      "context": "\n\n".join(doc.page_content for doc in inputs["context"]),
      "input": inputs["input"],
    }

  return RunnableLambda(format_inputs) | prompt | llm | StrOutputParser()


if __name__ == "__main__":
  api_key = os.getenv("DEEPSEEK_API_KEY")
  if not api_key:
    raise ValueError("请先设置环境变量 DEEPSEEK_API_KEY")

  llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
    temperature=0.2,
  )

  # stuff-chain 会把多个 Document 内容拼接进 {context}
  prompt = ChatPromptTemplate.from_messages(
    [
      (
        "system",
        "你是问答助手。仅基于提供的上下文回答；如果上下文没有答案，请明确说明不知道。",
      ),
      ("human", "问题：{input}\n\n上下文：\n{context}"),
    ]
  )

  stuff_chain = create_stuff_chain(llm=llm, prompt=prompt)

  docs = [
    Document(page_content="LangChain 是一个用于构建 LLM 应用的框架。"),
    Document(page_content="Stuff chain 会将多个文档拼接后一次性送入模型。"),
    Document(page_content="这种方式简单直接，适合文档总长度较短的场景。"),
  ]

  result = stuff_chain.invoke(
    {
      "input": "什么是 stuff chain？适合什么场景？",
      "context": docs,
    }
  )
  print(result)
