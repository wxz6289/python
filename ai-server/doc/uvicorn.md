# Uvicorn 核心内容与最佳实践

本文总结 **Uvicorn**（ASGI HTTP/WebSocket 服务器）的核心概念、常用配置与生产部署实践，并结合本仓库 **ai-server**（FastAPI + LangChain + Redis）给出可直接套用的命令与注意点。

| 相关文档 | 说明 |
|----------|------|
| [fastapi.md](./fastapi.md) | FastAPI 概念与 §17 部署概览 |
| [fastapi-learning-plan.md](./fastapi-learning-plan.md) | Day 3 部署实战 |
| [README.md](../README.md) | 项目快速启动 |

---

## 1. Uvicorn 是什么

**Uvicorn** 是一个轻量、高性能的 **ASGI** 服务器，负责：

- 监听 TCP 端口，解析 HTTP/1.1（及 WebSocket 升级）
- 管理事件循环，把请求交给 ASGI 应用（如 FastAPI）
- 在开发模式下提供 **热重载**（`--reload`）

在本项目中，技术栈关系为：

```
客户端
  │
  ▼
Uvicorn（ASGI Server）     ← 本文重点
  │
  ▼
Starlette（ASGI 工具包）
  │
  ▼
FastAPI（路由、校验、Depends）
  │
  ▼
业务代码（Master / LangChain / Redis）
```

| 角色 | 组件 | 职责 |
|------|------|------|
| 应用协议 | **ASGI** | Python 异步 Web 标准（类似 WSGI 的 async 版） |
| 框架 | FastAPI / Starlette | 实现 `async def app(scope, receive, send)` |
| 服务器 | **Uvicorn** | 运行 ASGI 应用、处理连接与并发 |

> **记忆**：FastAPI 不写 socket；Uvicorn 不处理业务路由。二者通过 ASGI 接口衔接。

---

## 2. ASGI 与 WSGI 简要对比

| 维度 | WSGI（如 gunicorn sync） | ASGI（Uvicorn） |
|------|--------------------------|-----------------|
| 调用模型 | 同步，一请求一线程/进程常见 | 原生 `async/await`，单线程事件循环处理大量 I/O |
| WebSocket | 需额外方案（如 gevent、独立服务） | 原生支持 |
| HTTP/2 | 需反向代理或专门服务器 | 通常由 Nginx/Caddy 终结 TLS 与 HTTP/2 |
| 典型框架 | Flask、Django（传统） | FastAPI、Starlette、Django 4+ ASGI |

**ai-server 为何用 Uvicorn**：FastAPI 基于 ASGI；`/chat` 等待 LLM I/O、`/ws` WebSocket 都更适合异步服务器；同步阻塞路由（`def chat`）由 Starlette 放入线程池，仍由 Uvicorn 的事件循环调度。

---

## 3. 安装与可选加速

本项目在 `pyproject.toml` 中声明：

```toml
"uvicorn>=0.46.0",
```

安装依赖：

```bash
uv sync --extra dev
```

### 3.1 `uvicorn[standard]`（推荐生产）

默认 `uvicorn` 包可运行；安装 **standard** 额外依赖可显著提升性能：

```bash
uv add "uvicorn[standard]"
```

| 组件 | 作用 |
|------|------|
| `uvloop` | 替代 asyncio 默认事件循环，降低 I/O 延迟 |
| `httptools` | 更快的 HTTP 解析 |
| `watchfiles` | 开发时 `--reload` 的文件监视 |

未装 `[standard]` 时 Uvicorn 会回退到纯 Python 实现，功能正常但吞吐更低。

---

## 4. 启动方式

### 4.1 命令行（最常用）

