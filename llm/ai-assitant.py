import os
import ast
import json
import operator
import sqlite3
import time
import urllib.parse
import urllib.request
from uuid import uuid4

import httpx
import streamlit as st
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "resources")
DB_PATH = os.path.join(STORAGE_DIR, "ai-assistant.db")
LEGACY_JSON_PATH = os.path.join(STORAGE_DIR, "ai-assistant-sessions.json")
SCHOOL_DB_PATH = os.path.join(BASE_DIR, "agent", "resources", "school.db")
load_dotenv(os.path.join(BASE_DIR, ".env"))

st.set_page_config(
  page_title="AI 智能伴侣",
  page_icon="🤖",
  layout="wide",
  initial_sidebar_state="expanded",
  menu_items={
    "Get Help": None,
    "Report a bug": None,
    "About": None,
  }
)

DEFAULT_COMPANION_NAME = "小灵"
DEFAULT_COMPANION_PERSONALITY = "温柔、耐心、积极，会用简洁的话陪伴用户。"


def now() -> str:
  return time.strftime("%Y-%m-%d %H:%M:%S")


def get_conn() -> sqlite3.Connection:
  os.makedirs(STORAGE_DIR, exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  conn.row_factory = sqlite3.Row
  return conn


def init_db() -> None:
  with get_conn() as conn:
    conn.executescript(
      """
      CREATE TABLE IF NOT EXISTS app_state (
        key TEXT PRIMARY KEY,
        value TEXT
      );

      CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        companion_name TEXT NOT NULL,
        companion_personality TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );

      CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
      );
      """
    )
  migrate_legacy_json()


def migrate_legacy_json() -> None:
  if not os.path.exists(LEGACY_JSON_PATH):
    return

  with get_conn() as conn:
    count = conn.execute("SELECT COUNT(*) AS total FROM sessions").fetchone()["total"]
    if count:
      return

  try:
    with open(LEGACY_JSON_PATH, "r", encoding="utf-8") as f:
      legacy = json.load(f)
  except (json.JSONDecodeError, OSError):
    return

  legacy_sessions = legacy.get("sessions", {})
  if not legacy_sessions:
    return

  default_name = legacy.get("companion_name", DEFAULT_COMPANION_NAME)
  default_personality = legacy.get("companion_personality", DEFAULT_COMPANION_PERSONALITY)

  with get_conn() as conn:
    for session_id, session in legacy_sessions.items():
      companion_name = session.get("companion_name", default_name)
      companion_personality = session.get("companion_personality", default_personality)
      created_at = session.get("created_at", now())
      conn.execute(
        """
        INSERT INTO sessions (
          id, title, companion_name, companion_personality, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
          session_id,
          session.get("title", "未命名会话"),
          companion_name,
          companion_personality,
          created_at,
          now(),
        ),
      )
      for message in session.get("messages", []):
        conn.execute(
          "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
          (
            session_id,
            message.get("role", "assistant"),
            message.get("content", ""),
            now(),
          ),
        )

    active_session_id = legacy.get("active_session_id")
    if active_session_id in legacy_sessions:
      conn.execute(
        "INSERT OR REPLACE INTO app_state (key, value) VALUES (?, ?)",
        ("active_session_id", active_session_id),
      )


def get_app_state(key: str) -> str | None:
  with get_conn() as conn:
    row = conn.execute("SELECT value FROM app_state WHERE key = ?", (key,)).fetchone()
  return row["value"] if row else None


def set_app_state(key: str, value: str | None) -> None:
  with get_conn() as conn:
    conn.execute(
      """
      INSERT INTO app_state (key, value) VALUES (?, ?)
      ON CONFLICT(key) DO UPDATE SET value = excluded.value
      """,
      (key, value),
    )


def load_sessions_from_db() -> dict:
  with get_conn() as conn:
    session_rows = conn.execute(
      "SELECT * FROM sessions ORDER BY created_at ASC"
    ).fetchall()
    message_rows = conn.execute(
      "SELECT session_id, role, content FROM messages ORDER BY id ASC"
    ).fetchall()

  sessions = {
    row["id"]: {
      "title": row["title"],
      "created_at": row["created_at"],
      "companion_name": row["companion_name"],
      "companion_personality": row["companion_personality"],
      "messages": [],
    }
    for row in session_rows
  }
  for row in message_rows:
    if row["session_id"] in sessions:
      sessions[row["session_id"]]["messages"].append({
        "role": row["role"],
        "content": row["content"],
      })
  return sessions


def insert_message(session_id: str, role: str, content: str) -> None:
  with get_conn() as conn:
    conn.execute(
      "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
      (session_id, role, content, now()),
    )
    conn.execute(
      "UPDATE sessions SET updated_at = ? WHERE id = ?",
      (now(), session_id),
    )


def update_session_field(session_id: str, field: str, value: str) -> None:
  allowed_fields = {"title", "companion_name", "companion_personality"}
  if field not in allowed_fields:
    raise ValueError(f"不允许更新字段: {field}")
  with get_conn() as conn:
    conn.execute(
      f"UPDATE sessions SET {field} = ?, updated_at = ? WHERE id = ?",
      (value, now(), session_id),
    )


def create_session(title: str | None = None) -> str:
  session_id = uuid4().hex
  st.session_state.sessions[session_id] = {
    "title": title or f"新会话 {len(st.session_state.sessions) + 1}",
    "created_at": now(),
    "companion_name": DEFAULT_COMPANION_NAME,
    "companion_personality": DEFAULT_COMPANION_PERSONALITY,
    "messages": [],
  }
  st.session_state.active_session_id = session_id
  with get_conn() as conn:
    conn.execute(
      """
      INSERT INTO sessions (
        id, title, companion_name, companion_personality, created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?)
      """,
      (
        session_id,
        st.session_state.sessions[session_id]["title"],
        DEFAULT_COMPANION_NAME,
        DEFAULT_COMPANION_PERSONALITY,
        st.session_state.sessions[session_id]["created_at"],
        now(),
      ),
    )
  set_app_state("active_session_id", session_id)
  return session_id


def init_state() -> None:
  init_db()
  if "sessions" not in st.session_state:
    st.session_state.sessions = load_sessions_from_db()
  if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = get_app_state("active_session_id")
  if not st.session_state.sessions:
    create_session("默认会话")


def get_active_session() -> dict:
  active_id = st.session_state.active_session_id
  if active_id not in st.session_state.sessions:
    active_id = next(iter(st.session_state.sessions))
    st.session_state.active_session_id = active_id
    set_app_state("active_session_id", active_id)
  return st.session_state.sessions[active_id]


def delete_session(session_id: str) -> None:
  st.session_state.sessions.pop(session_id, None)
  with get_conn() as conn:
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
  if not st.session_state.sessions:
    create_session("默认会话")
    return
  if st.session_state.active_session_id == session_id:
    st.session_state.active_session_id = next(iter(st.session_state.sessions))
  set_app_state("active_session_id", st.session_state.active_session_id)


@st.cache_resource
def get_llm(api_key: str, base_url: str | None, model: str) -> ChatOpenAI:
  http_client = httpx.Client(trust_env=False, timeout=30)
  return ChatOpenAI(
    model=model,
    temperature=0.7,
    api_key=SecretStr(api_key),
    base_url=base_url,
    timeout=30,
    max_retries=2,
    http_client=http_client,
  )


def build_system_prompt() -> str:
  active_session = get_active_session()
  name = active_session["companion_name"]
  personality = active_session["companion_personality"]
  return (
    f"你是用户的 AI 智能伴侣，名字叫{name}。\n"
    f"你的性格设定是：{personality}\n"
    "请用自然、温暖、真诚的中文与用户交流。"
    "你需要记住当前会话中的上下文，不要每轮都重新自我介绍。"
    "回答尽量简洁，但在用户需要陪伴或解释时可以更细致。"
    "当用户询问当前时间、数学计算、编程辅助、数据库查询或网络信息时，"
    "请优先调用可用工具获取结果，再结合工具结果回答。"
  )


def to_langchain_messages(messages: list[dict]) -> list:
  lc_messages = [SystemMessage(content=build_system_prompt())]
  for message in messages:
    if message["role"] == "user":
      lc_messages.append(HumanMessage(content=message["content"]))
    elif message["role"] == "assistant":
      lc_messages.append(AIMessage(content=message["content"]))
  return lc_messages


ALLOWED_MATH_OPERATORS = {
  ast.Add: operator.add,
  ast.Sub: operator.sub,
  ast.Mult: operator.mul,
  ast.Div: operator.truediv,
  ast.FloorDiv: operator.floordiv,
  ast.Mod: operator.mod,
  ast.Pow: operator.pow,
  ast.USub: operator.neg,
  ast.UAdd: operator.pos,
}


def safe_eval_math(expression: str) -> int | float:
  def eval_node(node: ast.AST) -> int | float:
    if isinstance(node, ast.Expression):
      return eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
      return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_MATH_OPERATORS:
      return ALLOWED_MATH_OPERATORS[type(node.op)](
        eval_node(node.left),
        eval_node(node.right),
      )
    if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_MATH_OPERATORS:
      return ALLOWED_MATH_OPERATORS[type(node.op)](eval_node(node.operand))
    raise ValueError(f"不支持的数学表达式: {expression}")

  return eval_node(ast.parse(expression, mode="eval"))


@tool
def get_current_time() -> str:
  """获取当前本地日期和时间。"""
  return time.strftime("%Y-%m-%d %H:%M:%S")


@tool
def calculate_math(expression: str) -> str:
  """执行数学表达式计算，例如 2**10 + 99。只支持基础四则运算、取模和幂运算。"""
  try:
    return str(safe_eval_math(expression))
  except Exception as exc:
    return f"计算失败: {exc}"


@tool
def programming_assistant(task: str, language: str = "Python") -> str:
  """为编程任务提供实现思路、代码结构或排错建议。"""
  return (
    f"编程辅助任务: {task}\n"
    f"建议语言: {language}\n"
    "建议先明确输入输出，再拆分为函数；如果需要代码，请在最终回答中给出"
    "可运行的最小示例，并解释关键步骤。"
  )


@tool
def query_school_database(sql: str) -> str:
  """
  查询 school.db 示例数据库。只允许执行 SELECT 语句。
  可用表:
  - students(id, name, age, gender, city)
  - teachers(id, name, age, gender, title)
  - courses(id, name, teacher_id)
  - scores(student_id, course_id, score)
  常见关联: scores.student_id = students.id, scores.course_id = courses.id,
  courses.teacher_id = teachers.id。
  """
  if not os.path.exists(SCHOOL_DB_PATH):
    return f"数据库不存在: {SCHOOL_DB_PATH}"

  statement = sql.strip().rstrip(";")
  if not statement.lower().startswith("select"):
    return "出于安全考虑，只允许执行 SELECT 查询。"

  with sqlite3.connect(SCHOOL_DB_PATH) as conn:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(statement).fetchall()
  return json.dumps([dict(row) for row in rows], ensure_ascii=False, indent=2)


@tool
def web_search(query: str) -> str:
  """使用 SerpAPI 进行网络搜索，并返回前 5 条结果摘要。"""
  api_key = os.getenv("SERPAPI_API_KEY")
  if not api_key:
    return "缺少 SERPAPI_API_KEY，无法执行网络搜索。"

  params = urllib.parse.urlencode({
    "q": query,
    "api_key": api_key,
    "engine": "google",
    "hl": "zh-cn",
    "num": 5,
  })
  url = f"https://serpapi.com/search.json?{params}"
  with urllib.request.urlopen(url, timeout=20) as response:
    payload = json.loads(response.read().decode("utf-8"))

  results = payload.get("organic_results", [])[:5]
  if not results:
    return "未检索到有效结果。"
  return "\n\n".join(
    f"{index}. {item.get('title', '无标题')}\n"
    f"链接: {item.get('link', '')}\n"
    f"摘要: {item.get('snippet', '')}"
    for index, item in enumerate(results, start=1)
  )


TOOLS = [
  get_current_time,
  calculate_math,
  programming_assistant,
  query_school_database,
  web_search,
]
TOOL_MAP = {tool_item.name: tool_item for tool_item in TOOLS}


def run_tool_call(tool_call: dict) -> ToolMessage:
  tool_name = tool_call["name"]
  tool_args = tool_call.get("args") or {}
  tool_id = tool_call.get("id", "")
  selected_tool = TOOL_MAP.get(tool_name)

  if not selected_tool:
    content = f"未知工具: {tool_name}"
  else:
    try:
      content = str(selected_tool.invoke(tool_args))
    except Exception as exc:
      content = f"工具 {tool_name} 执行失败: {exc}"

  return ToolMessage(content=content, tool_call_id=tool_id)


def get_model_config() -> tuple[str, str, str]:
  api_key = os.getenv("CLOSEAI_API_KEY") or os.getenv("OPENAI_API_KEY")
  if not api_key:
    raise EnvironmentError("请先在 .env 中设置 CLOSEAI_API_KEY 或 OPENAI_API_KEY")

  base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("CLOSEAI_BASE_URL")
  if not base_url:
    raise EnvironmentError("请先在 .env 中设置 OPENAI_BASE_URL")
  return api_key, base_url, os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def chunk_to_text(chunk) -> str:
  content = getattr(chunk, "content", "")
  if isinstance(content, str):
    return content
  return str(content) if content else ""


def stream_reply(messages: list[dict]):
  api_key, base_url, model = get_model_config()
  llm = get_llm(
    api_key=api_key,
    base_url=base_url,
    model=model,
  )
  llm_with_tools = llm.bind_tools(TOOLS)
  lc_messages = to_langchain_messages(messages)

  for _ in range(4):
    response = llm_with_tools.invoke(lc_messages)
    if not response.tool_calls:
      break

    lc_messages.append(response)
    for tool_call in response.tool_calls:
      lc_messages.append(run_tool_call(tool_call))

  for chunk in llm.stream(lc_messages):
    text = chunk_to_text(chunk)
    if text:
      yield text


def render_chat_bottom_spacer() -> None:
  st.markdown('<div class="chat-bottom-spacer"></div>', unsafe_allow_html=True)


def render_chat_bottom_anchor() -> None:
  st.markdown('<div class="chat-bottom-anchor"></div>', unsafe_allow_html=True)


def scroll_chat_to_bottom() -> None:
  st.html(
    """
    <script>
      function scrollParentContainerToBottom() {
        const frame = window.frameElement;
        let node = frame ? frame.parentElement : window.document.body;
        while (node) {
          const style = window.getComputedStyle(node);
          const canScroll = node.scrollHeight > node.clientHeight;
          const overflowY = style.overflowY;
          if (canScroll && (overflowY === "auto" || overflowY === "scroll")) {
            node.scrollTop = node.scrollHeight;
            break;
          }
          node = node.parentElement;
        }
      }

      setTimeout(scrollParentContainerToBottom, 80);
      setTimeout(scrollParentContainerToBottom, 300);
      setTimeout(scrollParentContainerToBottom, 800);
    </script>
    """,
    unsafe_allow_javascript=True,
  )


init_state()

st.markdown(
  """
  <style>
    header[data-testid="stHeader"] {
      display: none;
    }
    div[data-testid="stToolbar"] {
      display: none;
    }
    div[data-testid="stDecoration"] {
      display: none;
    }
    .block-container {
      padding-top: 0.75rem;
    }
    .app-header {
      margin: 0 0 0.75rem 0;
      line-height: 1.2;
    }
    .app-header h1 {
      font-size: 1.6rem;
      margin: 0;
    }
    .app-header p {
      color: #666;
      font-size: 0.9rem;
      margin: 0.15rem 0 0 0;
    }
    div[data-testid="stChatInput"] {
      margin-top: 0.5rem;
    }
    .chat-bottom-spacer {
      height: 180px;
    }
    .chat-bottom-anchor {
      height: 1px;
    }
  </style>
  <div class="app-header">
    <h1>AI 智能伴侣</h1>
    <p>左侧管理历史会话与伴侣设置，右侧对话。</p>
  </div>
  """,
  unsafe_allow_html=True,
)

side_col, chat_col = st.columns([1, 2.3], gap="large")

with side_col:
  st.subheader("历史会话")

  if st.button("创建会话", use_container_width=True):
    create_session()
    st.rerun()

  st.divider()

  for session_id, session in tuple(st.session_state.sessions.items()):
    is_active = session_id == st.session_state.active_session_id
    title_col, open_col, delete_col = st.columns([4, 1.2, 1])

    with title_col:
      new_title = st.text_input(
        "会话标题",
        value=session["title"],
        key=f"session_title_{session_id}",
        label_visibility="collapsed",
      )
      updated_title = new_title.strip() or session["title"]
      if updated_title != session["title"]:
        session["title"] = updated_title
        update_session_field(session_id, "title", updated_title)

    with open_col:
      if st.button("打开" if not is_active else "当前", key=f"open_{session_id}", use_container_width=True):
        st.session_state.active_session_id = session_id
        set_app_state("active_session_id", session_id)
        st.rerun()

    with delete_col:
      if st.button("删", key=f"delete_{session_id}", help="删除会话"):
        delete_session(session_id)
        st.rerun()

    st.caption(session["created_at"])

  st.divider()
  st.subheader("伴侣设置")

  active_session = get_active_session()
  active_session_id = st.session_state.active_session_id

  companion_name = st.text_input(
    "伴侣名字",
    value=active_session["companion_name"],
    key=f"companion_name_{active_session_id}",
    placeholder="例如：小灵",
  )
  updated_companion_name = companion_name.strip() or active_session["companion_name"]
  if updated_companion_name != active_session["companion_name"]:
    active_session["companion_name"] = updated_companion_name
    update_session_field(active_session_id, "companion_name", updated_companion_name)

  companion_personality = st.text_area(
    "伴侣性格",
    value=active_session["companion_personality"],
    key=f"companion_personality_{active_session_id}",
    height=120,
    placeholder="例如：温柔、幽默、善于鼓励",
  )
  updated_personality = companion_personality.strip() or active_session["companion_personality"]
  if updated_personality != active_session["companion_personality"]:
    active_session["companion_personality"] = updated_personality
    update_session_field(active_session_id, "companion_personality", updated_personality)

with chat_col:
  active_session = get_active_session()

  messages = active_session["messages"]
  chat_messages_box = st.container(height=680, border=False)

  with chat_messages_box:
    if not messages:
      st.info("开始和你的 AI 智能伴侣聊天吧。")

    for message in messages:
      with st.chat_message(message["role"]):
        st.markdown(message["content"])
    render_chat_bottom_anchor()
    scroll_chat_to_bottom()

  user_input = st.chat_input("请输入你想说的话...")
  if user_input:
    messages.append({"role": "user", "content": user_input})
    insert_message(st.session_state.active_session_id, "user", user_input)
    with chat_messages_box:
      with st.chat_message("user"):
        st.markdown(user_input)

    try:
      with chat_messages_box:
        assistant_message_box = st.container()
        render_chat_bottom_spacer()
        scroll_chat_to_bottom()
        with assistant_message_box:
          with st.chat_message("assistant"):
            with st.spinner("伴侣正在思考..."):
              reply = st.write_stream(stream_reply(messages))
        scroll_chat_to_bottom()
      messages.append({"role": "assistant", "content": reply})
      insert_message(st.session_state.active_session_id, "assistant", reply)
    except Exception as exc:
      error_message = f"调用大模型失败：{exc}"
      messages.append({
        "role": "assistant",
        "content": error_message,
      })
      insert_message(st.session_state.active_session_id, "assistant", error_message)
      with chat_messages_box:
        assistant_message_box = st.container()
        render_chat_bottom_spacer()
        scroll_chat_to_bottom()
        with assistant_message_box:
          with st.chat_message("assistant"):
            st.error(error_message)
        scroll_chat_to_bottom()
