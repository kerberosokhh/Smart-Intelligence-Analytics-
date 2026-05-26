# Smart Intelligence Analytics（智能数据分析助理）

基于 DeepSeek V4 Pro + LangChain + FastAPI + Vue3/Nuxt3 的自然语言数据分析系统。

## 文档

- [开发计划（口语 Phase）](docs/plans/plan.md)
- [Agent 实现详设](docs/plans/2026-05-24-intelligent-data-analysis-system.md)
- [ADR-001：DeepSeek 接入选型（LangChain MCP）](docs/adr/001-deepseek-via-chatdeepseek.md)
- [计划模板](docs/plans/TEMPLATE.md)

## 仓库

https://github.com/kerberosokhh/Smart-Intelligence-Analytics-

---

## DeepSeek + LangChain 接入（已通过 MCP 选型）

开发阶段使用 Cursor 集成的 **LangChain Docs MCP**（`docs-langchain`）检索官方文档，确定 DeepSeek V4 Pro 接入方案：

| 项 | 选型 |
|----|------|
| Python 包 | `langchain-deepseek` |
| 模型类 | `ChatDeepSeek` |
| 模型名 | `deepseek-v4-pro` |
| 封装 | `backend/app/core/llm.py` → `get_llm()` |

**官方文档（MCP 检索来源）：**

- [ChatDeepSeek integration](https://docs.langchain.com/oss/python/integrations/chat/deepseek)
- [DeepSeek API Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing)

完整决策记录见 [docs/adr/001-deepseek-via-chatdeepseek.md](docs/adr/001-deepseek-via-chatdeepseek.md)。

### 验证 LLM 连通

```bash
cd backend
# 配置 backend/.env：DEEPSEEK_API_KEY、DEEPSEEK_MODEL=deepseek-v4-pro
.\.venv\Scripts\pytest tests/test_llm.py -v -s
```

---

## 快速启动

### 后端（FastAPI）

```bash
cd backend
python -m venv .venv
# Windows
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

健康检查：`GET http://127.0.0.1:8000/api/health`

**Phase 3 API（已实现）：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/sessions` | 会话列表 |
| POST | `/api/sessions` | 新建会话 |
| PATCH | `/api/sessions/{id}` | 重命名 |
| DELETE | `/api/sessions/{id}` | 删除会话 |
| GET | `/api/sessions/{id}/messages` | 历史消息 |
| GET | `/api/schema` | 业务表结构 |
| POST | `/api/chat/stream` | SSE 流式问答（body: `session_id`, `message`） |

SSE 事件类型：`token` · `sql` · `data` · `chart` · `done` · `error`

测试：

```bash
cd backend
.\.venv\Scripts\pytest tests/ -v -m "not integration"
```

含真实 LLM 的 NL2SQL 集成测试：`pytest tests/test_nl2sql_agent.py -m integration -v`

环境变量：复制 `backend/.env.example` 为 `backend/.env`，填写 `DEEPSEEK_API_KEY` 与 `DEEPSEEK_MODEL`。

### 前端（Nuxt 3 SPA）

```bash
cd frontend
npm install
npm run dev
```

浏览器打开终端显示的 Local 地址（默认 http://localhost:3000）。开发环境通过 `nitro.devProxy` 将 `/api` 代理到 `http://127.0.0.1:8000`。

顶栏状态 **「API 已连接」** 表示前后端联通正常。

### 端到端演示（Phase 4）

1. **先启动后端**（需配置 `DEEPSEEK_API_KEY`），再启动前端
2. 点击 **新建会话**
3. 输入：`各品类销售总额是多少？` → 查看 SQL、右侧柱状图
4. 继续追问：`只要华东地区的` → 验证多轮上下文

可选环境变量（`frontend/.env` 或 shell）：

| 变量 | 默认 | 说明 |
|------|------|------|
| `NUXT_PUBLIC_API_BASE` | `/api` | REST/SSE 基路径 |
| `NUXT_DEV_PROXY_TARGET` | `http://127.0.0.1:8000` | 开发代理目标 |

### 目录结构

```
backend/
  app/
    api/             # sessions, chat/stream, schema
    agents/          # nl2sql_agent, chart_agent
    core/            # llm, memory, session
    db/              # sqlite, models, migrations
    services/        # query_service, viz_service
    schemas/
    config.py
    main.py
  data/              # app.db（启动时自动迁移）
  tests/
docs/
  adr/
frontend/            # Nuxt 3 SPA，已对接 REST + SSE
```
