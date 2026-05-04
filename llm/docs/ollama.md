# Ollama 核心内容总结

Ollama 是一个用于本地运行大语言模型（LLM）的工具，支持在 macOS、Linux、Windows 上快速拉取并运行开源模型，适合离线开发、隐私敏感场景与本地原型验证。

## 1. Ollama 能做什么

- 本地运行模型：无需把数据发到外部云端。
- 统一模型管理：拉取、查看、删除模型都可通过命令行完成。
- 支持 API 调用：可通过 HTTP 接口接入 Python、Node.js、LangChain 等应用。
- 支持自定义模型：可通过 `Modelfile` 对模型进行系统提示词和参数定制。

## 2. 安装与服务

安装完成后通常会启动本地服务（默认端口 `11434`）。

- macOS：下载官方安装包安装。
- Linux：使用官方脚本安装。
- Windows：安装官方桌面版。

检查是否可用：

```bash
ollama --version
ollama list
```

## 3. 常用命令（高频）

### 模型管理

```bash
# 拉取模型
ollama pull qwen2.5:7b

# 查看本地模型
ollama list

# 查看模型详情
ollama show qwen2.5:7b

# 删除模型
ollama rm qwen2.5:7b
```

### 运行与对话

```bash
# 启动交互式对话
ollama run qwen2.5:7b

# 单次提问
ollama run qwen2.5:7b "请用三句话解释什么是向量数据库"
```

## 4. HTTP API 核心接口

Ollama 提供本地 REST API（默认地址 `http://localhost:11434`）。

### 4.1 生成文本（Generate）

`POST /api/generate`

常见字段：

- `model`: 模型名称，如 `qwen2.5:7b`
- `prompt`: 用户输入
- `stream`: 是否流式返回（`true/false`）

### 4.2 聊天接口（Chat）

`POST /api/chat`

常见字段：

- `model`: 模型名称
- `messages`: 聊天消息数组（`role` + `content`）
- `stream`: 流式开关

### 4.3 Embeddings（向量）

`POST /api/embeddings`

用于把文本转换为向量，可用于语义检索、RAG 等场景。

## 5. Modelfile（自定义模型行为）

可以通过 `Modelfile` 设定系统提示词、温度参数和基础模型，实现团队内可复用的模型配置。

示例：

```dockerfile
FROM qwen2.5:7b
SYSTEM 你是一个简洁、专业的中文技术助手。
PARAMETER temperature 0.3
```

构建与运行：

```bash
ollama create my-assistant -f Modelfile
ollama run my-assistant
```

## 6. 典型开发流程

1. 选择模型并拉取（`ollama pull`）。
2. 命令行验证效果（`ollama run`）。
3. 通过 `/api/chat` 接入业务代码。
4. 若需固定风格和参数，使用 `Modelfile` 创建自定义模型。
5. 结合向量库与检索构建本地 RAG 应用。

## 7. 使用建议

- **模型选型**：先从 `7B` 级别开始，兼顾效果和资源占用。
- **资源评估**：关注内存（RAM）与 CPU/GPU 能力，模型越大开销越高。
- **流式输出**：聊天产品优先开启 `stream`，提升交互体验。
- **提示词规范化**：把角色与约束写入系统提示，减少回答漂移。
- **本地日志与安全**：生产环境中避免记录敏感原文，注意接口访问控制。
