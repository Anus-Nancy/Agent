import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function StudentDashboard() {
  const [complaints, setComplaints] = useState([])
  const [queries, setQueries] = useState([])

  useEffect(() => {
    api.get('/complaints').then((r) => setComplaints(r.data)).catch(() => setComplaints([]))
    api.get('/queries').then((r) => setQueries(r.data)).catch(() => setQueries([]))
  }, [])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Student Dashboard</h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded bg-white p-4 shadow"><p className="text-sm text-slate-500">Total Complaints</p><p className="text-3xl font-semibold">{complaints.length}</p></div>
        <div className="rounded bg-white p-4 shadow"><p className="text-sm text-slate-500">Resolved</p><p className="text-3xl font-semibold">{complaints.filter((c) => c.status === 'Resolved').length}</p></div>
        <div className="rounded bg-white p-4 shadow"><p className="text-sm text-slate-500">Queries</p><p className="text-3xl font-semibold">{queries.length}</p></div>
      </div>
    </div>
  )
}
