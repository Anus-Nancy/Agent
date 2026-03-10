import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function AdminDashboard() {
  const [complaints, setComplaints] = useState([])

  useEffect(() => {
    api.get('/complaints').then((r) => setComplaints(r.data)).catch(() => setComplaints([]))
  }, [])

  const total = complaints.length
  const pending = complaints.filter((c) => ['Submitted', 'In Progress', 'Escalated'].includes(c.status)).length
  const resolved = complaints.filter((c) => c.status === 'Resolved' || c.status === 'Closed').length

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Admin Dashboard</h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded bg-white p-4 shadow"><p className="text-sm text-slate-500">Total</p><p className="text-3xl font-semibold">{total}</p></div>
        <div className="rounded bg-white p-4 shadow"><p className="text-sm text-slate-500">Pending</p><p className="text-3xl font-semibold">{pending}</p></div>
        <div className="rounded bg-white p-4 shadow"><p className="text-sm text-slate-500">Resolved</p><p className="text-3xl font-semibold">{resolved}</p></div>
      </div>
    </div>
  )
}
