"""Minimal LangChain agent graph for deployment."""

from __future__ import annotations

import ast
import os
from datetime import datetime, timezone
from typing import Any
from langchain.agents import create_agent
from langchain_core.tools import tool, BaseTool
from pydantic import Field, BaseModel
from duckduckgo_search import DDGS

DEFAULT_MODEL = os.getenv("SIMPLE_AGENT_MODEL", "anthropic:claude-sonnet-4-6")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def send_mail(to: str, subject: str, content: str):
  """Send email to a recipient."""
  email = {
    "to": to,
    "subject": subject,
    "body": content,
  }
  return "邮件发送成功: {email}"

@tool
def utc_now() -> str:
    """Return the current UTC timestamp in ISO format."""
    return datetime.now(tz=timezone.utc).isoformat()


@tool
def calculator(expression: str) -> str:
    """Evaluate a simple arithmetic expression safely.

    Supported operators: +, -, *, /, %, ** and parentheses.
    """
    parsed = ast.parse(expression, mode="eval")
    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.USub,
        ast.UAdd,
        ast.Load,
    )

    for node in ast.walk(parsed):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Expression contains unsupported syntax")

    result: Any = eval(compile(parsed, "<calculator>", "eval"), {"__builtins__": {}}, {})
    return str(result)

class SearchArgs(BaseModel):
    query: str = Field(..., description="The query to search for.")

class MySearchTool(BaseTool):
    name: str = "search"
    description: str = "Search the web for the latest information using DuckDuckGo (no API key required). Returns up-to-date search results."
    args_schema: type[BaseModel] = SearchArgs

    def _run(self, query: str) -> str:
        """Run the tool to search the web for the latest information."""
        try:
            # Use DuckDuckGo Search library for real-time web search
            with DDGS() as ddgs:
                # Search for results
                results = list(ddgs.text(query, max_results=5))
            
            if not results:
                return f"No results found for '{query}'. Try rephrasing your query."
            
            # Format the results
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                url = result.get('href', 'No URL')
                
                formatted_results.append(
                    f"Result {i}:\n"
                    f"Title: {title}\n"
                    f"Summary: {body}\n"
                    f"Source: {url}\n"
                )
            
            return "\n---\n".join(formatted_results)
            
        except Exception as e:
            return f"Error during search: {str(e)}. Please try again."

# Create an instance of the search tool
search_tool = MySearchTool()

graph = create_agent(
    model=DEEPSEEK_MODEL,
    tools=[utc_now, calculator, send_mail, search_tool],
    system_prompt=(
        "You are a concise assistant. "
        "Use tools when they add factual precision, then return a direct answer."
    ),
    name="simple_agent",
)
