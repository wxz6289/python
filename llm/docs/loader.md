# LangChain Retrieval 中的文档加载器（Document Loaders）总结

## 1) 文档加载器是什么

- 文档加载器是 RAG（检索增强生成）链路中的**入口层**，负责把外部数据源读入为 LangChain 可处理的 `Document` 对象。
- 每个 `Document` 通常包含两部分：
  - `page_content`：正文文本
  - `metadata`：来源、路径、页码、URL、时间戳等元信息
- 在 Retrieval 中，加载器不做“语义检索”，它只负责“**正确读进来**”。检索质量的上限，很大程度取决于加载阶段的数据质量。

---

## 2) 在 Retrieval 全流程中的位置

标准链路通常是：

`Data Source -> Loader -> Text Splitter -> Embeddings -> Vector Store -> Retriever -> LLM`

其中 Loader 的关键价值：

- **统一格式**：把 PDF/网页/数据库/API 等异构数据，统一成 `Document` 列表。
- **保留上下文**：把文件名、章节、页码、URL 等写进 metadata，便于答案可追溯。
- **控制数据质量**：提前清理噪声（导航栏、页眉页脚、重复内容、乱码），减少后续检索污染。

---

## 3) 常见文档加载器分类

### 3.1 文件类加载器（本地数据）

- 典型场景：知识库文档在本地或挂载磁盘中。
- 常见类型：
  - 文本/Markdown：如 `.txt`、`.md`
  - PDF：适合论文、手册、制度文档
  - Word/PowerPoint/Excel：企业内部 Office 文档
  - CSV/JSON：结构化或半结构化数据
- 特点：稳定、可控、离线友好；但要处理编码、版式、扫描件 OCR 等问题。

### 3.2 Web 类加载器（在线内容）

- 典型场景：抓取官网文档、博客、帮助中心页面。
- 常见模式：
  - 直接抓取页面正文
  - 站点递归抓取（sitemap / crawl）
  - 按 URL 白名单增量更新
- 重点：要清理导航、广告、评论、脚本噪声，避免把“无关文本”写入向量库。

### 3.3 API / SaaS / 数据库加载器

- 典型场景：Confluence、Notion、Google Drive、Slack、数据库表等企业数据源。
- 特点：可做权限对接和增量同步，适合生产系统；但需要处理认证、限流、版本字段和脏数据。

### 3.4 云存储与对象存储加载器

- 典型场景：S3、GCS、Blob 等存储桶里的文档集合。
- 特点：易于规模化；要特别关注文件命名规范、目录分层、更新时间字段。

---

## 4) `Document` + metadata 设计要点（非常关键）

RAG 的可解释性，很大程度取决于 metadata 质量。建议至少包含：

- `source`：来源（文件路径、URL、数据集名）
- `doc_id`：稳定主键（用于去重/更新）
- `title`：文档标题
- `section` / `page`：章节或页码
- `updated_at`：更新时间（支持增量索引）
- `lang`：语言（中英混合场景很有用）

实践建议：

- metadata 要“够用但不过度”，避免塞入超大字段。
- 保证 `doc_id` 稳定，否则会出现重复入库与难以覆盖更新的问题。

---

## 5) 加载器在生产中的三种模式

### 模式 A：一次性全量导入

- 用于 PoC 或首次建库。
- 优点：实现简单。
- 缺点：数据变更后要重跑，成本高。

### 模式 B：定时增量同步（推荐）

- 基于 `updated_at` / ETag / hash 判断变更。
- 只处理新增与更新文档，降低 embedding 成本。

### 模式 C：事件驱动实时同步

- 文档更新即触发 ingestion。
- 适合高实时性场景，但系统复杂度更高。

---

## 6) 与 Text Splitter 的协同原则

加载器和切分器是强耦合关系：

- Loader 负责“读准 + 标注来源”
- Splitter 负责“切得可检索”

协同建议：

- 在加载阶段尽量清理无关噪声，避免切分后污染更多 chunk。
- 切分时把关键 metadata 透传到每个 chunk，保证召回后可追溯。
- 长文档建议按语义边界切分（标题/段落/小节），优于纯字符切分。

