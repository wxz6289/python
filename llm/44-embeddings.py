# from langchain_community.embeddings import  OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# e_model = OpenAIEmbeddings(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url= "https://deepseek.com/v1")
e_model = HuggingFaceEmbeddings(
  model_name = "sentence-transformers/all-MiniLM-L6-v2"
)
embeddings = e_model.embed_documents(
  [
    "你好",
    "你好啊！",
    "我叫Jhons",
    "很高兴认识你！"
  ]
)

embedded_query = e_model.embed_query("这段话中提及了谁?")
# print(len(embeddings), len(embeddings[0]))
print(embedded_query)
