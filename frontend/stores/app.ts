import { defineStore } from 'pinia'
import type { ChartSpec } from '~/types/chart'
import type { Message } from '~/types/message'
import type { Session } from '~/types/session'
import {
  createSession as apiCreateSession,
  deleteSession as apiDeleteSession,
  fetchMessages,
  fetchSessions,
  updateSession as apiUpdateSession,
} from '~/utils/api'

export const useAppStore = defineStore('app', () => {
  const sessions = ref<Session[]>([])
  const currentSessionId = ref<string | null>(null)
  const messages = ref<Record<string, Message[]>>({})
  const chartSpec = ref<ChartSpec | null>(null)
  const queryData = ref<Record<string, unknown>[] | null>(null)
  const isStreaming = ref(false)
  const isBootstrapping = ref(false)
  const bootstrapError = ref<string | null>(null)

  const currentSession = computed(() =>
    sessions.value.find((s) => s.id === currentSessionId.value) ?? null,
  )

  const currentMessages = computed(() => {
    if (!currentSessionId.value) return []
    return messages.value[currentSessionId.value] ?? []
  })

  function clearVisualization() {
    chartSpec.value = null
    queryData.value = null
  }

  async function bootstrap() {
    isBootstrapping.value = true
    bootstrapError.value = null
    try {
      await loadSessions()
      if (sessions.value.length > 0) {
        await selectSession(sessions.value[0].id)
      }
    } catch (error) {
      bootstrapError.value =
        error instanceof Error ? error.message : '初始化失败，请确认后端已启动'
      throw error
    } finally {
      isBootstrapping.value = false
    }
  }

  async function loadSessions() {
    sessions.value = await fetchSessions()
  }

  async function loadMessages(sessionId: string) {
    messages.value[sessionId] = await fetchMessages(sessionId)
  }

  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
    clearVisualization()
    await loadMessages(sessionId)
  }

  async function createSession(title?: string) {
    const session = await apiCreateSession(title ? { title } : {})
    sessions.value.unshift(session)
    messages.value[session.id] = []
    currentSessionId.value = session.id
    clearVisualization()
    return session
  }

  async function renameSession(sessionId: string, title: string) {
    const session = await apiUpdateSession(sessionId, {
      title: title.trim() || '未命名会话',
    })
    const idx = sessions.value.findIndex((s) => s.id === sessionId)
    if (idx !== -1) {
      sessions.value[idx] = session
    }
  }

  async function removeSession(sessionId: string) {
    await apiDeleteSession(sessionId)
    sessions.value = sessions.value.filter((s) => s.id !== sessionId)
    delete messages.value[sessionId]

    if (currentSessionId.value === sessionId) {
      const next = sessions.value[0]
      currentSessionId.value = next?.id ?? null
      clearVisualization()
      if (next) {
        await loadMessages(next.id)
      }
    }
  }

  function addMessage(message: Omit<Message, 'createdAt'> & { createdAt?: string }) {
    const sessionId = message.sessionId
    if (!messages.value[sessionId]) {
      messages.value[sessionId] = []
    }
    const full: Message = {
      createdAt: message.createdAt ?? new Date().toISOString(),
      ...message,
    }
    messages.value[sessionId].push(full)
    return full
  }

  function updateMessage(sessionId: string, messageId: string, patch: Partial<Message>) {
    const list = messages.value[sessionId]
    if (!list) return
    const idx = list.findIndex((m) => m.id === messageId)
    if (idx === -1) return
    list[idx] = { ...list[idx], ...patch }
  }

  function setChartSpec(spec: ChartSpec | null) {
    chartSpec.value = spec
  }

  function setQueryData(data: Record<string, unknown>[] | null) {
    queryData.value = data
  }

  function setStreaming(value: boolean) {
    isStreaming.value = value
  }

  return {
    sessions,
    currentSessionId,
    messages,
    chartSpec,
    queryData,
    isStreaming,
    isBootstrapping,
    bootstrapError,
    currentSession,
    currentMessages,
    bootstrap,
    loadSessions,
    loadMessages,
    selectSession,
    createSession,
    renameSession,
    removeSession,
    addMessage,
    updateMessage,
    setChartSpec,
    setQueryData,
    setStreaming,
  }
})
