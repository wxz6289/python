"""
对接 llm-demo MCP 服务示例（Streamable HTTP）

前置：先启动 MCP 服务
    cd llm && python mcp-server.py

运行：
    python 102-mcp.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, GetPromptResult, ReadResourceResult

load_dotenv(".env", override=True)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp/")


def tool_text(result: CallToolResult) -> str:
  if result.isError:
    return f"[tool error] {result.content}"
  for block in result.content:
    if block.type == "text":
      return block.text
  return str(result.structuredContent or result.content)


def prompt_text(result: GetPromptResult) -> str:
  lines: list[str] = []
  for message in result.messages:
    content = message.content
    if isinstance(content, str):
      lines.append(content)
    elif hasattr(content, "text"):
      lines.append(content.text)
  return "\n".join(lines)


def resource_text(result: ReadResourceResult) -> str:
  return result.contents[0].text if result.contents else ""


async def demo() -> None:
  print(f"连接 MCP 服务: {MCP_SERVER_URL}\n")

  async with streamable_http_client(MCP_SERVER_URL) as (read_stream, write_stream, _):
    async with ClientSession(read_stream, write_stream) as session:
      await session.initialize()

      # 1. 列出工具
      tools = await session.list_tools()
      print("Tools:", [tool.name for tool in tools.tools])

      # 2. 调用工具
      add_result = await session.call_tool("add", {"a": 12, "b": 30})
      echo_result = await session.call_tool("echo", {"message": "hello MCP"})
      now_result = await session.call_tool("now", {})
      print("add(12, 30) =", tool_text(add_result))
      print("echo =", tool_text(echo_result))
      print("now =", tool_text(now_result))

      # 3. 读取资源
      welcome = await session.read_resource("note://welcome")
      note_list = await session.read_resource("notes://list")
      print("note://welcome =", resource_text(welcome))
      print("notes://list =", resource_text(note_list))

      # 4. 获取 Prompt 模板
      prompt = await session.get_prompt(
        "summarize_topic",
        {"topic": "MCP 协议", "style": "concise"},
      )
      print("summarize_topic prompt =", prompt_text(prompt))


def main() -> None:
  asyncio.run(demo())


if __name__ == "__main__":
  main()
