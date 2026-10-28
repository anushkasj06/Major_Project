import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor — add auth token
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor — handle 401 / refresh
api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const { refreshToken, setAuth, logout, user } = useAuthStore.getState()
      if (refreshToken) {
        try {
          const res = await axios.post(`${API_URL}/api/auth/refresh`, null, {
            params: { refresh_token: refreshToken }
          })
          const { access_token } = res.data
          setAuth(user!, access_token, refreshToken)
          original.headers.Authorization = `Bearer ${access_token}`
          return api(original)
        } catch {
          logout()
        }
      } else {
        logout()
      }
    }
    return Promise.reject(error)
  }
)

// Auth
export const authAPI = {
  register: (data: { name: string; email: string; password: string }) =>
    api.post('/auth/register', data),
  login: (email: string, password: string) => {
    const form = new URLSearchParams()
    form.append('username', email)
    form.append('password', password)
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } })
  },
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
}

// Chat
export const chatAPI = {
  getSessions: () => api.get('/chat/sessions'),
  getHistory: (sessionId: string) => api.get(`/chat/history/${sessionId}`),
  deleteSession: (sessionId: string) => api.delete(`/chat/session/${sessionId}`),
  feedback: (data: { session_id: string; message_index: number; was_helpful: boolean }) =>
    api.post('/chat/feedback', data),
}

// Colleges
export const collegesAPI = {
  list: (params?: { search?: string; college_type?: string; city?: string; skip?: number; limit?: number }) =>
    api.get('/colleges/', { params }),
  get: (id: string) => api.get(`/colleges/${id}`),
}

// Admin
export const adminAPI = {
  getStats: () => api.get('/analytics/stats'),
  getUsers: () => api.get('/admin/users'),
  updateUserRole: (userId: string, role: string) =>
    api.put(`/admin/users/${userId}/role`, null, { params: { role } }),
  getCrawlerJobs: () => api.get('/admin/crawler/jobs'),
  startCrawl: (data: { url: string; college_id?: string }) => api.post('/crawler/start', data),
  uploadDocument: (formData: FormData) =>
    api.post('/documents/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getDocuments: () => api.get('/documents/'),
}

// Streaming chat
export function streamChat(
  payload: {
    message: string; session_id: string; language: string; college_filter?: string | null
  },
  onToken: (token: string) => void,
  onSources: (sources: any[]) => void,
  onDone: () => void,
  onError: (err: string) => void
) {
  const token = useAuthStore.getState().accessToken
  const url = `${API_URL}/api/chat/message`

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ ...payload, stream: true }),
  }).then(async (res) => {
    if (!res.ok) {
      onError(`HTTP ${res.status}`)
      return
    }
    const reader = res.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          if (data === '[DONE]') { onDone(); return }
          try {
            const parsed = JSON.parse(data)
            if (parsed.type === 'token') onToken(parsed.content)
            else if (parsed.type === 'sources') onSources(parsed.sources)
            else if (parsed.error) onError(parsed.error)
          } catch {}
        }
      }
    }
    onDone()
  }).catch((err) => onError(err.message))
}
