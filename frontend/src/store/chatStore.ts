import { create } from 'zustand'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  confidence?: number
  timestamp: Date
  isStreaming?: boolean
}

export interface Source {
  college_name?: string
  source_url?: string
  doc_type?: string
  relevance?: number
}

export interface Session {
  session_id: string
  title?: string
  updated_at: string
  messages?: Message[]
}

interface ChatState {
  messages: Message[]
  sessions: Session[]
  currentSessionId: string | null
  isLoading: boolean
  collegeFilter: string | null
  language: string
  addMessage: (msg: Message) => void
  updateLastMessage: (content: string, done?: boolean, sources?: Source[]) => void
  setLoading: (v: boolean) => void
  setSession: (id: string) => void
  clearMessages: () => void
  setSessions: (sessions: Session[]) => void
  setCollegeFilter: (id: string | null) => void
  setLanguage: (lang: string) => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  sessions: [],
  currentSessionId: null,
  isLoading: false,
  collegeFilter: null,
  language: 'en',
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateLastMessage: (content, done = false, sources) =>
    set((s) => {
      const msgs = [...s.messages]
      const last = msgs[msgs.length - 1]
      if (last && last.role === 'assistant') {
        msgs[msgs.length - 1] = {
          ...last, content: last.content + content,
          isStreaming: !done,
          sources: sources || last.sources,
        }
      }
      return { messages: msgs }
    }),
  setLoading: (v) => set({ isLoading: v }),
  setSession: (id) => set({ currentSessionId: id, messages: [] }),
  clearMessages: () => set({ messages: [] }),
  setSessions: (sessions) => set({ sessions }),
  setCollegeFilter: (id) => set({ collegeFilter: id }),
  setLanguage: (lang) => set({ language: lang }),
}))
