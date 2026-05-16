from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

with open("chat-stream.py") as code:
  content = code.read()
  code_split = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=50,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True,
  )

  text = code_split.create_documents([content])
  print(text)
