import json
import os
import xml.etree.ElementTree as ET
from typing import Any

# 关闭 LangSmith tracing，避免未配置有效 LangSmith 权限时后台上传 runs 报 403。
os.environ.setdefault("LANGSMITH_TRACING", "false")
os.environ.setdefault("LANGCHAIN_TRACING_V2", "false")

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

llm = init_chat_model(
  model="gpt-4o-mini",
  temperature=0,
  api_key=os.getenv("CLOSEAI_API_KEY"),
  base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL"),
)

def strip_namespace(tag: str) -> str:
  if "}" in tag:
    return tag.rsplit("}", 1)[-1]
  return tag


def element_to_dict(element: ET.Element) -> dict[str, Any]:
  children = [element_to_dict(child) for child in element]
  node: dict[str, Any] = {
    "tag": strip_namespace(element.tag),
  }

  if element.attrib:
    node["attributes"] = {
      strip_namespace(key): value for key, value in element.attrib.items()
    }

  text = (element.text or "").strip()
  if text:
    node["text"] = text

  if children:
    node["children"] = children

  return node


def parse_xml(xml_text: str) -> ET.Element:
  try:
    return ET.fromstring(xml_text)
  except ET.ParseError as exc:
    raise ValueError(f"XML 格式错误：{exc}") from exc


@tool
def xml_to_json(xml_text: str) -> str:
  """把 XML 字符串解析成 JSON，保留标签、属性、文本和子节点。"""
  try:
    root = parse_xml(xml_text)
    return json.dumps(element_to_dict(root), ensure_ascii=False, indent=2)
  except Exception as exc:
    return f"解析失败：{exc}"


@tool
def find_xml_tags(xml_text: str, tag_name: str) -> str:
  """从 XML 字符串中查找指定标签名的所有节点文本和属性。"""
  try:
    root = parse_xml(xml_text)
    matches = []
    for element in root.iter():
      if strip_namespace(element.tag) == tag_name:
        matches.append({
          "tag": strip_namespace(element.tag),
          "attributes": {
            strip_namespace(key): value for key, value in element.attrib.items()
          },
          "text": (element.text or "").strip(),
        })
    if not matches:
      return f"没有找到标签：{tag_name}"
    return json.dumps(matches, ensure_ascii=False, indent=2)
  except Exception as exc:
    return f"查询失败：{exc}"


agent = create_agent(
  model=llm,
  tools=[xml_to_json, find_xml_tags],
  system_prompt=(
    "你是一个 XML 解析器 Agent。"
    "当用户提供 XML 或询问 XML 内容时，必须优先调用工具解析，"
    "再用中文总结结构、字段含义或查询结果。"
  ),
)

xml = """
<library>
  <book id="b001" category="programming">
    <title>Python 入门</title>
    <author>张三</author>
    <price currency="CNY">59.00</price>
  </book>
  <book id="b002" category="ai">
    <title>LangChain 实战</title>
    <author>李四</author>
    <price currency="CNY">89.00</price>
  </book>
</library>
""".strip()

result = agent.invoke({
  "messages": [
    {
      "role": "user",
      "content": (
        "请解析下面的 XML，并告诉我有哪些书名，顺便说明根节点结构：\n\n"
        f"{xml}"
      ),
    },
  ]
})

last_message = result["messages"][-1]
if isinstance(last_message, AIMessage):
  print(last_message.content)
else:
  print(last_message)

