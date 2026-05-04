# 新版 LangChain 的 Text Embedding Model 总结与最佳实践

## 1. Embedding 是什么

- Text Embedding 是把文本映射为高维向量，用于计算语义相似度。
- 在 RAG 中，Embedding 主要用于两件事：
  - **离线建库**：把文档 chunk 向量化并写入向量库
  - **在线检索**：把用户 query 向量化后做相似检索
- 关键认知：Embedding 决定“能不能召回相关证据”，LLM 决定“如何组织答案”。

---

## 2. 新版 LangChain 中 Embedding 的接口变化

新版 LangChain 强调“集成包拆分”，常见模式是：

- 核心抽象在 `langchain_core`
- 各厂商集成在独立包（如 `langchain_openai`、`langchain_community` 等）

典型用法（OpenAI）：

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vec = embeddings.embed_query("LangChain 的 embedding 怎么用？")
```

两个常用方法：

- `embed_documents(texts: list[str]) -> list[list[float]]`
- `embed_query(text: str) -> list[float]`

实践约束：

- `query` 和 `documents` 必须使用同一 embedding 模型（同一向量空间）。
- 建库后不要随意切换模型，否则需要重建索引。

---

## 3. 常见 Text Embedding 模型（选型视角）

> 不同提供商会持续更新型号，这里强调选型原则与常见类别，不绑定单一厂商。

### 3.1 高质量通用模型

- 特点：语义效果好，多语言泛化强。
- 适合：企业知识库、复杂问答、跨领域检索。
- 代价：价格通常更高，向量维度可能更大。

### 3.2 轻量/低成本模型

- 特点：成本低、速度快，适合高吞吐。
- 适合：FAQ、短文本检索、预算敏感系统。
- 风险：复杂语义召回能力可能弱于高端模型。

### 3.3 本地开源 embedding 模型

- 特点：可私有化部署、数据不出域、可控性强。
- 适合：隐私合规、离线环境、边缘场景。
- 风险：需要自行维护推理服务和模型升级。

---

## 4. 新版 LangChain 常见接入方式

### 4.1 OpenAI Embeddings

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)
```

### 4.2 HuggingFace（本地/开源）

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

### 4.3 其他云厂商/向量平台

- 新版一般都通过独立集成包提供 Embeddings 类。
- 接入思路一致：初始化 embedding 实例 -> `embed_documents`/`embed_query` -> 交给向量库。

---

## 5. 与向量库的标准组合（LCEL/RAG 常用）

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

# chunks: List[Document]
vectorstore = FAISS.from_documents(chunks, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
```

在线查询时：

1. retriever 内部对 query 做 embedding  
2. 在向量库中做相似搜索  
3. 返回 top-k 文档给后续 prompt + LLM

---

## 6. Embedding 最佳实践（重点）

## 6.1 模型选型策略

- **默认起步**：先用一个质量稳定的通用模型做 baseline。
- **再做对比**：选 2-3 个候选模型，用同一测试集评估召回指标。
- **最终按业务目标取舍**：准确率优先 vs 延迟/成本优先。

## 6.2 文档预处理策略

- 去重（完全重复/高度重复段落）
- 清噪（导航、页眉页脚、版权模板）
- 统一编码与标点（尤其多源数据）
- 保留关键 metadata（source/page/section/doc_id）

说明：垃圾输入会稳定地产生垃圾向量，后续很难补救。

## 6.3 拆分策略与 embedding 联动

- chunk 太大：语义混杂，检索不聚焦
- chunk 太小：上下文碎片化，答案缺上下文
- 建议先用：
  - `chunk_size`: 600-1000（中文通用）
  - `chunk_overlap`: 80-150
- 然后基于真实 query 集迭代调参。

## 6.4 索引与检索参数

- `k` 不宜盲目增大（会加噪声）
- 通常先试 `k=3~6`
- 建议加 `score_threshold` 或后处理重排（rerank）
- 可结合 metadata filter（按租户、时间、文档类型过滤）

## 6.5 版本与一致性管理

- 在索引 metadata 中记录：
  - `embedding_model`
  - `embedding_version`
  - `chunk_strategy_version`
- 任何一项变化都要可追踪，便于回滚与 A/B。

## 6.6 增量更新与重建策略

- 新文档：增量入库
- 文档更新：按 `doc_id` upsert
- 大版本变更（模型切换/切分策略大改）：建议全量重建索引

## 6.7 多语言实践

- 混合语种场景优先选择多语言表现稳定的 embedding 模型
- 中文分词边界复杂，建议加结构化切分（标题/段落）减少语义断裂
- 评估集要覆盖中英混问，不要只测单语

## 6.8 成本优化

- 预计算文档向量，避免重复 embedding
- 缓存 query embedding（短时间窗口）
- 对低价值数据源降低更新频率
- 优先优化数据质量，再扩模型规格

---

## 7) 评估体系（没有评估就没有“最佳实践”）

建议至少建立三层指标：

### 7.1 检索层

- Recall@k（真实相关文档是否被召回）
- MRR / nDCG（排序质量）
- 命中率（top-k 中是否包含金标准证据）

### 7.2 答案层

- 引用充分性（答案是否引用到正确 source）
- 事实一致性（是否与证据冲突）
- 不可答问题的拒答率（防幻觉）

### 7.3 系统层

- P50/P95 延迟
- 单请求成本（embedding + LLM）
- 索引体积、更新时长

---

## 8. 端到端推荐配置（可作为初始模板）

适用于中小规模中文知识库：

- Loader：按数据源分批加载（PDF/Web/Markdown）
- Splitter：`RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)`
- Embedding：一个稳定的通用高质量模型
- Vector DB：FAISS（本地）或托管向量库（生产）
- Retriever：`k=4` + metadata filter
- 可选增强：rerank + query rewrite

---

## 9. 常见错误与排查

- **错误 1：更换 embedding 模型但不重建索引**  
  现象：召回质量突然下降。  
  原因：向量空间不一致。  
  处理：全量重建。

- **错误 2：只调模型，不清理数据**  
  现象：怎么换模型都不稳。  
  原因：噪声文本主导召回。  
  处理：先做清洗和去重。

- **错误 3：chunk 策略固定不评估**  
  现象：某些问题总是召回不到。  
  原因：粒度不匹配业务问题。  
  处理：建立 query 基准集做 A/B。

- **错误 4：只看最终回答，不看检索证据**  
  现象：排障困难。  
  原因：缺少中间可观测性。  
  处理：记录 top-k 文档与相似度分数。

---

## 10) 最小可用代码骨架（新版 LangChain）

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def build_retriever(chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vs = FAISS.from_documents(chunks, embeddings)
    return vs.as_retriever(search_kwargs={"k": 4})

def retrieve(retriever, question: str):
    docs = retriever.get_relevant_documents(question)
    return docs
```

---

## 11) 一句话结论

新版 LangChain 里的 text embedding 实践核心不是“选最贵模型”，而是：  
**模型选型 + 高质量切分 + 干净数据 + 可观测评估 + 稳定版本治理** 的组合优化。
