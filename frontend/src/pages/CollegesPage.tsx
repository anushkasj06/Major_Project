import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Search, MapPin, Building2, TrendingUp } from 'lucide-react'
import { collegesAPI } from '../services/api'
import { formatCurrency, formatLPA } from '../utils/formatters'
import { College } from '../types'
import { Spinner } from '../components/ui/Spinner'

export default function CollegesPage() {
  const [search, setSearch] = useState('')
  const [type, setType] = useState('')
  const [city, setCity] = useState('')

  const { data: colleges = [], isLoading } = useQuery<College[]>({
    queryKey: ['colleges', search, type, city],
    queryFn: async () => {
      const res = await collegesAPI.list({ search, college_type: type || undefined, city: city || undefined })
      return res.data
    },
    staleTime: 5 * 60 * 1000,
  })

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 py-8">
        <h1 className="font-display font-bold text-2xl mb-6">Browse Colleges</h1>

        {/* Filters */}
        <div className="flex gap-3 mb-6 flex-wrap">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Search colleges..."
              className="input-field pl-9"
            />
          </div>
          <select value={type} onChange={e => setType(e.target.value)} className="input-field w-40">
            <option value="">All Types</option>
            <option value="engineering">Engineering</option>
            <option value="polytechnic">Polytechnic</option>
            <option value="management">Management</option>
          </select>
          <input
            value={city}
            onChange={e => setCity(e.target.value)}
            placeholder="City..."
            className="input-field w-32"
          />
        </div>

        {/* Grid */}
        {isLoading ? (
          <div className="flex justify-center py-20"><Spinner size="lg" /></div>
        ) : colleges.length === 0 ? (
          <div className="text-center py-20 text-slate-400">No colleges found</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {colleges.map((c) => (
              <CollegeCard key={c.id} college={c} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function CollegeCard({ college }: { college: College }) {
  return (
    <div className="card p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center shrink-0">
          <Building2 className="w-5 h-5 text-primary-600" />
        </div>
        {college.ranking?.state_rank && (
          <span className="text-xs bg-saffron-100 text-saffron-700 px-2 py-0.5 rounded-full font-medium">
            State Rank #{college.ranking.state_rank}
          </span>
        )}
      </div>

      <h3 className="font-semibold text-slate-900 mb-1 leading-tight">{college.name}</h3>

      <div className="flex items-center gap-1 text-xs text-slate-400 mb-3">
        <MapPin className="w-3 h-3" />
        {college.location?.city}, {college.location?.state}
      </div>

      <div className="grid grid-cols-2 gap-2 mb-3">
        {college.fees?.annual_tuition && (
          <div className="bg-slate-50 rounded-lg p-2">
            <p className="text-xs text-slate-400">Fees/Year</p>
            <p className="font-semibold text-sm text-slate-800">{formatCurrency(college.fees.annual_tuition)}</p>
          </div>
        )}
        {college.placements?.avg_package_lpa && (
          <div className="bg-slate-50 rounded-lg p-2">
            <p className="text-xs text-slate-400">Avg Package</p>
            <p className="font-semibold text-sm text-green-700">{formatLPA(college.placements.avg_package_lpa)}</p>
          </div>
        )}
      </div>

      {college.branches?.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {college.branches.slice(0, 3).map((b) => (
            <span key={b.code} className="text-xs bg-primary-50 text-primary-700 px-1.5 py-0.5 rounded">
              {b.code}
            </span>
          ))}
          {college.branches.length > 3 && (
            <span className="text-xs text-slate-400">+{college.branches.length - 3} more</span>
          )}
        </div>
      )}
    </div>
  )
}
