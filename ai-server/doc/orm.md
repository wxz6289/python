# Python ORM 总结与最佳实践

**ORM**（Object-Relational Mapping，对象关系映射）在 Python 对象与关系型数据库表之间建立映射，让你用类、属性和方法操作数据，而不必手写大量 SQL。

本文梳理 Python 生态中主流的 ORM 方案，给出选型建议与工程最佳实践。本仓库 [ai-server](../README.md) 使用 **FastAPI + SQLAlchemy 2.x + aiomysql**，下文会结合该栈举例。

相关文档：[FastAPI 核心内容](./fastapi.md) · [框架对比](./framework-comparison.md)

---

## 1. ORM 解决什么问题

```
┌─────────────────────────────────────────────────────────────┐
│                    应用层（Python 对象）                      │
│         User(id=1, name="Alice")  ·  Order · Product         │
├─────────────────────────────────────────────────────────────┤
│                         ORM 层                               │
│   模型定义 · 关系映射 · 查询构建 · 事务 · 连接池 · 迁移       │
├─────────────────────────────────────────────────────────────┤
│                    数据库（MySQL / PostgreSQL …）             │
│              users 表 · orders 表 · 索引 · 约束              │
└─────────────────────────────────────────────────────────────┘
```


| 能力            | 说明                         |
| ------------- | -------------------------- |
| **模型映射**      | Python 类 ↔ 数据库表，属性 ↔ 列     |
| **关系映射**      | 一对多、多对多、外键、级联              |
| **查询抽象**      | 链式 API 或 Query 对象，减少拼接 SQL |
| **事务管理**      | commit / rollback，保证一致性    |
| **连接池**       | 复用连接，提升并发性能                |
| **Schema 迁移** | Alembic 等工具管理表结构变更         |


ORM 不是银弹：复杂报表、批量写入、特定数据库特性有时仍需要原生 SQL 或 SQLAlchemy Core。

---

## 2. 主流 ORM 一览

### 2.1 总览对比


| ORM                  | 类型                    | 异步                | 数据库                           | 生态/成熟度 | 典型场景                 |
| -------------------- | --------------------- | ----------------- | ----------------------------- | ------ | -------------------- |
| **SQLAlchemy 2.x**   | 全功能 ORM + Core        | ✅（2.0+ 原生 async）  | 几乎所有 SQL 库                    | ⭐⭐⭐⭐⭐  | 通用后端、FastAPI、企业项目    |
| **Django ORM**       | 框架内置 ORM              | ⚠️（3.1+ 有限 async） | 主流 SQL 库                      | ⭐⭐⭐⭐⭐  | Django 全栈、Admin、CMS  |
| **SQLModel**         | SQLAlchemy + Pydantic | ✅                 | 同 SQLAlchemy                  | ⭐⭐⭐    | FastAPI 项目、类型友好      |
| **ORM****Tortoise** | 独立 async ORM          | ✅ 原生              | PostgreSQL/MySQL/SQLite 等     | ⭐⭐⭐    | asyncio 服务、轻量 API    |
| **Peewee**           | 轻量 ORM                | ❌                 | 多种 SQL 库                      | ⭐⭐⭐⭐   | 脚本、小项目、学习            |
| **Piccolo**          | 现代 async ORM          | ✅                 | PostgreSQL/SQLite/CockroachDB | ⭐⭐⭐    | async API、Admin 自动生成 |
| **Ormar**            | async ORM             | ✅                 | PostgreSQL/MySQL/SQLite       | ⭐⭐     | FastAPI 紧耦合场景        |
| **Pony ORM**         | 声明式 ORM               | ❌                 | 多种 SQL 库                      | ⭐⭐     | 复杂查询、Python 风格 DSL   |
| **MongoEngine**      | ODM（文档库）              | ❌                 | MongoDB                       | ⭐⭐⭐    | MongoDB 文档型数据        |
| **Prisma Client Py** | 代码生成客户端               | ✅                 | PostgreSQL/MySQL/SQLite 等     | ⭐⭐⭐    | 类型安全、schema-first    |


### 2.2 SQLAlchemy 2.x（推荐，本仓库选用）

Python 生态事实标准，同时提供 **Core**（接近 SQL 的表达式语言）和 **ORM**（对象映射）。2.0 起统一 API，原生支持 `async/await`。

**特点**

- 功能最全：关系、继承、混合属性、事件钩子、多数据库方言
- 与 FastAPI 解耦，可配合 **Alembic** 做迁移
- 性能可控：可下沉到 Core 或 raw SQL
- 文档与社区资源最丰富

**Declarative 模型示例**

```python
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total: Mapped[float]

    user: Mapped["User"] = relationship(back_populates="orders")
```

