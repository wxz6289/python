# FastAPI 核心内容

FastAPI 是基于 **Python 类型注解** 的现代 Web 框架，底层基于 **Starlette**（ASGI）和 **Pydantic**（数据校验），默认生成 OpenAPI 文档，性能接近 Node.js / Go 框架。

本文结合本仓库 `ai-server` 项目（LangChain + Redis + WebSocket）讲解核心概念。按天学习安排见 [FastAPI 3 天学习计划](./fastapi-learning-plan.md)。

---

## 1. 架构全景

```
┌─────────────────────────────────────────────────────────────┐
│                    你的 Python 代码                           │
│         路由 · 依赖注入 · Pydantic 模型 · 业务逻辑              │
├─────────────────────────────────────────────────────────────┤
│                      FastAPI 框架层                          │
│   路由注册 · 参数解析 · 校验 · OpenAPI · 依赖注入系统           │
├─────────────────────────────────────────────────────────────┤
│                      Starlette（ASGI）                       │
│   请求/响应 · 中间件 · WebSocket · BackgroundTasks           │
├─────────────────────────────────────────────────────────────┤
│                   Uvicorn / Hypercorn（ASGI Server）          │
│   事件循环 · HTTP 解析 · 连接管理                             │
├─────────────────────────────────────────────────────────────┤
│                      操作系统 / 网络                          │
└─────────────────────────────────────────────────────────────┘
```

| 组件 | 职责 |
|------|------|
| **FastAPI** | 路由装饰器、自动文档、依赖注入、Pydantic 集成 |
| **Starlette** | 轻量 ASGI 工具包，FastAPI 的底层 |
| **Pydantic** | 请求/响应数据校验与序列化（v2 为当前主流） |
| **Uvicorn** | ASGI 服务器，开发/生产常用 |

### 框架选型速览

FastAPI 属于 **轻量 API 框架**，与 Flask 同类，但原生 async + 自动文档；与 Django 的全栈「电池Included」不同；与 Spring / NestJS 的企业级 DI 体系相近但更轻。详细对比见 [框架对比](./framework-comparison.md)。

---

## 2. 框架对比

FastAPI 与 Flask、Django、Spring Boot、NestJS 的详细对比已抽离至独立文档：[框架对比](./framework-comparison.md)。

---

## 3. 最小应用

```python
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

启动后访问：

| 地址 | 说明 |
|------|------|
| `http://127.0.0.1:8000/` | 接口 |
| `http://127.0.0.1:8000/docs` | Swagger UI（自动生成） |
| `http://127.0.0.1:8000/redoc` | ReDoc 文档 |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI Schema |

---

## 4. 路由与 HTTP 方法

### 3.1 基本路由

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")       # 路径参数
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(name: str):  # 也可作为 query 参数
    return {"name": name}
```

支持的装饰器：`@app.get` · `@app.post` · `@app.put` · `@app.patch` · `@app.delete` · `@app.options` · `@app.head`

### 3.2 路径参数 vs 查询参数

```python
@app.get("/users/{user_id}")
async def get_user(
    user_id: int,              # 路径参数（必填）
    q: str | None = None,      # 查询参数 ?q=xxx（可选）
    skip: int = 0,
    limit: int = 10,
):
    return {"user_id": user_id, "q": q, "skip": skip, "limit": limit}
```

**本项目的实际用法**（`main.py`）：

```python
@app.get("/chat", response_class=PlainTextResponse)
async def chat(query: str, session_id: str = "default") -> str:
    return master.chat(query, session_id)
```

- `query`：必填查询参数
- `session_id`：可选，默认 `"default"`
- `response_class=PlainTextResponse`：返回纯文本而非 JSON

### 3.3 APIRouter（模块化）

大型项目应按业务拆分路由：

```python
# routers/chat.py
from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/")
async def chat(query: str):
    ...

