# Deep Agents、LangChain、LangGraph 的区别与联系

> 参考：[Frameworks, runtimes, and harnesses](https://docs.langchain.com/oss/python/concepts/products)

## 一句话定位

三者处于 **Agent 开发栈的不同层级**，不是互斥替代品，而是 **自下而上层层叠加** 的关系：

```
Deep Agents（Harness / 束具层）
        ↓ 构建于
LangGraph（Runtime / 运行时层）
        ↑ 也被
LangChain（Framework / 框架层）使用
```

| 层级 | 代表 | 核心价值 |
|------|------|----------|
| **Framework（框架）** | LangChain | 抽象与集成，快速上手 |
| **Runtime（运行时）** | LangGraph | 持久化、流式、HITL、编排控制 |
| **Harness（束具）** | Deep Agents SDK | 开箱即用的工具、Prompt、子 Agent |

---

## 各自是什么

### LangChain — Agent 框架

提供 **高层抽象**，降低 LLM 应用开发门槛：

- 结构化内容块（content blocks）
- Agent 循环（agent loop）
- 中间件（middleware）
- 模型、工具、集成的标准化接口

**特点**：易上手，仍保留一定灵活性；**LangChain 1.0 底层基于 LangGraph**，但使用 LangChain 时 **不必了解 LangGraph**。

**适用场景**：

- 快速构建 Agent 与自主应用
- 团队需要统一抽象与集成方式
- 编排需求不复杂、偏「直来直去」的 Agent 应用

---

### LangGraph — Agent 运行时

提供 **生产级编排与执行基础设施**，偏底层、可控：

- **持久化执行（Durable execution）**：失败后可恢复，支持长时间运行
- **流式（Streaming）**
- **Human-in-the-loop（HITL）**：人工审查与修改 Agent 状态
- **状态持久化**：线程级与跨线程
- **细粒度编排**：确定性步骤 + Agent 步骤混合工作流

**特点**：框架层（如 LangChain）通常 **跑在运行时之上**；LangGraph 也可单独使用。

**适用场景**：

- 需要精细控制 Agent 编排逻辑
- 长时间、有状态的 Agent / 工作流
- 确定性流程与 Agent 行为混合
- 需要生产部署能力

---

### Deep Agents SDK — Agent 束具（Harness）

在 LangGraph 之上提供 **开箱即用、偏 opinionated 的能力**，面向 **更自主、更复杂** 的 Agent：

- **规划能力**：Todo 列表跟踪多任务
- **任务委派**：子 Agent（subagents）拆分工作、保持上下文干净
- **文件系统**：可插拔存储后端的读写能力
- **Token 管理**：对话摘要、大工具结果驱逐（context engineering）
- 预置工具（文件操作、bash 执行等）、Prompt、子 Agent

**特点**：**构建于 LangGraph 之上**，专为需要规划与任务分解的复杂多步任务设计（如处理搜索结果、脚本、状态中的各类产物）。

**适用场景**：

- 长时间运行的 Agent
- 复杂、非确定性、多步骤任务
- 希望直接用预置工具与 Prompt，而非从零搭建
- 需要子 Agent 与自动化上下文管理

---

## 三者的联系

1. **LangGraph 是共同底座**  
   LangChain 1.0 与 Deep Agents SDK 都 **基于 LangGraph** 运行。

2. **抽象层级递增**  
   - LangGraph：最底层，管「怎么跑、怎么持久、怎么编排」  
   - LangChain：中间层，管「怎么快速拼模型、工具、Agent 循环」  
   - Deep Agents：最上层，管「怎么像 Cursor/Claude Code 那样自主规划、委派、管理上下文」

3. **能力可重叠，集成深度不同**  
   三者都能做记忆、子 Agent、HITL、流式等，但 **接入方式与预设程度不同**（见下表）。

4. **选型不是非此即彼**  
   - 简单 Agent → LangChain 往往足够  
   - 复杂编排 / 生产状态机 → 直接用或透过 LangChain 使用 LangGraph  
   - 高度自主、长任务、要预置 filesystem/bash/规划 → Deep Agents

---

## 功能对比（同一能力，不同接入层）

| 能力 | LangChain | LangGraph | Deep Agents |
|------|-----------|-----------|-------------|
| 短期记忆 | [Short-term memory](https://docs.langchain.com/oss/python/langchain/short-term-memory) | [Add short-term memory](https://docs.langchain.com/oss/python/langgraph/add-memory#add-short-term-memory) | `StateBackend` |
| 长期记忆 | [Long-term memory](https://docs.langchain.com/oss/python/langchain/long-term-memory) | [Add long-term memory](https://docs.langchain.com/oss/python/langgraph/add-memory#add-long-term-memory) | [Memory](https://docs.langchain.com/oss/python/deepagents/memory) |
| Skills | Multi-agent skills | — | Skills |
| 子 Agent | Multi-agent subagents | Subgraphs | Subagents |
| Human-in-the-loop | HITL middleware | Interrupts | `interrupt_on` |
| 流式 | Agent Streaming | Streaming | Event Streaming |

---

## 选型建议

| 你的需求 | 推荐 |
|----------|------|
| 快速原型、标准 Agent、团队统一抽象 | **LangChain** |
| 精细编排、长运行、状态持久、生产部署 | **LangGraph**（可单独用，或由 LangChain 间接使用） |
| 复杂多步、高度自主、要规划/文件系统/子 Agent 开箱即用 | **Deep Agents SDK** |

---

## 延伸阅读

- [LangChain Overview](https://docs.langchain.com/oss/python/langchain/overview)
- [LangGraph Overview](https://docs.langchain.com/oss/python/langgraph/overview)
- [Deep Agents Overview](https://docs.langchain.com/oss/python/deepagents/overview)
