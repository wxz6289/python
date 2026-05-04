# LangChain Retrievers 核心总结与最佳实践

## 1. Retriever 是什么

- Retriever 是“检索器”，负责根据用户问题找出相关文档片段（`Document`）。
- 它不负责最终回答生成，核心职责是“把对的证据找回来”。
- 在 RAG 链路中，Retriever 位于 LLM 前面，直接决定回答质量上限。

一句话：Retriever 做得好，LLM 才有高质量上下文可用。

---

## 2. 在 RAG 中的位置与作用

标准链路：

`Loader -> Splitter -> Embeddings -> Vector Store -> Retriever -> Prompt -> LLM`

Retriever 的关键价值：

- 语义召回：从大规模知识库中找相关 chunk
- 结果裁剪：控制上下文长度和噪声
- 安全过滤：按 metadata 做租户/权限隔离
- 稳定性控制：通过阈值、重排、融合策略提升准确率

---

## 3. LangChain 中 Retriever 的统一抽象

在新版 LangChain 中，Retriever 是标准 `Runnable`，常用调用方式：

- `invoke(query)`：单次检索
- `batch(queries)`：批量检索
- `ainvoke(query)`：异步检索

典型构造方式：

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
docs = retriever.invoke("如何做增量索引？")
```

返回值通常是 `List[Document]`，每个文档含 `page_content + metadata`。

---

## 4. 常见 Retriever 类型

### 4.1 VectorStore Retriever（最常用）

- 基于向量相似度检索 top-k。
- 来源是向量数据库（FAISS、Chroma、Milvus、Qdrant 等）。
- 适合语义问答、知识库助手。

```python
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4}
)
```

### 4.2 MMR Retriever（去重复召回）

- 在相关性和多样性间平衡，减少 top-k 内容重复。
- 适合文档重复度高的知识库。

```python
retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={"k": 4, "fetch_k": 20, "lambda_mult": 0.5}
)
```

### 4.3 MultiQuery Retriever（多查询扩展）

- 先让 LLM 把一个问题改写成多个 query，再并行检索并合并结果。
- 能提升“问法不一致”场景下的召回率。

适用：

- 用户问题表达模糊
- 文档术语和用户语言差异较大

### 4.4 ParentDocument Retriever（父子块检索）

- 子块用于召回，父块用于返回更完整上下文。
- 解决“小 chunk 召回准，但上下文不完整”的问题。

适用：

- 长文档手册、制度、论文
- 需要引用更大段落进行回答

### 4.5 Contextual Compression Retriever（压缩检索）

- 先召回，再对候选文档做压缩/抽取，只保留与 query 高相关内容。
- 可明显降低提示词长度和噪声。

适用：

- 文档长、token 成本敏感
- 需要提高上下文密度

### 4.6 Ensemble Retriever（融合检索）

- 融合多个检索器结果（例如 BM25 + 向量检索）。
- 适合术语检索和语义检索都很重要的业务。

---

## 5. 关键词检索与语义检索如何搭配

### 5.1 关键词检索（BM25）

- 优点：对专有名词、型号、编号命中好。
- 缺点：语义泛化能力弱。

### 5.2 向量检索（Embedding Similarity）

- 优点：语义匹配强，能处理同义表达。
- 缺点：对字面精确匹配不稳定。

### 5.3 混合检索（Hybrid）

- 工程上常见最优解：`BM25 + Vector Retriever + Rerank`
- 用融合策略兼顾“词法精确匹配”和“语义泛化”。

---

## 6. Retriever 关键参数与调优

### 6.1 `k`

- 返回文档数量。
- 常见起步值：`k=3~6`。
- 太小会漏召回，太大会引入噪声和 token 成本。

### 6.2 `fetch_k`（MMR 常用）

- 先粗召回的候选数，再从中挑 `k` 个。
- 通常 `fetch_k` 大于 `k`，如 `k=4, fetch_k=20`。

### 6.3 `score_threshold`

- 相似度阈值过滤低质量结果。
- 对“宁缺毋滥”的业务很重要。

### 6.4 filter / metadata 限制

- 如 `tenant_id`、`doc_type`、`lang`、`updated_at`。
- 用于权限隔离和结果精准化。

---

## 7. 新版 LangChain 常见代码模式

### 7.1 基础向量检索

```python
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
docs = retriever.invoke(question)
```

### 7.2 带过滤条件的检索

```python
retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": 4,
        "filter": {"tenant_id": "acme", "doc_type": "policy"}
    }
)
```

### 7.3 接入 Retrieval Chain

```python
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

qa_chain = create_stuff_documents_chain(llm, prompt)
chain = create_retrieval_chain(retriever, qa_chain)
result = chain.invoke({"input": question})
```

---

## 8. 进阶策略

### 8.1 Query Rewrite

- 在检索前重写用户问题（补全上下文、标准化术语）。
- 提升模糊问题的召回率。

### 8.2 Rerank

- 第一阶段 Retriever 召回 top-N
- 第二阶段 reranker 重排到 top-k
- 显著提升最终证据质量

### 8.3 Self-Query Retriever

- 让 LLM 自动生成结构化过滤条件（如时间、作者、标签）。
- 适合 metadata 丰富的知识库。

### 8.4 Time-Weighted / Recency 策略

- 给新文档更高权重，平衡“语义相关”和“时效性”。
- 适合新闻、公告、运营文档。

---

## 9. 评估体系（Retriever 专项）

至少建立以下评估：

### 9.1 离线评估

- Recall@k
- Hit@k（是否命中金标准片段）
- MRR / nDCG（排序质量）

### 9.2 在线评估

- 空召回率
- 低分召回率
- 用户反馈命中率（是否“答案有依据”）

### 9.3 端到端联动指标

- 最终答案正确率
- 引用可追溯率
- 首 token 延迟与总延迟

---

## 10. 最佳实践清单

### 10.1 数据层

- 先做清洗与去重，再做检索优化
- metadata 至少包含 source、doc_id、section/page、updated_at
- 统一 chunk 方案，避免版本混乱

### 10.2 检索层

- 基线先用向量检索 `k=4`
- 重复多时启用 MMR
- 术语密集场景上 Hybrid
- 高精度场景加 rerank

### 10.3 工程层

- 记录 query、top-k、score、filter、最终答案
- 定期做检索回归测试（同一问题集）
- 对 retriever 参数做灰度发布和 A/B 实验

---

## 11. 常见问题与避坑

- **只调模型不调检索**  
  很多“回答差”本质是召回差，不是 LLM 差。

- **k 一路调大**  
  会把噪声也喂给模型，答案反而更差。

- **缺失 metadata 过滤**  
  多租户或多知识域会发生误召回和越权风险。

- **只看最终答案不看证据**  
  无法定位是“召回问题”还是“生成问题”。

- **模型或 chunk 策略升级不做回归**  
  容易出现静默质量下降。

---

## 12. 推荐落地路线

1. 先做最小基线：`Vector Retriever(k=4)`  
2. 建立评估集：20-50 条真实问题  
3. 加强召回：MMR 或 MultiQuery  
4. 加强精度：Rerank + metadata filter  
5. 做工程化：可观测、回归评估、A/B

---

## 13. 一句话结论

Retriever 是 RAG 的“证据引擎”：  
**先把检索做准，再谈生成质量；先建评估闭环，再做参数与模型优化。**
