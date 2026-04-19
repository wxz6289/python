# 常见大模型与服务平台对照

本文列举当前生态中较常见的模型系列，并说明其**官方或主流访问方式**，便于选型时对照「模型能力」与「部署/合规/成本」。

**时效说明**：下文在 **2026 年 4 月** 左右整理；大模型**名称与生命周期变化很快**，接入前务必以各厂商「模型目录 / 发布说明」与所用云平台控制台为准，并固定业务中的 `model` 字符串版本。

---

## 1. 按厂商与代表模型

| 厂商 / 系列 | 代表模型（示例，随官方更新） | 典型定位 |
|-------------|------------------------------|----------|
| **OpenAI** | GPT-5.x 系列（旗舰与轻量档位）、GPT-4.1 / GPT-4o 系列、**o** 系列（推理向） | 通用对话、多模态、编码与 Agent；API 与工具链成熟 |
| **Anthropic** | Claude 4.x / 3.5 各档位（如 Sonnet、Opus、Haiku 等命名以官方为准） | 长上下文、代码与写作；企业场景常见 |
| **Google** | Gemini 2.x（如 Flash、Pro 等；命名以 Google AI / Vertex 为准） | 长上下文、多模态；与 Google 云、AI Studio 集成 |
| **Meta** | Llama 4.x / 3.x（含视觉等变体） | 开源权重；可自托管或经第三方托管 API |
| **Mistral** | Mistral 大模型系列、Mixtral 等 | 欧洲厂商；开放权重与商业 API 并存 |
| **阿里通义** | Qwen3 系列（如 Max、Coder、开源权重等；具体以 Model Studio / 开源仓库为准） | 中文与代码场景常见；国内 API 与开源并行 |
| **DeepSeek** | DeepSeek-V3、R1（推理）及后续 | 性价比与推理讨论度高；API + 开源 |
| **Cohere** | Command 系列等 | 企业向、检索与 RAG 向能力常见 |
| **xAI** | Grok 系列 | 独立 API |

说明：同一厂商常有「聊天 / 推理 / 代码 / 多模态」多条产品线，**不要**仅凭系列名判断能力，以文档与评测场景为准。

---

## 2. 主要服务平台与特点

| 平台类型 | 代表服务 | 适合场景 |
|----------|----------|----------|
| **厂商官方 API** | OpenAI API、Anthropic API、Google AI Studio / Gemini API、Mistral API、Cohere、xAI 等 | 直连最新能力、按量计费；需处理密钥与区域合规 |
| **云厂商托管** | **Azure OpenAI**、**Azure AI**（多模型）、**AWS Bedrock**、**Google Vertex AI** | 企业合同、VPC、审计与统一账单；常为多模型「一站式」 |
| **聚合与推理云** | **Together**、**Fireworks**、**Replicate**、**Groq**（低延迟推理）等 | 开源权重模型、快速试验、按 token 或按请求 |
| **社区与本地** | **Hugging Face**（模型卡 + Inference / 自托管）、**Ollama**（本机拉模型） | 离线、隐私、算力自付 |
| **国内云与开放平台** | 阿里云（通义 / DashScope / Model Studio）、火山引擎、百度千帆、腾讯混元等 | 国内合规、备案与专线；常与自家模型深度绑定 |

---

## 3. 横向对比维度（选型时怎么用）

| 维度 | 说明 |
|------|------|
| **访问形态** | 仅云端 API / 仅开源权重 / 二者皆有（如 Llama、Qwen、Mistral） |
| **上下文长度** | 长文档、RAG 优先看窗口与「有效利用长上下文」的实际表现 |
| **多模态** | 是否支持图像、音频、视频；是否在同一对话混用 |
| **工具调用** | Function calling / JSON mode 的稳定度因模型与平台而异 |
| **延迟与吞吐** | 实时场景可看专用推理云或选 Flash / mini 档位 |
| **成本** | 按 token 计费；小模型 + 路由可显著降本 |
| **合规与数据驻留** | 金融、医疗、政务常选 Azure / 国内云 / 私有化部署 |
| **可复现与版本** | 生产环境应固定 `model` 名称与版本，避免静默升级 |

---

## 4. 常见组合速查

- **闭源 API、少运维**：OpenAI / Anthropic / Google 官方 API，或 Azure / Vertex 统一开票。
- **要 Llama 类又不想自建集群**：Bedrock、Together、Fireworks 等托管推理。
- **完全离线或内网**：Ollama + 开源权重，或 vLLM / TGI 等自托管推理服务。
- **中文 + 国内合规**：通义、混元、文心等国内平台 API；开源 Qwen 系列可私有化。

---

## 5. 使用建议

