
from langchain_core.output_parsers import CommaSeparatedListOutputParser
csv = """
name,age,gender
张三,20,男
李四,21,女
王五,22,男
"""

parser = CommaSeparatedListOutputParser()

# print(parser.parse(csv))

print(parser.get_format_instructions())
