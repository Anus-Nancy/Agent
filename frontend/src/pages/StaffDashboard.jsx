import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function StaffDashboard() {
  const [complaints, setComplaints] = useState([])

  const load = () => api.get('/complaints').then((r) => setComplaints(r.data)).catch(() => setComplaints([]))
  useEffect(() => { load() }, [])

  const updateStatus = async (id, status) => {
    await api.put(`/complaints/${id}/status`, { status })
    load()
  }

  return (
    <div className="rounded bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-semibold">Staff Dashboard</h2>
      {complaints.map((c) => (
        <div key={c.id} className="mb-3 rounded border p-3">
          <p className="font-medium">#{c.id} - {c.title}</p>
          <p className="text-sm text-slate-500">Status: {c.status}</p>
          <div className="mt-2 flex gap-2">
            <button className="rounded bg-amber-500 px-3 py-1 text-white" onClick={() => updateStatus(c.id, 'In Progress')}>In Progress</button>
            <button className="rounded bg-emerald-600 px-3 py-1 text-white" onClick={() => updateStatus(c.id, 'Resolved')}>Resolved</button>
            <button className="rounded bg-slate-700 px-3 py-1 text-white" onClick={() => updateStatus(c.id, 'Closed')}>Closed</button>
          </div>
        </div>
      ))}
    </div>
  )
}
