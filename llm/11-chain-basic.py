#%%
from langchain_classic import LLMChain
from langchain_classic.prompts import ChatPromptTemplate
from langchain_classic.llms import OpenAI

llm = OpenAI(
  model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0
)

template = "请帮为{product}写一个广告语"
prompt = ChatPromptTemplate.from_template(template)

chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

chain("幸惠超市")
