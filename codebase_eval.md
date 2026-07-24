# Codebase QA 评测集 V1

## 一、评测目标

本评测集用于检查 Codebase Agent 在代码仓库问答场景下的表现，重点观察：

- 回答是否正确
- sources 是否引用正确文件
- sources 是否包含合理行号
- 回答是否基于已检索资料
- 资料不足时是否拒答
- 是否出现幻觉
- 失败原因是什么

这份评测不是单纯测试接口能不能返回 200，而是评估 RAG 问答链路是否真的能帮助用户理解代码仓库。

## 二、当前评测范围

当前项目已经支持：

- 本地代码仓库扫描
- 安全文件读取
- Markdown / Python 文件切分
- Python AST 函数和类识别
- 函数级 chunk
- 类级 chunk
- module chunk
- Embedding 接入
- Qdrant 向量检索
- 多文件索引
- Codebase RAG 问答
- answer + sources 返回
- sources 返回 `file_path`、`start_line`、`end_line`、`chunk_type`、`symbol_name`

当前暂不评测：

- Tool Calling
- Agent Loop
- Memory
- Trace
- 自动修改代码
- 自动生成修改计划
- 多轮任务执行

## 三、评测前准备

评测前需要先启动服务：

```bash
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

然后打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

先调用 `/repositories/index`，索引本项目的主要文件。

推荐索引请求：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_paths": [
    "README.md",
    "app/main.py",
    "app/schemas.py",
    "app/services/repository_scanner.py",
    "app/services/code_reader.py",
    "app/services/code_chunker.py",
    "app/services/python_symbol_parser.py",
    "app/services/embedding_service.py",
    "app/services/vector_store.py",
    "app/services/index_service.py",
    "app/services/rag_service.py",
    "tests/test_code_reader.py",
    "tests/test_code_chunker.py",
    "tests/test_python_symbol_parser.py"
  ],
  "chunk_size": 120
}
```

如果一次索引过多文件导致 embedding 失败，可以减少文件数量分批测试。

## 四、评测指标

| 指标 | 说明 |
|---|---|
| answer_correct | 回答内容是否符合预期 |
| source_correct | sources 是否引用到正确文件 |
| line_correct | sources 行号是否大致正确 |
| grounded | 回答是否基于 sources，没有编造 |
| refusal_correct | 资料不足时是否正确拒答 |
| failure_reason | 失败原因 |

## 五、评分标准

| 结果 | 含义 |
|---|---|
| 通过 | 回答正确，sources 正确，行号基本合理 |
| 部分通过 | 回答大致正确，但 sources 或行号不够准确 |
| 失败 | 回答错误、引用错误、无依据编造，或该拒答时没有拒答 |

## 六、20 个测试问题

| 编号 | 测试问题 | 预期答案要点 | 预期 source 文件 | 评测重点 |
|---|---|---|---|---|
| 1 | 这个项目是做什么的？ | Codebase Agent 是面向代码仓库理解与修改规划的本地 Agent 系统 | README.md | 项目定位理解 |
| 2 | 项目入口在哪里？ | FastAPI 应用入口在 `app/main.py` | README.md / app/main.py | 项目结构问答 |
| 3 | `/health` 接口在哪里实现？ | 在 `app/main.py` 的 `health_check` 函数中实现 | app/main.py | 接口定位 |
| 4 | `/repositories/scan` 接口负责什么？ | 扫描本地仓库，返回文件路径、类型和大小 | app/main.py / app/services/repository_scanner.py | 接口职责 |
| 5 | 仓库扫描逻辑在哪个文件？ | 在 `app/services/repository_scanner.py` 中 | app/services/repository_scanner.py | 模块定位 |
| 6 | 仓库扫描会过滤哪些目录？ | 过滤 `.git`、`.venv`、`__pycache__`、`.pytest_cache` 等 | app/services/repository_scanner.py | 规则抽取 |
| 7 | `read_code_file` 负责什么？ | 安全读取仓库内文件，返回文件内容和行号 | app/services/code_reader.py | 函数职责 |
| 8 | 项目如何防止读取仓库外文件？ | 通过路径解析和仓库边界校验，拒绝仓库外路径 | app/services/code_reader.py | 安全边界 |
| 9 | `AskRequest` 这个类负责什么？ | 定义问答请求参数，包括 `question`、`top_k`、`score_threshold` | app/schemas.py | 类职责 |
| 10 | `SourceChunk` 返回哪些字段？ | 返回文件路径、行号、分数、内容、chunk 类型和符号名 | app/schemas.py | 响应结构 |
| 11 | Python 文件如何切分 chunk？ | 使用 AST 识别函数和类，函数/类独立成 chunk，其余代码为 module chunk | app/services/code_chunker.py / app/services/python_symbol_parser.py | Chunk 策略 |
| 12 | Markdown 文件如何切分 chunk？ | 按 Markdown 标题切分成 section chunk | app/services/code_chunker.py | 文档切分 |
| 13 | `parse_python_symbols` 能识别什么？ | 能识别 Python function 和 class，并记录名称和起止行号 | app/services/python_symbol_parser.py | AST 解析 |
| 14 | 为什么函数装饰器也要纳入 chunk？ | 装饰器是函数语义的一部分，例如 FastAPI 路由装饰器决定接口路径 | app/services/python_symbol_parser.py / app/main.py | 代码语义 |
| 15 | Embedding 在哪里调用？ | 在 embedding service 中调用 embedding model 生成向量 | app/services/embedding_service.py | 向量化链路 |
| 16 | Qdrant 写入逻辑在哪里？ | 在 `app/services/vector_store.py` 中创建 collection 并写入 chunk 向量和 metadata | app/services/vector_store.py | 向量库 |
| 17 | 多文件索引在哪里实现？ | 在 `app/services/index_service.py` 中遍历多个文件并写入向量库 | app/services/index_service.py | 多文件索引 |
| 18 | RAG 的 prompt 在哪里构造？ | 在 `app/services/rag_service.py` 中构造基于 sources 的 grounding prompt | app/services/rag_service.py | Prompt 设计 |
| 19 | 测试覆盖了哪些功能？ | 覆盖代码读取、Markdown 切分、Python AST 解析、函数/类 chunk 等 | tests/test_code_reader.py / tests/test_code_chunker.py / tests/test_python_symbol_parser.py | 测试覆盖 |
| 20 | 数据库相关代码在哪？ | 当前项目没有数据库相关代码，应该拒答 | 无明确 source | 拒答能力 |