# main.py
from routers.chat import router as chat_router
app.include_router(chat_router)
```

---

## 5. Pydantic 模型（核心）

FastAPI 的校验能力来自 **Pydantic v2**。函数参数类型 + `BaseModel` 自动完成解析与校验。

### 4.1 请求体（Body）

```python
from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    age: int = Field(ge=0, le=150)

@app.post("/users/")
async def create_user(user: UserCreate):
    return user  # 自动序列化为 JSON
```

### 4.2 响应模型

```python
class UserOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}  # 支持 ORM 对象转换

@app.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    ...
```

### 4.3 常用校验

| 方式 | 示例 |
|------|------|
| 字段约束 | `Field(min_length=1, pattern=r"^\d+$")` |
| 可选字段 | `nickname: str \| None = None` |
| 枚举 | `status: Literal["active", "banned"]` |
| 嵌套 | `address: AddressModel` |
| 自定义校验 | `@field_validator("name")` |

校验失败时 FastAPI 自动返回 **422 Unprocessable Entity**，附带详细错误字段。

---

## 6. 依赖注入（Depends）

FastAPI 的 **Depends** 类似 NestJS 的 DI，用于复用逻辑：数据库连接、鉴权、分页参数等。

```python
from fastapi import Depends, HTTPException, Header

async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    return authorization.removeprefix("Bearer ")

@app.get("/protected")
async def protected(token: str = Depends(verify_token)):
    return {"token": token}
```

### 依赖的类型

| 类型 | 说明 |
|------|------|
| 函数依赖 | `Depends(get_db)` |
| 类依赖 | `Depends(Pagination)`，可带 `__call__` |
| 子依赖 | 依赖 A 内部 `Depends(B)`，自动解析链 |
| `yield` 依赖 | 请求前初始化，请求后清理（类似 `try/finally`） |

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**最佳实践**：把 `Master`、Redis 连接、配置读取封装为依赖，而不是全局单例。

---

## 7. 请求与响应

### 6.1 获取原始请求

```python
from fastapi import Request

@app.post("/raw")
async def raw(request: Request):
    body = await request.body()
    headers = request.headers
    client = request.client
    return {"len": len(body)}
```

### 6.2 自定义响应

```python
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse, FileResponse

@app.get("/text", response_class=PlainTextResponse)
async def text(): return "hello"

@app.get("/stream")
async def stream():
    async def generate():
        for i in range(5):
            yield f"chunk {i}\n"
    return StreamingResponse(generate(), media_type="text/plain")
```

**AI 场景常用**：`StreamingResponse` 流式输出 LLM token。

### 6.3 状态码与 Header

```python
from fastapi import status

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create():
    return {"ok": True}

from fastapi import Response

@app.get("/custom")
async def custom(response: Response):
    response.headers["X-Custom"] = "value"
    return {"ok": True}
```

---

## 8. 异常处理

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id}
```

全局异常处理器：

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

---

## 9. 中间件

```python
from fastapi.middleware.cors import CORSMiddleware
import time

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return response
```

常见中间件：CORS · GZip · 请求日志 · 限流 · 认证。

---

## 10. 异步 vs 同步

| 写法 | 适用 |
|------|------|
| `async def` | I/O 密集：DB、HTTP 调用、WebSocket |
| `def`（同步） | CPU 密集或阻塞库；FastAPI 会放入线程池 |

```python
@app.get("/async-endpoint")
async def async_endpoint():
    result = await some_async_io()
    return result

@app.get("/sync-endpoint")
def sync_endpoint():
    return heavy_cpu_work()  # 在线程池执行，不阻塞事件循环
```

**本项目注意点**：`main.py` 中 `chat()` 是 `async def`，但内部调用 `master.chat()` 是 **同步阻塞** 的 LangChain 调用。高并发时应：

- 改为 `async def` + LangChain 异步 API（`ainvoke`），或
- 使用 `run_in_executor` / `def` 路由让 FastAPI 自动线程池处理

---

## 11. WebSocket

```python
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("WebSocket disconnected")
```