**Async Session 示例（FastAPI 常用）**

```python
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

DATABASE_URL = "mysql+aiomysql://user:pass@localhost:3306/ai_server"

engine = create_async_engine(DATABASE_URL, pool_pre_ping=True, pool_size=10)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
```

```python
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404)
    return user
```

**适用**：中大型 API、需要灵活 SQL、多数据库、与现有 SQL 共存的项目。

---

### 2.3 Django ORM

Django 框架内置，**Active Record** 风格（模型类同时承担持久化职责）。

**特点**

- 与 Django Admin、Auth、Migration 深度集成
- QuerySet API 表达力强，链式过滤、聚合、Prefetch 优化
- 离开 Django 生态后难以单独使用
- 异步支持仍在演进，复杂场景仍以同步为主

**示例**

```python
from django.db import models


class User(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    total = models.DecimalField(max_digits=10, decimal_places=2)


# 查询
User.objects.filter(email__endswith="@example.com").select_related("orders")
```

**适用**：Django 全栈、内容管理、需要 Admin 的后台系统。  
**不适用**：纯 FastAPI 微服务（除非引入 Django 作为子应用，成本高）。

---

### 2.4 SQLModel

由 FastAPI 作者开发，基于 **SQLAlchemy 2 + Pydantic v2**，一个类同时作为 DB 模型和 API Schema。

**特点**

- 与 FastAPI / Pydantic 类型体系统一
- 底层仍是 SQLAlchemy，可渐进迁移到完整 SQLAlchemy
- 复杂关系、高级 ORM 特性支持不如纯 SQLAlchemy 文档完善

**示例**

```python
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)

    orders: list["Order"] = Relationship(back_populates="user")


class Order(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    total: float

    user: User | None = Relationship(back_populates="orders")
```

**适用**：中小型 FastAPI 项目，希望减少 Model / Schema 重复定义。  
**注意**：API 响应模型与 DB 模型建议分离（见最佳实践）。

---

### 2.5 Tortoise ORM

专为 **asyncio** 设计的 ORM，API 风格类似 Django ORM。

**特点**

- 原生 async，与 FastAPI、Sanic 配合自然
- 内置 Aerich 迁移工具
- 关系、复杂查询能力弱于 SQLAlchemy
- 同步代码或混合栈中不如 SQLAlchemy 灵活

**示例**

```python
from tortoise import fields, models


class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)

    class Meta:
        table = "users"


# 查询
user = await User.get_or_none(id=1)
users = await User.filter(email__endswith="@example.com")
```

**适用**：纯 async 中小型服务，团队熟悉 Django ORM 风格。

本仓库 Tortoise 迁移详见 [Aerich 指南](./aerich.md)。

---

### 2.6 Peewee

轻量、API 简洁，适合小项目和脚本。

**特点**

- 学习曲线低，代码量少
- 支持 SQLite / MySQL / PostgreSQL 等
- 无原生 async（需 `peewee-async` 等扩展）
- 大型项目缺少 SQLAlchemy 级别的生态与扩展性

**示例**

```python
from peewee import *

db = MySQLDatabase("ai_server", user="root", password="pass")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    email = CharField(unique=True)

User.select().where(User.email.endswith("@example.com"))
```

**适用**：CLI 工具、数据脚本、原型验证。

---

### 2.7 其他方案（简要）


| 方案                       | 说明                                           |
| ------------------------ | -------------------------------------------- |
| **Piccolo**              | 现代 async ORM，自带 Admin；PostgreSQL 体验最好        |
| **Ormar**                | 基于 SQLAlchemy Core + Pydantic，与 FastAPI 绑定较紧 |
| **Pony ORM**             | 用 Python 生成式语法写查询，学习成本独特                     |
| **MongoEngine / Beanie** | MongoDB 文档库 ODM，Beanie 支持 async              |
| **Prisma Client Py**     | schema.prisma 驱动，强类型、代码生成，适合 TS/Python 全栈团队  |
| **datasets + pandas**    | 非 ORM，适合数据分析批处理，不适合在线事务服务                    |


---

## 3. 架构模式：Data Mapper vs Active Record


| 模式                | 代表                         | 特点                                                |
| ----------------- | -------------------------- | ------------------------------------------------- |
| **Data Mapper**   | SQLAlchemy ORM             | 模型类只管数据结构，Session/Repository 负责持久化；领域逻辑与 DB 解耦更好  |
| **Active Record** | Django ORM、Peewee、Tortoise | 模型类自带 `.save()`、`.delete()`、`.objects`；写法直观，模型易膨胀 |


SQLAlchemy 的 Session 显式管理单元工作（Unit of Work），更适合复杂业务与测试替换；Active Record 适合快速 CRUD。

---