---

## 7) 常见问题与避坑

- **问题 1：加载内容不完整**  
  常见于 PDF 版式复杂、网页 JS 渲染、表格提取失败。  
  对策：更换解析器、启用 OCR、做抽样人工验收。

- **问题 2：噪声太多导致召回变差**  
  导航栏、重复 footer、版权声明被重复向量化。  
  对策：在 Loader 后做清洗规则（正则/DOM 过滤/模板清洗）。

- **问题 3：增量更新不稳定**  
  没有稳定主键，导致重复文档越积越多。  
  对策：强制 `doc_id` 策略 + upsert。

- **问题 4：无法溯源**  
  答案引用不到原文位置。  
  对策：metadata 必须包含 source + page/section。

---

## 8) 选型建议（实战版）

- 数据在本地文件系统：优先文件类加载器，先把格式和编码问题清干净。
- 数据在网页文档站：优先网页加载器 + 内容清洗 + URL 去重策略。
- 数据在企业协作平台：优先官方/社区 connector，并设计增量同步机制。
- 想快速出效果：先从 1-2 类核心数据源做高质量导入，不要一开始全接入。

---

## 9) 最小可用实践（MVP）

一个稳定的 Retrieval 加载方案，至少要做到：

- 能批量加载目标数据源
- 每条文档有稳定 `doc_id`
- metadata 可支撑“来源引用”
- 有基础清洗（去空、去重、去噪）
- 支持增量更新

做到以上 5 点，检索质量与可维护性通常会明显好于“只把文本塞进向量库”的粗糙方案。

---

## 10) 一句话总结

在 LangChain Retrieval 里，文档加载器不是简单 I/O，而是 RAG 数据工程的起点：**把异构数据变成可检索、可追溯、可持续更新的高质量 `Document` 资产**。

---

## 11) 常见加载器使用方法（Python 示例）

下面示例基于 LangChain 新版生态，实际项目中常见导入路径是：

- 社区加载器：`langchain_community.document_loaders`
- 新版包加载器：`langchain_*`（具体看对应集成包）

先安装常见依赖（按需安装）：

```bash
pip install -U langchain langchain-community pypdf unstructured bs4 lxml
```

### 11.1 TextLoader（加载 txt / md）

适合快速读取纯文本、Markdown 文档。

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("docs/intro.md", encoding="utf-8")
docs = loader.load()  # List[Document]

print(len(docs))
print(docs[0].page_content[:120])
print(docs[0].metadata)  # 通常含 source
```

要点：

- 文本乱码优先检查 `encoding`
- 大文件建议后续配合 splitter 分块

### 11.2 DirectoryLoader（批量目录加载）

适合把某个目录下文档批量导入。

```python
from langchain_community.document_loaders import DirectoryLoader, TextLoader

loader = DirectoryLoader(
    path="knowledge",
    glob="**/*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
    show_progress=True,
)
docs = loader.load()
print(f"loaded docs = {len(docs)}")
```

要点：

- 用 `glob` 控制文件范围
- 混合格式目录建议分批加载（例如 md 一批、pdf 一批）

### 11.3 PyPDFLoader（PDF）

适合手册、论文、制度等 PDF 文档。

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("knowledge/handbook.pdf")
docs = loader.load()  # 默认按页返回 Document

print(len(docs))
print(docs[0].metadata)  # 常见包含 page, source 等
```

懒加载模式（节省内存）：

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("knowledge/handbook.pdf")
for doc in loader.lazy_load():
    # 在循环内直接清洗、切分或入库
    pass
```

要点：

- 扫描版 PDF 可能需要 OCR 方案
- 表格/双栏版式常出现错行，建议做抽样质检

### 11.4 CSVLoader（CSV 表格）

适合 FAQ、商品表、日志导出等表格数据。

```python
from langchain_community.document_loaders import CSVLoader

