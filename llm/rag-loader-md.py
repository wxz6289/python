from langchain_community.document_loaders import TextLoader, CSVLoader,JSONLoader
from langchain_unstructured import UnstructuredLoader
# loader = TextLoader("示例选择.md")
# content = loader.load()
# print(content)

# loader = CSVLoader(file_path = "test.csv")
# loader = JSONLoader(file_path="simple_prompt.json", jq_schema=".[]", text_content=False)
loader = UnstructuredLoader("simple_prompt.yml")
data = loader.load()
print(data)



