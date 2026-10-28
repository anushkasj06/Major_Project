import { useState, useRef, useEffect } from 'react'
import { Bot } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { useChat } from '../hooks/useChat'
import { SessionSidebar } from '../components/chat/SessionSidebar'
import { MessageBubble } from '../components/chat/MessageBubble'
import { ChatInput } from '../components/chat/ChatInput'

const QUICK_QUESTIONS = [
  "What are the fees for CSE at COEP Pune?",
  "Best placement colleges in Mumbai?",
  "VJTI cutoff for Computer Engineering 2024",
  "Scholarship options for OBC students in Maharashtra",
  "Hostel facilities at Government engineering colleges",
  "Compare COEP vs VJTI for CSE branch",
]

export default function ChatPage() {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const {
    messages, sessions, isLoading, currentSessionId, language,
    sendMessage, newSession, switchSession, deleteSession, loadSessions, setLanguage,
  } = useChat()

  useEffect(() => { loadSessions(); newSession() }, [])
  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = () => {
    if (!input.trim()) return
    sendMessage(input)
    setInput('')
  }

  const handleLogout = async () => { await logout(); navigate('/login') }

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <SessionSidebar
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewSession={newSession}
        onSelectSession={switchSession}
        onDeleteSession={deleteSession}
        userName={user?.name || ''}
        userEmail={user?.email || ''}
        userRole={user?.role || 'user'}
        onLogout={handleLogout}
      />

      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 px-6 py-3 flex items-center justify-between shrink-0">
          <div>
            <h1 className="font-semibold text-slate-900 text-sm">College Admission Assistant</h1>
            <p className="text-xs text-slate-400">RAG-powered · Grounded in official college data</p>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 border border-green-200 rounded-full text-xs text-green-700">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full" /> Live
            </span>
          </div>
        </header>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-5">
          {messages.length === 0 ? (
            <div className="max-w-2xl mx-auto animate-fade-in">
              <div className="text-center mb-8 pt-8">
                <div className="w-14 h-14 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-sm">
                  <Bot className="w-7 h-7 text-primary-600" />
                </div>
                <h2 className="font-display font-bold text-xl text-slate-900 mb-2">
                  Hi {user?.name?.split(' ')[0]}! How can I help?
                </h2>
                <p className="text-sm text-slate-500 max-w-md mx-auto">
                  Ask me anything about engineering college admissions in Maharashtra — fees, placements, cutoffs, scholarships, and more.
                </p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {QUICK_QUESTIONS.map((q) => (
                  <button
                    key={q}
                    onClick={() => { setInput(q); setTimeout(handleSend, 0) }}
                    className="text-left p-3.5 bg-white border border-slate-200 rounded-xl text-sm text-slate-600 hover:border-primary-300 hover:bg-primary-50 hover:text-primary-700 transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                sessionId={currentSessionId || ''}
                index={idx}
              />
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={isLoading}
          language={language}
          onLanguageChange={setLanguage}
        />
      </main>
    </div>
  )
}
