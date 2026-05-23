# pip 与 uv 详解与对比

本文分别介绍 Python 生态中 **pip**（传统包管理器）与 **uv**（新一代工具链）的特性与用法，并在最后给出详细对比，便于在项目中选型与迁移。

---

## 一、pip

### 1.1 是什么

**pip**（*Pip Installs Packages*）是 Python 官方推荐的第三方包安装与管理工具，随 Python 3.4+ 起通常已内置（或通过 `ensurepip` 提供）。它从 [PyPI](https://pypi.org/)（及私有索引）下载并安装 **wheel** 或 **源码包（sdist）**，是 Python 生态使用最广泛的包管理器。

pip 本身**只负责安装包**，不内置项目级工作流；虚拟环境、锁文件、Python 版本管理通常需要配合 `venv`、`requirements.txt`、`pip-tools` 等工具完成。

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **PyPI 原生支持** | 默认从 PyPI 解析并安装包，支持 `--index-url` / `--extra-index-url` 切换源 |
| **依赖解析** | 根据包元数据解析传递依赖，安装满足约束的版本 |
| **多种安装目标** | 可安装到系统 Python、用户目录（`--user`）、或当前激活的虚拟环境 |
| **格式支持** | wheel（优先）、sdist；支持 `--no-binary` / `--only-binary` |
| **可编辑安装** | `pip install -e .` 用于本地开发，修改源码即时生效 |
| **卸载与查询** | `pip uninstall`、`pip show`、`pip list` |
| **导出依赖** | `pip freeze` 导出已安装包列表（常用于生成 `requirements.txt`） |
| **配置文件** | 支持 `pip.conf` / `pip.ini`，可配置默认源、trusted-host 等 |
| **PEP 517/518** | 支持现代 `pyproject.toml` 构建后端（如 hatchling、setuptools） |

### 1.3 常见用法

#### 安装与升级

```bash
# 安装单个包
pip install requests

# 指定版本
pip install "fastapi>=0.100,<0.110"

# 从 requirements 安装
pip install -r requirements.txt

# 升级包
pip install -U requests

# 卸载
pip uninstall requests
```

#### 虚拟环境（需配合 venv）

```bash
# 创建虚拟环境
python -m venv .venv

# 激活（macOS/Linux）
source .venv/bin/activate

# 激活（Windows）
.venv\Scripts\activate

# 在虚拟环境中安装
pip install -r requirements.txt
```

#### 开发与可编辑安装

```bash
# 以可编辑模式安装当前项目
pip install -e .

# 同时安装可选依赖（若 pyproject.toml 中定义了 extras）
pip install -e ".[dev]"
```

#### 导出与锁文件（传统方式）

```bash
# 导出当前环境全部包（含传递依赖，版本固定）
pip freeze > requirements.txt

# 仅生产依赖时，常手写 requirements.in，再用 pip-tools：
# pip-compile requirements.in -o requirements.txt
# pip-sync requirements.txt
```

#### 常用查询

```bash
pip list                 # 已安装包列表
pip show fastapi         # 包详情
pip check                # 检查依赖冲突
pip index versions pydantic  # 查看 PyPI 上可用版本（pip 21.2+）
```

#### 国内镜像加速

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests

# 或写入 pip.conf
# [global]
# index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

### 1.4 典型项目工作流（pip 体系）

```text
requirements.in          # 人工维护顶层依赖
    ↓ pip-compile
requirements.txt         # 锁定全部传递依赖版本
    ↓ pip install -r
.venv/                   # python -m venv 手动创建
    ↓
运行：source .venv/bin/activate && python main.py
```

或使用 `pyproject.toml` 声明依赖，但仍需 `pip install .` 或 `pip install -e .`，锁文件需额外工具（pip-tools、Poetry 等）。

### 1.5 优势与局限

**优势：**

- 官方生态标准，文档与社区资源极多
- 几乎所有 Python 环境都支持
- 行为成熟、兼容面广

**局限：**

- **速度**：依赖解析与下载相对较慢（纯 Python 实现）
- **无内置锁文件**：`pip freeze` 粗粒度，需 pip-tools 等补充
- **无内置项目管理**：Python 版本、venv、运行脚本需多工具拼装
- **可复现性**：仅靠 `requirements.txt` 时，不同平台/时间可能解析结果略有差异（除非完全 pin 版本）

---

## 二、uv

### 2.1 是什么

**uv** 由 [Astral](https://astral.sh/)（Ruff 同一团队）用 **Rust** 编写，定位为 **Python 包与项目管理器**。它可替代或封装：

- **pip** / **pip-tools**（安装、锁依赖）
- **venv** / **virtualenv**（虚拟环境）
- 部分 **pipx** 场景（`uv tool`）
- 部分 **pyenv** 场景（`uv python` 管理 Python 版本）

在本项目（ai-server）中，依赖声明在 `pyproject.toml`，锁文件为 `uv.lock`，安装与运行统一用 uv 完成。

### 2.2 核心特性

| 特性 | 说明 |
|------|------|
| **极快** | Rust 实现，解析、下载、安装通常比 pip 快一个数量级以上 |
| **统一锁文件** | `uv.lock` 跨平台锁定完整依赖树，可复现构建 |
| **项目管理** | `uv init` / `uv add` / `uv sync` 一体化工作流 |
| **自动 venv** | `uv sync` 自动创建/更新 `.venv`，无需手动 activate |
| **uv run** | 在项目环境中执行命令，自动使用正确 Python 与依赖 |
| **Python 版本管理** | `uv python install 3.12`、`uv python pin 3.12` |
| **pip 兼容层** | `uv pip install` 可作为 pip  drop-in 使用 |
| **全局工具** | `uv tool install ruff` 类似 pipx |
| **依赖组** | 支持 `[dependency-groups]`（PEP 735）与 optional-dependencies |
| **索引与缓存** | 全局缓存 wheel，多项目共享；支持自定义 index |

### 2.3 常见用法

#### 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip（一次性 bootstrap）
pip install uv
```

#### 项目初始化与依赖

```bash
# 新建项目
uv init my-project
cd my-project

# 添加生产依赖（写 pyproject.toml + 更新 uv.lock）
uv add fastapi uvicorn

# 添加开发依赖
uv add --dev pytest httpx

# 或使用 dependency-groups（PEP 735）
uv add --group dev pytest-asyncio
```

#### 同步环境（核心命令）

```bash
# 按 uv.lock 安装依赖，创建/更新 .venv
uv sync

# 包含 optional extras（如 pyproject 中的 dev）
uv sync --extra dev

# 包含 dependency group
uv sync --group dev

# 不安装项目本身（仅依赖）
uv sync --no-install-project
```

#### 锁文件

```bash
# 根据 pyproject.toml 重新解析并生成/更新 uv.lock
uv lock

# 升级所有依赖到最新兼容版本
uv lock --upgrade

# 仅升级某个包
uv lock --upgrade-package fastapi
```

#### 运行（无需 activate）

```bash
# 在项目虚拟环境中执行
uv run python main.py
uv run pytest
uv run uvicorn app.main:app --reload

# 运行一次性脚本并临时加依赖
uv run --with httpx python script.py
```

#### Python 版本

```bash
# 安装指定 Python
uv python install 3.12

# 固定项目 Python 版本（写入 .python-version）
uv python pin 3.12

# 列出可用/已安装版本
uv python list
```

#### pip 兼容命令

```bash
# 在当前 uv 管理的 venv 中，语法类似 pip
uv pip install requests
uv pip list
uv pip freeze

# 从 requirements.txt 安装
uv pip install -r requirements.txt
```

#### 全局 CLI 工具

```bash
uv tool install ruff
uv tool run ruff check .
```

### 2.4 典型项目工作流（uv 体系）

以 **ai-server** 为例：

```text
pyproject.toml           # 声明项目元数据与顶层依赖
    ↓ uv lock
uv.lock                  # 完整锁定依赖树（提交 Git）
    ↓ uv sync --extra dev
.venv/                   # 自动创建
    ↓
运行：uv run python main.py
测试：uv run pytest
```

对应命令：

```bash
cd ai-server
uv sync --extra dev      # 安装生产 + dev 依赖
uv run python main.py    # 启动服务
uv run pytest            # 运行测试
uv add sqlalchemy        # 新增依赖并更新 lock
```

### 2.5 优势与局限

**优势：**

- **速度快**：安装与锁依赖显著快于 pip + pip-tools
- **开箱即用**：项目初始化、venv、锁文件、运行一条链完成
- **可复现性强**：`uv.lock` 保证团队/CI 环境一致
- **与 pyproject.toml 深度集成**：符合现代 Python 打包标准

**局限：**

- 相对较新，部分边缘场景或企业内部流程可能仍按 pip 文档建设
- 团队需学习新命令（虽与 pip 概念高度对应）
- 极个别老旧/非标准包在 uv 下可能需要 `uv pip` 或额外配置

---

## 三、pip 与 uv 详细对比

### 3.1 定位与范围

| 维度 | pip | uv |
|------|-----|-----|
| **定位** | 包安装器 | 包安装器 + 项目管理器 + 工具链 |
| **实现语言** | Python | Rust |
| **官方地位** | Python 内置/官方推荐安装器 | 第三方（Astral），生态快速增长 |
| **替代关系** | — | 可替代 pip、pip-tools、venv、部分 pipx/pyenv |

### 3.2 依赖声明与锁文件

| 维度 | pip | uv |
|------|-----|-----|
| **依赖声明** | `requirements.txt`、`pyproject.toml`、setup.cfg |  primarily `pyproject.toml` |
| **锁文件** | 无内置；常用 `pip freeze` 或 **pip-tools** 的 `requirements.txt` | 内置 **`uv.lock`** |
| **锁粒度** | freeze 为已安装列表；pip-compile 为解析结果 | 全依赖树哈希锁定，跨平台 |
| **更新锁** | `pip-compile -U` | `uv lock --upgrade` |
| **可复现安装** | 需纪律性提交 lock 文件 | `uv sync` 严格按 lock 安装 |

### 3.3 虚拟环境与 Python 版本

| 维度 | pip | uv |
|------|-----|-----|
| **创建 venv** | `python -m venv .venv`（另需手动） | `uv venv` 或 **`uv sync` 自动创建** |
| **激活 venv** | `source .venv/bin/activate` | 通常 **不需要**；用 `uv run` |
| **Python 版本** | pyenv / 系统 Python / 手动安装 | **`uv python install` / `uv python pin`** |
| **运行命令** | activate 后 `python` / `pytest` | **`uv run python`** / **`uv run pytest`** |

### 3.4 安装速度与体验

| 维度 | pip | uv |
|------|-----|-----|
| **解析速度** | 中等 | 快 |
| **下载与安装** | 中等 | 快（并行 + 全局缓存） |
| **冷启动大项目** | 明显等待 | 通常秒级完成 |
| **缓存** | 有 pip 缓存 | 统一全局缓存，多项目复用 |

### 3.5 常用命令对照

| 场景 | pip 体系 | uv |
|------|----------|-----|
| 安装依赖 | `pip install -r requirements.txt` | `uv sync` |
| 添加依赖 | 手改 requirements.in + pip-compile | `uv add package` |
| 开发安装 | `pip install -e ".[dev]"` | `uv sync --extra dev` |
| 导出锁 | `pip freeze` / `pip-compile` | `uv lock`（已自动生成） |
| 运行脚本 | `python main.py`（需先 activate） | `uv run python main.py` |
| 运行测试 | `pytest` | `uv run pytest` |
| 安装 CLI 工具 | `pipx install ruff` | `uv tool install ruff` |
| 兼容 pip 语法 | — | `uv pip install ...` |

### 3.6 配置文件

| 文件 | pip | uv |
|------|-----|-----|
| 项目依赖 | `pyproject.toml` / `requirements.txt` | **`pyproject.toml`** |
| 锁文件 | `requirements.txt`（pip-tools） | **`uv.lock`** |
| Python 版本 | `.python-version`（pyenv） | **`.python-version`**（uv 同样支持） |
| 索引/源 | `pip.conf` | `uv.toml` / 环境变量 / 命令行 `--index-url` |

### 3.7 CI/CD 与团队协作

| 维度 | pip | uv |
|------|-----|-----|
| **CI 安装** | `pip install -r requirements.txt` | `uv sync --frozen`（严格按 lock，不改动） |
| **一致性** | 依赖 lock 是否提交、是否用 compile | **`uv.lock` 提交 Git 为标准做法** |
| **新人上手** | venv + activate + pip install 多步 | `uv sync` + `uv run` 两步 |

CI 示例（uv）：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync --frozen --extra dev
uv run pytest
```

### 3.8 迁移参考（pip → uv）

已有 `requirements.txt` 的项目：

```bash
# 在项目根目录
uv init --app          # 若尚无 pyproject.toml
uv add $(cat requirements.txt | grep -v '^#' | tr '\n' ' ')
uv lock
uv sync
```

之后删除或归档 `requirements.txt`，以 `pyproject.toml` + `uv.lock` 为准。

本仓库已采用 uv，新依赖请使用：

```bash
uv add <package>           # 生产依赖
uv add --group dev <package>  # 开发依赖组
```

### 3.9 选型建议

| 场景 | 建议 |
|------|------|
| **新项目** | 优先 **uv**：锁文件、速度、项目管理一体 |
| **学习/极简脚本** | **pip** + venv 足够 |
| **遗留项目** | 可继续 pip；迁移 uv 成本低，尤其已有 `pyproject.toml` |
| **企业内网/固定 pip 流程** | 暂用 pip；或用 **`uv pip`** 加速安装 |
| **与本 ai-server 一致** | **uv sync / uv run / uv add** |

---

## 四、总结

- **pip** 是 Python 包安装的**事实标准**：轻量、 universal，但完整「可复现项目」需自己组合 venv、requirements、pip-tools 等。
- **uv** 是**现代 Python 项目工具链**：在兼容 pip 生态的前提下，用 `pyproject.toml` + `uv.lock` + `uv sync` + `uv run` 覆盖依赖安装、环境隔离与日常开发命令，并显著提速。

两者不是互斥关系：uv 提供 **`uv pip`** 子命令，可在需要时完全按 pip 习惯操作；长期项目维护则更推荐 uv 的项目模式，与本仓库 README 中的工作流保持一致。

---

## 参考链接

| 资源 | URL |
|------|-----|
| pip 官方文档 | https://pip.pypa.io/ |
| uv 官方文档 | https://docs.astral.sh/uv/ |
| pipx 详解（本项目） | [pipx.md](./pipx.md) |
| PEP 621（pyproject 项目元数据） | https://peps.python.org/pep-0621/ |
| PEP 735（dependency-groups） | https://peps.python.org/pep-0735/ |
| 本项目 README | [../README.md](../README.md) |
