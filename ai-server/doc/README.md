# ai-server 文档索引

| 文档 | 说明 |
|------|------|
| [fastapi.md](./fastapi.md) | FastAPI 核心概念与示例 |
| [fastapi-learning-plan.md](./fastapi-learning-plan.md) | 3 天学习计划（对照本仓库源码） |
| [dependon.md](./dependon.md) | 依赖注入（Depends）总结与实践 |
| [uvicorn.md](./uvicorn.md) | Uvicorn 部署与 worker |
| [framework-comparison.md](./framework-comparison.md) | Web 框架对比 |
| [ddd.md](./ddd.md) | 领域驱动设计 |
| [cqrs.md](./cqrs.md) | CQRS 命令查询分离 |
| [orm.md](./orm.md) | ORM 选型与 SQLAlchemy |
| [aerich.md](./aerich.md) | Tortoise + Aerich 迁移 |
| [pip-vs-uv.md](./pip-vs-uv.md) · [pipx.md](./pipx.md) | Python 包管理工具 |

源码按限界上下文组织：`app/{auth,chat,catalog,system}/` 各含 `interface/` · `application/` · `domain/` · `infrastructure/`（demo 学习路由在 `app/demo/`）。
