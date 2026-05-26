<script setup lang="ts">
import { fetchHealth } from '~/utils/api'

const { bootstrap, bootstrapError, isBootstrapping } = useSessions()
const healthOk = ref<boolean | null>(null)

onMounted(async () => {
  try {
    const health = await fetchHealth()
    healthOk.value = health.status === 'ok'
    await bootstrap()
  } catch {
    healthOk.value = false
  }
})

const statusLabel = computed(() => {
  if (isBootstrapping.value) return '加载中…'
  if (healthOk.value === false || bootstrapError.value) return '后端未连接'
  if (healthOk.value) return 'API 已连接'
  return '检测中…'
})

const statusClass = computed(() => {
  if (healthOk.value && !bootstrapError.value) return 'status-pill--ok'
  if (healthOk.value === false || bootstrapError.value) return 'status-pill--err'
  return ''
})
</script>

<template>
  <div class="workspace">
    <header class="topbar tech-glass">
      <div class="brand">
        <div class="brand-icon">
          <span class="brand-dot" />
          <span class="brand-ring" />
        </div>
        <div class="brand-text">
          <h1 class="brand-title">
            <span class="tech-gradient-text">IntelliGate</span>
            <span class="brand-sub">Analytics</span>
          </h1>
          <p class="brand-desc">智能数据分析助理 · NL2SQL</p>
        </div>
      </div>
      <div class="topbar-meta">
        <span class="status-pill" :class="statusClass">
          <span class="status-dot" />
          {{ statusLabel }}
        </span>
      </div>
    </header>

    <div class="app-shell">
      <aside class="panel panel-sessions tech-glass">
        <header class="panel-header">
          <span class="panel-icon panel-icon--cyan">◈</span>
          <span>会话管理</span>
        </header>
        <div class="panel-body panel-body--flush">
          <SessionList />
        </div>
      </aside>

      <main class="panel panel-chat tech-glass panel-chat-main">
        <header class="panel-header">
          <span class="panel-icon panel-icon--indigo">◎</span>
          <span>智能问答</span>
        </header>
        <div class="panel-body panel-body--chat">
          <ChatPanel />
        </div>
      </main>

      <aside class="panel panel-chart tech-glass">
        <header class="panel-header">
          <span class="panel-icon panel-icon--violet">▣</span>
          <span>数据可视化</span>
        </header>
        <div class="panel-body">
          <ChartPanel />
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.workspace {
  display: flex;
  flex-direction: column;
  height: 100vh;
  padding: 12px 14px 14px;
  gap: 12px;
  box-sizing: border-box;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 18px;
  border-radius: var(--tech-radius);
  flex-shrink: 0;
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-icon {
  position: relative;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.brand-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--tech-gradient);
  box-shadow: 0 0 12px rgba(14, 165, 233, 0.6);
  z-index: 1;
}

.brand-ring {
  position: absolute;
  inset: 0;
  border-radius: 12px;
  border: 1px solid var(--tech-border-strong);
  background: var(--tech-gradient-soft);
  animation: pulse-ring 3s ease-in-out infinite;
}

@keyframes pulse-ring {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.85;
    transform: scale(1.02);
  }
}

.brand-title {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.02em;
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.brand-sub {
  font-size: 18px;
  font-weight: 600;
  color: var(--tech-text);
}

.brand-desc {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--tech-text-muted);
  letter-spacing: 0.02em;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 500;
  color: var(--tech-text-secondary);
  background: var(--tech-gradient-soft);
  border: 1px solid var(--tech-border);
  border-radius: 999px;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
  animation: blink-dot 2s ease-in-out infinite;
}

@keyframes blink-dot {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-pill--ok .status-dot {
  background: #22c55e;
  box-shadow: 0 0 8px rgba(34, 197, 94, 0.6);
}

.status-pill--err .status-dot {
  background: #ef4444;
  box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
  animation: none;
}

.status-pill--err {
  color: #b91c1c;
  border-color: rgba(239, 68, 68, 0.25);
  background: rgba(254, 226, 226, 0.5);
}

.app-shell {
  display: grid;
  grid-template-columns: 260px minmax(0, 1fr) 420px;
  gap: 12px;
  flex: 1;
  min-height: 0;
}

.panel {
  display: flex;
  flex-direction: column;
  border-radius: var(--tech-radius);
  min-height: 0;
  overflow: hidden;
}

.panel-chat-main {
  box-shadow: var(--tech-shadow-glow);
}

.panel-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  font-weight: 600;
  font-size: 14px;
  letter-spacing: 0.01em;
  border-bottom: 1px solid var(--tech-border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, transparent 100%);
  flex-shrink: 0;
}

.panel-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

.panel-icon--cyan {
  color: var(--tech-accent);
  background: rgba(14, 165, 233, 0.12);
}

.panel-icon--indigo {
  color: var(--tech-accent-2);
  background: rgba(99, 102, 241, 0.12);
}

.panel-icon--violet {
  color: #8b5cf6;
  background: rgba(139, 92, 246, 0.12);
}

.panel-body {
  flex: 1;
  overflow: auto;
  padding: 16px;
  min-height: 0;
}

.panel-body--flush {
  padding: 12px;
}

.panel-body--chat {
  display: flex;
  flex-direction: column;
  padding: 12px 16px 16px;
  overflow: hidden;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.3) 0%, transparent 120px);
}
</style>
