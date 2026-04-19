from langchain_core.prompts import load_prompt

prompt = load_prompt("simple_prompt.json")
print(prompt.format(name="嫦娥", what="奔月"))