## 七、评测记录表

| 编号 | 测试问题 | 实际回答摘要 | 实际 sources | answer_correct | source_correct | line_correct | grounded | 结果 | 失败原因 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 这个项目是做什么的？ | 回答为代码仓库理解与修改规划的本地 Agent 系统 | README.md 多个 section | 是 | 是 | 部分 | 是 | 部分通过 | 回答正确，但首位 source 不是最直接的项目定位段落 |
| 2 | 项目入口在哪里？ | 回答入口为 `app/main.py` | README.md 项目结构相关段落 | 是 | 是 | 是 | 是 | 通过 | 无 |
| 3 | `/health` 接口在哪里实现？ | 回答在 `app/main.py` 的 `health_check` 中实现 | README.md / app/main.py:28-30 | 是 | 是 | 是 | 是 | 通过 | 无 |
| 4 | `/repositories/scan` 接口负责什么？ | 回答负责扫描仓库并返回文件列表 | app/main.py / README.md / schemas.py | 是 | 是 | 是 | 是 | 通过 | 无 |
| 5 | 仓库扫描逻辑在哪个文件？ | 回答 API 入口在 `app/main.py`，核心逻辑推测在 `repository_scanner.py` | app/main.py / README.md / schemas.py | 部分 | 部分 | 部分 | 部分 | 部分通过 | 没有优先召回 `app/services/repository_scanner.py` 的实现片段 |
| 6 | 仓库扫描会过滤哪些目录？ | 回答过滤 `.git`、`.venv`、`__pycache__`、`.pytest_cache` | README.md / app/main.py | 是 | 是 | 是 | 是 | 通过 | 无 |
| 7 | `read_code_file` 负责什么？ | 回答负责安全读取文件并返回行号内容 | app/main.py / README.md / tests 等 | 是 | 部分 | 部分 | 部分 | 部分通过 | 回答正确，但 source 排序没有优先展示 `code_reader.py` 实现 |
| 8 | 项目如何防止读取仓库外文件？ | 回答通过路径校验拒绝仓库外路径 | README.md / tests/test_code_reader.py / app/main.py | 是 | 是 | 是 | 是 | 通过 | 无 |
| 9 | `AskRequest` 这个类负责什么？ | 回答用于定义问答请求参数，包括 `question`、`top_k`、`score_threshold` | app/schemas.py / app/main.py / README.md | 是 | 是 | 是 | 是 | 通过 | source 排序可优化，`AskRequest` 不是第一条 |
| 10 | `SourceChunk` 返回哪些字段？ | 回答返回 `file_path`、`start_line`、`end_line`、`score`、`content`、`chunk_type`、`symbol_name` | app/schemas.py:89-96 | 是 | 是 | 是 | 是 | 通过 | 无 |
| 11 | Python 文件如何切分 chunk？ | 回答使用 AST 识别函数和类，其他代码作为 module chunk | README.md / code_chunker.py / tests | 是 | 是 | 是 | 是 | 通过 | 无 |
| 12 | Markdown 文件如何切分 chunk？ | 回答按标题切分，超长 section 再按固定行数切分 | app/services/code_chunker.py / README.md | 是 | 是 | 是 | 是 | 通过 | 无 |
| 13 | `parse_python_symbols` 能识别什么？ | 回答能识别 function 和 class，并返回名称、类型、起止行号 | python_symbol_parser.py / tests | 是 | 是 | 是 | 是 | 通过 | 无 |
| 14 | 为什么函数装饰器也要纳入 chunk？ | 回答拒答 | tests/test_code_chunker.py / README.md 等 | 否 | 部分 | 部分 | 是 | 失败 | 已实现该能力，但已索引资料缺少“为什么”的说明，属于 over_refusal |
| 15 | Embedding 在哪里调用？ | 回答主要在 `index_service.py` 中调用 `create_embedding`，也涉及问答 query embedding | index_service.py / embedding_service.py / rag_service.py | 是 | 是 | 是 | 是 | 通过 | 无 |
| 16 | Qdrant 写入逻辑在哪里？ | 回答位于 `vector_store.py`，但认为具体写入函数未详细展示 | vector_store.py / README.md | 部分 | 是 | 部分 | 部分 | 部分通过 | 召回到 `vector_store.py` module，但没有召回具体 upsert 实现片段 |
| 17 | 多文件索引在哪里实现？ | 回答在 `index_repository_files` 中遍历 `file_paths` 实现 | schemas.py / main.py / index_service.py | 是 | 是 | 是 | 是 | 通过 | 无 |
| 18 | RAG 的 prompt 在哪里构造？ | 回答在 `rag_service.py` 的 `build_grounding_prompt` 中构造 | app/services/rag_service.py:47-82 | 是 | 是 | 是 | 是 | 通过 | 无 |
| 19 | 测试覆盖了哪些功能？ | 回答只提到 README 中的测试状态，没有列出具体测试文件覆盖内容 | README.md | 否 | 否 | 否 | 是 | 失败 | 没有召回 tests 目录具体测试文件，属于 retrieval_miss |
| 20 | 关系型数据库相关代码在哪？ | 回答没有找到相关内容 | README.md / vector_store.py / rag_service.py | 是 | 是 | 是 | 是 | 通过 | 题目需要明确“关系型数据库”，否则模型可能把 Qdrant 视为数据库相关代码 |

