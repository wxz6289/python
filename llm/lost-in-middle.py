from langchain_community.document_transformers import LongContextReorder
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import os

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

text = [
    "篮球是一项伟大的运动",
    "带我飞上月球是首美妙的曲子",
    "今天天气非常好",
    "学习机器学习需要耐心和坚持",
    "Python是一种非常流行的编程语言",
    "春天的花开得特别美丽",
    "人工智能正在改变我们的生活方式",
    "阅读是获取知识的重要途径",
    "运动可以让人保持健康",
    "音乐能够治愈人的心灵",
    "科技创新推动社会进步",
]

retrival = Chroma.from_texts(text, embeddings).as_retriever(search_kwargs={"k": 10})

query = "音乐有什么作用?"

docs = retrival.invoke(query)

# print(docs)
recording = LongContextReorder()
reo_docs = recording.transform_documents(docs)
# print(reo_docs)

context = "\n".join([doc.page_content for doc in docs])

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=deepseek_api_key,
    temperature=0,
    base_url="https://api.deepseek.com/v1",
)

doc_prompt = PromptTemplate(input_variables=["page_content"], template="{page_content}")

stuff_prompt_override = """Given this text extracts:
---------------------------
{context}
---------------------------
Please answer the following questions:
{query}
"""

prompt = PromptTemplate(
    template=stuff_prompt_override, input_variables=["context", "query"]
)

chain = prompt | llm

result = chain.invoke({"context": context, "query": query})

print(result.content)
