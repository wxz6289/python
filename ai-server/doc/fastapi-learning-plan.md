# FastAPI 3 天学习计划（ai-server 实战）

结合本仓库 **ai-server** 的 3 天可执行学习路径：每天约 **3～4 小时**，按「阅读理论 → 对照源码 → 动手改造 → 自检验收」推进。

| 文档 | 用途 |
|------|------|
| [fastapi.md](./fastapi.md) | 概念讲解与代码示例（知识库） |
| [framework-comparison.md](./framework-comparison.md) | 框架选型对比（可选阅读） |
| 本文 | 按天、按时段的学习安排与验收标准 |

---

## 学习路径总览

```
Day 1  基础 ──► 能读懂路由、Pydantic、OpenAPI，会用 /docs 调试
         │
Day 2  工程化 ──► 理解 Depends / 中间件 / 异步边界，能维护模块化结构
         │
Day 3  进阶 ──► WebSocket / 流式 / 测试 / 部署，达到可演示交付
```

| 天 | 主题 | 核心技能 | 对照 ai-server |
|----|------|----------|----------------|
| **Day 1** | 基础入门 | 路由 · Pydantic · OpenAPI | `routers/chat.py`、`schemas/`、`/docs` |
| **Day 2** | 工程化 | Depends · 中间件 · 异步 · 结构 | `dependencies.py`、`config.py`、`app/main.py` |
| **Day 3** | 进阶交付 | WebSocket · 流式 · 测试 · 部署 | `routers/ws.py`、`tests/`、uvicorn 生产启动 |

---

## 前置准备（约 30 分钟，不计入三天）

### 环境

```bash
cd ai-server
uv sync --extra dev
cp .env.example .env   # 填写 DEEPSEEK_API_KEY、REDIS_URL 等
uv run python main.py
```

### 验收

- [ ] 浏览器打开 http://127.0.0.1:8000/docs 能看到 Swagger UI
- [ ] `curl http://127.0.0.1:8000/health` 返回 `{"status":"ok"}`
- [ ] Redis 已启动（`/chat` 集成测试需要）

### 建议先浏览的源码（不求全懂）

| 文件 | 关注点 |
|------|--------|
| `app/main.py` | `FastAPI` 实例、`lifespan`、`include_router` |
| `app/routers/chat.py` | `GET /chat`、查询参数、`Depends(get_master)` |
| `app/services/master.py` | LangChain + Redis（业务层，Day 1 可略读） |

---

## 与 fastapi.md 章节对照

| 学习日 | 必读章节 | 选读 |
|--------|----------|------|
| Day 1 | §1 架构、§3 最小应用、§4 路由、§5 Pydantic、§7 请求与响应 | §2 框架对比 |
| Day 2 | §6 Depends、§9 中间件、§10 异步、§12 生命周期、§14 配置、§15 项目结构 | §8 异常处理 |
| Day 3 | §11 WebSocket、§8 异常、§13 安全、§16 测试、§17 部署、§18 现状与改进 | §12 BackgroundTasks |

---

## Day 1：基础入门 — 路由、Pydantic、自动文档

**当日目标**：理解 FastAPI 如何把「类型注解」变成校验与 OpenAPI；能独立新增一个带 Pydantic 校验的接口，并在 `/docs` 中调试。

**预计用时**：3.5～4 小时

---

### 1.1 上午 · 架构与文档（约 2h）

#### 1.1.1 FastAPI 分层（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §1 架构全景](./fastapi.md#1-架构全景) |
| **学习目标** | 说清 FastAPI / Starlette / Pydantic / Uvicorn 各层职责 |
| **概念要点** | ASGI 与 WSGI 区别；请求从 Uvicorn → Starlette → FastAPI 路由的流向 |
| **动手** | 启动服务，依次访问 `/`、`/docs`、`/redoc`、`/openapi.json` |
| **自测** | 用一句话解释：为什么改 Pydantic 模型后 `/docs` 里的 Schema 会变？ |