1. **先用官方或单一聚合平台做小流量验证**，再决定是否多供应商冗余。
2. **同一业务固定模型版本**，并在日志中记录 `model` 与提示词版本，便于回溯。
3. **别把「平台名字」和「模型名字」混为一谈**：例如「Azure OpenAI」是平台，上面跑的是具体 GPT 系列型号。

如需与仓库内脚本对齐，可结合 `llm/chat-qwen.py` 等示例看各平台 SDK 与鉴权差异。

---

## 6. LangChain 相关 Python 依赖（与模型接入）

LangChain 在 **1.x** 时代采用**元包 + 核心库 + 厂商集成包**结构。下面与 **PyPI 上 `langchain` 包声明**一致（版本会滚动升级，安装前可用 `pip index versions langchain` 自查）。

### 6.1 核心依赖（安装 `langchain` 时常被一并解析）

| 包名 | 作用 |
|------|------|
| **`langchain`** | 元包：聚合常用能力，并声明各「可选集成」的 extra |
| **`langchain-core`** | Runnable、消息、提示词等核心抽象；**`langsmith`** 作为链路追踪依赖常随核心引入 |
| **`langgraph`** | 图状态机 / Agent 编排（`langchain` 1.x 起与主线强相关） |
| **`pydantic`** | 数据校验与模型配置（v2） |

说明：实际项目里也可**只装** `langchain-core` + 需要的 `langchain-xxx`，按官方文档最小安装。

### 6.2 厂商与平台集成包（`pip install "langchain[extra]"` 或单独安装同名包）

下列 extra 名称与 **PyPI `langchain` 包可选依赖**对应（名称即 `pip install "langchain[openai]"` 中的方括号内关键字）：

| extra / 集成包 | 典型对接场景 |
|----------------|--------------|
| **`openai`** → `langchain-openai` | OpenAI 官方 API、Azure OpenAI 等 |
| **`anthropic`** → `langchain-anthropic` | Claude 系列 |
| **`google-genai`** → `langchain-google-genai` | Google Generative AI（Gemini 等，以文档为准） |
| **`google-vertexai`** → `langchain-google-vertexai` | Vertex AI 上的 Gemini 等 |
| **`aws`** → `langchain-aws` | Amazon Bedrock 等 |
| **`azure-ai`** → `langchain-azure-ai` | Azure AI 相关服务 |
| **`mistralai`** → `langchain-mistralai` | Mistral 官方 API |
| **`huggingface`** → `langchain-huggingface` | Hugging Face 模型与推理端点 |
| **`ollama`** → `langchain-ollama` | 本机 Ollama |
| **`groq`** → `langchain-groq` | Groq 推理 API |
| **`fireworks`** → `langchain-fireworks` | Fireworks |
| **`together`** → `langchain-together` | Together AI |
| **`deepseek`** → `langchain-deepseek` | DeepSeek |
| **`xai`** → `langchain-xai` | xAI / Grok |
| **`perplexity`** → `langchain-perplexity` | Perplexity |
| **`baseten`** → `langchain-baseten` | Baseten 托管 |

**社区集成大包**：**`community`** → `langchain-community`（大量第三方向量库、文档加载器、工具等；体积与传递依赖较多，按需安装）。

### 6.3 安装示例

```bash
# 最小：仅核心栈（按你实际 import 调整）
pip install "langchain>=1.2"

# 按需叠加厂商（示例：OpenAI + 社区集成）
pip install "langchain[openai,community]"

# 与上面 extra 等价的一种写法：直接装集成包
pip install langchain-openai langchain-community
```

### 6.4 其他常与 LangChain 搭配、但角色不同的库

| 包名 | 作用 |
|------|------|
| **`langchain-text-splitters`** | 文本切分（RAG 常用），有时单独引用 |
| **`langchain-cohere`** | Cohere 官方集成（单独包；不在 `langchain[...]` 的上述 extra 列表里） |
| **`langsmith`** | 调试、追踪、评估（**`langchain-core` 已依赖其客户端范围**；完整平台能力需在 [LangSmith](https://smith.langchain.com) 配置项目与密钥） |

更多 `langchain-*` 集成可在 [PyPI 搜索 `langchain-`](https://pypi.org/search/?q=langchain-) 或查阅官方集成列表。

### 6.5 版本与 Python 环境

- **以 PyPI 页面为准**：`langchain`、`langchain-core` 的 `Requires-Python` 与依赖范围会随版本更新。
- 生产环境建议在 **`requirements.txt` / `pyproject.toml` 中锁定** `langchain*` 主版本，避免 CI 与本地行为不一致。

官方文档与包索引：**[https://python.langchain.com](https://python.langchain.com)**、**[https://pypi.org/project/langchain/](https://pypi.org/project/langchain/)**。
