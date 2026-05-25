# 开发计划模板（Markdown → Linear Todo）

主计划文件：**`docs/plans/plan.md`**（在 `.cursor/rules/dev-workflow.mdc` 的 `plan_sync` 配置）。

---

## 推荐写法

```markdown
## Phase 1 — 基础框架
- 后端脚手架
- 健康检查

## phase2 — 前端 UI
- 三栏布局
- SessionList
```

---

## 常用口语

| 说法 | 效果 |
|------|------|
| 同步计划到 Linear | `plan.md` → Linear Todo |
| 只同步 Phase 2 | 仅 Phase 2 条目 |
| Phase 1 完成了 | plan 划线 + Linear Done |
| 开始做登录系统 | Issue In Progress + 分支名 |

---

## 已完成

```markdown
- ~~后端脚手架~~ ✅
```

同步或完成时会标 Linear **Done**，不会重复创建。

---

## 与详设文档区别

| 文件 | 用途 |
|------|------|
| `plan.md` | 你的 Phase 口语计划，**同步 Linear** |
| `2026-05-24-....md` | Agent 实现详设（Task 步骤），默认不同步 |

要同步详设时：`@2026-05-24-....md 同步到 Linear`
