# Python 学习与实验 monorepo

本仓库聚合多个独立的 Python 子项目与示例代码，彼此目录隔离、依赖各自管理。

## 子项目一览

| 目录 | 说明 | 入口 |
|------|------|------|
| [ai-server](./ai-server/) | FastAPI + LangChain 命理对话服务（DDD 分层、Tortoise ORM） | [README](./ai-server/README.md) · `cd ai-server && uv run python main.py` |
| [llm](./llm/) | LangChain / Agent / RAG 等编号示例脚本 | 在 `llm/` 下 `python NN-*.py` |
| [LlamaIndex](./LlamaIndex/) | LlamaIndex 示例（**git submodule**） | 子模块内 README |
| [data-analysis](./data-analysis/) | 数据分析（如 pandas-for-everyone） | 各子目录 README |
| [deep-learning](./deep-learning/) | 深度学习相关笔记与代码 | — |
| [tiny_python_projects](./tiny_python_projects/) | 《Tiny Python Projects》练习 | 子目录 README |
| [web-claw](./web-claw/) | 爬虫与 Web 相关（含 scrapybook） | — |
| [doc](./doc/) | 通用学习笔记 | — |
| [scripts](./scripts/) | 仓库脚本（如 [git-hooks](./scripts/git-hooks/)） | — |

## 推荐工作方式

- **只开发 ai-server**：用 Cursor/VS Code 打开 [`ai-server/ai-server.code-workspace`](./ai-server/ai-server.code-workspace)，在子目录执行 `uv sync`。
- **在 monorepo 根目录做类型检查**：根目录 [`pyrightconfig.json`](./pyrightconfig.json) 已配置 `ai-server` 执行环境；`ai-server` 内另有独立 [`pyrightconfig.json`](./ai-server/pyrightconfig.json)。
- **克隆含子模块**：`git clone --recurse-submodules …` 或 `git submodule update --init --recursive`。

## Python 语言备忘

简单易用；高级数据结构；模块化；解释型；可扩展 C/C++。

- 高级数据类型允许在单一语句中表述复杂操作；
- 使用缩进，而不是括号实现代码块分组；
- 无需预声明变量或参数。

### 代码风格

- 使用 4 个空格缩进，不要混用 Tab
- 函数之间空一行，类之间空两行
- `,` 与字典 `:` 后加空格；赋值/比较运算符两侧加空格，括号内侧不加
