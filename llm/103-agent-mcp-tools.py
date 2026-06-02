"""
Deep Agent 对接 MCP 工具示例（HTTP / stdio + 可选身份认证）

HTTP 模式（需先启动 HTTP 服务）:
    python mcp-server.py
    python 103-agent-mcp-tools.py --transport http

stdio 模式（由客户端拉起子进程，无需单独启动服务）:
    python 103-agent-mcp-tools.py --transport stdio

启用 MCP 认证:
    export MCP_AUTH_ENABLED=true
    export MCP_USERNAME=demo
    export MCP_PASSWORD=demo
    # HTTP 可直接登录；stdio 需共享密钥
    export MCP_API_TOKEN=your-secret-token

    python mcp-server.py
    python 103-agent-mcp-tools.py --transport http
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import httpx
from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest, ToolCallInterceptor
from langchain_deepseek import ChatDeepSeek
from pydantic import SecretStr

from mcp_auth import auth_enabled, get_static_token

load_dotenv(".env", override=True)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")
MCP_SERVER_BASE = os.getenv("MCP_SERVER_BASE", "http://127.0.0.1:8000")
MCP_STDIO_SCRIPT = Path(__file__).resolve().parent / "mcp-server.py"
MCP_PYTHON = os.getenv("MCP_PYTHON", sys.executable)


def create_model() -> ChatDeepSeek:
  api_key = os.getenv("DEEPSEEK_API_KEY")
  if not api_key:
    raise EnvironmentError("请设置 DEEPSEEK_API_KEY")

  return ChatDeepSeek(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=SecretStr(api_key),
    api_base=os.getenv("DEEPSEEK_BASE_URL"),
    temperature=0,
    max_tokens=1000,
  )


def last_ai_text(messages: list) -> str:
  for message in reversed(messages):
    content = getattr(message, "content", "")
    if content:
      return str(content)
  return ""


async def resolve_access_token() -> str:
  static_token = get_static_token()
  if static_token:
    return static_token

  username = os.getenv("MCP_USERNAME", "demo")
  password = os.getenv("MCP_PASSWORD", "demo")
  async with httpx.AsyncClient(timeout=10.0) as client:
    response = await client.post(
      f"{MCP_SERVER_BASE.rstrip('/')}/auth/token",
      json={"username": username, "password": password},
    )
    if response.status_code == 401:
      raise RuntimeError("MCP 认证失败，请检查 MCP_USERNAME / MCP_PASSWORD")
    response.raise_for_status()
    payload = response.json()
    access_token = payload.get("access_token")
    if not access_token:
      raise RuntimeError("MCP 认证响应缺少 access_token")
    return str(access_token)


class AccessTokenInterceptor:
  """在每次 MCP 工具调用时注入 Authorization Bearer Token。"""

  def __init__(self, access_token: str) -> None:
    self.access_token = access_token

  async def __call__(self, request: MCPToolCallRequest, handler):
    headers = dict(request.headers or {})
    headers["Authorization"] = f"Bearer {self.access_token}"
    return await handler(request.override(headers=headers))


def apply_bootstrap_auth(config: dict, transport: str, access_token: str | None) -> dict:
  """为 get_tools / initialize 等会话建立阶段注入认证（拦截器仅作用于 tool call）。"""
  if not access_token:
    return config

  if transport == "http":
    return {
      **config,
      "headers": {"Authorization": f"Bearer {access_token}"},
    }

  if transport == "stdio":
    return {
      **config,
      "env": {"MCP_API_TOKEN": access_token},
    }

  return config


def build_mcp_client(transport: str, access_token: str | None = None) -> MultiServerMCPClient:
  if transport == "http":
    config: dict = {
      "transport": "http",
      "url": MCP_SERVER_URL,
    }
    interceptors: list[ToolCallInterceptor] = []
    if access_token:
      interceptors.append(AccessTokenInterceptor(access_token))
    return MultiServerMCPClient(
      {"llm-demo": apply_bootstrap_auth(config, transport, access_token)},
      tool_interceptors=interceptors,
    )

  if transport == "stdio":
    if auth_enabled() and not access_token:
      raise ValueError("stdio 模式启用认证时必须设置 MCP_API_TOKEN")

    config = {
      "transport": "stdio",
      "command": MCP_PYTHON,
      "args": [str(MCP_STDIO_SCRIPT), "--stdio"],
      "cwd": str(MCP_STDIO_SCRIPT.parent),
    }
    return MultiServerMCPClient(
      {"llm-demo": apply_bootstrap_auth(config, transport, access_token)},
    )

  raise ValueError(f"不支持的 transport: {transport}，请使用 http 或 stdio")


async def run_agent(transport: str, question: str) -> None:
  model = create_model()
  access_token = await resolve_access_token() if auth_enabled() else None
  client = build_mcp_client(transport, access_token)

  tools = await client.get_tools()
  print(f"[{transport}] MCP tools:", [tool.name for tool in tools])

  agent = create_deep_agent(
    model=model,
    tools=tools,
    system_prompt="你是一个数学助手，优先调用 MCP 工具 add 完成计算。",
  )

  response = await agent.ainvoke(
    {
      "messages": [
        {"role": "user", "content": question},
      ],
    },
  )

  print(last_ai_text(response["messages"]))


async def main() -> None:
  parser = argparse.ArgumentParser(description="Deep Agent 对接 MCP 工具")
  parser.add_argument(
    "--transport",
    choices=["http", "stdio"],
    default=os.getenv("MCP_TRANSPORT", "stdio"),
    help="MCP 传输方式：http 或 stdio（默认 stdio）",
  )
  parser.add_argument(
    "--question",
    default="使用MCP服务计算1229除以345的商?",
    help="发给 Agent 的问题",
  )
  args = parser.parse_args()

  if args.transport == "http":
    print("HTTP 模式：请确保已运行 python mcp-server.py")
  if auth_enabled():
    if args.transport == "stdio" and not get_static_token():
      raise SystemExit("stdio 认证需要设置 MCP_API_TOKEN")
    print("MCP 认证已启用\n")

  await run_agent(args.transport, args.question)


if __name__ == "__main__":
  asyncio.run(main())
