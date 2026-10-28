import { useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useChatStore } from '../store/chatStore'
import { useAuthStore } from '../store/authStore'
import { streamChat, chatAPI } from '../services/api'

export function useChat() {
  const {
    messages, sessions, isLoading, currentSessionId, language, collegeFilter,
    addMessage, updateLastMessage, setLoading, setSession, clearMessages,
    setSessions, setCollegeFilter, setLanguage,
  } = useChatStore()
  const { user } = useAuthStore()

  const loadSessions = useCallback(async () => {
    try {
      const res = await chatAPI.getSessions()
      setSessions(res.data)
    } catch {}
  }, [setSessions])

  const newSession = useCallback(() => {
    const sid = uuidv4()
    setSession(sid)
  }, [setSession])

  const sendMessage = useCallback((input: string) => {
    if (!input.trim() || isLoading || !currentSessionId) return

    const userMsg = {
      id: uuidv4(),
      role: 'user' as const,
      content: input.trim(),
      timestamp: new Date(),
    }
    const assistantMsg = {
      id: uuidv4(),
      role: 'assistant' as const,
      content: '',
      timestamp: new Date(),
      isStreaming: true,
    }

    addMessage(userMsg)
    addMessage(assistantMsg)
    setLoading(true)

    streamChat(
      {
        message: input.trim(),
        session_id: currentSessionId,
        language: language || user?.preferred_language || 'en',
        college_filter: collegeFilter,
      },
      (token) => updateLastMessage(token),
      (sources) => updateLastMessage('', false, sources),
      () => {
        updateLastMessage('', true)
        setLoading(false)
        loadSessions()
      },
      (err) => {
        updateLastMessage(`\n\n*Sorry, an error occurred: ${err}*`, true)
        setLoading(false)
      }
    )
  }, [isLoading, currentSessionId, language, collegeFilter, user])

  const switchSession = useCallback(async (sessionId: string) => {
    setSession(sessionId)
    try {
      const res = await chatAPI.getHistory(sessionId)
      const msgs = (res.data?.messages || []).map((m: any) => ({
        id: uuidv4(),
        role: m.role,
        content: m.content,
        sources: m.sources,
        confidence: m.confidence,
        timestamp: new Date(m.timestamp),
        isStreaming: false,
      }))
      clearMessages()
      msgs.forEach((m: any) => addMessage(m))
    } catch {}
  }, [setSession, clearMessages, addMessage])

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await chatAPI.deleteSession(sessionId)
      await loadSessions()
      if (sessionId === currentSessionId) newSession()
    } catch {}
  }, [currentSessionId, loadSessions, newSession])

  return {
    messages, sessions, isLoading, currentSessionId, language, collegeFilter,
    sendMessage, newSession, switchSession, deleteSession, loadSessions,
    setCollegeFilter, setLanguage,
  }
}
