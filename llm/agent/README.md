# lang-smith

## 依赖版本（与 `deepagents` 对齐）

`deepagents` 依赖 **`langchain>=1.2.15`**，但其中 **`langchain==1.2.15` 不含 `langchain.agents.AgentState`**，会导致：

```text
ImportError: cannot import name 'AgentState' from 'langchain.agents'
```

解决：**升级到至少 `langchain>=1.2.17`**（本项目 `pyproject.toml` 已约束）。

```bash
# conda / pip 全局环境
pip install -U "langchain>=1.2.17"

# 或使用本目录 uv 锁定的依赖（推荐）
cd lang-smith && uv sync && uv run python 02-deepagent.py
```

详见上游：`deepagents` 的 `Requires-Dist` 与 [Deep Agents 文档](https://docs.langchain.com/oss/python/deepagents/overview)。
