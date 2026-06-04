# FastAPI 依赖注入（Dependency Injection）总结与最佳实践

FastAPI 的依赖注入系统由 **`Depends()`** 驱动：在路由函数签名中声明「需要什么」，框架在每次请求时自动解析、执行并注入结果。它把**鉴权、数据库会话、参数解析、业务服务组装**等横切逻辑从路由里抽离出来，使路由保持薄、逻辑可复用、可测试。

相关文档：[FastAPI 核心内容](./fastapi.md) · 本仓库示例路由 [`app/demo/depend.py`](../app/demo/depend.py)

---

## 1. 依赖注入解决什么问题

```
┌─────────────────────────────────────────────────────────────┐
│                      路由函数（薄）                           │
│   async def chat(..., user=Depends(get_current_user))       │
├─────────────────────────────────────────────────────────────┤
│                   FastAPI 依赖解析器                          │
│   解析签名 → 构建依赖图 → 按序执行 → 注入返回值               │
├─────────────────────────────────────────────────────────────┤
│                   依赖函数 / 类（可复用）                     │
│   get_db_session · get_current_user · get_auth_service      │
└─────────────────────────────────────────────────────────────┘
```

| 能力 | 说明 |
|------|------|
| **复用** | 同一套鉴权、DB 会话逻辑供多个路由共享 |
| **组合** | 依赖可以依赖其他依赖，形成自动解析的依赖链 |
| **声明式** | 需要什么写在函数参数里，OpenAPI 文档可感知 |
| **可测试** | 测试时可用 `app.dependency_overrides` 替换依赖 |
| **生命周期** | `yield` 依赖支持请求前初始化、请求后清理 |

与 Spring / NestJS 的全局 IoC 容器不同，FastAPI 的 DI **更轻量**：没有 `@Autowired` 注解扫描，完全基于**函数签名 + 类型注解**在运行时解析。

---

## 2. 核心 API：`Depends()`

### 2.1 基本用法

```python
from fastapi import APIRouter, Depends

router = APIRouter()

def get_query_params(q: str = Query(default="")) -> str:
    return q

@router.get("")
async def depend_v1(query: str = Depends(get_query_params)) -> dict[str, str]:
    return {"message": query}
```

要点：

- **`Depends(可调用对象)`**：可调用对象可以是普通函数、async 函数、类（需实现 `__call__`）或 generator。
- **返回值注入参数**：依赖函数的返回值赋给路由参数 `query`。
- **依赖本身也是「参数解析器」**：`get_query_params` 内部仍可使用 `Query()`、`Header()` 等，FastAPI 会一并解析。

### 2.2 执行时机

每个请求到达时：

1. FastAPI 读取路由函数及所有依赖的**类型注解**和 **`Depends()` 声明**。
2. 构建**依赖图**（DAG），检测循环依赖。
3. 按拓扑顺序执行各依赖（子依赖先于父依赖）。
4. 将结果注入路由函数并调用。

同一请求内，**相同依赖默认只执行一次**（结果被缓存复用），详见 [§7 作用域与缓存](#7-作用域与缓存)。

### 2.3 同步 vs 异步

依赖可以是 `def` 或 `async def`。FastAPI 会在合适的上下文中 await 异步依赖。数据库、HTTP 客户端等 I/O 操作建议用 `async def`。

---

## 3. 依赖的类型

### 3.1 函数依赖（最常用）

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    ...
```

本仓库 [`app/auth/interface/dependencies.py`](../app/auth/interface/dependencies.py) 中的 `get_current_user`、`get_auth_service` 均属此类。

### 3.2 类依赖

类也可以作为依赖，通常实现 `__init__` 接收子依赖，或实现 `__call__`：

```python
class Pagination:
    def __init__(self, page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
        self.page = page
        self.page_size = page_size

@router.get("/items")
async def list_items(pagination: Pagination = Depends()):
    ...
```

`Depends()` 无参时，FastAPI 会把类本身当作依赖工厂实例化。

### 3.3 子依赖（依赖链）

依赖 A 的参数里再 `Depends(B)`，B 会先执行，结果注入 A，再注入路由：

```
get_db_session
      ↓
get_auth_service(session)
      ↓
get_current_user(token, session)
      ↓
路由函数
```

本仓库登录与鉴权链：

```python
# app/db/session.py
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

# app/auth/interface/dependencies.py
async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthorizationService:
    return AuthorizationService(session)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    ...
```

注意：`get_db_session` 在同一请求中被 `get_auth_service` 和 `get_current_user` 同时依赖时，**只 yield 一次**，两个调用方拿到同一个 session 实例。

### 3.4 `yield` 依赖（资源生命周期）

用于「请求前打开、请求后关闭」的资源，语义类似 `try/finally`：

```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
        # 请求结束后：async with 退出，session 自动 close
```

执行顺序：

1. `yield` **之前**的代码 → 请求处理前（setup）
2. 路由与后续依赖使用 yield 的值
3. 响应发送后 → `yield` **之后**的代码（teardown）

若 setup 或路由中抛出异常，teardown 仍会执行（generator 的 `finally` 语义）。

### 3.5 内置依赖

FastAPI / Starlette 提供的「依赖型参数」：

| 依赖 | 说明 |
|------|------|
| `OAuth2PasswordRequestForm = Depends()` | OAuth2 密码模式登录表单 |
| `Request` | 原始 ASGI 请求（无需 Depends，直接注入） |
| `Response` | 可写响应对象 |
| `BackgroundTasks` | 后台任务 |

本仓库登录接口：

```python
@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db_session),
) -> Token:
    ...
