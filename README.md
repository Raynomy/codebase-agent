# Codebase Agent

Codebase Agent 是一个面向代码仓库理解与修改规划的本地 Agent 系统。

项目目标是帮助开发者在接手陌生代码仓库时，快速理解项目结构、模块职责、核心文件、接口链路和潜在修改范围。

## 项目背景

开发者在接手一个陌生项目时，通常需要手动阅读 README、目录结构、源码文件和测试文件，再通过搜索和调试逐步建立项目理解。

这个过程存在几个问题：

- 项目结构理解成本高
- 相关代码定位效率低
- 修改影响范围难判断
- 回答依据不可追溯
- 多轮追问时上下文容易丢失
- 代码阅读过程难复盘

Codebase Agent 面向这个场景，目标是通过代码仓库扫描、代码切分、语义检索、问答生成、sources 引用和后续工具调用，辅助用户理解项目并规划修改。

## 核心流程

```text
输入本地代码仓库
-> 扫描文件目录
-> 安全读取 README / Markdown / Python / tests
-> 按文档标题、函数、类、模块切分 chunk
-> 为 chunk 保存 metadata
-> 调用 embedding model 生成向量
-> 写入 Qdrant 向量库
-> 用户用自然语言提问
-> query embedding
-> top-k 检索相关 chunks
-> 拼接代码上下文
-> 构造 grounding prompt
-> LLM 基于 sources 生成回答
-> 返回 answer + sources
```

## 当前能力

当前项目已经实现 Codebase RAG 基础主链路：

- 扫描本地代码仓库
- 过滤 `.git`、`.venv`、`__pycache__`、`.pytest_cache` 等无关目录
- 安全读取仓库内文件，防止路径逃逸
- 读取文件内容并保留行号
- Markdown 按标题切分 chunk
- Python 文件基于 AST 识别函数和类
- 函数级 chunk
- 类级 chunk
- module chunk
- 保存 chunk metadata
- 接入 embedding model
- 接入 Qdrant 内存向量库
- 支持多文件索引
- 支持基于代码仓库的自然语言问答
- 返回 answer + sources
- sources 返回文件路径、行号范围、代码片段、chunk 类型和符号名
- 通过基础测试覆盖代码读取、chunk 切分、AST 符号解析
- 建立 Codebase QA 评测集 V1

## 技术栈

- Python
- FastAPI
- Pydantic
- OpenAI-compatible LLM API
- Embedding Model
- Qdrant
- Python AST
- pytest

后续计划补充：

- Tool Calling
- Agent Loop
- Memory
- Trace
- Hybrid Search
- Rerank
- Docker / Docker Compose

## 项目结构

```text
2026-07-codebase-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── code_chunker.py
│       ├── code_reader.py
│       ├── embedding_service.py
│       ├── index_service.py
│       ├── python_symbol_parser.py
│       ├── rag_service.py
│       ├── repository_scanner.py
│       └── vector_store.py
├── tests/
│   ├── test_code_chunker.py
│   ├── test_code_reader.py
│   └── test_python_symbol_parser.py
├── .env.example
├── .gitignore
├── codebase_eval.md
├── requirements.txt
├── week2_review.md
└── README.md
```

## 模块说明

| 文件 | 作用 |
|---|---|
| `app/main.py` | FastAPI 应用入口，定义 API 路由 |
| `app/schemas.py` | Pydantic 请求和响应模型 |
| `app/services/repository_scanner.py` | 扫描本地代码仓库，返回文件路径、类型和大小 |
| `app/services/code_reader.py` | 安全读取仓库内文件，返回带行号的内容 |
| `app/services/python_symbol_parser.py` | 使用 Python AST 识别函数和类 |
| `app/services/code_chunker.py` | 将 Markdown / Python 文件切分为 chunks |
| `app/services/embedding_service.py` | 调用 embedding model 生成向量 |
| `app/services/vector_store.py` | 使用 Qdrant 保存和检索 chunk 向量 |
| `app/services/index_service.py` | 组织多文件索引流程 |
| `app/services/rag_service.py` | 组织 query embedding、检索、prompt 构造和问答生成 |
| `tests/` | 基础单元测试 |
| `codebase_eval.md` | Codebase QA 评测集 V1 |
| `week2_review.md` | Week 2 项目复盘 |

## Metadata 设计

每个 chunk 会保存以下 metadata：

| 字段 | 说明 |
|---|---|
| `file_path` | chunk 所属文件路径 |
| `file_type` | 文件类型，例如 `py`、`md` |
| `start_line` | chunk 起始行号 |
| `end_line` | chunk 结束行号 |
| `chunk_type` | chunk 类型，例如 `function`、`class`、`module`、`markdown_section` |
| `symbol_name` | 函数名或类名，普通 chunk 为空 |
| `content` | chunk 原始内容 |

metadata 的作用：

- 让回答能够引用具体文件和行号
- 让模型知道代码片段属于函数、类还是模块级代码
- 支持后续按符号、文件、模块做检索增强
- 支持评测 sources 是否正确

## Chunk 策略

当前切分策略：

| 文件类型 | 切分方式 |
|---|---|
| Markdown / README | 优先按标题切分，超长 section 再按固定行数切分 |
| Python | 优先使用 AST 识别函数和类 |
| Python function | 函数作为独立 chunk |
| Python class | 类作为独立 chunk |
| Python module | 非函数、非类的模块级代码作为 module chunk |
| 其他文本文件 | 按固定行数切分 |