```bash
# 开发：热重载
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 生产：多 worker（不要与 --reload 同时使用）
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**应用路径格式**：`模块路径:属性名`

- `app.main:app` → 导入 `app.main` 模块中的 `app` 对象
- 本仓库 `app` 在 `app/main.py` 的 `create_app()` 末尾导出：`app = create_app()`

### 4.2 项目入口 `main.py`（开发）

```python
uvicorn.run(
    "app.main:app",   # 字符串形式，reload 才能正确重载子模块
    host=settings.host,
    port=settings.port,
    reload=True,
)
```

```bash
uv run python main.py
```

| 方式 | 适用场景 |
|------|----------|
| `uvicorn app.main:app ...` | 与文档、CI、Docker CMD 一致，推荐 |
| `python main.py` | 本地开发，host/port 读 `.env` 的 `Settings` |

### 4.3 代码内传入 app 对象（不推荐配合 reload）

```python
from app.main import app
uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)  # reload 可能无法监视包内文件变更
```

**最佳实践**：需要 `--reload` 时始终使用 **`"app.main:app"` 字符串**。

---

## 5. 核心配置项

### 5.1 网络与进程

| 参数 | CLI | 说明 | 开发 | 生产 |
|------|-----|------|------|------|
| 监听地址 | `--host` | `127.0.0.1` 仅本机；`0.0.0.0` 对所有网卡 | `127.0.0.1` | `0.0.0.0`（容器/VM 内） |
| 端口 | `--port` | 默认 `8000` | 与 `.env` 的 `PORT` 一致 | 常由 Nginx 反代，容器内 8000 |
| Worker 数 | `--workers` | 多进程，每进程独立事件循环 | **不用** | `2 × CPU + 1` 为起点 |
| 热重载 | `--reload` | 代码变更自动重启 | ✅ | ❌ 禁止 |

```bash
# 查看 CPU 核数（估算 worker）
python -c "import os; print(os.cpu_count())"
```

### 5.2 日志

| 参数 | 说明 |
|------|------|
| `--log-level debug\|info\|warning\|error` | 访问日志与错误级别 |
| `--access-log` / `--no-access-log` | 是否打印每条 HTTP 访问 |
| `--log-config <path>` | 自定义 logging 配置文件（JSON/YAML） |

生产建议：`info` 或 `warning`，访问日志可交给 Nginx；需要审计时再开 Uvicorn access log。

### 5.3 超时与连接

| 参数 | 说明 | ai-server 注意 |
|------|------|----------------|
| `--timeout-keep-alive` | 保持连接空闲超时（秒） | 默认通常够用 |
| `--limit-concurrency` | 最大并发连接/任务数 | LLM 慢请求多时防止拖垮内存 |
| `--backlog` | OS 监听队列长度 | 高并发入口前可调 |

`/chat` 调用 DeepSeek 可能 **数十秒**，应在 Nginx 侧加大 `proxy_read_timeout`，而非仅依赖 Uvicorn 默认。

### 5.4 SSL（可选）

```bash
uv run uvicorn app.main:app \
  --host 0.0.0.0 --port 8443 \
  --ssl-keyfile=key.pem --ssl-certfile=cert.pem
```

**最佳实践**：TLS 在 **Nginx / Caddy / 云 LB** 终结，Uvicorn 在内网跑 HTTP，证书与续期更简单。

### 5.5 环境变量

Uvicorn 也支持 `UVICORN_*` 环境变量（与 CLI 等价），例如：

```bash
export UVICORN_HOST=0.0.0.0
export UVICORN_PORT=8000
export UVICORN_WORKERS=4
uv run uvicorn app.main:app
```

---

## 6. 开发环境最佳实践

### 6.1 推荐命令

```bash
cd ai-server
uv sync --extra dev
cp .env.example .env
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

或使用项目入口（从 `Settings` 读 host/port）：

```bash
uv run python main.py
```

### 6.2 开发时应做的

| 实践 | 原因 |
|------|------|
| 使用 `--reload` | 改路由/依赖后自动重启 |
| `host=127.0.0.1` | 避免开发机暴露到局域网 |
| 单 worker（默认） | 日志、断点、内存状态简单 |
| 用 `uv run` | 保证使用项目 `.venv` 中的 Uvicorn 版本 |

### 6.3 开发时不要做的

