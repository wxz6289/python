import inspect
import os
from typing import Any

from langchain_core.prompts import StringPromptTemplate
from langchain_openai import ChatOpenAI


def hello_world() -> tuple[str, str]:
    print("Hello world")
    return ("Hello", "world")


PROMPT = """
你是一个天才程序员，现给你如下函数名称，你会按照如下格式，输出函数的名称、源码和中文注释。
函数名称: {fn_name}
源码:
{source_code}
中文解释:

"""

def get_source_code(fn: Any) -> str:
    return inspect.getsource(fn)


class CustomPrompt(StringPromptTemplate):
    def format(self, **kwargs: Any) -> str:
        fn = kwargs["fn_name"]
        source_code = get_source_code(fn)
        return PROMPT.format(fn_name=fn.__name__, source_code=source_code)


if __name__ == "__main__":
    prompt_template = CustomPrompt(input_variables=["fn_name"])
    prompt_text = prompt_template.format(fn_name=hello_world)

    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not deepseek_api_key:
        raise EnvironmentError("Please set DEEPSEEK_API_KEY (or OPENAI_API_KEY).")

    llm = ChatOpenAI(
        model="deepseek-chat",
        temperature=0,
        api_key=deepseek_api_key,
        base_url="https://api.deepseek.com/v1",
    )

    try:
        result = llm.invoke(prompt_text)
        print(result.content)
    except Exception as e:
        print(e)
