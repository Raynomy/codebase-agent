# Codebase Agent

Codebase Agent 是一个面向代码仓库理解与修改规划的本地 Agent 系统。

项目目标是帮助开发者在接手陌生代码仓库时，快速理解项目结构、模块职责、核心文件、接口链路和潜在修改范围。

## 项目背景

开发者在接手一个陌生项目时，通常需要手动阅读 README、目录结构、源码文件和测试文件，再通过搜索和调试逐步建立项目理解。

这个过程存在几个问题：

- 项目结构理解成本高
- 相关代码定位效率低
- 修改影响范围难判断
- 多轮追问时上下文容易丢失
- 回答依据不可追溯
- 代码阅读过程难复盘

Codebase Agent 面向这个场景，目标是通过代码仓库扫描、语义检索、工具调用、上下文管理和运行 trace，辅助用户理解项目、定位代码并生成修改建议。

## 项目定位

本项目不是普通聊天机器人，也不是单纯的 RAG 文档问答系统。

它面向的是代码仓库场景：

```text
输入一个本地代码仓库
-> 扫描项目目录
-> 读取 README / docs / Python 源码 / 测试文件
-> 对代码和文档进行 chunk 切分
-> 建立代码语义索引
-> 支持自然语言问答
-> 返回相关文件、代码片段和行号来源
-> 后续支持工具调用、多轮上下文、记忆和运行 trace
```

## 核心目标

当前项目最终希望具备以下能力：

- 扫描本地代码仓库
- 读取 README、Markdown 文档、Python 源码和测试文件
- 按文件、函数、类进行代码切分
- 保存代码 metadata：
  - `file_path`
  - `chunk_type`
  - `symbol_name`
  - `start_line`
  - `end_line`
- 基于 embedding 和 Qdrant 建立代码语义索引
- 支持基于代码上下文的自然语言问答
- 返回 answer + sources
- sources 包含文件路径、行号范围和代码片段
- 支持工具调用：
  - `list_files`
  - `read_file`
  - `search_code`
  - `inspect_symbol`
- 支持多轮追问和上下文管理
- 支持项目级、文件级摘要记忆
- 支持运行 trace 和评测闭环

## 技术栈

计划使用：

- Python
- FastAPI
- Pydantic
- LLM API
- Embedding Model
- Qdrant
- Tool Calling
- pytest
- Docker / Docker Compose

## 版本路线

### V0：项目骨架与业务定义

目标：

- 搭建项目目录结构
- 编写 README 初稿
- 实现基础 FastAPI 应用
- 实现 `/health`
- 明确项目业务场景和版本路线

### V1：Codebase RAG 基础版

目标：

- 扫描本地项目目录
- 读取 README / docs / Python 文件 / tests
- 切分代码 chunks
- 写入向量库
- 实现代码仓库问答接口
- 返回 answer + sources

### V2：代码元数据增强版

目标：

- 使用 AST 解析 Python 函数和类
- 保存 `file_path`、`symbol_name`、`chunk_type`、`start_line`、`end_line`
- 支持回答引用具体文件和行号

### V3：Tool Calling Agent 版本

目标：

- 实现 `list_files`
- 实现 `read_file`
- 实现 `search_code`
- 实现 `inspect_symbol`
- 设计简单 Agent Loop
- 让 Agent 能按任务需要主动调用工具读取代码仓库

## 项目结构

当前项目结构：

```text
2026-07-codebase-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── services/
│   │   ├── code_chunker.py
│   │   ├── code_reader.py
│   │   ├── embedding_service.py
│   │   ├── index_service.py
│   │   ├── repository_scanner.py
│   │   └── vector_store.py
│   ├── core/
│   ├── scanners/
│   ├── parsers/
│   ├── vector_store/
│   ├── tools/
│   ├── agent/
│   ├── memory/
│   ├── tracing/
│   └── evaluation/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

模块说明：

```text
app/scanners
负责扫描本地代码仓库，识别文件和目录。

app/services
负责组织业务逻辑，例如仓库扫描、文件列表查询和后续问答流程。

app/core
负责配置、日志、异常处理等项目基础设施。

app/parsers
负责解析代码文件，进行 chunk 切分和 metadata 提取。

app/vector_store
负责 embedding、向量入库和语义检索。

app/tools
负责 list_files、read_file、search_code 等工具调用。

app/agent
负责 Agent Loop、模型调用和最终回答生成。

app/memory
负责项目摘要、文件摘要和会话记忆。

app/tracing
负责记录 Agent 执行过程。

app/evaluation
负责评测集和结果统计。
```

## 环境变量

本项目使用 `.env` 保存本地真实配置，`.env` 不提交到 GitHub。

`.env.example` 示例：

```env
AIHUBMIX_API_KEY=your-api-key-here
AIHUBMIX_BASE_URL=https://aihubmix.com/v1
AIHUBMIX_EMBEDDING_MODEL=text-embedding-3-small
```

## API 接口

### 健康检查

```http
GET /health
```

用于确认服务是否正常启动。

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

用于触发代码仓库扫描，返回有效文件数量和文件列表。

当前扫描能力：

- 校验 `repo_path` 是否存在
- 校验 `repo_path` 是否为目录
- 递归扫描目录文件
- 过滤 `.git`
- 过滤 `.venv`
- 过滤 `__pycache__`
- 过滤 `.pytest_cache`
- 过滤 `.pyc`、`.pyo`、`.DS_Store` 等无关文件
- 返回文件相对路径、文件类型和文件大小

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
  "file_count": 6,
  "files": [
    {
      "path": "README.md",
      "file_type": "md",
      "size": 6089
    },
    {
      "path": "app/main.py",
      "file_type": "py",
      "size": 1137
    },
    {
      "path": "app/services/repository_scanner.py",
      "file_type": "py",
      "size": 1668
    }
  ]
}
```