| 反模式 | 原因 |
|--------|------|
| 生产环境开 `--reload` | 监视文件开销大，且可能加载未保存的中间状态 |
| `--workers` + `--reload` | **互斥**，Uvicorn 会报错或行为异常 |
| 在 `async def` 路由里直接跑阻塞 `invoke` | 卡住**整个** worker 的事件循环（本项目 `/chat` 已用 `def` 路由规避） |

---

## 7. 生产环境最佳实践

### 7.1 部署形态选型

```
                    ┌─────────────────┐
                    │ Nginx / Caddy   │  TLS、HTTP/2、限流、静态资源
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   Uvicorn :8000      Uvicorn :8000       ...（多 worker 同机）
   （单进程多 worker 或多机 replicas）
```

| 方案 | 命令/配置 | 适用 |
|------|-----------|------|
| **Uvicorn 多 worker** | `--workers 4` | 中小型 API、运维简单 |
| **Gunicorn + UvicornWorker** | 见 §7.3 | 需要 Gunicorn 进程管理、平滑重启 |
| **Kubernetes / Docker** | 每 Pod 1 worker，靠副本数扩展 | 云原生、水平扩展 |

### 7.2 推荐生产命令（ai-server）

```bash
uv sync
uv run uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info \
  --no-access-log
```

Worker 数量起点：

```text
workers ≈ (2 × CPU 核心数) + 1
```

再根据 **内存**（每个 worker 一份 `Master`/连接池）与 **LLM 延迟** 压测调整。CPU 密集应减少 worker；I/O 密集（本项目的 LLM 等待）可适当增加，但注意 Redis/API 连接总数。

### 7.3 Gunicorn + Uvicorn Worker

```bash
uv add gunicorn
uv run gunicorn app.main:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  -b 0.0.0.0:8000 \
  --timeout 120
```

| 优点 | 说明 |
|------|------|
| 成熟进程管理 | 优雅重启、信号处理 |
| 与 Uvicorn 相同 ASGI 栈 | 仍跑 FastAPI，无框架差异 |

`--timeout` 应大于最长 LLM 请求时间，否则 worker 会被强杀。

### 7.4 生产检查清单

- [ ] 关闭 `--reload`
- [ ] 使用 `0.0.0.0` 仅在容器/内网；公网前必有反向代理
- [ ] 安装 `uvicorn[standard]`（或镜像内装好 uvloop/httptools）
- [ ] Nginx `proxy_read_timeout` / `proxy_send_timeout` 适配 LLM 延迟
- [ ] WebSocket 多 worker 时配置 **sticky session**（见 §8.3）
- [ ] 健康检查走 `GET /health`，负载均衡探活
- [ ] 日志：应用结构化日志 + 集中收集（不依赖默认 access log 长期存储）

---

## 8. 与 FastAPI / ai-server 的协作要点

### 8.1 生命周期 `lifespan` 与多 Worker

本仓库 `app/main.py`：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.master = Master(get_settings()) if init_master else None
    yield
