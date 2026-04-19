from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os

# 1. 数据
docs = [
  Document(page_content="LangChain 是一个 AI 框架"),
  Document(page_content="RAG 是检索增强生成"),
]

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")

# 2. 向量库
# embedding = OpenAIEmbeddings(
#   model= "text-embedding-3-small",
#   api_key= deepseek_api_key,
#   base_url= "https://api.deepseek.com/v1"
# )
embeddings = HuggingFaceEmbeddings(
  model_name = "BAAI/bge-small-en"
)

db = Chroma.from_documents(docs, embeddings)

# 3. 检索
retriever = db.as_retriever(search_kwargs={"k": 3})

# 4. LLM
if not deepseek_api_key:
  raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")
llm = ChatOpenAI(
  model="deepseek-chat",
  temperature=0,
  api_key=deepseek_api_key,
  base_url="https://api.deepseek.com/v1",
  max_tokens=512
)

# 5. 查询
query = "什么是 RAG？"
retrieved_docs = retriever.invoke(query)

context = "\n".join([d.page_content for d in retrieved_docs])

prompt = f"""
基于以下内容回答问题：
{context}

问题：{query}
"""

res = llm.invoke(prompt)
print(res.content)