#### 1.1.2 OpenAPI 与 Swagger UI（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §3 最小应用](./fastapi.md#3-最小应用) |
| **学习目标** | 会在 Swagger UI 里填参数、发请求、看响应与状态码 |
| **动手** | 在 `/docs` 中调用 `GET /chat`，观察 `query`、`session_id` 参数说明 |
| **对照代码** | `app/routers/chat.py`：`response_class=PlainTextResponse` 为何在文档里显示为 text |
| **自测** | `session_id` 不传时默认值是什么？在 OpenAPI 里哪里能看到？ |

#### 1.1.3 路由与 HTTP 方法（30 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §4 路由与 HTTP 方法](./fastapi.md#4-路由与-http-方法) |
| **学习目标** | 区分路径参数、查询参数、请求体；掌握 `@router.get` / `post` |
| **动手** | 用 curl 调用 `/chat` 与 `/items`（POST JSON） |
| **对照代码** | `app/routers/items.py` + `app/schemas/item.py` |
| **练习命令** | 见下方「Day 1 命令速查」 |

---

### 1.2 下午 · Pydantic 与健康检查（约 2h）

#### 1.2.1 Pydantic v2 基础（60 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §5 Pydantic 模型](./fastapi.md#5-pydantic-模型核心) |
| **学习目标** | 会用 `BaseModel`、`Field`；理解 422 校验错误结构 |
| **概念要点** | `min_length`、默认值、`description` 如何进入 OpenAPI |
| **动手 1** | 阅读 `app/schemas/chat.py` 中的 `ChatQuery` |
| **动手 2** | 为 `ChatQuery` 增加 `max_length=2000`，故意传超长 `query`，观察 422 响应体 |
| **动手 3** | 对照 `app/schemas/item.py`，给 `price` 传负数，确认 422 |

#### 1.2.2 响应模型与 HTTPException（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §7 请求与响应](./fastapi.md#7-请求与响应)、§8 异常处理（浏览） |
| **学习目标** | 使用 `response_model`；会用 `HTTPException` 返回 4xx |
| **动手** | 确认 `GET /health` 已存在（`app/main.py`）；若删除后自行加回 |
| **可选进阶** | 新增 `ChatResponse` 模型，另写 `GET /chat/json` 返回 JSON（保留原 `/chat` 纯文本） |

#### 1.2.3 当日综合练习（15 min）

| 项目 | 内容 |
|------|------|
| **任务** | 新增 `POST /chat`，Body 使用 `ChatQuery`，内部仍调用 `master.chat()` |
| **提示** | 路由签名示例：`def chat_post(body: ChatQuery, master: Master = Depends(...))` |
| **注意** | POST + JSON 更适合前端；GET + query 适合简单 curl |

---

### Day 1 命令速查

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# GET /chat（URL 编码中文）
curl -G "http://127.0.0.1:8000/chat" \
  --data-urlencode "query=你好" \
  --data-urlencode "session_id=day1-test"

# POST /items（Pydantic 校验示例）
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"foo","description":"bar","price":9.9}'

