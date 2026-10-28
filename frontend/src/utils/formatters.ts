export const formatCurrency = (amount: number): string => {
  if (!amount) return 'N/A'
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
  return `₹${amount.toLocaleString('en-IN')}`
}

export const formatLPA = (lpa: number): string => {
  if (!lpa) return 'N/A'
  return `${lpa} LPA`
}

export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export const truncate = (str: string, maxLen: number): string => {
  if (!str) return ''
  return str.length > maxLen ? str.slice(0, maxLen) + '...' : str
}

export const getStatusColor = (status: string): string => {
  const map: Record<string, string> = {
    indexed: 'success', completed: 'success',
    failed: 'error',
    pending: 'warning', running: 'info',
  }
  return map[status] || 'default'
}
