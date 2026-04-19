from langchain_text_splitters import CharacterTextSplitter, Language

with open("chat-stream.py") as f:
  content = f.read()
  f_split = CharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=50,
    chunk_overlap=20,
  )

  text = f_split.create_documents([content])
  print(text)
