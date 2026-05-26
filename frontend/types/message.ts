export type MessageRole = 'user' | 'assistant' | 'system'

export interface Message {
  id: string
  sessionId: string
  role: MessageRole
  content: string
  sql?: string
  createdAt: string
}