| 方法 | 说明 |
|------|------|
| `await websocket.accept()` | 握手接受连接 |
| `receive_text()` / `receive_json()` | 接收消息 |
| `send_text()` / `send_json()` | 发送消息 |
| `WebSocketDisconnect` | 客户端断开 |

**AI 场景**：WebSocket 适合流式对话、打字机效果；HTTP SSE 也是常见替代方案。

---

## 12. 生命周期与 BackgroundTasks

### 11.1 应用生命周期

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动：连接池、Redis、模型预热
    app.state.master = Master()
    yield
    # 关闭：释放连接
    ...

app = FastAPI(lifespan=lifespan)
```

替代旧的 `@app.on_event("startup")` / `"shutdown"`。

### 11.2 后台任务

```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(message)

@app.post("/send-notification/")
async def send_notification(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, f"sent to {email}")
    return {"message": "Notification sent"}
```

---

## 13. 安全与认证

### 12.1 OAuth2 + JWT（常见模式）

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    user = decode_jwt(token)
    return user
```

FastAPI 内置：`OAuth2PasswordBearer` · `HTTPBearer` · `APIKeyHeader` · `APIKeyQuery`。

### 12.2 安全最佳实践

| 实践 | 说明 |
|------|------|
| API Key 走 Header | 不要放 URL 查询参数（易泄露到日志） |
| CORS 白名单 | 生产禁止 `allow_origins=["*"]` + credentials |
| 限流 | slowapi / Redis 计数 |
| 输入校验 | 全部走 Pydantic，禁止信任原始 body |
| 密钥 | `.env` + `pydantic-settings`，不入 Git |

---

## 14. 配置管理

推荐使用 **pydantic-settings**：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    deepseek_api_key: str
    deepseek_base_url: str
    redis_url: str = "redis://localhost:6380/1"
    redis_ttl_seconds: int = 604800
    host: str = "127.0.0.1"
    port: int = 8000

settings = Settings()
```

替代手动 `os.getenv()` + 散落的环境变量检查。

---

## 15. 项目结构（推荐）

```
ai-server/
├── main.py                      # 开发启动入口
├── app/
│   ├── main.py                  # create_app、lifespan、路由注册
│   ├── config.py
│   ├── chat/
│   │   ├── interface/router.py  # /chat
│   │   ├── interface/dependencies.py
│   │   ├── interface/schemas.py
│   │   └── infrastructure/master.py
│   ├── catalog/interface/router.py
│   ├── auth/interface/          # 登录、权限
│   ├── demo/ws.py               # WebSocket 学习示例
│   └── middleware/
├── demo/main.py                 # 独立最小示例
├── tests/
└── doc/
```

原则：**路由薄、领域/infrastructure 厚、模型清晰、依赖可测**。详见 [doc/README.md](./README.md)。

---

## 16. 测试

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat():
    response = client.get("/chat", params={"query": "你好", "session_id": "test"})
    assert response.status_code == 200
    assert isinstance(response.text, str)
```

| 工具 | 用途 |
|------|------|
| `TestClient` | 同步集成测试 |
| `httpx.AsyncClient` | 异步测试 |
| `pytest` | 测试框架 |

---

## 17. 部署

### 17.1 开发（ai-server 项目）

```bash
cd ai-server
uv sync --extra dev
cp .env.example .env   # 填写 DEEPSEEK_API_KEY 等
uv run python main.py
# 或
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 17.2 生产

```bash
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
# 或 gunicorn + uvicorn worker
uv run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

| 选项 | 说明 |
|------|------|
| `--workers N` | 多进程，利用多核 |
| 反向代理 | Nginx 做 TLS 终结、负载均衡 |
| Docker | 容器化部署 |

---

## 18. 本项目（ai-server）现状与改进方向

### 18.1 当前架构

```
GET /chat?query=...&session_id=...
  → app/chat/interface/router.py
  → Depends(get_master) → app.state.master（lifespan 初始化）
  → Master.chat()（LangChain + Redis）
  → PlainTextResponse

POST /items
  → app/catalog/interface/router.py → Pydantic 校验

WS /ws
  → app/demo/ws.py（echo，尚未接入 LLM）

GET /health
  → app/system/interface/router.py
```

