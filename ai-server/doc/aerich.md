# Aerich 数据库迁移指南

**Aerich** 是 [Tortoise ORM](https://tortoise.github.io/) 官方推荐的数据库迁移工具，角色类似 SQLAlchemy 生态中的 **Alembic** 或 Django 的 `migrate`。它根据模型定义自动生成迁移 SQL，并在数据库中记录已应用的版本，保证多环境、多成员之间的表结构一致。

本仓库中：

| 栈 | 迁移工具 | 管理范围 |
| --- | --- | --- |
| **SQLAlchemy 2.x** | `app/db/init.sql` + 手工维护 | RBAC / ACL（`users`、`roles` 等） |
| **Tortoise ORM** | **Aerich** | Tortoise 模型（如 `tortoise_notes`） |

相关文档：[ORM 总结与最佳实践](./orm.md) · [项目 README](../README.md)

---

## 1. Aerich 解决什么问题

```
┌──────────────────────────────────────────────────────────────────┐
│  开发者修改 Tortoise Model（app/db/tortoise_models.py）            │
└────────────────────────────┬─────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  aerich migrate   →  对比「当前模型」与「上次快照」，生成迁移文件     │
└────────────────────────────┬─────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  代码审查（Git）→  migrations/models/N_xxx.py                     │
└────────────────────────────┬─────────────────────────────────────┘
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│  aerich upgrade   →  在目标库执行 SQL，并写入 aerich 版本表          │
└──────────────────────────────────────────────────────────────────┘
```

| 能力 | 说明 |
| --- | --- |
| **版本化** | 每次结构变更对应一个迁移文件，可回溯、可审计 |
| **差异检测** | `migrate` 自动对比模型与数据库快照，减少手写 DDL |
| **多环境一致** | 开发 / 测试 / 生产通过同一套迁移文件对齐 schema |
| **与 Tortoise 集成** | 直接读取 `TORTOISE_ORM` 配置与模型模块 |

Aerich **只管理 Tortoise 注册的模型**，不会触碰 SQLAlchemy 维护的表。

---

## 2. 本仓库目录与配置

### 2.1 关键文件

```
ai-server/
├── pyproject.toml              # [tool.aerich] 段
├── migrations/
│   └── models/                 # app 名称为 "models"（见 TORTOISE_ORM.apps）
│       └── 0_20260523185834_init.py
├── app/db/
│   ├── tortoise_config.py      # TORTOISE_ORM + 运行时 init
│   └── tortoise_models.py      # Tortoise 模型定义
```

### 2.2 `pyproject.toml` 中的 Aerich 配置

```toml
[tool.aerich]
tortoise_orm = "app.db.tortoise_config.TORTOISE_ORM"
location = "./migrations"
src_folder = "./."
```

| 字段 | 含义 |
| --- | --- |
| `tortoise_orm` | 指向模块内的 **dict 变量**（不是函数），Aerich CLI 会 `import` 该路径 |
| `location` | 迁移文件根目录 |
| `src_folder` | 加入 `sys.path` 的前缀，保证 `app.*` 可被导入 |

### 2.3 `TORTOISE_ORM` 配置要点

配置位于 `app/db/tortoise_config.py`：

```python
TORTOISE_ORM = {
    "connections": {"default": build_tortoise_db_url()},
    "apps": {
        "models": {
            "models": ["app.db.tortoise_models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
```

**必须包含 `aerich.models`**：Aerich 用它维护内部的 `aerich` 版本表（记录每个 app 已应用的迁移及模型快照）。

**CLI 与运行时的配置要一致**：应用启动时 `init_tortoise_orm()` 使用同一份 `TORTOISE_ORM`，避免「迁移按 A 建表、运行时连 B」的不一致。

### 2.4 连接串与 `.env`

`build_tortoise_db_url()` 的优先级：

1. 环境变量：`MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`
2. 回退到 `docker-compose.yml` 中的 MySQL 配置

Aerich 执行时会 `load_dotenv(.env)`，但**不会**走 `get_settings()`（避免校验 `DEEPSEEK_API_KEY` 导致迁移命令失败）。迁移专用配置应保持**简单、无副作用**。

MySQL 连接串格式（asyncmy 驱动）：

```
mysql://user:password@host:port/database
```

密码中的特殊字符需 URL 编码（项目内使用 `quote_plus`）。

---

## 3. 命令参考

在项目根目录执行（推荐 `uv run`）：

```bash
uv run aerich <command> [options]
```

### 3.1 一次性初始化（已完成可跳过）

| 命令 | 作用 |
| --- | --- |
| `aerich init -t app.db.tortoise_config.TORTOISE_ORM` | 创建 `migrations/` 目录，写入 `[tool.aerich]` |
| `aerich init-db` | 根据当前模型生成**首个**迁移文件，并在数据库建表 |

本仓库已执行过上述步骤，新克隆仓库**不需要**再 `init`，只需 `upgrade`（见下文）。

### 3.2 日常开发

| 命令 | 作用 |
| --- | --- |
| `aerich migrate --name <描述>` | 检测模型变更，生成新迁移文件 |
| `aerich migrate --empty --name <描述>` | 生成空迁移，用于手写 SQL |
| `aerich upgrade` | 将未应用的迁移执行到数据库 |
| `aerich history` | 列出所有迁移文件 |
| `aerich heads` | 显示尚未应用的迁移（待 upgrade 的 head） |
| `aerich downgrade` | 回退到上一版本（危险，需确认） |
| `aerich downgrade -v 0` | 回退到指定版本号 |
| `aerich downgrade -d` | 回退并删除迁移文件 |
| `aerich inspectdb` | 从现有表反向生成 Tortoise 模型代码（辅助） |
| `aerich inspectdb -t tortoise_notes` | 只检查指定表 |

`upgrade` 支持 `--in-transaction` / `-i`（默认 `true`）：在单个事务中执行迁移，适合 MySQL 等支持 DDL 事务的场景；超大表变更可按需关闭。

### 3.3 多 App 名称

`TORTOISE_ORM.apps` 的 key 即 app 名（本仓库为 `models`）。若存在多个 app，需显式指定：

```bash
uv run aerich --app models migrate --name add_field
uv run aerich --app models upgrade
```

---

## 4. 标准工作流

### 4.1 修改模型后（本地开发）

```bash
# 1. 编辑 app/db/tortoise_models.py（或新增模型文件并注册到 TORTOISE_MODEL_MODULES）

# 2. 确保 MySQL 已启动（docker compose up -d mysql）

# 3. 生成迁移
uv run aerich migrate --name add_note_tags

# 4. 检查生成的 migrations/models/*.py（务必 code review）

# 5. 应用到本地库
uv run aerich upgrade

# 6. 提交迁移文件到 Git
git add migrations/ app/db/
```

若 `migrate` 输出 `No changes detected`，说明模型与 Aerich 上次记录的快照一致，无需新迁移。

### 4.2 新环境 / 新成员 / CI 部署

```bash
# 拉代码后，仅需升级（不要重复 init-db）
uv run aerich upgrade
```

**不要**在生产环境使用 `Tortoise.generate_schemas()` 或 `aerich init-db` 替代迁移——本仓库运行时已移除 `generate_schemas`，表结构统一由 Aerich 管理。

### 4.3 迁移文件结构

每个迁移文件包含 `upgrade` / `downgrade` 两个异步函数，返回要执行的 SQL 字符串：

```python
async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tortoise_notes` ADD `tags` JSON;
    """

async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `tortoise_notes` DROP COLUMN `tags`;
    """
```

- 文件名格式：`{序号}_{时间戳}_{name}.py`
- `aerich` 表记录 `version`、`app`、`content`（模型快照 JSON）

---

## 5. 最佳实践

### 5.1 配置与模块

| 实践 | 说明 |
| --- | --- |
| **独立 `TORTOISE_ORM` 模块** | 放在 `tortoise_config.py`，避免 Aerich import 时触发 FastAPI / LangChain / JWT 等副作用 |
| **始终注册 `aerich.models`** | 仅在一个 app 的 `models` 列表中加入即可 |
| **模型路径写全** | 使用 `app.db.tortoise_models`，不要写无法 import 的包名 |
| **迁移文件入库** | `migrations/` 与代码一同版本管理，禁止只改库不提交迁移 |

### 5.2 开发与生产

| 实践 | 说明 |
| --- | --- |
| **先 migrate 再 upgrade** | 生成 → 审查 → 应用，顺序不要颠倒 |
| **禁止依赖 `generate_schemas`** | 开发/生产统一走 Aerich，避免双轨建表 |
| **部署前跑 `upgrade`** | 在 CI/CD 或发布脚本中执行，而不是在应用 lifespan 里自动迁移（便于控制与回滚） |
| **大表变更单独规划** | 加索引、改列类型等可能锁表，评估 `in_transaction`、在线 DDL、分批执行 |
| **downgrade 慎用** | 生产回退前备份；空 `downgrade` 的初始迁移无法真正回退删表 |

### 5.3 与 SQLAlchemy 共存

本仓库 **两套 ORM 各管各的表**：

- SQLAlchemy：`app/auth/models.py` + `app/db/init.sql`
- Tortoise：`app/db/tortoise_models.py` + Aerich

不要在 Tortoise 模型中映射 SQLAlchemy 已管理的表，反之亦然。跨栈关联在应用层用 ID 关联，而非 ORM 级联。

### 5.4 测试

| 场景 | 建议 |
| --- | --- |
| 单元测试（无 DB） | `create_app(init_db=False)`，不初始化 Tortoise |
| 集成测试 | 独立测试库 + `aerich upgrade`，或 SQLite `:memory:` + 单独 `TORTOISE_ORM` |
| 并行测试 | Tortoise 1.1+ 使用 `TortoiseContext` 隔离；Aerich 命令本身串行操作同一库 |

### 5.5 代码审查清单

- [ ] 迁移 SQL 是否与模型变更一致？
- [ ] 是否误删列/索引？`NOT NULL` 新列是否有默认值或回填？
- [ ] `downgrade` 是否可执行（可为空，但需知晓风险）？
- [ ] 是否需要数据迁移（Aerich 只生成 DDL，复杂 DML 用 `--empty` 手写）？
- [ ] 多环境字符集是否为 `utf8mb4`（与项目 MySQL 配置一致）？

---

## 6. 常见问题

### 6.1 `Module "xxx" not found`

常见原因并非路径错误，而是 **import 时循环依赖** 或模块内执行了过重逻辑。处理：

- 保持 `tortoise_config.py` 精简
- 模型文件避免在顶层 import FastAPI、settings 等
- 用完整模块路径：`app.db.tortoise_models`

### 6.2 `No TortoiseContext is currently active`

这是 **运行时** FastAPI 与 Tortoise 1.1 的 task 隔离问题，与 Aerich 无关。应用侧需 `_enable_global_fallback=True`（见 `init_tortoise_orm()`）。

### 6.3 `You need to run aerich init-db first`

表示 `migrations/models/` 下尚无迁移目录。新仓库应执行 `aerich upgrade`；全新 Tortoise 项目才需要 `init-db`。

### 6.4 `App models is already initialized`

已对同一 app 执行过 `init-db`。不要删除生产库后重复 `init-db`；应继续使用 `migrate` + `upgrade`。

### 6.5 表已存在 / 与迁移不同步

若曾用 `generate_schemas(safe=True)` 手动建表：

1. 确认表结构与初始迁移一致
2. 在 `aerich` 表中插入对应版本记录，或
3. 开发环境删表后重新 `upgrade`（**勿**对生产库随意删表）

### 6.6 缺少 `tomlkit`

`aerich init` 写入 `pyproject.toml` 需要 `tomlkit`（或 `tomli_w`）。本仓库已在依赖中声明。

---

## 7. CI/CD 示例

```yaml
# 片段：部署前迁移 Tortoise 表
- name: Upgrade Tortoise schema
  run: uv run aerich upgrade
  env:
    MYSQL_HOST: ${{ secrets.MYSQL_HOST }}
    MYSQL_PORT: 3306
    MYSQL_USER: ${{ secrets.MYSQL_USER }}
    MYSQL_PASSWORD: ${{ secrets.MYSQL_PASSWORD }}
    MYSQL_DATABASE: ai_server
```

注意：CI 只需数据库相关环境变量，**不需要** `DEEPSEEK_API_KEY`。

---

## 8. Aerich vs Alembic（本仓库对照）

| 维度 | Aerich（Tortoise） | Alembic（SQLAlchemy） |
| --- | --- | --- |
| 配置入口 | `TORTOISE_ORM` dict | `alembic.ini` + `env.py` |
| 模型来源 | Tortoise `models.Model` | SQLAlchemy `DeclarativeBase` |
| 生成命令 | `aerich migrate` | `alembic revision --autogenerate` |
| 应用命令 | `aerich upgrade` | `alembic upgrade head` |
| 版本表 | `aerich` | `alembic_version` |
| 本仓库现状 | ✅ 已接入 `tortoise_notes` | RBAC 使用 `init.sql` 手工维护 |

未来若 RBAC 也迁到 Alembic，与 Aerich **并行**即可：两者操作不同的表集合，互不影响。

---

## 9. 快速命令备忘

```bash
# 模型变更 → 生成并应用
uv run aerich migrate --name <变更描述>
uv run aerich upgrade

# 查看状态
uv run aerich history
uv run aerich heads

# 新机器 / 新库
uv run aerich upgrade

# 从已有表生成模型草稿
uv run aerich inspectdb -t tortoise_notes
```

---

## 10. 参考链接

| 资源 | 链接 |
| --- | --- |
| Aerich 仓库 | [https://github.com/tortoise/aerich](https://github.com/tortoise/aerich) |
| Tortoise ORM 文档 | [https://tortoise.github.io/](https://tortoise.github.io/) |
| Tortoise 迁移说明 | [https://tortoise.github.io/migration.html](https://tortoise.github.io/migration.html) |
| FastAPI + Tortoise 示例 | [https://tortoise.github.io/examples/fastapi](https://tortoise.github.io/examples/fastapi) |
| 本仓库 Tortoise 配置 | `app/db/tortoise_config.py` |
| 本仓库示例 API | `/tortoise/notes`（`app/demo/tortoise_demo.py`） |
