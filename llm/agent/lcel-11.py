import os

from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))


def get_api_key() -> str:
  api_key = os.getenv("CLOSEAI_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not api_key:
    raise EnvironmentError("请先设置 CLOSEAI_API_KEY 或 OPENAI_API_KEY")
  return api_key


def build_llm() -> ChatOpenAI:
  return ChatOpenAI(
    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    api_key=SecretStr(get_api_key()),
    base_url=os.getenv("OPENAI_BASE_URL"),
    temperature=0,
  )


def build_embeddings() -> OpenAIEmbeddings:
  base_url = os.getenv("OPENAI_BASE_URL")
  return OpenAIEmbeddings(
    model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    api_key=SecretStr(get_api_key()),
    base_url=base_url,
    tiktoken_enabled=True,
  )


def build_demo_docs() -> list[Document]:
  texts = [
    """
LangChain 是一个构建大模型应用的开发框架。它提供 Prompt、Model、OutputParser、
Retriever、Tool、Agent 等组件，适合搭建聊天机器人、RAG、Agent 和自动化工作流。
""",
    """
LCEL 是 LangChain Expression Language 的缩写。它使用 Runnable 抽象和管道符 |
组合链路，例如 prompt | model | parser。LCEL 支持 invoke、batch、stream 和异步调用。
""",
    """
RAG 是 Retrieval-Augmented Generation，中文常称为检索增强生成。
典型流程是先把文档切块并向量化，用户提问时从向量库检索相关片段，再把片段作为上下文交给模型回答。
""",
    """
FAISS 是常用的本地向量检索库，适合快速搭建向量相似度搜索示例。
tiktoken 是 OpenAI 常用的 token 计算工具，在文本切分时可以按 token 长度控制 chunk 大小。
""",
  ]
  return [
    Document(page_content=text.strip(), metadata={"source": f"demo-{index}"})
    for index, text in enumerate(texts, start=1)
  ]


def format_docs(docs: list[Document]) -> str:
  return "\n\n".join(
    f"[{doc.metadata.get('source', 'unknown')}]\n{doc.page_content}"
    for doc in docs
  )


def build_vectorstore() -> FAISS:
  splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    model_name="gpt-4o-mini",
    chunk_size=120,
    chunk_overlap=20,
  )
  splits = splitter.split_documents(build_demo_docs())
  embeddings = build_embeddings()
  return FAISS.from_documents(splits, embeddings)


if __name__ == "__main__":
  llm = build_llm()
  vectorstore = build_vectorstore()
  retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

  prompt = ChatPromptTemplate.from_template(
    """
请根据检索到的上下文回答问题。
如果上下文中没有答案，请直接说“上下文中没有相关信息”。

上下文:
{context}

问题:
{question}
"""
  )

  rag_chain = (
    {
      "context": retriever | format_docs,
      "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
  )

  question = "LCEL 和 RAG 分别是什么？FAISS 和 tiktoken 在这个流程里有什么作用？"
  result = rag_chain.invoke(question)
  print(result)
