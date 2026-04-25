import os
from typing import List
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RerankResult(BaseModel):
  answer: str = Field(description="基于当前文本块给出的候选答案")
  score: int = Field(description="候选答案置信分，0-100")
  reason: str = Field(description="给该分数的简短原因")


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

  question = "请提取这篇文章的主要内容，并给出 5 条核心要点。"
  parser = PydanticOutputParser(pydantic_object=RerankResult)

  # map-rerank: 每个文档块先回答，再给出分数
  map_rerank_prompt = ChatPromptTemplate.from_template(
    """你是一个阅读助手。请基于给定文本片段回答问题，并对答案质量打分。

问题:
{question}

文本片段:
{text}

请严格按以下格式输出:
{format_instructions}
"""
  )
  map_rerank_chain = map_rerank_prompt | llm | parser

  base_dir = os.path.dirname(os.path.abspath(__file__))
  pdf_path = os.path.join(base_dir, "rmrb2026042305.pdf")
  if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"未找到 PDF 文件: {pdf_path}")

  loader = PyPDFLoader(pdf_path)
  docs = loader.load()

  splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
  )
  split_docs = splitter.split_documents(docs)

  candidates: List[RerankResult] = []
  for doc in split_docs:
    result = map_rerank_chain.invoke(
      {
        "question": question,
        "text": doc.page_content,
        "format_instructions": parser.get_format_instructions(),
      }
    )
    candidates.append(result)

  if not candidates:
    raise ValueError("没有可用于 rerank 的文档块。")

  best = max(candidates, key=lambda x: x.score)

  print(f"原始页数: {len(docs)}")
  print(f"切分后块数: {len(split_docs)}")
  print(f"候选答案数: {len(candidates)}")
  print("\n===== Map-Rerank 最终结果 =====\n")
  print(f"最高分: {best.score}")
  print(f"打分理由: {best.reason}\n")
  print(best.answer)
