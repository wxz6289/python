# demo

与 `app/demo/`（挂载在主应用上的学习路由）不同，本目录是**可单独运行**的最小 FastAPI 示例，用于快速试验路径参数等语法。

```bash
cd ai-server
uv run python demo/main.py
```

主服务请使用项目根目录的 `main.py` 或 `uv run uvicorn app.main:app --reload`。
