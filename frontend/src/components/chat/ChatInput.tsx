import { useRef, useEffect, KeyboardEvent } from 'react'
import { Send, Mic, MicOff } from 'lucide-react'

interface Props {
  value: string
  onChange: (v: string) => void
  onSend: () => void
  disabled?: boolean
  language: string
  onLanguageChange: (l: string) => void
}

export function ChatInput({ value, onChange, onSend, disabled, language, onLanguageChange }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 128)}px`
  }, [value])

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (value.trim() && !disabled) onSend()
    }
  }

  const placeholders: Record<string, string> = {
    en: 'Ask about fees, placements, cutoffs... (Enter to send)',
    hi: 'फीस, प्लेसमेंट, कटऑफ के बारे में पूछें...',
    mr: 'फी, प्लेसमेंट, कटऑफबद्दल विचारा...',
  }

  return (
    <div className="bg-white border-t border-slate-200 px-4 py-3">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-2xl px-3 py-2 focus-within:border-primary-400 focus-within:ring-2 focus-within:ring-primary-100 transition-all">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={e => onChange(e.target.value)}
            onKeyDown={handleKey}
            placeholder={placeholders[language] || placeholders.en}
            rows={1}
            disabled={disabled}
            className="flex-1 resize-none bg-transparent text-sm text-slate-800 placeholder-slate-400 focus:outline-none py-1 min-h-[36px] max-h-32"
          />
          <div className="flex items-center gap-1 shrink-0 pb-0.5">
            <select
              value={language}
              onChange={e => onLanguageChange(e.target.value)}
              className="text-xs text-slate-500 bg-transparent border-none focus:outline-none cursor-pointer"
            >
              <option value="en">EN</option>
              <option value="hi">HI</option>
              <option value="mr">MR</option>
            </select>
            <button
              onClick={onSend}
              disabled={!value.trim() || disabled}
              className="w-8 h-8 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white rounded-xl flex items-center justify-center transition-colors"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
        <p className="text-xs text-center text-slate-400 mt-1.5">
          Answers grounded in official data. Verify important decisions with the college directly.
        </p>
      </div>
    </div>
  )
}