```

| 模式 | 行为 |
|------|------|
| 单 worker | 全局一个 `Master` 实例在 `app.state` |
| `--workers N` | **每个进程** 各执行一次 `lifespan`，各有独立 `Master` |

这是预期行为：进程间不共享内存。会话数据在 **Redis**，多 worker 仍可共享 `session_id`；勿依赖进程内全局变量做跨请求状态。

### 8.2 同步路由 `def` 与线程池

`app/routers/chat.py` 使用同步 `def chat` + 阻塞 `master.chat()`：

- Starlette 将同步路由放到 **线程池** 执行
- Uvicorn 事件循环可继续处理其他连接

**最佳实践**：阻塞第三方 SDK（LangChain `invoke`）用 **`def` 路由** 或改 `ainvoke` / `asyncio.to_thread`，不要放在 `async def` 里直接调用。

### 8.3 WebSocket 与多 Worker

`app/routers/ws.py` 的 WebSocket 连接会 **粘在某个 worker 进程** 上。

| 部署 | 建议 |
|------|------|
| `--workers 1` | 开发/演示最简单 |
| 多 worker + Nginx | `ip_hash` 或 `hash $remote_addr` 保持同源 IP 粘滞 |
| 大规模 | 独立 WS 服务或消息总线，避免长连接占满通用 API worker |

### 8.4 配置与启动参数统一

| 来源 | 用途 |
|------|------|
| `.env` → `Settings.host` / `port` | `python main.py` |
| CLI `--host` / `--port` | 直接 `uvicorn` 时显式传参，**覆盖** 未读 Settings 的启动方式 |

**最佳实践**：Docker/K8s 用环境变量 + 统一启动脚本，避免文档写 8000 而实际 `.env` 为其他端口。

---

## 9. 性能调优要点

| 手段 | 说明 |
|------|------|
| `uvicorn[standard]` | uvloop + httptools |
| 合理 `--workers` | 过多导致内存翻倍、上下文切换增加 |
| `--limit-concurrency` | 防止慢 LLM 请求堆积耗尽资源 |
| 反向代理缓冲 | Nginx 对慢客户端与上游解耦 |
| 应用层异步化 | 长远用 `ainvoke`、流式响应减少线程池占用 |

**不宜指望**：仅靠加 Uvicorn worker 解决 **LLM 本身慢**；瓶颈常在 API 延迟与模型推理，应做流式、缓存、队列。

---

## 10. Docker 示例

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

Compose 中 Redis、环境变量与 `DEEPSEEK_API_KEY` 需一并注入；健康检查：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://127.0.0.1:8000/health"]
  interval: 30s
  timeout: 5s
  retries: 3
```

---

## 11. 常见问题排查

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| `Address already in use` | 端口被占用 | 换 `--port` 或 `lsof -i :8000` 杀进程 |
| 改代码不生效 | 未开 reload 或传了 app 对象而非字符串 | `--reload` + `app.main:app` |
| 生产 CPU 低但响应慢 | worker 少 + LLM I/O 等待 | 正常；优化上游或加流式 |
| 偶发 502（Nginx） | 上游超时 | 增大 `proxy_read_timeout` |
| WebSocket 经常断 | 多 worker 无粘滞 | Nginx `ip_hash` 或减 worker |
| 内存随时间涨 | 每 worker 缓存/连接泄漏 | 查 `Master`/Redis 客户端生命周期 |
| `Error loading ASGI app` | 模块路径错误 | 确认在项目根执行且为 `app.main:app` |

---

## 12. 最佳实践速查表

| 场景 | 推荐 |
|------|------|
| 本地开发 | `uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000` |
| 本地（读 .env 端口） | `uv run python main.py` |
| 生产（简单） | `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers N`，前置 Nginx |
| 生产（进程管理） | `gunicorn -k uvicorn.workers.UvicornWorker -w N` |
| 依赖 | 生产安装 `uvicorn[standard]` |
| 应用路径 | 始终 `app.main:app`（与仓库结构一致） |
| 热重载 | 仅开发；字符串导入 |
| TLS | 交给反向代理 |
| LLM 长耗时 | 调 Nginx/网关超时；应用层流式 |
| 状态 | 会话放 Redis，不依赖单进程内存 |

---

## 13. 相关链接

| 资源 | URL |
|------|-----|
| Uvicorn 官方文档 | <https://www.uvicorn.org/> |
| Settings 参考 | <https://www.uvicorn.org/settings/> |
| Deployment | <https://www.uvicorn.org/deployment/> |
| ASGI 规范 | <https://asgi.readthedocs.io/> |
| FastAPI 部署 | <https://fastapi.tiangolo.com/deployment/> |
| 本项目 FastAPI 笔记 | [fastapi.md](./fastapi.md) |

---

## 14. 一句话总结

**Uvicorn = 运行 FastAPI 的 ASGI 服务器**：开发用 `--reload` + 单 worker；生产用多 worker（或 Gunicorn 管理）+ `uvicorn[standard]` + 反向代理，并结合 ai-server 的 **阻塞 LLM 调用、Redis 会话、WebSocket** 特性配置超时与粘滞策略。