## 4. 本仓库推荐栈

```
FastAPI 路由
    ↓ Depends(get_db)
AsyncSession（SQLAlchemy 2.x）
    ↓
aiomysql 驱动 → MySQL
    ↓
Alembic 管理迁移
```


| 组件                | 作用                          |
| ----------------- | --------------------------- |
| `sqlalchemy>=2.0` | ORM + 连接池 + 查询              |
| `aiomysql`        | 异步 MySQL 驱动                 |
| `pymysql`         | 同步驱动（脚本、Alembic 离线迁移可选）     |
| `Alembic`         | 表结构版本管理（建议加入 dev 依赖）        |
| `Pydantic`        | API 请求/响应 Schema，与 ORM 模型分离 |


为何不用 Django ORM：本项目是 FastAPI 微服务，不需要 Django 全栈能力。  
为何优先 SQLAlchemy 而非 SQLModel：SQLAlchemy 文档与社区更成熟；复杂查询、性能调优路径更清晰；需要时可局部引入 SQLModel 或 Pydantic 做 DTO。

---

## 5. 最佳实践

### 5.1 分层：ORM 模型 ≠ API Schema

不要把 SQLAlchemy / SQLModel 实体直接作为 FastAPI 响应返回。

```python
# app/schemas/user.py — API 层
from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str


# app/models/user.py — 持久化层
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))  # 不应暴露给 API
```

好处：隐藏内部字段（密码哈希、软删除标记）、稳定 API 契约、避免懒加载序列化问题。

---

### 5.2 Session 生命周期与依赖注入

- **一个请求一个 Session**（FastAPI `Depends` + `yield`）
- 读操作：`async with session` 或依赖注入自动关闭
- 写操作：显式 `await session.commit()`，异常时 `rollback`
- 不要在全局共享 Session

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # 可选：也可在 service 层 commit
        except Exception:
            await session.rollback()
            raise
```

---

### 5.3 避免 N+1 查询

循环访问关联对象时，ORM 可能为每条记录单独查库。

```python
# ❌ N+1：每个 user 访问 orders 时各查一次
users = (await db.execute(select(User))).scalars().all()
for user in users:
    print(user.orders)

# ✅ 预加载
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.orders))
users = (await db.execute(stmt)).scalars().all()
```


| 策略             | 适用                       |
| -------------- | ------------------------ |
| `selectinload` | 一对多、多对多（额外 IN 查询，通常首选）   |
| `joinedload`   | 多对一、一对一（JOIN 一次取出）       |
| `subqueryload` | 旧式优化，现代代码优先 selectinload |


开发环境可开启 SQL echo 或 APM 追踪 SQL 条数，排查 N+1。

---

### 5.4 查询与写入性能


| 场景    | 建议                                                     |
| ----- | ------------------------------------------------------ |
| 大批量插入 | `session.add_all()` + bulk，`insert().values()` Core 批量 |
| 只读列表  | 只 `select` 需要的列，避免 `SELECT *`                          |
| 分页    | `LIMIT/OFFSET` 或 keyset pagination（大表更优）               |
| 计数    | `func.count()` 而非 `len(list(query))`                   |
| 复杂报表  | 原生 SQL 或 SQLAlchemy Core，不必强行 ORM                      |
| 索引    | 在模型上声明 `index=True`，迁移中补充复合索引                          |


---

### 5.5 事务边界

- 一个业务用例 = 一个事务（转账、下单）
- 不要在路由函数里散落多次 `commit`
- 跨多个 Repository 的操作放在同一 Session 内

```python
async def transfer(db: AsyncSession, from_id: int, to_id: int, amount: float) -> None:
    async with db.begin():  # 自动 commit/rollback
        sender = await db.get(Account, from_id, with_for_update=True)
        receiver = await db.get(Account, to_id, with_for_update=True)
        if sender.balance < amount:
            raise ValueError("insufficient funds")
        sender.balance -= amount
        receiver.balance += amount
