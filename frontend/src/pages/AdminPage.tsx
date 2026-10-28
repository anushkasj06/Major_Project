import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { adminAPI } from '../services/api'
import { BarChart2, Users, FileText, Globe, Upload, Play, ArrowLeft, RefreshCw } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function AdminPage() {
  const [tab, setTab] = useState<'stats'|'users'|'documents'|'crawl'>('stats')
  const [stats, setStats] = useState<any>(null)
  const [users, setUsers] = useState<any[]>([])
  const [jobs, setJobs] = useState<any[]>([])
  const [documents, setDocuments] = useState<any[]>([])
  const [crawlUrl, setCrawlUrl] = useState('')
  const [uploading, setUploading] = useState(false)
  const [crawling, setCrawling] = useState(false)
  const navigate = useNavigate()
  const { user } = useAuthStore()

  useEffect(() => {
    loadStats()
    loadCrawlerJobs()
    loadDocuments()
  }, [])

  useEffect(() => {
    if (tab === 'users') loadUsers()
  }, [tab])

  const loadStats = async () => {
    try { const r = await adminAPI.getStats(); setStats(r.data) } catch {}
  }
  const loadUsers = async () => {
    try { const r = await adminAPI.getUsers(); setUsers(r.data) } catch {}
  }
  const loadCrawlerJobs = async () => {
    try { const r = await adminAPI.getCrawlerJobs(); setJobs(r.data) } catch {}
  }
  const loadDocuments = async () => {
    try { const r = await adminAPI.getDocuments(); setDocuments(r.data) } catch {}
  }

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.[0]) return
    setUploading(true)
    const form = new FormData()
    form.append('file', e.target.files[0])
    form.append('document_type', 'general')
    try { await adminAPI.uploadDocument(form); loadDocuments() } catch {}
    setUploading(false)
  }

  const handleCrawl = async () => {
    if (!crawlUrl) return
    setCrawling(true)
    try { await adminAPI.startCrawl({ url: crawlUrl }); loadCrawlerJobs() } catch {}
    setCrawling(false)
    setCrawlUrl('')
  }

  const tabs = [
    { id: 'stats', label: 'Overview', icon: BarChart2 },
    { id: 'users', label: 'Users', icon: Users },
    { id: 'documents', label: 'Documents', icon: FileText },
    { id: 'crawl', label: 'Crawler', icon: Globe },
  ] as const

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center gap-4">
        <button onClick={() => navigate('/chat')} className="p-1.5 hover:bg-slate-100 rounded-lg">
          <ArrowLeft className="w-4 h-4 text-slate-600" />
        </button>
        <div>
          <h1 className="font-display font-bold text-slate-900">Admin Dashboard</h1>
          <p className="text-xs text-slate-500">{user?.email}</p>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-6 py-6">
        {/* Tabs */}
        <div className="flex gap-1 bg-white border border-slate-200 rounded-xl p-1 mb-6 w-fit">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setTab(id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${tab === id ? 'bg-primary-600 text-white' : 'text-slate-600 hover:bg-slate-100'}`}>
              <Icon className="w-4 h-4" /> {label}
            </button>
          ))}
        </div>

        {/* Stats */}
        {tab === 'stats' && stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: 'Total Queries', value: stats.total_queries, color: 'text-primary-600' },
              { label: 'Helpful Responses', value: stats.helpful_responses, color: 'text-green-600' },
              { label: 'Total Users', value: stats.total_users, color: 'text-purple-600' },
              { label: 'Colleges', value: stats.total_colleges, color: 'text-saffron-600' },
            ].map(({ label, value, color }) => (
              <div key={label} className="card p-5">
                <p className="text-sm text-slate-500">{label}</p>
                <p className={`text-3xl font-display font-bold mt-1 ${color}`}>{value ?? 0}</p>
              </div>
            ))}
            {stats.top_queries?.length > 0 && (
              <div className="card p-5 col-span-full">
                <h3 className="font-semibold mb-3">Top Queries</h3>
                <div className="space-y-2">
                  {stats.top_queries.slice(0, 5).map((q: any) => (
                    <div key={q._id} className="flex items-center justify-between text-sm">
                      <span className="text-slate-700 truncate">{q._id}</span>
                      <span className="text-slate-400 ml-3 shrink-0">{q.count}×</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Users */}
        {tab === 'users' && (
          <div className="card overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>{['Name','Email','Role','Joined'].map(h => <th key={h} className="text-left px-4 py-3 text-slate-500 font-medium text-xs">{h}</th>)}</tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u._id} className="border-b border-slate-100 hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium">{u.name}</td>
                    <td className="px-4 py-3 text-slate-500">{u.email}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${u.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-700'}`}>{u.role}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{new Date(u.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Documents */}
        {tab === 'documents' && (
          <div>
            <div className="card p-4 mb-4 flex items-center gap-3">
              <label className="btn-primary flex items-center gap-2 cursor-pointer">
                <Upload className="w-4 h-4" />
                {uploading ? 'Uploading...' : 'Upload PDF / DOCX'}
                <input type="file" accept=".pdf,.docx,.txt" onChange={handleUpload} className="hidden" />
              </label>
              <p className="text-sm text-slate-500">Upload official college documents for indexing</p>
            </div>
            <div className="card overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>{['Filename','Type','Status','Chunks','Uploaded'].map(h => <th key={h} className="text-left px-4 py-3 text-slate-500 font-medium text-xs">{h}</th>)}</tr>
                </thead>
                <tbody>
                  {documents.map((d) => (
                    <tr key={d._id} className="border-b border-slate-100">
                      <td className="px-4 py-3 font-medium truncate max-w-xs">{d.original_filename}</td>
                      <td className="px-4 py-3 text-slate-500">{d.document_type}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          d.status === 'indexed' ? 'bg-green-100 text-green-700' :
                          d.status === 'failed' ? 'bg-red-100 text-red-700' :
                          'bg-yellow-100 text-yellow-700'
                        }`}>{d.status}</span>
                      </td>
                      <td className="px-4 py-3 text-slate-500">{d.chunk_count || 0}</td>
                      <td className="px-4 py-3 text-slate-400">{new Date(d.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Crawler */}
        {tab === 'crawl' && (
          <div>
            <div className="card p-4 mb-4">
              <h3 className="font-semibold mb-3">Start New Crawl</h3>
              <div className="flex gap-3">
                <input value={crawlUrl} onChange={e => setCrawlUrl(e.target.value)}
                  className="input-field flex-1" placeholder="https://coep.org.in" />
                <button onClick={handleCrawl} disabled={!crawlUrl || crawling} className="btn-primary flex items-center gap-2">
                  <Play className="w-4 h-4" />{crawling ? 'Starting...' : 'Start Crawl'}
                </button>
                <button onClick={loadCrawlerJobs} className="btn-secondary"><RefreshCw className="w-4 h-4" /></button>
              </div>
            </div>
            <div className="card overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50 border-b border-slate-200">
                  <tr>{['URL','Status','Pages Crawled','Indexed','Started'].map(h => <th key={h} className="text-left px-4 py-3 text-slate-500 font-medium text-xs">{h}</th>)}</tr>
                </thead>
                <tbody>
                  {jobs.map((j) => (
                    <tr key={j._id} className="border-b border-slate-100">
                      <td className="px-4 py-3 truncate max-w-xs text-xs text-slate-600">{j.url}</td>
                      <td className="px-4 py-3">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          j.status === 'completed' ? 'bg-green-100 text-green-700' :
                          j.status === 'running' ? 'bg-blue-100 text-blue-700' :
                          j.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-slate-100 text-slate-700'
                        }`}>{j.status}</span>
                      </td>
                      <td className="px-4 py-3 text-slate-500">{j.pages_crawled}</td>
                      <td className="px-4 py-3 text-slate-500">{j.pages_indexed}</td>
                      <td className="px-4 py-3 text-slate-400 text-xs">{j.created_at ? new Date(j.created_at).toLocaleString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
