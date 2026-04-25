import ast
import contextlib
import io
import multiprocessing
import os
import traceback
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, "..", ".env"))

api_key = os.getenv("CLOSEAI_API_KEY")
if not api_key:
  raise EnvironmentError("CLOSEAI_API_KEY is not set")

base_url = os.getenv("OPENAI_BASE_URL")
if not base_url:
  raise EnvironmentError("OPENAI_BASE_URL is not set")

llm = ChatOpenAI(
  model="gpt-4o-mini",
  temperature=0,
  api_key=SecretStr(api_key),
  base_url=base_url,
)


class CodeOutput(BaseModel):
  explanation: str = Field(description="代码思路说明")
  code: str = Field(description="可直接执行的 Python 代码")


class ExecutionResult(BaseModel):
  ok: bool
  stdout: str
  error: str


parser = JsonOutputParser(pydantic_object=CodeOutput)

code_prompt = PromptTemplate(
  template=(
    "你是一个 Python 代码编写助手。请根据用户需求生成可执行的 Python 代码。\n\n"
    "用户需求：\n{requirement}\n\n"
    "要求：\n"
    "- 只能使用 Python 标准库中的基础能力。\n"
    "- 不要读写文件，不要访问网络，不要启动子进程。\n"
    "- 代码必须定义 solve() 函数，并在最后 print(solve())。\n"
    "- 只输出 JSON，不要输出 Markdown 代码块或额外解释。\n\n"
    "{format_instructions}"
  ),
  input_variables=["requirement"],
  partial_variables={"format_instructions": parser.get_format_instructions()},
)

summary_prompt = PromptTemplate.from_template(
  """
你是代码执行结果分析助手。请根据用户需求、生成代码和执行结果，给出简洁总结。

用户需求：
{requirement}

代码思路：
{explanation}

生成代码：
{code}

执行结果：
{execution}

请输出：
1. 是否执行成功
2. 运行结果
3. 如有错误，说明原因和修改建议
"""
)


def validate_code(code: str) -> None:
  tree = ast.parse(code)
  blocked_nodes = (
    ast.Import,
    ast.ImportFrom,
    ast.With,
    ast.AsyncWith,
    ast.Global,
    ast.Nonlocal,
  )
  blocked_calls = {
    "open",
    "exec",
    "eval",
    "compile",
    "__import__",
    "input",
    "breakpoint",
  }

  for node in ast.walk(tree):
    if isinstance(node, blocked_nodes):
      raise ValueError(f"不允许的语法: {type(node).__name__}")
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
      if node.func.id in blocked_calls:
        raise ValueError(f"不允许调用函数: {node.func.id}")


def _run_code_worker(code: str, queue: multiprocessing.Queue) -> None:
  allowed_builtins: dict[str, Any] = {
    "abs": abs,
    "all": all,
    "any": any,
    "bool": bool,
    "dict": dict,
    "enumerate": enumerate,
    "filter": filter,
    "float": float,
    "int": int,
    "len": len,
    "list": list,
    "map": map,
    "max": max,
    "min": min,
    "pow": pow,
    "print": print,
    "range": range,
    "round": round,
    "set": set,
    "sorted": sorted,
    "str": str,
    "sum": sum,
    "tuple": tuple,
    "zip": zip,
  }
  namespace = {"__builtins__": allowed_builtins}
  stdout = io.StringIO()

  try:
    validate_code(code)
    with contextlib.redirect_stdout(stdout):
      exec(compile(code, "<generated_code>", "exec"), namespace, namespace)
    queue.put(ExecutionResult(ok=True, stdout=stdout.getvalue(), error="").model_dump())
  except Exception:
    queue.put(
      ExecutionResult(
        ok=False,
        stdout=stdout.getvalue(),
        error=traceback.format_exc(),
      ).model_dump()
    )


def execute_generated_code(generation: dict) -> dict:
  code = generation["code"]
  context = multiprocessing.get_context("fork")
  queue = context.Queue()
  process = context.Process(target=_run_code_worker, args=(code, queue))
  process.start()
  process.join(timeout=5)

  if process.is_alive():
    process.terminate()
    process.join()
    return ExecutionResult(ok=False, stdout="", error="代码执行超时").model_dump()

  if queue.empty():
    return ExecutionResult(ok=False, stdout="", error="代码执行失败，未返回结果").model_dump()
  return queue.get()


def show_steps(data: dict) -> dict:
  generation = data["generation"]
  print("\n===== 生成代码思路 =====")
  print(generation["explanation"])
  print("\n===== 生成代码 =====")
  print(generation["code"])
  print("\n===== 执行结果 =====")
  print(data["execution"])
  return data


code_chain = code_prompt | llm | parser

summary_chain = (
  {
    "requirement": lambda x: x["requirement"],
    "explanation": lambda x: x["generation"]["explanation"],
    "code": lambda x: x["generation"]["code"],
    "execution": lambda x: x["execution"],
  }
  | summary_prompt
  | llm
  | StrOutputParser()
)

chain = (
  RunnablePassthrough.assign(generation=code_chain)
  .assign(execution=lambda x: execute_generated_code(x["generation"]))
  | RunnableLambda(show_steps)
  | RunnablePassthrough.assign(summary=summary_chain)
)


if __name__ == "__main__":
  result = chain.invoke({
    "requirement": "请统一1000以内有多少个质数,并给出中位数的质数是什么"
  })
  print("\n===== 最终总结 =====")
  print(result["summary"])
