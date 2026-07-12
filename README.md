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

## API 草案

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

用于触发代码仓库扫描。当前版本先定义接口结构，后续会接入真实扫描逻辑。

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
  "file_count": 0
}
```

### 查看仓库文件列表

```http
GET /repositories/files?repo_path=/Users/xiongzehao/代码/2026-07-codebase-agent
```

用于查看指定代码仓库下的文件列表。当前版本先返回空列表，后续会接入真实文件扫描结果。

响应示例：

```json
{
  "repo_path": "/Users/xiongzehao/代码/2026-07-codebase-agent",
  "files": []
}
```

## 当前状态

当前处于 V0 阶段：

- [x] 确定项目名称
- [x] 明确业务场景
- [x] 设计核心能力清单
- [x] 设计 V0 / V1 / V2 / V3 版本路线
- [x] 创建项目目录结构
- [x] 实现 FastAPI 最小应用
- [x] 实现 `/health`
- [x] 设计 `/repositories/scan` 接口
- [x] 设计 `/repositories/files` 接口
- [ ] 实现真实代码仓库扫描
- [ ] 忽略 `.git`、`.venv`、`__pycache__` 等无关目录
- [ ] 返回真实文件数量和文件列表
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
