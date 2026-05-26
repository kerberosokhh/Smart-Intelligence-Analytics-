# 智能数据分析助理 — 开发计划

> 口语计划源文件。写完后说：**「同步计划到 Linear」**。  
> Agent 详设见 `2026-05-24-intelligent-data-analysis-system.md`。

---

## Phase 1 — 前后端基础框架

- ~~后端脚手架：FastAPI + CORS + config~~ ✅
- ~~健康检查：GET /api/health + pytest~~ ✅
- ~~后端环境模板：.env.example~~ ✅
- ~~Nuxt3 脚手架：ssr false + TypeScript~~ ✅
- ~~前端依赖：Pinia、Element Plus、vue-echarts~~ ✅
- ~~Nuxt 开发代理：devProxy /api~~ ✅
- ~~联调探针：首页 fetch /api/health~~ ✅

## Phase 2 — 前端 UI（Mock）

- ~~三栏布局 layouts/default.vue~~ ✅
- ~~SessionList 会话列表 Mock~~ ✅
- ~~SessionItem 单条会话~~ ✅
- ~~ChatPanel 与 MessageList~~ ✅
- ~~ChatInput 输入与 Mock 流式~~ ✅
- ~~ChartPanel 与 ChartRenderer~~ ✅
- ~~Pinia 全局状态~~ ✅
- ~~类型定义 session / message / chart~~ ✅

## Phase 3 — 后端接口

- ~~SQLite 连接与 Schema 迁移~~ ✅
- ~~Demo 订单示例数据~~ ✅
- ~~DeepSeek LLM 接入~~ ✅
- ~~会话管理 API CRUD~~ ✅
- ~~上下文记忆模块~~ ✅
- ~~LangChain NL2SQL Agent~~ ✅
- ~~图表规格 Agent~~ ✅
- ~~查询编排 query_service~~ ✅
- ~~SSE 聊天接口 /api/chat/stream~~ ✅

## Phase 4 — 前后端联调

- ~~前端 API 服务层 utils/api.ts~~ ✅
- ~~SSE 客户端 utils/sse.ts~~ ✅
- ~~会话与聊天 composables 对接真实 API~~ ✅
- ~~图表 chart 事件动态渲染~~ ✅
- ~~端到端：各品类销售总额 + 多轮上下文~~ ✅
- ~~README 与环境说明~~ ✅
