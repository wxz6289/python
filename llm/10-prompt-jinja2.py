from langchain_core.prompts import PromptTemplate

jinja2_template = "给我讲一个关于{{name}}的{{what}}故事"
prompt = PromptTemplate.from_template(jinja2_template, template_format="jinja2")

text = prompt.format(name="狗屎", what="美味")
print(text)