# 故意触发 422
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"foo","description":"bar","price":-1}'
```

---

### Day 1 当日产出

| 产出 | 说明 |
|------|------|
| 理解文档 | 能对照 `openapi.json` 找到 `/chat` 的参数定义 |
| 代码（建议） | `POST /chat` 使用 `ChatQuery`；或完善 `schemas/chat.py` 的 `ChatResponse` |
| 笔记 | 记录 422 与 400 在本项目中的区别（items vs chat） |

### Day 1 验收标准

- [ ] 能解释 `@router.get("/chat")` 的 `query`、`session_id` 如何映射到函数参数
- [ ] 能说出 Pydantic 校验失败时的 HTTP 状态码及响应字段结构
- [ ] 能在 `/docs` 中成功调试 `/chat` 与 `/items`
- [ ] （可选）`POST /chat` 在 `/docs` 中可调试且返回正确文本

### Day 1 参考资料

- [FastAPI 官方教程 - 第一步](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI 查询参数](https://fastapi.tiangolo.com/tutorial/query-params/)
- [Pydantic v2 文档](https://docs.pydantic.dev/latest/)

---

## Day 2：依赖注入、中间件、异步、项目结构

**当日目标**：掌握 `Depends` 与 `lifespan` 协作方式；理解 sync/async 路由选型；能按模块定位代码并添加 CORS。

**预计用时**：3.5～4 小时

> **说明**：本仓库已完成模块化拆分（`routers/`、`services/`、`config.py`）。Day 2 以**阅读 + 小步增强**为主，不必从零重构。

---

### 2.1 上午 · 依赖注入（约 2h）

#### 2.1.1 Depends 机制（60 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §6 依赖注入](./fastapi.md#6-依赖注入depends) |
| **学习目标** | 理解 `Depends(get_master)` 的解析时机；yield 依赖用于资源释放 |
| **对照代码** | `app/dependencies.py` → `app/routers/chat.py` |
| **概念要点** | `request.app.state.master` 与 `lifespan` 里初始化的关系 |
| **动手** | 在 `get_master` 内加一行日志，请求 `/chat` 观察是否每次请求都打印 |
| **自测** | `Depends` 与直接 `from app.services import master` 单例有何区别？ |

#### 2.1.2 lifespan 与 app.state（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §12 生命周期](./fastapi.md#12-生命周期与-backgroundtasks) |
| **学习目标** | 启动时创建 `Master`，关闭时释放资源（若需要） |
| **对照代码** | `app/main.py` 中 `create_app` 的 `lifespan` |
| **动手** | 阅读 `tests/conftest.py`（若有）中 `init_master=False` 的测试用法 |
| **延伸** | 思考：测试时如何避免真实调用 DeepSeek API |

#### 2.1.3 配置管理（15 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §14 配置管理](./fastapi.md#14-配置管理) |
| **对照代码** | `app/config.py`：`Settings` + `get_settings()` |
| **动手** | 修改 `.env` 中 `PORT`，确认 `main.py` 读取的是 settings |

---

### 2.2 下午 · 中间件、异步、结构（约 2h）

#### 2.2.1 中间件（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §9 中间件](./fastapi.md#9-中间件) |
| **学习目标** | 中间件执行顺序；CORS 对前端联调的意义 |
| **动手** | 在 `app/main.py` 添加 `CORSMiddleware`（`allow_origins=["*"]` 仅开发用） |
| **动手** | 添加自定义 HTTP 中间件，响应头写入 `X-Process-Time`（请求耗时） |
| **自测** | 用浏览器或 curl 看响应头是否包含 `X-Process-Time` |

#### 2.2.2 异步 vs 同步（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §10 异步 vs 同步](./fastapi.md#10-异步-vs-同步) |
| **学习目标** | 为何 `chat` 用 `def` 而非 `async def`；线程池行为 |
| **对照代码** | `app/routers/chat.py` 注释：阻塞调用在线程池执行 |
| **概念要点** | `master.chat()` 内部 `invoke` 阻塞；`async def` 里直接调用会卡死事件循环 |
| **动手** | 临时把 `chat` 改成 `async def` 并保留同步 `master.chat()`，压测或观察延迟（理解即可，改回 `def`） |
| **延伸阅读** | LangChain `ainvoke`（Day 3 或后续改进） |

#### 2.2.3 项目结构梳理（30 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §15 项目结构](./fastapi.md#15-项目结构推荐)、§18 现状与改进 |
| **学习目标** | 能向他人画出请求链路：Router → Depends → Service |
| **动手** | 画一张 ASCII 图：从 `GET /chat` 到 Redis 的调用链 |
| **验收** | 不看文档也能说出 `schemas/`、`routers/`、`services/` 各放什么 |

---

### Day 2 当日产出

| 产出 | 说明 |
|------|------|
| 代码 | `CORSMiddleware` + `X-Process-Time` 中间件 |
| 文档 | 一张 `/chat` 请求链路图（可写在个人笔记里） |
| 理解 | 能解释 `def chat` + 阻塞 `invoke` 的设计原因 |

### Day 2 验收标准

- [ ] 能说明 `Depends(get_master)` 如何拿到 `Master` 实例
- [ ] 能解释为什么 sync 阻塞代码不应写在 `async def` 路由里
- [ ] 能独立找到 chat、items、ws 三个路由文件并说明职责
- [ ] CORS 已配置，前端（或 curl -H Origin）可跨域访问（开发环境）

### Day 2 参考资料

- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [FastAPI Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [FastAPI Lifespan](https://fastapi.tiangolo.com/advanced/events/)

---

## Day 3：WebSocket、流式响应、测试、部署

**当日目标**：完成可演示的 WebSocket 对话或流式输出；补齐测试；能用 uv 命令部署运行。

**预计用时**：3.5～4 小时

---

### 3.1 上午 · 实时通信（约 2h）

#### 3.1.1 WebSocket 基础（60 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §11 WebSocket](./fastapi.md#11-websocket) |
| **学习目标** | `accept` / `receive_text` / `send_text` / `WebSocketDisconnect` |
| **对照代码** | `app/routers/ws.py`：当前为 echo |
| **动手** | 用浏览器控制台或 `websocat` 连接 `ws://127.0.0.1:8000/ws` 发消息 |
| **协议约定** | 定义 JSON 消息格式，例如 `{"query":"...","session_id":"ws-001"}` |

