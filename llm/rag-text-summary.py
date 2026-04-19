from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os

from rag import deepseek_api_key

loader = UnstructuredFileLoader("html.txt")
docs = loader.load()

for d in docs:
  d.page_content = d.page_content.strip()

splitter = RecursiveCharacterTextSplitter(
  chunk_size=500,
  chunk_overlap=80,
)

chunks = splitter.split_documents(docs)
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
embedding = OpenAIEmbeddings(
  model="text-embedding-3-small",
    api_key= deepseek_api_key,
    base_url= "https://api.deepseek.com/v1"
)

db = Chroma.from_documents(chunks, embedding)
print("RAG ready")
