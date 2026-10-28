import { Plus, MessageSquare, Trash2, Settings, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Session } from '../../store/chatStore'

interface Props {
  sessions: Session[]
  currentSessionId: string | null
  onNewSession: () => void
  onSelectSession: (id: string) => void
  onDeleteSession: (id: string) => void
  userName: string
  userEmail: string
  userRole: string
  onLogout: () => void
}

export function SessionSidebar({
  sessions, currentSessionId, onNewSession, onSelectSession,
  onDeleteSession, userName, userEmail, userRole, onLogout
}: Props) {
  const navigate = useNavigate()

  return (
    <aside className="w-60 bg-slate-900 flex flex-col h-full shrink-0">
      {/* Logo */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-7 h-7 bg-saffron-500 rounded-lg flex items-center justify-center font-bold text-white text-xs font-display">
            अ
          </div>
          <div>
            <p className="font-display font-bold text-white text-sm leading-none">Arambh</p>
            <p className="text-white/40 text-xs">Admission Assistant</p>
          </div>
        </div>
        <button
          onClick={onNewSession}
          className="w-full flex items-center gap-2 px-3 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-xs font-medium transition-colors"
        >
          <Plus className="w-3.5 h-3.5" /> New Chat
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {sessions.length === 0 && (
          <p className="text-white/30 text-xs px-3 py-4 text-center">No conversations yet</p>
        )}
        {sessions.map((s) => (
          <div
            key={s.session_id}
            className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
              s.session_id === currentSessionId
                ? 'bg-white/20 text-white'
                : 'text-white/50 hover:bg-white/10 hover:text-white/80'
            }`}
            onClick={() => onSelectSession(s.session_id)}
          >
            <MessageSquare className="w-3 h-3 shrink-0" />
            <span className="flex-1 text-xs truncate">
              {s.title || 'New conversation'}
            </span>
            <button
              onClick={(e) => { e.stopPropagation(); onDeleteSession(s.session_id) }}
              className="opacity-0 group-hover:opacity-100 p-0.5 hover:text-red-400 transition-all"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-white/10 space-y-1">
        <div className="px-3 py-1.5">
          <p className="text-white text-xs font-medium truncate">{userName}</p>
          <p className="text-white/40 text-xs truncate">{userEmail}</p>
        </div>
        <div className="flex gap-1">
          {(userRole === 'admin' || userRole === 'superadmin') && (
            <button
              onClick={() => navigate('/admin')}
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 text-white/50 hover:bg-white/10 hover:text-white rounded-lg text-xs transition-colors"
            >
              <Settings className="w-3.5 h-3.5" /> Admin
            </button>
          )}
          <button
            onClick={onLogout}
            className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 text-white/50 hover:bg-white/10 hover:text-red-400 rounded-lg text-xs transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" /> Logout
          </button>
        </div>
      </div>
    </aside>
  )
}
