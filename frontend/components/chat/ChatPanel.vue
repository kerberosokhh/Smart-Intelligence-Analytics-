<script setup lang="ts">
const { messages, isStreaming, sendMessage } = useChatStream()

const listRef = ref<HTMLElement | null>(null)

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    listRef.value?.scrollTo({ top: listRef.value.scrollHeight, behavior: 'smooth' })
  },
)

watch(
  () => messages.value.at(-1)?.content,
  async () => {
    await nextTick()
    listRef.value?.scrollTo({ top: listRef.value.scrollHeight })
  },
)
</script>

<template>
  <div class="chat-panel">
    <div ref="listRef" class="messages-scroll">
      <MessageList :messages="messages" :is-streaming="isStreaming" />
    </div>
    <ChatInput :disabled="isStreaming" @send="sendMessage" />
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
  width: 100%;
}

.messages-scroll {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  padding-right: 4px;
}
</style>