AST chunk 的价值：

- 函数和类天然是代码理解的最小语义单元
- 比固定行数切分更适合回答“这个函数在哪”“这个类负责什么”
- 可以保留 `symbol_name`，提升 sources 可解释性
- 可以支持后续 `inspect_symbol` 等工具能力

## 环境变量

本项目使用 `.env` 保存本地真实配置，`.env` 不提交到 GitHub。

`.env.example`：

```env
AIHUBMIX_API_KEY=your-api-key-here
AIHUBMIX_BASE_URL=https://aihubmix.com/v1
AIHUBMIX_MODEL=deepseek-v4-flash
AIHUBMIX_EMBEDDING_MODEL=text-embedding-3-small
```

## 启动方式

安装依赖后启动服务：

```bash
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

访问 Swagger：

```text
http://127.0.0.1:8000/docs
```

## API 接口

### 健康检查

```http
GET /health
```

响应示例：

```json
{
  "status": "ok"
}
```

### 扫描代码仓库

```http
POST /repositories/scan
```

请求示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent"
}
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_count": 3,
  "files": [
    {
      "path": "README.md",
      "file_type": "md",
      "size": 12000
    },
    {
      "path": "app/main.py",
      "file_type": "py",
      "size": 3200
    }
  ]
}
```

### 查看仓库文件列表

```http
GET /repositories/files?repo_path=/Users/xiongzehao/代码/2026-07-codebase-agent
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "files": [
    {
      "path": "README.md",
      "file_type": "md",
      "size": 12000
    }
  ]
}
```

### 读取代码文件

```http
POST /code/files/read
```

请求示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "app/main.py"
}
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "app/main.py",
  "file_type": "py",
  "line_count": 123,
  "lines": [
    {
      "line_number": 1,
      "content": "from fastapi import FastAPI, HTTPException"
    }
  ]
}
```

### 预览代码 Chunk

```http
POST /repositories/chunks/preview
```

请求示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "app/main.py",
  "chunk_size": 120
}
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "app/main.py",
  "chunk_size": 120,
  "chunk_count": 14,
  "chunks": [
    {
      "file_path": "app/main.py",
      "file_type": "py",
      "start_line": 108,
      "end_line": 123,
      "chunk_type": "function",
      "content": "def ask_repository(request: AskRequest):\n    ...",
      "symbol_name": "ask_repository"
    }
  ]
}
```

### 索引代码文件

```http
POST /repositories/index
```

请求示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_paths": [
    "README.md",
    "app/main.py",
    "app/schemas.py",
    "tests/test_code_reader.py"
  ],
  "chunk_size": 120
}
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_paths": [
    "README.md",
    "app/main.py",
    "app/schemas.py",
    "tests/test_code_reader.py"
  ],
  "chunk_size": 120,
  "file_count": 4,
  "chunk_count": 42,
  "indexed_count": 42
}
```

### 基于代码仓库问答

```http
POST /repositories/ask
```

请求示例：

```json
{
  "question": "AskRequest 这个类负责什么？",
  "top_k": 8,
  "score_threshold": 0.25
}
```

响应示例：

```json
{
  "question": "AskRequest 这个类负责什么？",
  "answer": "结论：AskRequest 是用于接收代码仓库问答请求的请求体模型...",
  "sources": [
    {
      "file_path": "app/schemas.py",
      "start_line": 83,
      "end_line": 86,
      "score": 0.7131,
      "content": "class AskRequest(BaseModel):\n    question: str = Field(min_length=1)\n    top_k: int = Field(default=3, ge=1, le=10)\n    score_threshold: float = Field(default=0.5, ge=0, le=1)",
      "chunk_type": "class",
      "symbol_name": "AskRequest"
    }
  ]
}
```

## 评测

项目包含 Codebase QA 评测集 V1：

```text
codebase_eval.md
```

当前评测覆盖：

- 项目定位
- 项目入口
- 接口职责
- 文件定位
- 函数职责
- 类职责
- chunk 策略
- embedding 调用
- Qdrant 写入
- RAG prompt 构造
- 测试覆盖
- 资料不足时拒答

最近一次评测结果：

```text
通过：14 / 20
部分通过：4 / 20
失败：2 / 20
```

## 当前不足

当前系统仍然是 Codebase RAG 基础版，主要不足包括：

- Qdrant 使用内存模式，服务重启后索引丢失
- 每次索引会重建 collection
- 还没有持久化项目索引
- 还没有实现 hybrid search
- 还没有实现 rerank
- 函数名、类名、文件名等精确查询仍依赖语义召回
- sources 排序有时不够理想
- tests 目录的问题召回质量仍需优化
- 还没有 Tool Calling
- 还没有 Agent Loop
- 还没有多轮上下文和记忆
- 还没有 trace 和可视化执行过程

## 下一步计划

- 增加 keyword match / hybrid search
- 增加 source rerank
- 增加符号索引和 `inspect_symbol`
- 增加工具调用：
  - `list_files`
  - `read_file`
  - `search_code`
  - `inspect_symbol`
- 设计 Agent Loop
- 增加运行 trace
- 增加持久化向量库
- 完善评测集和失败案例复盘

## 参考项目

本项目参考 Pico 的 Agent Harness 思路，但不会照搬其代码。

重点参考方向：

- Agent Harness
- Tool Calling
- Context Management
- Layered Memory
- Run Trace
- Evaluation