```

---

## 4. 常见使用场景

### 4.1 数据库会话

**最佳实践**：用 `yield` 依赖管理 session 生命周期，不要把 session 存成全局变量。

```python
# app/db/session.py — 本仓库做法
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
```

路由中：

```python
async def create_user(
    body: UserCreate,
    session: AsyncSession = Depends(get_db_session),
):
    ...
```

### 4.2 鉴权与授权

**认证（Authentication）**：验证「你是谁」—— 解析 Token、查用户。

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> UserRead:
    payload = decode_access_token(token)
    user = await get_user_by_username(session, payload["sub"])
    if user is None:
        raise HTTPException(status_code=401, ...)
    return UserRead(...)
```

**授权（Authorization）**：验证「你能做什么」—— 权限检查。

本仓库用**依赖工厂**按资源/动作动态生成检查器：

```python
def require_permission(resource: str, action: str, ...):
    async def checker(
        request: Request,
        current_user: UserRead = Depends(get_current_user),
        auth_service: AuthorizationService = Depends(get_auth_service),
    ) -> UserRead:
        allowed = await auth_service.authorize(...)
        if not allowed:
            raise HTTPException(status_code=403, ...)
        return current_user
    return checker

# 使用
@router.delete("/items/{id}")
async def delete_item(
    id: int,
    user: UserRead = Depends(require_permission("item", "delete")),
):
    ...
```

### 4.3 业务服务注入

把 Service 类组装也放进依赖，路由只关心业务调用：

```python
async def get_auth_service(
    session: AsyncSession = Depends(get_db_session),
) -> AuthorizationService:
    return AuthorizationService(session)
```

### 4.4 复用路由前置逻辑

本仓库 [`app/chat/interface/router.py`](../app/chat/interface/router.py) 的 `prepare_chat_access`：在对话前完成 ACL 校验 + 会话初始化，路由只声明依赖、不使用返回值：

```python
async def prepare_chat_access(
    request: Request,
    current_user: UserRead = Depends(get_current_user),
    auth_service: AuthorizationService = Depends(get_auth_service),
) -> UserRead:
    session_id = request.query_params.get("session_id", "default")
    allowed = await auth_service.authorize(...)
    if not allowed:
        raise HTTPException(status_code=403, ...)
    await auth_service.ensure_chat_session(...)
    return current_user

@router.get("/chat")
def chat(
    query: str,
    _: UserRead = Depends(prepare_chat_access),  # 仅触发副作用
    master: Master = Depends(get_master),
):
    ...
```

用 `_` 命名表示「只需要执行依赖，不需要返回值」—— 这是常见模式。

### 4.5 从 `app.state` 获取应用级单例

```python
# app/chat/interface/dependencies.py
def get_master(request: Request) -> Master:
    master = request.app.state.master
    if master is None:
        master = Master(get_settings())
        request.app.state.master = master
    return master
```

`Request` 由 Starlette 直接注入，无需 `Depends`。更推荐在 **lifespan** 中初始化 `app.state.master`，依赖只负责读取。

### 4.6 参数解析依赖

把 Query / Header / Cookie 的解析封装成依赖，避免路由参数列表过长：

