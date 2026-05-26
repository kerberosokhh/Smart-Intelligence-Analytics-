<script setup lang="ts">
import type { Message } from '~/types/message'

defineProps<{
  messages: Message[]
  isStreaming: boolean
}>()

const suggestions = ['各品类销售总额是多少？', '只要华东地区的', '按月统计订单趋势']
</script>

<template>
  <div class="message-list">
    <div v-if="messages.length === 0" class="empty">
      <div class="empty-hero">
        <div class="empty-glow" />
        <span class="empty-symbol">AI</span>
      </div>
      <h3 class="empty-title">开始你的数据探索</h3>
      <p class="empty-desc">用自然语言提问，系统将生成 SQL 与可视化图表</p>
      <div class="suggestions">
        <span
          v-for="item in suggestions"
          :key="item"
          class="suggestion-chip"
        >{{ item }}</span>
      </div>
    </div>

    <div
      v-for="msg in messages"
      :key="msg.id"
      class="message-row"
      :class="msg.role"
    >
      <div class="avatar" :class="msg.role">
        {{ msg.role === 'user' ? 'U' : 'AI' }}
      </div>
      <div class="bubble">
        <div class="role-label">
          {{ msg.role === 'user' ? '你' : '智能助理' }}
        </div>
        <div class="content">
          {{ msg.content }}
          <span v-if="msg.role === 'assistant' && !msg.content && isStreaming" class="cursor">▍</span>
        </div>
        <pre v-if="msg.sql" class="sql-block"><code>{{ msg.sql }}</code></pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding-bottom: 16px;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
}

.empty-hero {
  position: relative;
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

.empty-glow {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  background: var(--tech-gradient);
  opacity: 0.15;
  filter: blur(12px);
}

.empty-symbol {
  position: relative;
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.05em;
  background: var(--tech-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.empty-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 700;
  color: var(--tech-text);
}

.empty-desc {
  margin: 0 0 20px;
  font-size: 14px;
  color: var(--tech-text-secondary);
  max-width: 320px;
  line-height: 1.6;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  max-width: 420px;
}

.suggestion-chip {
  padding: 6px 12px;
  font-size: 12px;
  color: var(--tech-text-secondary);
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid var(--tech-border);
  border-radius: 999px;
  transition: all 0.15s;
}

.suggestion-chip:hover {
  color: var(--tech-accent);
  border-color: var(--tech-accent);
  background: rgba(14, 165, 233, 0.08);
}

.message-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.message-row.user {
  flex-direction: row-reverse;
}

.avatar {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.avatar.user {
  background: var(--tech-gradient);
  color: #fff;
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.35);
}

.avatar.assistant {
  background: rgba(99, 102, 241, 0.12);
  color: var(--tech-accent-2);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.bubble {
  max-width: min(85%, 560px);
  padding: 12px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--tech-border);
  box-shadow: var(--tech-shadow-sm);
}

.message-row.user .bubble {
  background: var(--tech-gradient);
  color: #fff;
  border: none;
  box-shadow: 0 6px 20px rgba(14, 165, 233, 0.3);
}

.role-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  opacity: 0.7;
  margin-bottom: 6px;
}

.content {
  font-size: 14px;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

.cursor {
  animation: blink 1s step-end infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

.sql-block {
  margin: 12px 0 0;
  padding: 12px 14px;
  border-radius: 10px;
  background: #0f172a;
  color: #e2e8f0;
  font-size: 12px;
  font-family: var(--tech-mono);
  overflow-x: auto;
  border: 1px solid rgba(14, 165, 233, 0.25);
  box-shadow: inset 0 0 20px rgba(14, 165, 233, 0.05);
}

.message-row.user .sql-block {
  background: rgba(15, 23, 42, 0.35);
  border-color: rgba(255, 255, 255, 0.2);
  color: #f1f5f9;
}
</style>
