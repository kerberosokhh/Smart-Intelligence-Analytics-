<script setup lang="ts">
import type { Session } from '~/types/session'

const props = defineProps<{
  session: Session
  active: boolean
}>()

const emit = defineEmits<{
  select: [sessionId: string]
  rename: [sessionId: string, title: string]
  remove: [sessionId: string]
}>()

const editing = ref(false)
const draftTitle = ref(props.session.title)

watch(
  () => props.session.title,
  (title) => {
    if (!editing.value) draftTitle.value = title
  },
)

function startEdit() {
  editing.value = true
  draftTitle.value = props.session.title
}

function commitEdit() {
  editing.value = false
  const next = draftTitle.value.trim()
  if (next && next !== props.session.title) {
    emit('rename', props.session.id, next)
  }
}

function onRemove() {
  emit('remove', props.session.id)
}
</script>

<template>
  <div
    class="session-item"
    :class="{ active }"
    @click="emit('select', session.id)"
  >
    <span class="active-bar" />
    <div class="session-main">
      <el-input
        v-if="editing"
        v-model="draftTitle"
        size="small"
        @click.stop
        @keyup.enter="commitEdit"
        @blur="commitEdit"
      />
      <span v-else class="session-title" @dblclick.stop="startEdit">
        {{ session.title }}
      </span>
      <span class="session-time">
        {{ new Date(session.updatedAt).toLocaleDateString() }}
      </span>
    </div>

    <div class="session-actions" @click.stop>
      <button type="button" class="action-btn" title="重命名" @click="startEdit">✎</button>
      <el-popconfirm title="确定删除该会话？" @confirm="onRemove">
        <template #reference>
          <button type="button" class="action-btn action-btn--danger" title="删除">×</button>
        </template>
      </el-popconfirm>
    </div>
  </div>
</template>

<style scoped>
.session-item {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 12px 12px 12px 14px;
  border-radius: var(--tech-radius-sm);
  cursor: pointer;
  border: 1px solid transparent;
  background: rgba(255, 255, 255, 0.45);
  transition: all 0.2s ease;
}

.session-item:hover {
  background: rgba(255, 255, 255, 0.85);
  border-color: var(--tech-border);
  box-shadow: var(--tech-shadow-sm);
}

.session-item.active {
  background: rgba(255, 255, 255, 0.95);
  border-color: var(--tech-border-strong);
  box-shadow: var(--tech-shadow-md);
}

.active-bar {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%) scaleY(0);
  width: 3px;
  height: 60%;
  border-radius: 0 3px 3px 0;
  background: var(--tech-gradient);
  transition: transform 0.2s ease;
}

.session-item.active .active-bar {
  transform: translateY(-50%) scaleY(1);
}

.session-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.session-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.session-time {
  font-size: 11px;
  color: var(--tech-text-muted);
  font-family: var(--tech-mono);
}

.session-actions {
  display: none;
  flex-shrink: 0;
  gap: 4px;
}

.session-item:hover .session-actions,
.session-item.active .session-actions {
  display: flex;
}

.action-btn {
  width: 26px;
  height: 26px;
  border: 1px solid var(--tech-border);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.8);
  color: var(--tech-text-secondary);
  font-size: 14px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  color: var(--tech-accent);
  border-color: var(--tech-accent);
  background: rgba(14, 165, 233, 0.08);
}

.action-btn--danger:hover {
  color: #ef4444;
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.06);
}
</style>