```python
def get_query_params(q: str = Query(default="", description="Query string")) -> str:
    return q

@router.get("")
async def depend_v1(query: str = Depends(get_query_params)):
    return {"message": query}
```

---

## 5. 作用域层级

FastAPI 支持在不同层级挂载依赖：

| 层级 | 写法 | 作用范围 |
|------|------|----------|
| **路由参数** | `user=Depends(get_user)` | 单个 endpoint |
| **Router** | `APIRouter(dependencies=[Depends(...)])` | 该 router 下所有路由 |
| **App** | `FastAPI(dependencies=[Depends(...)])` | 全局所有路由 |

Router 级适合「整组 API 都要登录」：

```python
router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_current_user)],
)
```

子依赖仍会参与全局依赖图解析；Router 级依赖的执行结果同样在同一请求内缓存。

---

## 6. `Security()` 与 `Depends()` 的区别

```python
from fastapi import Security, Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def get_user(token: str = Security(oauth2_scheme, scopes=["items:read"])):
    ...
```

| | `Depends()` | `Security()` |
|---|-------------|--------------|
| 用途 | 通用依赖 | 安全相关依赖 |
| OpenAPI | 普通 parameter | 出现在 **securitySchemes**，支持 **scopes** |
| 行为 | 相同 | 相同（Security 是 Depends 的特例） |

OAuth2 / API Key / HTTP Bearer 等应优先用 `Security()`，文档更准确。

---

## 7. 作用域与缓存

**同一请求、同一依赖函数，默认只调用一次。**

```python
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

async def get_auth_service(session: AsyncSession = Depends(get_db_session)):
    return AuthorizationService(session)

async def get_current_user(session: AsyncSession = Depends(get_db_session)):
    # 这里的 session 与 get_auth_service 拿到的是同一个对象
    ...
```

若需要**每次调用都重新执行**（少见），使用 `Depends(..., use_cache=False)`：

```python
async def get_fresh_token(token: str = Depends(oauth2_scheme, use_cache=False)):
    ...
```

---

## 8. 依赖中的异常

依赖里可以直接 `raise HTTPException` 或任意异常；FastAPI 会中断依赖链，走已注册的异常处理器。

```python
async def get_current_user(...):
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="...") from exc
```

**最佳实践**：

- 401 / 403 等 HTTP 语义明确的错误 → `HTTPException`
- 业务错误 → 自定义异常 + 全局 `exception_handler`
- 不要在依赖里 `return None` 表示失败再让路由判断（除非明确是 Optional 场景）

---

## 9. 测试：覆盖依赖

`TestClient` / `AsyncClient` 可通过 `dependency_overrides` 替换依赖，无需真实数据库或 Token：

```python
from app.main import app
from app.db.session import get_db_session

async def override_get_db():
    async with test_session_factory() as session:
        yield session

app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)
response = client.get("/auth/me", headers={"Authorization": "Bearer test"})
```

测试结束后清理：

```python
app.dependency_overrides.clear()
```

本仓库 [`tests/conftest.py`](../tests/conftest.py) 中可结合 `create_app(init_db=False)` 与 overrides 构建轻量测试环境。

---

## 10. 最佳实践清单

### 10.1 推荐做法

| 实践 | 说明 |
|------|------|
| **依赖放独立模块** | 如 `app/auth/interface/dependencies.py`、`app/db/session.py`，不要堆在路由文件里 |
| **路由保持薄** | 路由只做参数接收 + 调用 service + 返回；鉴权/DB/组装放依赖 |
| **yield 管理资源** | DB session、文件句柄、临时连接用 generator 依赖 |
| **子依赖传递** | Service 依赖 session，而不是在 service 内部自己创建 session |
| **lifespan 初始化重资源** | LLM 客户端、连接池放 `lifespan` → `app.state`，依赖负责读取 |
| **依赖工厂处理参数化鉴权** | `require_permission("chat", "read")` 比复制粘贴检查逻辑更好 |
| **用 `_` 忽略仅副作用的依赖** | `_: UserRead = Depends(prepare_chat_access)` |
| **测试用 overrides** | 不 mock 整个 FastAPI，只替换边界依赖 |

### 10.2 反模式（避免）

