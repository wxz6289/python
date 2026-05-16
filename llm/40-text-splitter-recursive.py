from langchain_text_splitters import RecursiveCharacterTextSplitter,CharacterTextSplitter,Language

with open("resources/html.txt") as html:
  content = html.read()
  # text_split = RecursiveCharacterTextSplitter(
  #   chunk_size=50,
  #   chunk_overlap=20,
  #   length_function=len,
  #   add_start_index=True
  # )
  text_split = CharacterTextSplitter(
    separator=".",
    chunk_size=300,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True,
    is_separator_regex=False
  )

  text = text_split.create_documents([content])
  print(text[0])
