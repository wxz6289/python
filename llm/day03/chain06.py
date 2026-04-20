from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from duckduckgo_search import DDGS
import os

deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
if not deepseek_api_key:
    raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

llm = init_chat_model(
    model="deepseek-chat", base_url="http://api.deepseek.com/v1", temperature=0, api_key=deepseek_api_key
)

class GraphState(TypedDict):
  input: str
  category: str
  messages: List[BaseMessage]
  output: str

router_prompt = ChatPromptTemplate.from_template("""
你是一个请求分类器, 请分类：
- rag
- translate
- agent

只返回分类名称

用户输入：{input}
""")

router_chain = router_prompt | llm

def router_node(state: GraphState):
  resoult = (router_prompt | llm).invoke({"input": state["input"]})
  category = resoult.content.strip().lower()
  return {
    "category": category
  }

translate_prompt = ChatPromptTemplate.from_template("请翻译：{input}")
def translate_node(state: GraphState):
  resoult = (translate_prompt | llm).invoke({
    "input": state["input"]
  })
  return {
    "output": resoult.content
  }

def rag_node(state: GraphState):
  # 👉 这里可以接 FAISS / Milvus / PGVector
  context = "（这里是检索到的知识）"

  prompt = ChatPromptTemplate.from_template("""
基于以下知识回答问题：
{context}

问题：
{input}
""")
  result = (prompt | llm).invoke({
    "context": context,
    "input": state["input"]
  })

  return {
    "output": result.content
  }

@tool
def search_tool(q: str) -> str:
  """
  执行 Web 搜索（DuckDuckGo）
  """
  results = []
  with DDGS() as ddgs:
    for r in ddgs.text(q, max_results=5):
      results.append(f"{r['title']}\n{r['href']}\n{r['body']}")
  return "\n\n".join(results)

def agent_node(state: GraphState):
  result = llm.invoke(
    f"你可以使用工具回答：{state['input']}"
  )
  return {
    "output": result.content
  }

builder = StateGraph(GraphState)

# 注册节点
builder.add_node("router", router_node)
builder.add_node("translate", translate_node)
builder.add_node("rag", rag_node)
builder.add_node("agent", agent_node)

def route_decision(state: GraphState):
  if "translate" in state["category"]:
    return "translate"
  elif "rag" in state["category"]:
    return "rag"
  return "agent"

builder.set_entry_point("router")

# 定义流程
builder.add_conditional_edges(
  "router",
  route_decision,
  {
    "translate": "translate",
    "rag": "rag",
    "agent": "agent",
  }
)

# 所有节点结束
builder.add_edge("translate", END)
builder.add_edge("rag", END)
builder.add_edge("agent", END)
# 编译graph
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)
# graph = builder.compile()

# 支持流
for chunk in graph.stream({
  "input": "请翻译 Nothing will work unless you do",
},
  config= {
    "configurable": {
      "thread_id": "user-king"
    }
  },
  stream_mode="values"
):
  print(chunk)
