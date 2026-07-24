# Week 2 复盘：Codebase RAG 主链路

## 一、本周目标

Week 2 的目标是把 Codebase Agent 从“能扫描和读取代码”的基础项目，推进到“能够基于代码仓库进行 RAG 问答”的基础版本。

本周重点不只是让模型能回答问题，而是让回答能够带上可追溯的 sources，包括文件路径、行号范围、chunk 类型和函数 / 类名称。

## 二、本周完成内容

本周完成了 Codebase RAG 的核心链路：

```text
读取代码文件
-> 切分代码 chunk
-> 保存 metadata
-> 生成 embedding
-> 写入 Qdrant
-> query embedding
-> top-k 检索
-> 拼接代码上下文
-> 构造 grounding prompt
-> 生成 answer
-> 返回 sources
```

核心接口包括：

- `/repositories/chunks/preview`
- `/repositories/index`
- `/repositories/ask`

## 三、Codebase RAG 主链路

Codebase RAG 的主链路可以拆成三段。

第一段是 indexing：

```text
文件读取
-> chunk 切分
-> metadata 构造
-> embedding
-> 向量入库
```

第二段是 retrieval：

```text
用户问题
-> query embedding
-> Qdrant top-k 检索
-> score_threshold 过滤
-> 返回相关 chunks
```

第三段是 generation：

```text
检索结果
-> 拼接 context
-> grounding prompt
-> LLM 回答
-> answer + sources
```

这个链路已经具备 RAG 项目的基本工程形态。

## 四、Metadata 设计

本周最重要的工程设计之一是 metadata。

每个 chunk 保存：

- `file_path`
- `file_type`
- `start_line`
- `end_line`
- `chunk_type`
- `symbol_name`
- `content`

metadata 的价值：

- 让回答可以引用具体文件
- 让回答可以引用具体行号
- 让模型知道片段来自函数、类还是模块级代码
- 让 sources 能被用户复查
- 为后续 Tool Calling 和 trace 打基础

如果没有 metadata，RAG 只能回答“可能在某段内容里”，很难变成可落地的代码仓库助手。

## 五、AST Chunk 的作用

普通固定行数切分的问题是：

- 可能把一个函数切断
- 可能把两个函数混在一起
- 很难回答“某个函数在哪”
- 很难回答“某个类负责什么”

AST chunk 的优势是：

- Python 函数可以作为独立 chunk
- Python 类可以作为独立 chunk
- 可以保存 `symbol_name`
- 可以保存准确的 `start_line` 和 `end_line`
- 更适合代码仓库问答

当前 AST chunk 支持：

- function chunk
- class chunk
- module chunk

这让项目从普通文档 RAG 进一步接近 Codebase Agent。

## 六、Prompt 约束

本周对 Codebase QA prompt 做了 grounding 约束。

核心要求：

- 只能基于 sources 回答
- 资料不足时必须拒答
- 回答中尽量引用文件路径和行号
- 如果 source 包含函数名或类名，需要说明对应符号
- 不允许编造不存在的文件、函数、类、接口或调用关系

这个 prompt 的作用是降低幻觉，让回答更适合工程场景。

## 七、评测结果

本周新增 `codebase_eval.md`，准备了 20 个 Codebase QA 测试问题，并完成了一轮真实评测。

评测结果：

```text
通过：14 / 20
部分通过：4 / 20
失败：2 / 20
```

主要发现：

- 主链路可以跑通
- 大多数项目结构、接口、类和函数问题可以回答
- 部分问题回答正确，但 sources 排序不够理想
- tests 目录相关问题召回质量不足
- 部分“为什么”类问题因为资料不足而拒答

这说明系统已经具备基础能力，但距离高质量 Codebase Agent 还有明显优化空间。

## 八、当前问题

当前主要问题包括：

- 语义检索对函数名、类名、文件名等精确问题不够稳定
- sources 排序有时不是最直接的证据
- tests 目录召回不稳定
- Qdrant 当前使用内存模式，索引不能持久化
- 每次索引会重建 collection
- 还没有 hybrid search
- 还没有 rerank
- 还没有 Tool Calling
- 还没有 Agent Loop
- 还没有 trace

这些问题也是 Week 3 的优化方向。

## 九、本周项目价值

本周完成后，项目已经不是简单 demo，而是具备了代码仓库问答系统的核心工程闭环：

```text
代码读取
代码切分
符号识别
向量索引
语义检索
基于 sources 回答
评测集验证
失败案例复盘
```

这套链路是后续 Agent Harness、Tool Calling、Memory、Trace 的基础。

## 十、下一步优化方向

下一步重点：

- 增加 keyword match / hybrid search
- 增加 rerank
- 增强函数名、类名、文件名查询能力
- 针对 tests 目录设计测试语义索引
- 增加 `inspect_symbol` 工具
- 增加 Tool Calling
- 设计 Agent Loop
- 增加运行 trace
- 将 Qdrant 从内存模式升级为持久化模式

Week 2 的核心结论是：

```text
Codebase Agent 的难点不只是让模型回答，而是让回答能被 sources 支撑，并且能通过评测发现系统哪里不可靠。
```
