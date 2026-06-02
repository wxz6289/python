"""
MCP 服务示例（FastAPI + Streamable HTTP + 可选身份认证）

启动:
    pip install mcp fastapi uvicorn
    cd llm && python mcp-server.py

MCP 端点: http://127.0.0.1:8000/mcp/
健康检查: http://127.0.0.1:8000/health

启用认证（HTTP Bearer / stdio 环境变量）:
    export MCP_AUTH_ENABLED=true
    export MCP_USERNAME=demo
    export MCP_PASSWORD=demo
    # 可选：静态 Token，stdio 模式必须设置
    export MCP_API_TOKEN=your-secret-token

    python mcp-server.py

HTTP 获取访问 Token:
    curl -X POST http://127.0.0.1:8000/auth/token \\
      -H "Content-Type: application/json" \\
      -d '{"username":"demo","password":"demo"}'

Cursor / Claude 配置示例（启用认证时加 Authorization）:
    {
      "mcpServers": {
        "llm-demo": {
          "url": "http://127.0.0.1:8000/mcp/",
          "headers": {
            "Authorization": "Bearer your-secret-token"
          }
        }
      }
    }
"""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from mcp_auth import (
  TokenStore,
  auth_enabled,
  build_auth_settings,
  create_token_verifier,
  issue_login_token,
  validate_stdio_auth,
)

load_dotenv(".env", override=True)

MCP_SERVER_BASE = os.getenv("MCP_SERVER_BASE", "http://127.0.0.1:8000")
token_store = TokenStore()

mcp_kwargs: dict = {
  "name": "llm-demo",
  "json_response": True,
  "stateless_http": True,
  "streamable_http_path": "/",
}

if auth_enabled():
  mcp_kwargs["auth"] = build_auth_settings(MCP_SERVER_BASE)
  mcp_kwargs["token_verifier"] = create_token_verifier(token_store)

mcp = FastMCP(**mcp_kwargs)

NOTES: dict[str, str] = {
  "welcome": "欢迎使用 MCP 示例服务",
  "docs": "详见 llm/docs/mcp.md",
}


@mcp.tool()
def add(a: float, b: float) -> float:
  """两数相加。"""
  return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
  """两数相减。"""
  return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
  """两数相乘。"""
  return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
  """两数相除。"""
  return a / b


@mcp.tool()
def echo(message: str) -> str:
  """原样返回输入文本。"""
  return message


@mcp.tool()
def now(timezone: str = "local") -> str:
  """返回当前时间（示例工具，timezone 参数仅作演示）。"""
  _ = timezone
  return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.resource("note://{key}")
def get_note(key: str) -> str:
  """读取内置说明资源。"""
  return NOTES.get(key, f"未找到 note: {key}")


@mcp.resource("notes://list")
def list_notes() -> str:
  """列出所有可用 note 键。"""
  return ", ".join(sorted(NOTES))


@mcp.prompt()
def summarize_topic(topic: str, style: str = "concise") -> str:
  """生成「总结某主题」的提示词模板。"""
  styles = {
    "concise": "用 3-5 条要点简洁总结",
    "detailed": "写一份结构化的详细总结",
  }
  instruction = styles.get(style, styles["concise"])
  return f"请{instruction}以下主题：{topic}"


class TokenRequest(BaseModel):
  username: str
  password: str


@asynccontextmanager
async def lifespan(app: FastAPI):
  async with mcp.session_manager.run():
    yield


app = FastAPI(
  title="LLM MCP Demo",
  description="FastAPI 挂载的 MCP Streamable HTTP 服务示例",
  lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str | bool]:
  return {
    "status": "ok",
    "service": "llm-demo-mcp",
    "auth_enabled": auth_enabled(),
  }


@app.post("/auth/token")
def auth_token(body: TokenRequest) -> dict[str, str | int]:
  if not auth_enabled():
    raise HTTPException(status_code=400, detail="MCP 认证未启用")

  access_token = issue_login_token(token_store, body.username, body.password)
  if access_token is None:
    raise HTTPException(status_code=401, detail="用户名或密码错误")

  return {
    "access_token": access_token,
    "token_type": "bearer",
    "expires_in": token_store.ttl_seconds,
  }


app.mount("/mcp", mcp.streamable_http_app())


if __name__ == "__main__":
  if len(sys.argv) > 1 and sys.argv[1] == "--stdio":
    validate_stdio_auth()
    mcp.run(transport="stdio")
  else:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