| 反模式 | 问题 | 更好做法 |
|--------|------|----------|
| 全局可变 session | 并发请求共享状态，连接泄漏 | `yield` 依赖或 `async with` |
| 在依赖里写大量业务逻辑 | 难测试、难复用 | 依赖只做组装/鉴权，逻辑进 Service |
| 路由里手动调 `get_db_session()` | 绕过 DI，生命周期不受控 | `Depends(get_db_session)` |
| 循环依赖 A→B→A | 启动/请求时报错 | 抽取公共依赖 C，或合并 |
| 每个路由复制鉴权代码 | 维护成本高 | `Depends(get_current_user)` 或 router 级依赖 |
| 滥用 `use_cache=False` | 重复 I/O、重复建连 | 仅在确实需要多次执行时使用 |
| 依赖函数副作用过多 | 难以推理执行顺序 | 副作用集中、命名清晰（如 `prepare_*`） |

---

## 11. 依赖 vs 中间件：何时用哪个

| | 依赖注入 | 中间件 |
|---|----------|--------|
| **粒度** | 单个路由 / Router | 全局或路径级 |
| **访问返回值** | 可以，注入路由参数 | 不行，只能改 request/response |
| **OpenAPI** | 体现在参数/安全方案 | 不可见 |
| **典型用途** | 鉴权、DB、分页、Service | CORS、日志、统一响应包装、计时 |

经验法则：

- **与具体业务参数相关** → 依赖（当前用户、DB session、分页）
- **与 HTTP 管道相关、与业务无关** → 中间件（本仓库的 `UnifiedResponseMiddleware`）

两者可并存：中间件处理响应格式，依赖处理鉴权。

---

## 12. 本仓库依赖结构一览

```
app/
├── chat/interface/
│   ├── dependencies.py          # get_master（app.state）
│   └── router.py                # /chat、prepare_chat_access
├── auth/interface/
│   └── dependencies.py          # oauth2_scheme, get_current_user,
│                                # get_auth_service, require_permission
├── db/
│   └── session.py               # get_db_session（yield）
└── demo/
    └── depend.py                # 学习用：Query 封装为依赖
```

请求 `/chat` 时的依赖解析顺序示意：

```
oauth2_scheme ──┐
                ├──► get_current_user ──┐
get_db_session ─┤                       ├──► prepare_chat_access ──► chat()
                ├──► get_auth_service ──┘
                └──► get_master ──────────────────────────────────► chat()
```

---

## 13. Python 3.9+：`Annotated` 写法（推荐）

FastAPI 0.95+ 推荐使用 `Annotated` 把类型与 `Depends` 分离，签名更清晰：

```python
from typing import Annotated
from fastapi import Depends

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[UserRead, Depends(get_current_user)]

@router.get("/me")
async def read_me(current_user: CurrentUser) -> UserRead:
    return current_user
```

优点：

- 类型别名可在多处复用
- IDE 类型提示更准确
- 参数默认值位置更自然

本仓库目前使用经典 `= Depends(...)` 写法，两种形式等价，新代码可逐步迁移到 `Annotated`。

---

## 14. 常见问题

| 问题 | 答案 |
|------|------|
| 依赖执行顺序？ | 子依赖先于父依赖；同级按签名从左到右 |
| 同一依赖会执行几次？ | 同一请求内默认一次（缓存） |
| 依赖可以用 `Request` 吗？ | 可以，Starlette 会自动注入 |
| 依赖里能再依赖路由参数吗？ | 不能反向依赖；路由参数不能传给 Depends 图外的逻辑，但 Path/Query 可以在依赖函数签名里声明 |
| 如何跳过某个依赖的 OpenAPI 展示？ | `include_in_schema=False` |
| 和 Flask `g` / 全局对象比？ | FastAPI 显式依赖链更可测、无隐式全局状态 |
| 异步 generator 依赖？ | 支持，`async def` + `yield` 与 sync generator 语义一致 |

---

## 15. 小结

**FastAPI 依赖注入 = 用函数签名声明需求 + `Depends()` 自动解析执行 + 子依赖组合 + yield 生命周期 + 请求级缓存。**

掌握四条主线即可应对大部分项目：

1. **`yield` 依赖**管理 DB / 连接等资源  
2. **依赖链**组装 Service（session → service → user）  
3. **依赖工厂**处理参数化鉴权（`require_permission(...)`）  
4. **`dependency_overrides`** 做测试隔离  

结合本仓库：路由只负责 HTTP 边界，[`app/auth/interface/dependencies.py`](../app/auth/interface/dependencies.py) 负责身份与权限，[`app/db/session.py`](../app/db/session.py) 负责数据访问生命周期——这是 FastAPI 项目中依赖注入的典型分层方式。
