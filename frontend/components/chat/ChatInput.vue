<script setup lang="ts">
const emit = defineEmits<{
  send: [content: string]
}>()

defineProps<{
  disabled?: boolean
}>()

const draft = ref('')

function submit() {
  const text = draft.value.trim()
  if (!text) return
  emit('send', text)
  draft.value = ''
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    submit()
  }
}
</script>

<template>
  <div class="chat-input">
    <div class="input-wrap">
      <el-input
        v-model="draft"
        class="chat-textarea"
        type="textarea"
        :rows="3"
        :disabled="disabled"
        placeholder="输入分析问题，Enter 发送 · Shift+Enter 换行"
        @keydown="onKeydown"
      />
    </div>
    <div class="actions">
      <span class="hint">Powered by DeepSeek V4 Pro</span>
      <el-button type="primary" :disabled="disabled || !draft.trim()" @click="submit">
        发送分析
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
  box-sizing: border-box;
  padding-top: 14px;
  border-top: 1px solid var(--tech-border);
  flex-shrink: 0;
}

.input-wrap {
  width: 100%;
  box-sizing: border-box;
  padding: 2px;
  border-radius: calc(var(--tech-radius-sm) + 2px);
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.2), rgba(99, 102, 241, 0.15));
}

.input-wrap :deep(.el-textarea) {
  width: 100%;
  display: block;
}

.input-wrap :deep(.chat-textarea),
.input-wrap :deep(.chat-textarea.el-textarea) {
  width: 100%;
  display: block;
}

.input-wrap :deep(.el-textarea__inner) {
  width: 100% !important;
  min-width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: block;
  border: none !important;
  box-shadow: none !important;
  resize: vertical;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
}

.hint {
  font-size: 11px;
  color: var(--tech-text-muted);
  font-family: var(--tech-mono);
  letter-spacing: 0.02em;
}
</style>
