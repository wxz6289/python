# Streamlit 核心内容与最佳实践

## 1. Streamlit 是什么

Streamlit 是一个面向 Python 开发者的“快速构建数据应用/AI 应用”框架。
核心特点是：不用写前后端分离代码，只用 Python 脚本就能生成交互式 Web 页面。

典型场景：

- 数据分析看板
- 模型推理演示（NLP/CV/LLM）
- 内部工具原型
- AI Agent 可视化交互界面

---

## 2. 运行方法

### 2.1 安装

```bash
pip install streamlit
```

如果项目使用虚拟环境，先激活环境后再安装和运行。

### 2.2 最小启动命令

假设入口文件是 `app.py`：

```bash
streamlit run app.py
```

如果当前项目里的脚本是 `llm/learn-streamlit.py`，可以这样运行：

```bash
streamlit run llm/learn-streamlit.py
```

启动后，终端通常会显示本地访问地址：

```text
Local URL: http://localhost:8501
```

### 2.3 指定端口和地址

```bash
streamlit run app.py --server.port 8502
```

如果需要在局域网或服务器中访问：

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

### 2.4 常用运行参数

```bash
streamlit run app.py \
  --server.port 8501 \
  --server.headless true
```

常见参数：

- `--server.port`：指定端口。
- `--server.address`：指定监听地址。
- `--server.headless true`：服务器环境运行时不自动打开浏览器。

### 2.5 停止应用

在运行 Streamlit 的终端按：

```bash
Ctrl + C
```

即可停止服务。

---

## 3. 核心运行机制（必须理解）

### 3.1 脚本自上而下重跑

Streamlit 每次用户交互（按钮点击、输入变化）后，默认会触发脚本重新执行。
这带来两个关键结论：

- 页面状态需要显式保存（`st.session_state`）
- 耗时计算需要缓存（`st.cache_data` / `st.cache_resource`）

### 3.2 声明式 UI

你写的 Python 代码即页面声明，组件按执行顺序渲染。

---

## 4. 常用核心 API

### 4.1 页面与布局

- `st.set_page_config()`：页面标题、图标、布局
- `st.title/header/subheader/markdown/write`：文本展示
- `st.columns()`：多列布局
- `st.tabs()`：标签页
- `st.expander()`：可折叠区域
- `st.sidebar`：侧边栏参数区

### 4.2 输入组件

- `st.text_input`, `st.text_area`
- `st.number_input`, `st.slider`
- `st.selectbox`, `st.multiselect`, `st.radio`
- `st.file_uploader`
- `st.button`, `st.form_submit_button`

### 4.3 输出组件

- `st.dataframe`, `st.table`
- `st.metric`
- `st.line_chart`, `st.bar_chart`, `st.pyplot`, `st.plotly_chart`
- `st.image`, `st.audio`, `st.video`
- `st.json`, `st.code`

### 4.4 交互反馈

- `st.spinner()`：耗时操作提示
- `st.progress()`：进度条
- `st.toast()`, `st.success/warning/error/info`

---

## 5. 状态管理最佳实践

### 5.1 使用 `st.session_state` 保存会话状态

适合保存：

- 表单输入中间值
- 当前选中的对象
- 多轮对话记录（Chat 历史）
- 分页和筛选条件

建议：

- 统一用 `if "key" not in st.session_state` 初始化
- key 命名加前缀（如 `chat_messages`, `filters_region`）
- 对复杂对象做浅拷贝，避免意外引用修改

### 5.2 避免“按钮即消失”问题

按钮返回值只在当次 rerun 为 `True`。
如果动作需要持续状态，点击后应立即写入 `session_state`。

---

## 6. 缓存与性能优化

### 6.1 两种缓存的职责

- `st.cache_data`：缓存“数据结果”（DataFrame、列表、字典等）
- `st.cache_resource`：缓存“重量资源”（模型、数据库连接、客户端）

### 6.2 推荐策略

- 读取 CSV/SQL/API 用 `cache_data`
- 加载 LLM、embedding 模型、向量库 client 用 `cache_resource`
- 设置合理 TTL（比如 5 分钟、1 小时）避免旧数据长期不刷新

### 6.3 性能常见坑

- 每次 rerun 重新加载大模型（应放 `cache_resource`）
- 大表每次全量重算（应缓存中间结果）
- 重复调用外部 API（应加缓存 + 限流）

---

## 7. 表单与回调实践

### 7.1 `st.form` 适合“批量提交”

当多个输入项要一次提交时，用 `st.form` 可避免每个输入都触发 rerun。

### 7.2 回调函数

可使用 `on_change` / `on_click` 管理副作用逻辑。
建议把回调逻辑写成纯函数，减少对全局变量的依赖。

---

## 8. Streamlit 做 LLM / Agent 的建议

### 8.1 Chat 结构建议

- `st.chat_input` 接收用户输入
- `st.chat_message` 渲染多轮消息
- 历史放 `st.session_state.messages`

### 8.2 与 LangChain 集成

- 把 LLM/向量库/检索器放 `st.cache_resource`
- 把对话上下文放 `session_state`
- 通过 `st.spinner` 提示推理中状态
- 异常捕获后用 `st.error` 给出可理解提示

### 8.3 长响应体验

- 使用流式输出（token streaming）提升感知速度
- 对长文本分块显示，避免页面卡顿

---

## 9. 项目结构建议

建议目录结构：

- `app.py`：入口
- `pages/`：多页面
- `components/`：可复用 UI 组件
- `services/`：数据/模型/外部 API 调用
- `state/`：状态管理
- `utils/`：公共函数
- `.streamlit/config.toml`：主题和运行配置

保持“UI 层”和“业务层”分离，避免所有逻辑塞在一个脚本里。

---

## 10. 部署与运维实践

### 10.1 常见部署方式

- Streamlit Community Cloud（快速）
- Docker + 云主机（灵活）
- 内网服务器（企业内部工具）

### 10.2 配置建议

- `server.headless=true`
- `server.enableCORS` 按需配置
- 通过环境变量管理密钥（不要硬编码）

### 10.3 可观测性

- 记录关键交互日志（请求、耗时、错误）
- 对外部服务调用做超时和重试
- 给核心路径加埋点（首屏时间、接口耗时）

---

## 11. 安全最佳实践

- 所有密钥放环境变量或密钥管理系统
- 上传文件做类型/大小校验
- 用户输入统一做清洗和长度限制
- 如果接 LLM，增加提示注入防护策略
- 高风险操作（删除/写库）加二次确认

---

## 12. 典型开发流程（推荐）

1. 先做最小 MVP 页面（核心输入 + 核心输出）
2. 加 `session_state` 让流程可连续
3. 加缓存优化性能
4. 抽离服务层与组件层
5. 加错误处理和日志
6. 最后做样式和部署

---

## 13. 一句话总结

Streamlit 的本质是：**Python 驱动的声明式前端 + rerun 执行模型**。
掌握 `session_state`、缓存和模块化结构，就能把 Demo 做成可维护的生产应用。
