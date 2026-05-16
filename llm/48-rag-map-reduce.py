import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter

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

  # step 1: map
  map_prompt = ChatPromptTemplate.from_template("""
  总结这段内容：
  {text}
  """)

  map_chain = map_prompt | llm | StrOutputParser()

  # step 2: reduce
  reduce_prompt = ChatPromptTemplate.from_template("""
  合并以下总结：

  {summaries}
  """)

  reduce_chain = reduce_prompt | llm | StrOutputParser()
  base_dir = os.path.dirname(os.path.abspath(__file__))
  pdf_path = os.path.join(base_dir, "rmrb2026042201.pdf")
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

  summaries = [map_chain.invoke({"text": doc.page_content}) for doc in split_docs]

  # 分批 reduce，避免一次拼接过长导致上下文超限
  batch_size = 8
  current = summaries
  while len(current) > 1:
    merged = []
    for i in range(0, len(current), batch_size):
      batch = current[i : i + batch_size]
      merged.append(reduce_chain.invoke({"summaries": "\n\n".join(batch)}))
    current = merged

  final_summary = current[0] if current else ""
  print(final_summary)
