import { ThumbsUp, ThumbsDown, ExternalLink, Bot, User } from 'lucide-react'
import { Message } from '../../store/chatStore'
import { chatAPI } from '../../services/api'

interface Props {
  message: Message
  sessionId: string
  index: number
}

export function MessageBubble({ message, sessionId, index }: Props) {
  const isUser = message.role === 'user'

  const handleFeedback = (helpful: boolean) => {
    chatAPI.feedback({ session_id: sessionId, message_index: index, was_helpful: helpful })
  }

  return (
    <div className={`flex gap-3 max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : ''}`}>
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 ${
        isUser ? 'bg-primary-600' : 'bg-primary-100'
      }`}>
        {isUser
          ? <User className="w-4 h-4 text-white" />
          : <Bot className="w-4 h-4 text-primary-600" />
        }
      </div>

      <div className={`flex-1 min-w-0 ${isUser ? 'max-w-md' : ''}`}>
        {/* Bubble */}
        <div className={`rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? 'bg-primary-600 text-white rounded-tr-sm'
            : 'bg-white border border-slate-200 text-slate-800 rounded-tl-sm shadow-sm'
        }`}>
          {message.content}
          {message.isStreaming && !message.content && <StreamingDots />}
        </div>

        {/* Sources */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1.5">
            <span className="text-xs text-slate-400 self-center">Sources:</span>
            {message.sources.map((src, i) => (
              <a
                key={i}
                href={src.source_url || '#'}
                target={src.source_url ? '_blank' : '_self'}
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-xs text-slate-600 rounded-full transition-colors"
              >
                {src.college_name || src.doc_type || 'Source'}
                {src.source_url && <ExternalLink className="w-2.5 h-2.5" />}
              </a>
            ))}
          </div>
        )}

        {/* Confidence */}
        {!isUser && message.confidence !== undefined && message.confidence < 0.5 && (
          <p className="mt-1 text-xs text-amber-600">
            ⚠️ Low confidence — please verify with official source
          </p>
        )}

        {/* Feedback */}
        {!isUser && !message.isStreaming && message.content && (
          <div className="flex gap-1 mt-1.5">
            <button
              onClick={() => handleFeedback(true)}
              title="Helpful"
              className="p-1 text-slate-300 hover:text-green-500 transition-colors"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => handleFeedback(false)}
              title="Not helpful"
              className="p-1 text-slate-300 hover:text-red-500 transition-colors"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
            <span className="text-xs text-slate-300 self-center ml-1">
              {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

function StreamingDots() {
  return (
    <span className="inline-flex gap-1 items-center">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-1.5 h-1.5 bg-slate-400 rounded-full animate-pulse"
          style={{ animationDelay: `${i * 200}ms` }}
        />
      ))}
    </span>
  )
}
