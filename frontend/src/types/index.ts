export interface College {
  id: string
  name: string
  short_name?: string
  college_type: string
  location: { city: string; district?: string; state: string; pincode?: string }
  website?: string
  established_year?: number
  affiliation?: string
  branches: Array<{ name: string; code: string; seats: number }>
  fees: { annual_tuition?: number; hostel_annual?: number; other_fees?: number }
  placements: { avg_package_lpa?: number; highest_package_lpa?: number; placement_percentage?: number }
  cutoffs: Record<string, Record<string, Record<string, number>>>
  ranking: { nirf?: number; state_rank?: number }
}

export interface CrawlJob {
  _id: string
  url: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  pages_crawled: number
  pages_indexed: number
  created_at: string
  completed_at?: string
}

export interface Document {
  _id: string
  original_filename: string
  document_type: string
  status: 'pending' | 'processing' | 'indexed' | 'failed'
  chunk_count: number
  created_at: string
  college_name?: string
}

export interface AdminStats {
  total_queries: number
  helpful_responses: number
  total_users: number
  total_colleges: number
  top_queries: Array<{ _id: string; count: number }>
}
