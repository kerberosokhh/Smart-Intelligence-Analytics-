import type { ChartSpec } from '~/types/chart'
import { ElMessage } from 'element-plus'
import { useAppStore } from '~/stores/app'
import { createId } from '~/utils/id'
import { connectChatStream } from '~/utils/sse'

export function useChatStream() {
  const store = useAppStore()
  let abortStream: (() => void) | null = null

  async function sendMessage(content: string) {
    const text = content.trim()
    if (!text || store.isStreaming) return

    let sessionId = store.currentSessionId
    try {
      if (!sessionId) {
        const session = await store.createSession()
        sessionId = session.id
      }

      store.addMessage({
        id: createId(),
        sessionId,
        role: 'user',
        content: text,
      })

      const assistantId = createId()
      store.addMessage({
        id: assistantId,
        sessionId,
        role: 'assistant',
        content: '',
      })

      store.setStreaming(true)
      let assistantText = ''
      let assistantSql: string | undefined

      abortStream = connectChatStream(sessionId, text, {
        onEvent: (event) => {
          if (event.type === 'token' && typeof event.content === 'string') {
            assistantText += event.content
            store.updateMessage(sessionId!, assistantId, { content: assistantText })
          }

          if (event.type === 'sql' && typeof event.content === 'string') {
            assistantSql = event.content
            store.updateMessage(sessionId!, assistantId, { sql: assistantSql })
          }

          if (event.type === 'data' && Array.isArray(event.content)) {
            store.setQueryData(event.content as Record<string, unknown>[])
          }

          if (event.type === 'chart' && event.content && typeof event.content === 'object') {
            store.setChartSpec(event.content as ChartSpec)
          }

          if (event.type === 'done') {
            store.setStreaming(false)
            abortStream = null
            void finalizeStream(sessionId!)
          }

          if (event.type === 'error') {
            store.setStreaming(false)
            const errMsg = typeof event.content === 'string' ? event.content : '生成失败'
            store.updateMessage(sessionId!, assistantId, { content: errMsg })
            ElMessage.error(errMsg)
            abortStream = null
          }
        },
      }).abort
    } catch (error) {
      store.setStreaming(false)
      const errMsg = error instanceof Error ? error.message : '发送失败'
      ElMessage.error(errMsg)
    }
  }

  async function finalizeStream(sessionId: string) {
    try {
      await store.loadSessions()
      await store.loadMessages(sessionId)
    } catch {
      // 流式已完成，刷新失败不阻断主流程
    }
  }

  function cancelStream() {
    abortStream?.()
    abortStream = null
    store.setStreaming(false)
  }

  return {
    messages: computed(() => store.currentMessages),
    isStreaming: computed(() => store.isStreaming),
    currentSessionId: computed(() => store.currentSessionId),
    sendMessage,
    cancelStream,
  }
}
