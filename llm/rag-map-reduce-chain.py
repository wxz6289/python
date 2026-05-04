from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os


deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
llm = ChatOpenAI(
  model="deepseek-chat",
  temperature=0,
  api_key=deepseek_api_key,
  base_url="https://api.deepseek.com/v1",
)

summarize_prompt = ChatPromptTemplate.from_template(
  "请总结以下内容：\n\n{text}"
)

def summerize(text):
  return llm.invoke(summarize_prompt.format(text=text)).content


refine_prompt = ChatPromptTemplate.from_template(
  "请精炼以下内容(去除冗余、保留核心): \n\n{text}"
)

def refine(text):
  return llm.invoke(refine_prompt.format(text=text)).content


translate_prompt = ChatPromptTemplate.from_template(
  "请将以下内容翻译成中文：\n\n{text}"
)

def translate(text):
  return llm.invoke(translate_prompt.format(text=text)).content


def map_stage(chunks):
  summaries = llm.batch([
    summarize_prompt.format(text=c.page_content)
    for c in chunks
  ])

  refined = llm.batch([
    refine_prompt.format(text=s) for s in summaries
  ])

  translated = llm.batch([
    translate_prompt.format(text=r) for r in refined
  ])

  return {
    "summary": summaries,
    "refined": refined,
    "translated": translated
  }


reduce_prompt = ChatPromptTemplate.from_template(
  """
你是文档分析专家，请将以下内容整合成最终报告：

{context}
"""
)

def reduce_stage(items):
  merged = "\n".join([x.content for x in items])
  return llm.invoke(reduce_prompt.format(context=merged)).content

def lcel_map_reduce(chunks):
  # 1. Map阶段
  summaries = llm.batch([
    summarize_prompt.format(text=c.page_content)
    for c in chunks
  ])

  refined = llm.batch([
    refine_prompt.format(text=s)
    for s in summaries
  ])

  translated = llm.batch([
    translate_prompt.format(text=r)
    for r in refined
  ])

  # 2. Reduce阶段
  final_summary = reduce_stage(refined)

  return {
    "summary": [x.content for x in summaries],
    "refined": [x.content for x in refined],
    "translated": [x.content for x in translated],
    "final": final_summary
  }

loader = UnstructuredLoader('resources/Pinia-Cheat-Sheet.pdf')
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(
  chunk_size=500,
  chunk_overlap=80
)
chunks = splitter.split_documents(docs)
result = lcel_map_reduce(chunks)
print(result)
