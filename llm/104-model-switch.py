import os
from dataclasses import dataclass
from typing import Callable

from dotenv import load_dotenv
from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

# override=True：避免 shell 中旧的 DEEPSEEK_API_KEY 覆盖 .env
load_dotenv(".env", override=True)

DEFAULT_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def create_chat_model(model_name: str):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise EnvironmentError("请设置 DEEPSEEK_API_KEY")

    # 支持 "deepseek:model-id" 或裸 model id
    model = model_name.split(":", 1)[-1] if ":" in model_name else model_name
    return init_chat_model(
        model=model,
        model_provider="deepseek",
        api_key=api_key,
        base_url=os.getenv("DEEPSEEK_BASE_URL"),
        temperature=0,
    )


@dataclass
class Context:
    model: str


@wrap_model_call
def configurable_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    model_name = request.runtime.context.model
    model = create_chat_model(model_name)
    return handler(request.override(model=model))


default_model = create_chat_model(DEFAULT_MODEL)

agent = create_deep_agent(
    model=default_model,
    middleware=[configurable_model],
    context_schema=Context,
)

# Invoke with the user's model selection
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Hello!"}]},
    context=Context(model=DEFAULT_MODEL),
)
print(result)