#### 3.1.2 WebSocket 接入 LLM（60 min）

| 项目 | 内容 |
|------|------|
| **学习目标** | 在 WS  handler 中 `Depends(get_master)` 或从 `websocket.app.state` 取 Master |
| **动手** | 改造 `/ws`：收到 JSON 后调用 `master.chat()`，将回复发回客户端 |
| **注意** | WS 路由应为 `async def`；`master.chat()` 仍为阻塞，考虑 `asyncio.to_thread` |
| **错误处理** | 捕获异常，向客户端发送 `{"error":"..."}` 而非直接断连 |

**参考实现思路**：

```python
@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    master: Master = websocket.app.state.master
    try:
        while True:
            raw = await websocket.receive_text()
            # 解析 JSON，调用 master.chat，send 回复
    except WebSocketDisconnect:
        pass
```

---

### 3.2 下午 · 流式、测试、部署（约 2h）

#### 3.2.1 流式响应（可选，45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §7](./fastapi.md#7-请求与响应) 中 StreamingResponse 相关段落 |
| **学习目标** | SSE 或分块返回适合 LLM token 流 |
| **动手** | 新增 `GET /chat/stream`（Generator + `StreamingResponse`） |
| **延伸** | 对接 LangChain `.stream()` 而非一次性 `invoke` |

#### 3.2.2 异常与全局处理（30 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §8 异常处理](./fastapi.md#8-异常处理) |
| **动手** | 注册 `@app.exception_handler(Exception)` 返回统一 JSON 错误体 |
| **注意** | 生产环境避免把堆栈直接返回给客户端 |

#### 3.2.3 测试（45 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §16 测试](./fastapi.md#16-测试) |
| **对照代码** | `tests/test_api.py`、`tests/conftest.py`（若存在） |
| **学习目标** | `TestClient` 夹具、`init_master=False` 避免真实 LLM 调用 |
| **动手 1** | 为 `GET /chat` 缺少 `query` 时断言 `422` |
| **动手 2** | mock `get_master` 返回假 Master，断言返回固定字符串 |
| **运行** | `uv run pytest -v` |

