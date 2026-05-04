from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv('../.env')
openai_api_key = os.getenv("CLOSEAI_API_KEY")
base_url = os.getenv("CLOSEAIAI_BASE_URL")

with open("../resources/html.txt") as html:
  content = html.read()

embeddings = OpenAIEmbeddings(
  api_key=openai_api_key,
  base_url=base_url,
)

chunker = SemanticChunker(
  embeddings,
  breakpoint_threshold_type="percentile",
  breakpoint_threshold_amount=95,
)

chunks = chunker.split_text(content)
for chunk in chunks:
  print(chunk, "\n")

