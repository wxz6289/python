# uv 核心内容总结

`uv` 是一个高性能的 Python 包与项目管理工具，可替代 `pip`、`virtualenv`、`pip-tools`、部分 `poetry`/`pipenv` 场景。它强调**速度快、命令统一、可复现环境**。

## 1. uv 是什么

- **包管理**：安装、升级、卸载依赖。
- **环境管理**：创建与使用虚拟环境。
- **项目管理**：基于 `pyproject.toml` 管理项目依赖。
- **锁定依赖**：通过锁文件保证多人/多环境安装一致。
- **工具运行**：可临时运行 Python 工具，无需全局安装。

## 2. 为什么使用 uv

- **速度快**：解析与安装依赖明显快于传统 `pip` 工作流。
- **命令统一**：同一套 CLI 覆盖“环境 + 依赖 + 执行”。
- **兼容现代 Python 项目**：围绕 `pyproject.toml` 工作。
- **更容易复现**：锁文件让 CI、本地、生产环境一致性更高。

## 3. 常见工作流

### 3.1 初始化项目

```bash
# 新建项目（会生成 pyproject.toml）
uv init myproj
cd myproj
```

### 3.2 创建虚拟环境

```bash
# 在当前目录创建 .venv
uv venv
```

### 3.3 添加/移除依赖

```bash
# 添加运行时依赖
uv add requests

# 添加开发依赖
uv add --dev pytest ruff

# 移除依赖
uv remove requests
```

### 3.4 安装与同步

```bash
# 根据锁文件/配置同步环境（推荐团队使用）
uv sync
```

### 3.5 运行命令

```bash
# 在项目环境中执行脚本
uv run python main.py

# 在项目环境中执行工具
uv run pytest
uv run ruff check .
```

## 4. 依赖与锁文件

`uv` 通常基于以下文件协作：

- `pyproject.toml`：声明项目元信息与依赖。
- 锁文件（如 `uv.lock`）：记录精确版本与解析结果。

推荐实践：

1. 修改依赖后提交锁文件。
2. 团队与 CI 使用 `uv sync` 保证环境一致。
3. 避免手动改锁文件，交由 `uv` 生成。

## 5. 与 pip 的关系

`uv` 可以覆盖多数 `pip + venv + requirements.txt` 工作流：

- 传统方式：`python -m venv` + `pip install ...`
- uv 方式：`uv venv` + `uv add ...` + `uv sync`

如果你在维护旧项目，仍可逐步迁移，不必一次性重构全部流程。

## 6. 常用命令速查

```bash
# 查看帮助
uv --help

# 查看版本
uv --version

# 初始化项目
uv init

# 创建虚拟环境
uv venv

# 添加依赖
uv add <package>

# 添加开发依赖
uv add --dev <package>

# 删除依赖
uv remove <package>

# 同步依赖
uv sync

# 在环境中运行命令
uv run <command>
```

## 7. 团队实践建议

- **统一入口**：文档与脚本统一使用 `uv run`、`uv sync`。
- **锁文件入库**：将锁文件提交到 Git，避免“我这能跑你那不能跑”。
- **区分依赖类型**：运行时依赖与开发依赖分开维护。
- **CI 一致化**：CI 使用和本地相同命令，减少环境差异。
- **小步迁移**：老项目先接入 `uv run` 和 `uv sync`，再逐步整理依赖声明。