## 八、失败原因分类

| 失败类型 | 说明 |
|---|---|
| retrieval_miss | 没有召回正确 chunk |
| wrong_source | 回答正确，但 sources 引错文件 |
| line_inaccurate | 文件正确，但行号不准确 |
| hallucination | 模型编造了 sources 中没有的信息 |
| over_refusal | 明明有资料，但模型拒答 |
| under_refusal | 资料不足时没有拒答 |
| vague_answer | 回答太泛，没有具体到文件、函数或类 |
| bad_prompt | prompt 约束不够清晰 |
| bad_chunk | chunk 太大、太小或切分不合理 |
| embedding_error | embedding 调用失败 |

## 九、评测结论模板

完成评测后，可以按下面格式总结：

```text
本轮共测试 20 个问题。

回答正确：x / 20
source 正确：x / 20
行号基本正确：x / 20
正确拒答：x / x

主要失败原因：
1. ...
2. ...
3. ...

下一步优化：
1. ...
2. ...
3. ...
```

## 十、本轮实际评测结论

本轮评测时间：2026-07-24

索引范围：

```text
README.md
app/main.py
app/schemas.py
app/services/repository_scanner.py
app/services/code_reader.py
app/services/code_chunker.py
app/services/python_symbol_parser.py
app/services/embedding_service.py
app/services/vector_store.py
app/services/index_service.py
app/services/rag_service.py
tests/test_code_reader.py
tests/test_code_chunker.py
tests/test_python_symbol_parser.py
```

索引结果：

```text
file_count: 14
chunk_count: 88
indexed_count: 88
chunk_size: 120
```

评测结果：

```text
通过：14 / 20
部分通过：4 / 20
失败：2 / 20
```

主要失败或不足：

1. 部分问题回答正确，但 sources 排序不够理想。
2. 某些问题没有优先召回最直接的实现文件，例如 `repository_scanner.py`、`code_reader.py`、`vector_store.py` 的具体函数片段。
3. “为什么函数装饰器也要纳入 chunk？”出现 over_refusal，说明代码资料中缺少设计原因说明。
4. “测试覆盖了哪些功能？”没有召回 tests 目录中的具体测试文件，属于 retrieval_miss。
5. “数据库相关代码在哪？”需要明确区分关系型数据库和向量库，否则模型可能将 Qdrant 也理解成数据库相关代码。

下一步优化方向：

1. 为代码 chunk 增加更丰富的 metadata，例如 `module_name`、`function_name`、`class_name`、`api_path`。
2. 对函数名、类名、文件名查询增加 keyword match 或 hybrid search。
3. 对 tests 目录建立更明确的测试语义索引，例如从测试函数名中抽取被测能力。
4. 在 README 或代码注释中补充关键设计原因，例如为什么装饰器要包含进函数 chunk。
5. 对 source rerank 做优化，让最直接支持回答的 source 排在前面。

## 十一、本轮评测关注点

这轮评测最重要的不是追求全部回答完美，而是发现系统当前瓶颈：

- 哪类问题容易召回错误
- 哪些文件需要更好的 chunk 策略
- 哪些问题需要更强的 prompt 约束
- sources 是否真的能支撑回答
- 项目是否已经具备可解释、可复盘、可优化的工程闭环

对 Codebase Agent 来说，评测集本身就是项目工程化能力的一部分。
