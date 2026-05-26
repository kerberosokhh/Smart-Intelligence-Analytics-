import type { ChartSpec } from '~/types/chart'

export type SseEventType = 'token' | 'sql' | 'data' | 'chart' | 'done' | 'error'

export interface SseEvent {
  type: SseEventType
  content?: string | Record<string, unknown>[] | ChartSpec
  message_id?: string
}

export interface StreamCallbacks {
  onEvent: (event: SseEvent) => void
}

function apiBase(): string {
  const config = useRuntimeConfig()
  return String(config.public.apiBase).replace(/\/$/, '')
}

/** 对接 POST /api/chat/stream（fetch + SSE 解析） */
export function connectChatStream(
  sessionId: string,
  message: string,
  callbacks: StreamCallbacks,
): { abort: () => void } {
  const controller = new AbortController()
  let aborted = false

  ;(async () => {
    try {
      const res = await fetch(`${apiBase()}/chat/stream`, {
        method: 'POST',
        headers: {
          Accept: 'text/event-stream',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id: sessionId, message }),
        signal: controller.signal,
      })

      if (!res.ok) {
        const detail = await res.text().catch(() => '')
        throw new Error(detail || `SSE 连接失败 (${res.status})`)
      }

      const reader = res.body?.getReader()
      if (!reader) {
        throw new Error('浏览器不支持流式响应')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (!aborted) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const chunks = buffer.split('\n\n')
        buffer = chunks.pop() ?? ''

        for (const chunk of chunks) {
          const event = parseSseChunk(chunk)
          if (event) {
            callbacks.onEvent(event)
          }
        }
      }
    } catch (error) {
      if (aborted) return
      const messageText =
        error instanceof Error ? error.message : '流式请求失败，请稍后重试'
      callbacks.onEvent({ type: 'error', content: messageText })
    }
  })()

  return {
    abort: () => {
      aborted = true
      controller.abort()
    },
  }
}

function parseSseChunk(chunk: string): SseEvent | null {
  const lines = chunk.split('\n').filter(Boolean)
  let dataLine = ''

  for (const line of lines) {
    if (line.startsWith('data:')) {
      dataLine += line.slice(5).trim()
    }
  }

  if (!dataLine) return null

  try {
    return JSON.parse(dataLine) as SseEvent
  } catch {
    return null
  }
}
