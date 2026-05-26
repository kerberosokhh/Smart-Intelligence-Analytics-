export interface Session {
  id: string
  title: string
  createdAt: string
  updatedAt: string
}

export interface SessionCreatePayload {
  title?: string
}

export interface SessionUpdatePayload {
  title: string
}
