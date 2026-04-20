import os
from langchain.chat_models import init_chat_model
from langchain_classic.chains import ConversationChain, LLMChain
from langchain_classic.chains.router import MultiPromptChain
from langchain_classic.chains.router.llm_router import LLMRouterChain, \
  RouterOutputParser
from langchain_classic.chains.router.multi_prompt_prompt import \
  MULTI_PROMPT_ROUTER_TEMPLATE
from langchain_core.prompts import PromptTemplate

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

model = init_chat_model(
    model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0, api_key=deepseek_api_key
)

prompt_infos = [
  {
    "name": "tech",
    "description": "回答技术问题",
    "prompt_template": "你是技术专家：{input}"
  },
  {
    "name": "translate",
    "description": "做翻译",
    "prompt_template": "请翻译：{input}"
  },
]

destination_chains = {}
for p_info in prompt_infos:
  name = p_info["name"]
  prompt_template = p_info["prompt_template"]
  prompt = PromptTemplate(
    template= prompt_template,
    input_variables=["input"]
  )
  chain = LLMChain(
    llm = model,
    prompt = prompt
  )
  destination_chains[name] = chain

default_chain = ConversationChain(
  llm = model,
  output_key = "text"
)

destinations = [f"{p['name']}:{p['description']}" for p in prompt_infos]
destinations_str = "\n".join(destinations)

router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
router_prompt = PromptTemplate(
  template=router_template,
  input_variables=["input"],
  output_parser=RouterOutputParser()
)
router_chain = LLMRouterChain.from_llm(model, router_prompt)
chain = MultiPromptChain(
  router_chain = router_chain,
  destination_chains=destination_chains,
  default_chain=default_chain,
  verbose=True
)

result = chain.invoke("请解释什么是TLS协议")
print(result)
