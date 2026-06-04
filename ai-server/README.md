# ai-server

基于 **FastAPI** 的 AI 对话服务：接入 **DeepSeek**（LangChain），使用 **Redis** 持久化多轮会话，并提供 WebSocket 示例接口。

依赖与运行统一使用 **[uv](https://docs.astral.sh/uv/)** 管理。

## 技术栈

| 类别 | 选型 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| LLM | LangChain + DeepSeek Chat |
| 会话存储 | Redis（`RedisChatMessageHistory`） |
| 配置 | pydantic-settings + `.env` |
| 校验 | Pydantic v2 |
| 包管理 | uv + `pyproject.toml` + `uv.lock` |

## 项目结构

```text
ai-server/
├── app/
│   ├── main.py                 # FastAPI 工厂、lifespan、路由与中间件注册
│   ├── config.py               # Settings（环境变量）
│   ├── handlers.py             # 全局异常处理
│   ├── auth/                   # 认证与 RBAC/ACL（DDD 分层）
│   ├── chat/                   # 命理对话（LangChain + Redis）
│   ├── catalog/                # 商品示例 API
│   ├── system/                 # 健康检查等系统接口
│   ├── db/                     # SQLAlchemy + Tortoise ORM、迁移种子
│   ├── demo/                   # FastAPI 学习示例路由（挂载到主应用）
│   ├── middleware/             # 统一响应、清理等中间件
│   ├── schemas/                # 通用响应与 OpenAPI 定制
│   └── infra/                  # 组合根等基础设施
├── demo/
│   └── main.py                 # 独立最小 FastAPI 示例（不依赖 app 包）
├── doc/                        # 学习与架构笔记（FastAPI、DDD、CQRS、ORM 等）
├── migrations/                 # Aerich / Tortoise 迁移
├── tests/
├── main.py                     # 开发启动入口（uvicorn --reload）
├── docker-compose.yml          # 本地 MySQL + Redis
├── .env.example
├── pyproject.toml
├── uv.lock
└── ai-server.code-workspace    # Cursor/VS Code 子项目工作区
```

## 快速开始

### 1. 环境要求

- [uv](https://docs.astral.sh/uv/getting-started/installation/)（推荐）
- Python 3.12+（uv 会自动按 `.python-version` 安装）
- Redis（默认 `localhost:6380`，与 `REDIS_URL` 一致）
- DeepSeek API Key

安装 uv（若尚未安装）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装依赖

在项目根目录执行：

```bash
cd ai-server
uv sync --extra dev
```

说明：

| 命令 | 作用 |
|------|------|
| `uv sync` | 按 `uv.lock` 安装生产依赖，创建/更新 `.venv` |
| `uv sync --extra dev` | 同时安装 `pytest`、`httpx` 等开发依赖 |
| `uv lock` | 根据 `pyproject.toml` 更新锁文件 |
| `uv add <pkg>` | 添加生产依赖并更新 lock |
| `uv add --dev <pkg>` | 添加开发依赖 |

> 无需手动 `pip install` 或 `source .venv/bin/activate`；使用 `uv run` 会自动使用项目虚拟环境。

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少填写：

| 变量 | 必填 | 说明 |
|------|------|------|
| `DEEPSEEK_API_KEY` | ✅ | DeepSeek API 密钥 |
| `DEEPSEEK_BASE_URL` | ✅ | 如 `https://api.deepseek.com/v1` |
| `REDIS_URL` | | 默认 `redis://localhost:6380/1` |
| `REDIS_TTL_SECONDS` | | 会话 TTL，默认 7 天 |
| `HOST` | | 默认 `127.0.0.1` |
| `PORT` | | 默认 `8000` |

### 4. 启动服务

```bash
uv run python main.py
uv run main.py
```

或直接：

```bash
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

生产环境（多 worker）：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

启动后访问：

| 地址 | 说明 |
|------|------|
| <http://127.0.0.1:8000/docs> | Swagger UI |
| <http://127.0.0.1:8000/redoc> | ReDoc |
| <http://127.0.0.1:8000/health> | 健康检查 |

## 常用 uv 命令

```bash
# 安装/同步依赖
uv sync --extra dev

# 开发启动（热重载）
uv run python main.py

# 运行测试
uv run pytest

# 添加新依赖
uv add httpx
uv add --dev ruff

# 更新锁文件
uv lock --upgrade
```

## API 说明

### `GET /health`

健康检查，无需鉴权。

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

### `GET /chat`

命理对话接口，返回 **纯文本**。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `query` | string | ✅ | 用户问题 |
| `session_id` | string | | 会话 ID，默认 `default`；相同 ID 共享 Redis 多轮记忆 |

```bash
curl -G "http://127.0.0.1:8000/chat" \
  --data-urlencode "query=你好，请介绍一下自己" \
  --data-urlencode "session_id=user-001"
```

### `POST /items`

Pydantic 校验示例（FastAPI 学习用）。

```bash
curl -X POST http://127.0.0.1:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"foo","description":"bar","price":9.9}'
```

### `WS /ws`

WebSocket 回显示例，发送文本后返回 `Message received: ...`。

```javascript
const ws = new WebSocket("ws://127.0.0.1:8000/ws");
ws.onopen = () => ws.send("hello");
ws.onmessage = (e) => console.log(e.data);
```

## 架构说明

```
Client
  │
  ├─ GET /chat ──► chat router ──► Master.chat()
  │                                    │
  │                                    ├─ LangChain Chain
  │                                    └─ Redis 会话历史
  │
  ├─ POST /items ──► items router ──► Pydantic 校验
  │
  └─ WS /ws ──► ws router ──► echo
```

- **`Master`**：封装 LangChain Prompt + DeepSeek + Redis 历史
- **`lifespan`**：应用启动时初始化 `Master`，挂载到 `app.state`
- **`Depends(get_master)`**：路由层注入服务实例
- **`/chat` 使用同步 `def`**：LangChain `invoke` 为阻塞调用，FastAPI 自动放入线程池，避免阻塞事件循环

## 测试

```bash
uv sync --extra dev
uv run pytest
```

当前覆盖：`/health`、`/items` 正常与校验失败场景。`/chat` 需真实 API Key 与 Redis，建议作为集成测试手动验证。

## 常见问题

**Q: IDE 提示找不到 `app` 或 `fastapi` 模块？**
A: 1) 执行 `uv sync --extra dev`；2) 选择解释器为 `ai-server/.venv/bin/python`（命令面板 → `Python: Select Interpreter`）；3) 推荐用 Cursor 打开 `ai-server/ai-server.code-workspace` 以获得独立工作区配置。

**Q: 报 `No module named 'pydantic_settings'`？**
A: 执行 `uv sync` 或 `uv sync --extra dev`，不要直接用系统 Python 运行。

**Q: 启动报 `DEEPSEEK_API_KEY` 缺失？**
A: 复制 `.env.example` 为 `.env` 并填写密钥。

**Q: Redis 连接失败？**
A: 确认 Redis 已启动且 `REDIS_URL` 正确（默认端口 `6380`）。

**Q: `/chat` 响应慢？**
A: LLM 调用本身耗时；后续可改为 WebSocket 流式输出（见 [doc/fastapi-learning-plan.md](./doc/fastapi-learning-plan.md) Day 3）。

**Q: IDE 提示找不到包？**
A: 将 Python 解释器设为 `ai-server/.venv/bin/python`（由 `uv sync` 创建）。

## 相关文档

- [FastAPI 核心内容](./doc/fastapi.md)
- [FastAPI 3 天学习计划](./doc/fastapi-learning-plan.md)
- [框架对比：FastAPI vs Flask / Django / Spring / NestJS](./doc/framework-comparison.md)
- [Uvicorn 核心内容与最佳实践](./doc/uvicorn.md)
- [领域驱动设计](./doc/ddd.md)
- [CQRS 命令查询分离](./doc/cqrs.md)
- [依赖注入](./doc/dependon.md)
- [ORM 与 Aerich](./doc/orm.md) · [Aerich 迁移](./doc/aerich.md)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [uv 官方文档](https://docs.astral.sh/uv/)

## 后续改进

- [ ] WebSocket 接入流式 LLM 输出
- [ ] `/chat` 改用 POST + Pydantic Body
- [ ] 添加 CORS 中间件（对接前端）
- [ ] LangChain 异步 `ainvoke` 或 SSE 流式接口

## License

MIT
