import type { Session, SessionCreatePayload, SessionUpdatePayload } from '~/types/session'
import type { Message } from '~/types/message'

function apiBase(): string {
  const config = useRuntimeConfig()
  return String(config.public.apiBase).replace(/\/$/, '')
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase()}${path}`, {
    headers: {
      Accept: 'application/json',
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...init?.headers,
    },
    ...init,
  })

  if (!res.ok) {
    const detail = await res.text().catch(() => '')
    throw new Error(detail || `请求失败 (${res.status})`)
  }

  if (res.status === 204) {
    return undefined as T
  }

  return res.json() as Promise<T>
}

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  return apiFetch('/health')
}

export async function fetchSessions(): Promise<Session[]> {
  return apiFetch('/sessions')
}

export async function createSession(payload: SessionCreatePayload = {}): Promise<Session> {
  return apiFetch('/sessions', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function updateSession(
  sessionId: string,
  payload: SessionUpdatePayload,
): Promise<Session> {
  return apiFetch(`/sessions/${sessionId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function deleteSession(sessionId: string): Promise<void> {
  await apiFetch(`/sessions/${sessionId}`, { method: 'DELETE' })
}

export async function fetchMessages(sessionId: string): Promise<Message[]> {
  return apiFetch(`/sessions/${sessionId}/messages`)
}