路径错误时返回：

```json
{
  "detail": "Repository path does not exist: /not/exist/path"
}
```

### 查看仓库文件列表

```http
GET /repositories/files?repo_path=/Users/xiongzehao/代码/2026-07-codebase-agent
```

用于查看指定代码仓库下的文件列表。

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "files": [
    {
      "path": "README.md",
      "file_type": "md",
      "size": 6089
    },
    {
      "path": "app/main.py",
      "file_type": "py",
      "size": 1137
    }
  ]
}
```

### 读取代码文件

```http
POST /code/files/read
```

用于安全读取目标仓库内的指定文件，并返回带行号的文件内容。

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
  "line_count": 59,
  "lines": [
    {
      "line_number": 1,
      "content": "from fastapi import FastAPI, HTTPException"
    }
  ]
}
```

安全限制：

- 只能读取 `repo_path` 内部文件
- 通过 `../` 逃逸到仓库外部的路径会被拒绝

### 预览代码 Chunk

```http
POST /repositories/chunks/preview
```

用于预览某个文件会被切分成哪些 chunks。该接口只返回切分结果，不写入向量库。

请求示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "app/main.py",
  "chunk_size": 20
}
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "app/main.py",
  "chunk_size": 20,
  "chunk_count": 5,
  "chunks": [
    {
      "file_path": "app/main.py",
      "file_type": "py",
      "start_line": 1,
      "end_line": 20,
      "chunk_type": "python_lines",
      "content": "..."
    }
  ]
}
```

当前切分策略：

- Markdown / README：优先按标题切分，超长 section 再按固定行数切分
- Python：基础版按固定行数切分
- 其他文本文件：按固定行数切分

### 索引代码文件

```http
POST /repositories/index
```

用于将指定文件切分成 chunks，调用 embedding model 生成向量，并写入 Qdrant。

请求示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "README.md",
  "chunk_size": 40
}
```

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "file_path": "README.md",
  "chunk_size": 40,
  "chunk_count": 19,
  "indexed_count": 19
}
```

当前索引流程：

```text
读取文件
-> 切分 chunks
-> 调用 embedding model
-> 创建 Qdrant collection
-> 写入向量和 payload metadata
```

当前保存的 payload metadata：

- `file_path`
- `file_type`
- `start_line`
- `end_line`
- `chunk_type`
- `content`

当前阶段限制：

- Qdrant 使用内存模式 `QdrantClient(":memory:")`
- 每次索引都会重建 collection
- 当前只支持索引单个文件
- 暂未实现多文件共同检索
- 暂未实现稳定 `chunk_id`

Embedding 失败时，接口会返回 `503`。

### 基于代码仓库问答

```http
POST /repositories/ask
```

用于对已索引的代码仓库内容进行问答。

当前问答流程：

```text
用户问题
-> query embedding
-> Qdrant top-k 检索
-> 相似度阈值过滤
-> 拼接代码上下文 context
-> 构造 grounding prompt
-> LLM 基于资料生成回答
-> 返回 answer + sources
```

请求示例：

```json
{
  "question": "这个项目是做什么的？",
  "top_k": 3,
  "score_threshold": 0.5
}
```

响应示例：

```json
{
  "question": "这个项目是做什么的？",
  "answer": "根据提供的代码仓库资料，该项目是一个代码仓库理解助手...",
  "sources": [
    {
      "file_path": "README.md",
      "start_line": 81,
      "end_line": 90,
      "score": 0.65,
      "content": "..."
    }
  ]
}
```

当前返回的 `sources` 包含：

- `file_path`
- `start_line`
- `end_line`
- `score`
- `content`

当前限制：

- 需要先调用 `/repositories/index` 建立索引
- 当前 Qdrant 使用内存模式，服务重启后索引会丢失
- 当前索引单个文件时会重建 collection
- 当前回答质量依赖检索到的 chunks 是否足够相关

## 当前状态

当前处于 V1 初始阶段：

- [x] 确定项目名称
- [x] 明确业务场景
- [x] 设计核心能力清单
- [x] 设计 V0 / V1 / V2 / V3 版本路线
- [x] 创建项目目录结构
- [x] 实现 FastAPI 最小应用
- [x] 实现 `/health`
- [x] 设计 `/repositories/scan` 接口
- [x] 设计 `/repositories/files` 接口
- [x] 实现真实代码仓库扫描
- [x] 校验仓库路径参数
- [x] 忽略 `.git`、`.venv`、`__pycache__`、`.pytest_cache` 等无关目录
- [x] 过滤二进制文件和无关文件
- [x] 返回文件路径、文件类型和文件大小
- [x] 实现安全读取代码文件
- [x] 实现基础 chunk 切分
- [x] 接入 embedding model
- [x] 接入 Qdrant 内存向量库
- [x] 实现 `/repositories/index`
- [x] 实现向量检索
- [x] 实现相似度阈值过滤
- [x] 实现 `/repositories/ask`
- [x] 实现基于代码上下文的问答
- [x] 返回 answer + sources
- [ ] 实现多文件索引
- [ ] 提交代码

## 参考项目

本项目会参考 Pico 的 Agent Harness 设计思路：

```text
Pico：本地代码智能体 Harness
```

重点参考：

- Agent Harness 架构
- Tool Calling
- Context Management
- Layered Memory
- Run Trace
- Evaluation

但本项目不会照搬 Pico 的代码，而是围绕代码仓库理解与修改规划场景，设计自己的 Codebase Agent。