**测试示例**：

```python
def test_chat_missing_query_returns_422(client):
    response = client.get("/chat")
    assert response.status_code == 422


def test_chat_with_mock_master(client, monkeypatch):
    class FakeMaster:
        def chat(self, query: str, session_id: str = "default") -> str:
            return f"echo:{query}"

    # 通过 dependency_overrides 或 patch get_master 注入 FakeMaster
    ...
```

#### 3.2.4 部署与演示（30 min）

| 项目 | 内容 |
|------|------|
| **阅读** | [fastapi.md §17 部署](./fastapi.md#17-部署) |
| **动手** | `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2` |
| **演示清单** | `/docs` 调 `/health`、`/items`；curl `/chat`；WS 一轮对话；`pytest` 全绿 |

---

### Day 3 当日产出

| 产出 | 说明 |
|------|------|
| 代码 | `/ws` 能完成至少一轮 AI 对话（或 mock 对话） |
| 测试 | 新增 ≥2 个用例（422 + mock master） |
| 可选 | `GET /chat/stream` 流式接口 |

### Day 3 验收标准

- [ ] WebSocket 能完成一轮对话（真实 API 或 mock）
- [ ] `uv run pytest` 至少通过原有 + 新增用例
- [ ] 能用 `uv run python main.py` 或 uvicorn 稳定启动
- [ ] 能向他人演示：REST +（WS 或流式）+ 测试通过

### Day 3 参考资料

- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Starlette StreamingResponse](https://www.starlette.io/responses/#streamingresponse)

---

## 三天总验收清单

完成以下全部项，即达到本计划「结业」标准：

| # | 能力 | 验证方式 |
|---|------|----------|
| 1 | 阅读 OpenAPI / Swagger | 在 `/docs` 调试主要接口 |
| 2 | Pydantic 校验 | 能触发并读懂 422 响应 |
| 3 | 依赖注入 | 能解释 `get_master` 与 `lifespan` |
| 4 | 异步边界 | 能说明 `def chat` vs `async def` 选型 |
| 5 | 模块化 | 能定位 routers / services / schemas |
| 6 | 实时通信 | WS 或流式至少完成一种 |
| 7 | 测试 | `pytest` 通过且含 chat 相关用例 |
| 8 | 部署 | uvicorn 多 worker 或文档中的生产命令能跑通 |

---

## 延伸学习（第 4～7 天，可选）

| 天 | 主题 | 建议任务 |
|----|------|----------|
| Day 4 | 安全 | API Key Header、`OAuth2PasswordBearer` 保护 `/chat` |
| Day 5 | 可观测 | 结构化日志、请求 ID、Prometheus metrics |
| Day 6 | 容器化 | Dockerfile + docker-compose（app + redis） |
| Day 7 | 性能 | `ainvoke`、连接池、Redis 会话 key 设计优化 |

---

## 常见卡点与排查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 422 Unprocessable Entity | 缺少必填参数或 Pydantic 校验失败 | 看响应体 `detail` 字段 |
| `/chat` 500 | `DEEPSEEK_API_KEY` 或 Redis 未配置 | 检查 `.env` 与服务日志 |
| `async def` 路由卡住 | 路由内直接调用阻塞 `invoke` | 改 `def` 路由或 `to_thread` / `ainvoke` |
| pytest 调用了真实 API | 未 mock `get_master` / 未 `init_master=False` | 看 `tests/conftest.py` |
| WS 连接立即断开 | 未 `await websocket.accept()` | 对照 `ws.py` |

---

## 相关链接

| 资源 | URL |
|------|-----|
| FastAPI 核心文档（本项目） | [fastapi.md](./fastapi.md) |
| 框架对比 | [framework-comparison.md](./framework-comparison.md) |
| 项目 README | [../README.md](../README.md) |
| FastAPI 官方 | https://fastapi.tiangolo.com/ |
