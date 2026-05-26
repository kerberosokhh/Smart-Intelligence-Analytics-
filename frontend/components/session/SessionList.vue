<script setup lang="ts">
import { ElMessage } from 'element-plus'

const {
  sessions,
  currentSessionId,
  isBootstrapping,
  selectSession,
  createSession,
  renameSession,
  removeSession,
} = useSessions()

const creating = ref(false)

async function onCreate() {
  if (creating.value) return
  creating.value = true
  try {
    await createSession()
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '创建会话失败')
  } finally {
    creating.value = false
  }
}

async function onSelect(sessionId: string) {
  try {
    await selectSession(sessionId)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '加载会话失败')
  }
}

async function onRename(sessionId: string, title: string) {
  try {
    await renameSession(sessionId, title)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '重命名失败')
  }
}

async function onRemove(sessionId: string) {
  try {
    await removeSession(sessionId)
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '删除失败')
  }
}
</script>

<template>
  <div v-loading="isBootstrapping" class="session-list">
    <el-button type="primary" class="new-btn" :loading="creating" @click="onCreate">
      <span class="btn-icon">+</span>
      新建会话
    </el-button>

    <div v-if="sessions.length === 0" class="empty">
      <div class="empty-icon">◇</div>
      <p>暂无会话</p>
      <span>点击上方按钮开始分析</span>
    </div>

    <div v-else class="items">
      <SessionItem
        v-for="session in sessions"
        :key="session.id"
        :session="session"
        :active="session.id === currentSessionId"
        @select="onSelect"
        @rename="onRename"
        @remove="onRemove"
      />
    </div>
  </div>
</template>

<style scoped>
.session-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  height: 100%;
}

.new-btn {
  width: 100%;
  height: 40px;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.btn-icon {
  margin-right: 4px;
  font-size: 16px;
  font-weight: 700;
}

.items {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
  padding-right: 2px;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 32px 12px;
  color: var(--tech-text-muted);
  font-size: 13px;
}

.empty-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  font-size: 22px;
  color: var(--tech-accent);
  background: var(--tech-gradient-soft);
  border: 1px solid var(--tech-border);
  border-radius: 14px;
}

.empty p {
  margin: 0 0 4px;
  font-weight: 600;
  color: var(--tech-text-secondary);
}
</style>