loader = CSVLoader(
    file_path="data/faq.csv",
    encoding="utf-8",
    source_column="question",  # 可选：把某列作为 source
)
docs = loader.load()
print(docs[0].page_content)
print(docs[0].metadata)
```

要点：

- CSV 每行通常转成一个 Document
- 建议把主键列写入 metadata，便于增量更新

### 11.5 JSONLoader（JSON / JSONL）

适合结构化接口数据、日志、工单记录。

```python
from langchain_community.document_loaders import JSONLoader

loader = JSONLoader(
    file_path="data/tickets.json",
    jq_schema=".tickets[]",        # 选取数组元素
    content_key="description",     # 指定正文字段
    text_content=False,            # 非纯文本对象时常用
)
docs = loader.load()
print(len(docs))
```

要点：

- `jq_schema` 决定抽取粒度
- 复杂 JSON 先本地验证抽取规则，再批量入库

### 11.6 WebBaseLoader（网页）

适合抓取公开网页内容（文档站、博客等）。

```python
from langchain_community.document_loaders import WebBaseLoader

urls = [
    "https://python.langchain.com/docs/introduction/",
]
loader = WebBaseLoader(web_paths=urls)
docs = loader.load()

print(len(docs))
print(docs[0].metadata)  # 常见包含 source(URL)
```

要点：

- 网页噪声较多，建议清洗导航栏/页脚/脚本内容
- 注意站点 robots、访问频率与合规策略

### 11.7 UnstructuredFileLoader（通用文件兜底）

适合格式杂、类型多的场景，作为通用 fallback。

```python
from langchain_community.document_loaders import UnstructuredFileLoader

loader = UnstructuredFileLoader("knowledge/report.docx")
docs = loader.load()
print(len(docs))
```

要点：

- 通用性高，但速度和稳定性受文件质量影响明显
- 生产中建议“主加载器 + 兜底加载器”组合

### 11.8 NotionDirectoryLoader（Notion 导出）

适合团队先从 Notion 导出后离线建库。

```python
from langchain_community.document_loaders import NotionDirectoryLoader

loader = NotionDirectoryLoader("notion_export")
docs = loader.load()
print(len(docs))
```

要点：

- 目录结构通常对应页面层级，可写入 metadata
- 线上同步场景建议改用 API/connector 方案

---

## 12) 组合示例：加载 -> 切分 -> 入向量库（最小骨架）

```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1) 批量加载 PDF
loader = DirectoryLoader(
    path="knowledge",
    glob="**/*.pdf",
    loader_cls=PyPDFLoader,
)
docs = loader.load()

# 2) 切分
splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
)
chunks = splitter.split_documents(docs)

# 3) 向量化并建索引
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vs = FAISS.from_documents(chunks, embeddings)

# 4) 检索器
retriever = vs.as_retriever(search_kwargs={"k": 4})
```

---

## 13) 加载器实战建议（落地清单）

- 先做小样本验证：每种数据源抽 20-50 条人工验收。
- 明确 `doc_id` 规则：建议 `source + 更新版本/hash`。
- 清洗先于向量化：去噪声比“盲目调 embedding”更有效。
- 保留可追溯 metadata：至少 `source`、`title`、`page/section`。
- 设计增量策略：按 `updated_at` 或内容 hash 做 upsert。

---

## 14) 文档拆分器（Text Splitters）总结

在 Retrieval 中，拆分器决定了“检索单元”的粒度。  
同样的向量模型，不同拆分策略会直接影响召回率、答案完整性和成本。

核心目标：

- **可检索**：chunk 不能太大，否则相似度不聚焦
- **可理解**：chunk 不能太碎，否则语义断裂
- **可追溯**：chunk 要携带来源 metadata

---

## 15) 常见拆分器与使用方法

先安装：

```bash
pip install -U langchain-text-splitters
```

### 15.1 CharacterTextSplitter（固定字符切分）

按固定字符长度切分，简单直接。

```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=800,
    chunk_overlap=100,
)
chunks = splitter.split_documents(docs)
```

适用：

- 文本结构比较规整
- 先快速做 PoC

限制：

- 语义边界不一定自然

### 15.2 RecursiveCharacterTextSplitter（推荐默认）

按分隔符优先级递归切分（段落 -> 句子 -> 字符），是实践中最常用方案。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=120,
    separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
)
chunks = splitter.split_documents(docs)
```

