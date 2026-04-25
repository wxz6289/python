import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.output_parsers import StrOutputParser


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

  pdf_path = "./rmrb2026042201.pdf"
  if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"未找到 PDF 文件: {pdf_path}")

  # 1) 加载 PDF
  loader = PyPDFLoader(pdf_path)
  docs = loader.load()

  # 2) 文本分割
  splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
  )
  split_docs = splitter.split_documents(docs)

  # 3) refine_documents: 首段生成初始总结，后续分段循环补充/修正
  initial_prompt = ChatPromptTemplate.from_template(
    """请基于以下文本提炼主要内容，输出 5-8 条要点：

文本：
{context}"""
  )

  refine_prompt = ChatPromptTemplate.from_template(
    """你已有一版总结：
{existing_answer}

请结合新增文本，更新总结并保持结构清晰：
{context}

要求：
1. 若新增文本没有新信息，保留原总结；
2. 若有新信息，补充到要点中并去重；
3. 最终输出 5-10 条高质量要点。"""
  )

  initial_chain = initial_prompt | llm | StrOutputParser()
  refine_chain = refine_prompt | llm | StrOutputParser()

  initial_summary = initial_chain.invoke({"context": split_docs})
  final_summary = refine_chain.invoke({"context": split_docs, "existing_answer": initial_summary})

  print(f"原始页数: {len(docs)}")
  print(f"切分后块数: {len(split_docs)}")
  print("\n===== 提取的主要内容 =====\n")
  print(final_summary)
