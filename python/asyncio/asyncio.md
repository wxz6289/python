# asyncio 协程与异步 I/O

`asyncio` 是 Python 3.4 引入的标准库，用于编写**基于 `async`/`await` 语法的异步并发代码**。它通过单线程事件循环（Event Loop）实现高并发，特别适合 **I/O 密集型**任务（网络请求、文件读写、数据库查询等）。自 Python 3.7 引入 `asyncio.run()` 后，异步编程体验已非常成熟。

更多示例见 [`asyncio/`](./) 目录下的脚本与 Notebook。

## 目录

1. [核心概念](#核心概念)
2. [工作原理](#工作原理)
3. [基础示例](#基础示例)
4. [适用场景与局限](#适用场景与局限)
5. [最佳实践与避坑](#最佳实践与避坑)
6. [生态与框架](#生态与框架)

---

## 核心概念

| 概念 | 说明 |
|------|------|
| **事件循环 (Event Loop)** | 异步程序的调度中枢，负责注册、唤醒和切换协程，监听 I/O 事件 |
| **协程 (Coroutine)** | 用 `async def` 定义的函数，执行时返回协程对象，可通过 `await` 挂起/恢复 |
| **任务 (Task)** | 将协程包装成可调度对象，支持取消、获取状态/结果 |
| **Future** | 表示尚未完成的计算结果，通常供底层 API 使用 |
| `async` / `await` | 语法糖，让异步代码写法接近同步，底层仍是非阻塞协作式调度 |

---

## 工作原理

`asyncio` 采用**协作式多任务**模型：

1. 事件循环启动后，按注册顺序执行协程。
2. 当协程遇到 `await`（如网络 I/O、`asyncio.sleep()`）时，**主动让出控制权**。
3. 事件循环立即切换到其他就绪的协程继续执行。
4. I/O 完成后，事件循环将原协程重新加入就绪队列，恢复执行。

整个过程在**单线程**中完成，无线程切换开销，无锁竞争问题，内存占用极低。

---

## 基础示例

```python
import asyncio

async def fetch_data(delay: int) -> str:
    print(f"开始请求，模拟等待 {delay}s...")
    await asyncio.sleep(delay)
    print(f"请求完成，耗时 {delay}s")
    return f"data_{delay}"

async def main():
    results = await asyncio.gather(
        fetch_data(2),
        fetch_data(1),
        fetch_data(3),
    )
    print("所有结果:", results)

asyncio.run(main())
```

`gather` 按传入顺序返回结果：`['data_2', 'data_1', 'data_3']`，与完成先后无关。

---

## 适用场景与局限

| 适合 | 不适合 |
|------|--------|
| 高并发网络爬虫 / API 网关 | CPU 密集型计算（图像处理、科学计算） |
| WebSocket / 实时消息推送 | 调用阻塞型第三方库（如 `requests`、`time.sleep()`） |
| 批量数据库/缓存查询 | 需要复杂同步原语（重入锁、条件变量）的场景 |
| 微服务异步编排 | |

CPU 密集型任务建议使用 `multiprocessing` 或 `concurrent.futures.ProcessPoolExecutor`。

---

## 最佳实践与避坑

1. **严禁在异步代码中直接调用阻塞函数**，会卡死整个事件循环。应使用 `aiohttp`/`httpx`（替代 `requests`）、`asyncpg`（替代 `psycopg2`）、`aiofiles`（替代内置 `open`）。
2. **包装阻塞代码**：
   ```python
   result = await asyncio.to_thread(time.sleep, 2)
   ```
3. **合理管理任务生命周期**：使用 `asyncio.create_task()` 启动后台任务；Python 3.11+ 推荐 `asyncio.TaskGroup` 自动管理并发与异常。
4. **调试**：设置 `PYTHONASYNCIODEBUG=1` 可输出协程调度详情。
5. **异常处理**：`asyncio.gather(..., return_exceptions=True)` 可收集异常而非直接中断。

异步上下文管理器配合 `async with` 使用，详见 [11-context-managers.md](../docs/11-context-managers.md)。

---

## 生态与框架

| 类别 | 代表 |
|------|------|
| Web 框架 | FastAPI、Sanic、Starlette |
| HTTP 客户端 | httpx、aiohttp |
| 数据库 | asyncpg（PostgreSQL）、motor（MongoDB）、aiosqlite |
| 任务队列 | ARQ、Dramatiq |

本仓库 [ai-server](../ai-server/) 基于 FastAPI，是 asyncio 的典型应用场景。
