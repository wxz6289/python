import logging
import os

from langchain_community.document_loaders import (Docx2txtLoader, PyPDFLoader)
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import CharacterTextSplitter
from langchain_unstructured import UnstructuredLoader


class ChatDoc():
  def __init__(self, doc_path):
    self.doc = doc_path
    self.split_texts = None
    self.db = None
    self.llm = None
    self.template = [
      ("system", "你是一个文档检索助手，但从不说自己是大模型或AI助手，只是从文档中检索信息。上下文内容：{context}"),
      ("human", "你好，我是{name}，请根据上下文内容回答问题：{question}"),
      ("ai", "你好，很高兴为你服务，我可以帮助你从文档中检索信息。")
    ]
    self.prompt = ChatPromptTemplate.from_messages(self.template)

  def get_file(self):
    doc = self.doc
    loaders = {
      "docx": Docx2txtLoader,
      "pdf": PyPDFLoader,
      "xlsx": UnstructuredLoader,
      "xls": UnstructuredLoader
    }
    extension = doc.split(".")[-1]
    loader_cls = loaders.get(extension)
    if not loader_cls:
      raise  Exception("Unsupported file type")
    loader = loader_cls(self.doc)
    docs = loader.load()
    return docs

  def split_sentence(self):
    if self.split_texts is None:
      docs = self.get_file()
      text_spliter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
      self.split_texts = text_spliter.split_documents(docs)

    return self.split_texts

  def build_DB(self):
    if self.db is None:
       embeddings = HuggingFaceEmbeddings(model_name = "BAAI/bge-small-en")
       texts = self.split_sentence()
       self.db = Chroma.from_documents(documents=texts, embedding = embeddings)
    return self.db

  def askForFiles(self, question):
    db = self.build_DB()
    # retriever = db.as_retriever()
    # results = retriever.invoke(question)
    if self.llm is None:
      self.llm = ChatOpenAI(
        model="deepseek-chat",
        api_key= os.getenv("DEEPSEEK_API_KEY"),
        base_url= "https://api.deepseek.com/v1",
        temperature=0
      )
      # 使用多查询检索
    # retriever = MultiQueryRetriever.from_llm(
    #   retriever = db.as_retriever(),
    #   llm = self.llm
    # )

    # 使用LLM链式提取器压缩文档
    # retriever = db.as_retriever()
    # compressor = LLMChainExtractor.from_llm(llm= self.llm)
    # docs = retriever.invoke(question)
    # compressor_retriever = ContextualCompressionRetriever(
    #   base_retriever=retriever,
    #   base_compressor=compressor
    # )
    # docs = compressor_retriever.invoke(question)
    # 使用MMR检索
    # retriever = db.as_retriever(search_type="mmr")
    # 使用相似度得分阈值检索
    retriever = db.as_retriever(search_type="similarity_score_threshold",
                                search_kwargs={"score_threshold": 0.5})
    docs = retriever.invoke(question)
    return docs

  def chatWithDocs(self, question):
    _context = ""
    context = self.askForFiles(question)
    for doc in context:
      _context += doc.page_content + "\n"

    message = self.prompt.format(context=_context, question=question, name="文档检索助手")
    return self.llm.invoke(message)

cd = ChatDoc("example/test.pdf")
logging.basicConfig(level=logging.INFO)
result = cd.chatWithDocs("他具有哪些个人优势?")
print(result.content)

result = cd.chatWithDocs("任职时间最长多久?")
print(result.content)