适用：

- 中英文混合文档
- 通用知识库默认方案

### 15.3 TokenTextSplitter（按 token 切分）

更贴近模型上下文窗口，便于控制真实推理成本。

```python
from langchain_text_splitters import TokenTextSplitter

splitter = TokenTextSplitter(
    chunk_size=300,      # token 数
    chunk_overlap=50,
)
chunks = splitter.split_documents(docs)
```

适用：

- 对 token 成本敏感
- 多模型场景需要统一 token 预算

### 15.4 MarkdownHeaderTextSplitter（按标题层级切）

先按 Markdown 标题切，再按长度二次切分，语义可解释性最好。

```python
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
)
docs_by_header = md_splitter.split_text(markdown_text)

child_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
chunks = child_splitter.split_documents(docs_by_header)
```

适用：

- 技术文档、教程、SOP 文档
- 希望在 metadata 中保留章节层级

### 15.5 代码文本拆分（按语言语法）

代码知识库建议按语言语法或函数边界拆分，避免跨函数混切。

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=600,
    chunk_overlap=80,
)
chunks = splitter.split_text(code_text)
```

适用：

- 代码问答、代码检索、Copilot 场景

---

## 16) 拆分策略设计（从“能用”到“好用”）

### 策略 A：单阶段切分

- 直接使用一个 splitter 完成切分
- 优点：实现快
- 缺点：对复杂文档鲁棒性一般

### 策略 B：两阶段切分（推荐）

- 第一步：按结构切（标题、章节、页、记录）
- 第二步：按长度切（字符/token）
- 优点：兼顾语义完整与召回颗粒度

### 策略 C：父子块（Parent-Child Retrieval）

- 子块用于向量召回（小 chunk，检索更准）
- 父块用于生成答案（大 chunk，上下文更完整）
- 适合长文档问答与证据引用场景

---

## 17) 关键参数怎么调

`chunk_size`、`chunk_overlap` 没有万能值，建议按文档类型起步：

- 通用中文文档：`chunk_size=600~1000`，`overlap=80~150`
- 英文技术文档：`chunk_size=400~900`，`overlap=50~120`
- 代码：`chunk_size=300~700`，`overlap=40~100`
- FAQ/短句：可更小，如 `200~500`

调参原则：

- 召回不准：适当减小 `chunk_size`
- 答案断裂：适当增大 `overlap`
- 成本太高：减小 `k` 或增大 `chunk_size`（先评估精度影响）

---

## 18) 不同数据类型的推荐拆分模板

- **Markdown/文档站**：标题拆分 + 递归长度拆分
- **PDF 手册**：先按页读取，再递归切分并保留 `page`
- **FAQ/工单**：一条记录一个 chunk，不要过度切碎
- **日志/事件流**：按时间窗口或会话 ID 切分
- **代码库**：按文件 -> 类/函数 -> 长度二次切

---

## 19) 拆分质量评估方法（实战）

至少做三类检查：

- **覆盖检查**：原文关键段落是否都能在 chunk 中找到
- **语义检查**：chunk 是否经常出现“半句话、断上下文”
- **检索检查**：用 20-50 条真实问题评估 top-k 召回命中率

建议记录：

- chunk 总数、平均长度、空 chunk 比例
- 每类问题的召回率变化（改参数前后对比）
- 典型失败案例（用于反推拆分策略）

---

## 20) 与加载器联动的最佳实践

- 加载阶段写好 metadata，拆分后原样继承
- 先清洗再拆分，避免噪声扩散到更多 chunk
- 结构化文档优先“结构切分”，再做长度控制
- 保留 `doc_id` + `chunk_id`，便于重建索引和排障

---

## 21) 一句话结论（拆分器）

拆分器是 Retrieval 的“召回放大器”：**切得合理，检索才准；切得可追溯，答案才可信；切得可控，成本才可持续**。
