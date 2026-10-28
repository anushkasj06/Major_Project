import { Link } from 'react-router-dom'
import { MessageSquare, Search, FileText, BarChart2, Globe, Shield } from 'lucide-react'

export default function LandingPage() {
  const features = [
    { icon: MessageSquare, title: 'AI-Powered Chat', desc: 'Ask anything about fees, placements, cutoffs in plain language' },
    { icon: Search, title: 'Smart Search', desc: 'Hybrid semantic + keyword search across official college data' },
    { icon: FileText, title: 'Document RAG', desc: 'Answers grounded in official PDFs and government notices' },
    { icon: BarChart2, title: 'College Compare', desc: 'Compare colleges side-by-side on placements, fees, rankings' },
    { icon: Globe, title: 'Multilingual', desc: 'Ask in English, Hindi, or Marathi — get answers in your language' },
    { icon: Shield, title: 'No Hallucinations', desc: 'Every answer cites its source — verified, grounded responses only' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-slate-900 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-5 max-w-6xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-saffron-500 rounded-lg flex items-center justify-center font-display font-bold text-sm">अ</div>
          <span className="font-display font-bold text-xl">Arambh</span>
        </div>
        <div className="flex gap-3">
          <Link to="/login" className="px-4 py-2 text-sm text-white/80 hover:text-white transition-colors">Login</Link>
          <Link to="/register" className="px-4 py-2 text-sm bg-saffron-500 hover:bg-saffron-600 rounded-lg font-medium transition-colors">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <div className="max-w-4xl mx-auto px-8 pt-20 pb-16 text-center">
        <div className="inline-block px-3 py-1 bg-white/10 rounded-full text-xs text-white/70 mb-6">
          🎓 Powered by RAG + Multi-Agent AI
        </div>
        <h1 className="font-display text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Your College Admission<br />
          <span className="text-saffron-400">Intelligence Engine</span>
        </h1>
        <p className="text-lg text-white/70 mb-10 max-w-2xl mx-auto">
          Ask about fees, placements, cutoffs, scholarships for any engineering college in Maharashtra — 
          get instant, accurate, source-cited answers.
        </p>
        <div className="flex gap-4 justify-center">
          <Link to="/register" className="px-6 py-3 bg-saffron-500 hover:bg-saffron-600 rounded-xl font-semibold transition-colors">
            Start Chatting Free
          </Link>
          <Link to="/login" className="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-xl font-semibold transition-colors">
            Sign In
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="max-w-6xl mx-auto px-8 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {features.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="bg-white/5 border border-white/10 rounded-xl p-5 hover:bg-white/10 transition-colors">
              <Icon className="w-6 h-6 text-saffron-400 mb-3" />
              <h3 className="font-semibold mb-1">{title}</h3>
              <p className="text-sm text-white/60">{desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-white/10 text-center py-6 text-sm text-white/40">
        Arambh — Final Year Major Project · Built with LangGraph + RAG + React
      </div>
    </div>
  )
}