```

---

### 5.6 迁移（Schema Migration）

- 使用 **Alembic**（SQLAlchemy 官方推荐），不要手工改生产表
- 迁移脚本纳入版本控制，CI 中做 upgrade 演练
- destructive 变更（删列、改类型）先备份，分步迁移
- 模型是真相源（Single Source of Truth），`alembic revision --autogenerate` 后务必人工审查

```bash
alembic init alembic
alembic revision --autogenerate -m "add users table"
alembic upgrade head
```

---

### 5.7 连接池配置

```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,           # 常驻连接数
    max_overflow=20,        # 峰值额外连接
    pool_pre_ping=True,     # 使用前检测连接是否有效
    pool_recycle=3600,      # 定期回收，避免 MySQL wait_timeout 断连
)
```

生产环境根据 QPS 与 DB `max_connections` 调参；监控连接池等待时间与慢查询。

---

### 5.8 异步与同步混用


| 规则                     | 说明                                    |
| ---------------------- | ------------------------------------- |
| FastAPI `async def` 路由 | 使用 `AsyncSession`，不要在其中调用阻塞 IO        |
| 阻塞 ORM 调用              | 放 `run_in_executor` 或改用 sync 路由 `def` |
| Alembic / 脚本           | 可用同步 `create_engine` + `pymysql`      |
| 懒加载                    | async 下访问未加载关系会报错，务必 eager load 或显式查询 |


---

### 5.9 测试策略

- 集成测试：SQLite 内存库或 Testcontainers 启动真实 MySQL
- 每个测试函数独立 Session，测试后 rollback 或重建 schema
- Factory（factory_boy）或 fixture 构造测试数据
- 不要依赖开发库跑测试

```python
@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
```

---

### 5.10 安全与健壮性

- **永远参数化查询**：ORM 默认绑定参数，禁止 f-string 拼 SQL
- 敏感字段（密码）存哈希，不入日志、不出 API
- 软删除：`deleted_at` 列 + 全局 filter，而非物理删除
- 乐观锁：`version` 列或 `updated_at` 条件更新，防止并发覆盖
- 限流 + 连接池 + 慢查询日志，防止 DB 被打满

---

## 6. 常见反模式


| 反模式                     | 问题         | 改进                      |
| ----------------------- | ---------- | ----------------------- |
| 在模型里写 HTTP / FastAPI 逻辑 | 层次混乱，难测试   | 放到 service / router     |
| 全局可变 Session            | 并发竞态、连接泄漏  | 请求级依赖注入                 |
| 返回 ORM 对象给前端            | 泄露字段、懒加载异常 | Pydantic Response Model |
| 过度 ORM 嵌套               | 生成低效 SQL   | 拆分查询或 Core / raw SQL    |
| 忽略迁移                    | 环境不一致      | Alembic 流程化             |
| 生产 `create_all()`       | 无法追踪变更     | 仅测试环境使用                 |
| 大事务长时间占连接               | 池耗尽        | 缩小事务范围                  |


---

## 7. 选型决策树

```
需要 Django Admin / 全栈？
├─ 是 → Django ORM
└─ 否 → 需要 asyncio 原生？
         ├─ 是 → FastAPI / 纯 async 服务
         │        ├─ 要最全生态、复杂 SQL → SQLAlchemy 2.x async ✅（本仓库）
         │        ├─ 要极简 + Pydantic 一体 → SQLModel
         │        └─ 要 Django 风格 async → Tortoise ORM
         └─ 否 → 脚本 / 小工具 → Peewee
                  企业 Java 团队 schema-first → Prisma Client Py
```

---

## 8. 参考资源


| 资源                        | 链接                                                                                                           |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| SQLAlchemy 2.0 文档         | [https://docs.sqlalchemy.org/en/20/](https://docs.sqlalchemy.org/en/20/)                                     |
| Alembic 文档                | [https://alembic.sqlalchemy.org/](https://alembic.sqlalchemy.org/)                                           |
| SQLModel 文档               | [https://sqlmodel.tiangolo.com/](https://sqlmodel.tiangolo.com/)                                             |
| Django ORM 文档             | [https://docs.djangoproject.com/en/stable/topics/db/](https://docs.djangoproject.com/en/stable/topics/db/)   |
| Tortoise ORM 文档           | [https://tortoise.github.io/](https://tortoise.github.io/)                                                   |
| FastAPI + SQLAlchemy 官方教程 | [https://fastapi.tiangolo.com/tutorial/sql-databases/](https://fastapi.tiangolo.com/tutorial/sql-databases/) |


---

## 9. 小结


| 要点              | 结论                                                               |
| --------------- | ---------------------------------------------------------------- |
| **默认首选**        | SQLAlchemy 2.x：功能、生态、async 支持最均衡                                 |
| **Django 项目**   | 直接用 Django ORM，不要强行拆出                                            |
| **FastAPI 小项目** | SQLModel 或 SQLAlchemy + Pydantic 均可                              |
| **工程关键**        | 模型分层、Session 管理、N+1 防护、Alembic 迁移、连接池调优                          |
| **本仓库**         | `sqlalchemy` + `aiomysql` + 请求级 `AsyncSession` + Pydantic Schema |


ORM 的目标是让 **80% 的 CRUD 更高效**，同时保留 **20% 复杂场景** 下沉 SQL 的灵活性。掌握 SQLAlchemy 2.x 的 Declarative 模型、Async Session、关系加载与 Alembic，足以支撑大多数 Python 后端项目。