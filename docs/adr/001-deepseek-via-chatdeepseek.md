# ADR-001：DeepSeek V4 Pro 通过 ChatDeepSeek 接入

**状态：** 已采纳（部分实现）  
**日期：** 2026-05-25

## Context

智能数据分析系统需要接入 DeepSeek V4 Pro，用于 NL2SQL Agent、图表规格生成与 SSE 流式回答。早期详设草案使用 `ChatOpenAI` + OpenAI 兼容 `base_url` 方案，需在实现前确认 LangChain 官方推荐做法。

## Investigation（LangChain MCP）

开发阶段通过 Cursor 集成的 **LangChain Docs MCP**（`user-docs-langchain` / `docs-langchain`）检索官方文档：

| MCP 工具 | 用途 |
|----------|------|
| `search_docs_by_lang_chain` | 语义搜索 LangChain 文档 |
| `query_docs_filesystem_docs_by_lang_chain` | 按路径读取完整文档页 |

**检索结论摘要：**

1. 官方 DeepSeek 集成包为 **`langchain-deepseek`**，聊天模型类为 **`ChatDeepSeek`**
2. 官方文档：[ChatDeepSeek integration](https://docs.langchain.com/oss/python/integrations/chat/deepseek)
3. DeepSeek API 模型名 **`deepseek-v4-pro`**（见 [DeepSeek Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing)）
4. `ChatDeepSeek` 支持 Tool calling、Structured output、Token 流式——满足 NL2SQL Agent 需求
5. `ChatOpenAI` + `base_url` 为 OpenAI 兼容备选，但不保留 DeepSeek 特有字段（如 thinking）；官方建议 DeepSeek 原生能力优先用 `langchain-deepseek`

**备选方案对比：**

| 方案 | 优点 | 缺点 |
|------|------|------|
| `ChatDeepSeek` + `langchain-deepseek` | 官方集成、Tool calling 完整 | 需额外依赖包 |
| `ChatOpenAI` + `base_url` | 与详设草案一致、包已存在 | 非 DeepSeek 一等公民，thinking 等字段可能丢失 |
| `init_chat_model(..., model_provider="deepseek")` | 统一入口 | 底层仍为 `langchain-deepseek` |

## Decision

采用 **`langchain-deepseek`** 的 **`ChatDeepSeek`**，模型 **`deepseek-v4-pro`**，封装于 `backend/app/core/llm.py` 的 `get_llm()`。

环境变量：

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_MODEL=deepseek-v4-pro`（默认）

## Implementation

| 文件 | 说明 |
|------|------|
| `backend/app/core/llm.py` | `get_llm()` → `ChatDeepSeek` |
| `backend/app/config.py` | `deepseek_api_key`、`deepseek_model` |
| `backend/tests/test_llm.py` | 连通性 pytest（需配置 API Key） |
| `backend/requirements.txt` | 含 `langchain-deepseek` |

验证命令：

```bash
cd backend
.\.venv\Scripts\pytest tests/test_llm.py -v -s
```

## Consequences

- Phase 3 Agent 开发统一通过 `get_llm()` 获取 LLM 实例，避免散落构造
- 详设 §4.1 与 Task 3 由 `ChatOpenAI` 更新为 `ChatDeepSeek`
- 后续若需 Thinking 模式，在 `ChatDeepSeek` 上扩展 `model_kwargs` / 官方参数，而非回退 `ChatOpenAI`

## References

- [ChatDeepSeek integration — LangChain Docs](https://docs.langchain.com/oss/python/integrations/chat/deepseek)
- [LangChain Python Chat model integrations](https://docs.langchain.com/oss/python/integrations/chat/index)
- [DeepSeek API Models & Pricing](https://api-docs.deepseek.com/quick_start/pricing)