目录结构：`app/main.py` · `app/{auth,chat,catalog,system}/` · `app/demo/` · `config.py`

技术栈：`FastAPI` · `Uvicorn` · `LangChain` · `Redis` · `pydantic-settings` · **uv**

工程命令：

```bash
uv sync --extra dev
uv run python main.py
uv run pytest
```

### 18.2 可改进点（学习计划 Day 3 及延伸）

| 现状 | 建议 | 对应学习日 |
|------|------|------------|
| `/chat` 仅 GET + query | 增加 `POST /chat` + `ChatQuery` Body | Day 1 |
| `ChatQuery` 已定义未用于路由 | 路由参数改用 schema 或 POST Body | Day 1 |
| 无 CORS | 添加 `CORSMiddleware` 便于前端联调 | Day 2 |
| WebSocket 仅 echo | 接入 `Master.chat()` 或流式输出 | Day 3 |
| `/chat` 测试未覆盖 | mock `get_master`，测 422 与正常响应 | Day 3 |
| 同步 `invoke` | 后续 `ainvoke` 或 SSE `/chat/stream` | Day 3 / 延伸 |

---

## 19. 学习计划

三天可执行学习安排（按时段、验收标准、命令速查）已抽离至独立文档：[FastAPI 3 天学习计划](./fastapi-learning-plan.md)。

---

## 20. 常见面试题速记

| 问题 | 要点 |
|------|------|
| FastAPI 为什么快？ | Starlette 异步 + Pydantic 校验用 Rust 核心（v2） |
| 和 Flask 区别？ | 原生 async、Pydantic 内置校验、自动 OpenAPI；Flask 更轻但需扩展 |
| 和 Django 区别？ | FastAPI 专注 API；Django 全栈含 ORM/Admin/模板，更重 |
| 和 Spring Boot 区别？ | Spring 完整 IoC/AOP/事务；FastAPI 轻量 Depends，无 ORM 内置 |
| 和 NestJS 区别？ | 概念最接近（DI、模块化）；NestJS 用 TS + 装饰器，Guard/Pipe 更细分 |
| 什么时候选 FastAPI 不选 Flask？ | 需要 async、自动文档、类型校验的 API 服务（尤其 AI/ML） |
| Depends 原理？ | 解析函数签名，构建依赖图，请求时注入 |
| 422 是什么？ | Pydantic 校验失败 |
| async 路由里能写阻塞代码吗？ | 不能，会阻塞整个事件循环 |
| 如何部署？ | `uv sync` + `uv run uvicorn` / gunicorn+uvicorn worker / Docker |

---

## 21. 相关链接

| 资源 | URL |
|------|-----|
| 3 天学习计划（本项目） | [fastapi-learning-plan.md](./fastapi-learning-plan.md) |
| 框架对比（本项目） | [framework-comparison.md](./framework-comparison.md) |
| FastAPI 官方文档 | https://fastapi.tiangolo.com/ |
| Pydantic v2 | https://docs.pydantic.dev/latest/ |
| Starlette | https://www.starlette.io/ |
| Uvicorn（本项目） | [uvicorn.md](./uvicorn.md) |
| Uvicorn 官方 | https://www.uvicorn.org/ |
| uv（包管理） | https://docs.astral.sh/uv/ |
| 本项目入口 | `../main.py` |

---

## 22. 一句话总结

**FastAPI = 类型注解驱动的 Web 框架 + Pydantic 自动校验 + Starlette 异步底层 + 开箱即用的 OpenAPI 文档**；结合本项目的 AI 场景，重点掌握 **Pydantic 模型、Depends 注入、异步阻塞边界、WebSocket/流式响应** 四项能力。按 [学习计划](./fastapi-learning-plan.md) 推进，三天可从「能跑」到「能维护、能扩展」。
