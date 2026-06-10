# Python 语言学习

Python 3.10+ 语法与标准库笔记、示例代码与 Notebook 实验环境。

## 目录结构

```
python/
├── docs/              # 结构化 Markdown 教程（推荐阅读）
├── notebook/          # 原始 Notebook，供交互实验
├── asyncio/           # 协程与异步 I/O 专题
├── code/              # 独立练习脚本
├── sys/               # sys 模块小示例
├── test/              # 测试数据文件
└── todo.md            # 学习进度清单
```

## 推荐阅读路径

1. **基础语法**：按 [docs/README.md](docs/README.md) 中 01–11 的顺序阅读。
2. **标准库专题**：完成基础后阅读 [docs/topics/](docs/topics/) 下的模块文档。
3. **异步编程**：阅读 [asyncio/asyncio.md](asyncio/asyncio.md) 并运行 `asyncio/` 下示例。
4. **动手练习**：在 `code/` 或对应 Notebook 中验证。

## 文档与 Notebook 对应

| 源 Notebook | Markdown 文档 |
|-------------|---------------|
| `0.basic.ipynb` | 01、09、10 |
| `1.statement.ipynb` | 02 |
| `2.funtion.ipynb` | 03 |
| `3.std.ipynb` | 04 |
| `4.execption.ipynb` | 05 |
| `6.file.ipynb` | 07 |
| 其余 `.ipynb` | `topics/` 下对应文件 |

Notebook 保留用于交互实验；日常查阅以 `docs/` 为准。

## 相关子项目

本目录位于 [Python monorepo](../README.md) 内。Web 服务、LLM、数据分析等见仓库根目录 README。
