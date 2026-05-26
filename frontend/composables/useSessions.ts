import { useAppStore } from '~/stores/app'

export function useSessions() {
  const store = useAppStore()

  return {
    sessions: computed(() => store.sessions),
    currentSessionId: computed(() => store.currentSessionId),
    currentSession: computed(() => store.currentSession),
    isBootstrapping: computed(() => store.isBootstrapping),
    bootstrapError: computed(() => store.bootstrapError),
    selectSession: (sessionId: string) => store.selectSession(sessionId),
    createSession: (title?: string) => store.createSession(title),
    renameSession: (sessionId: string, title: string) => store.renameSession(sessionId, title),
    removeSession: (sessionId: string) => store.removeSession(sessionId),
    bootstrap: () => store.bootstrap(),
  }
}
