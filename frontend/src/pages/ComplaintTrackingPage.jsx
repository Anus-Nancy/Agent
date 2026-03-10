import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function ComplaintTrackingPage() {
  const [complaints, setComplaints] = useState([])

  useEffect(() => {
    api.get('/complaints').then((r) => setComplaints(r.data)).catch(() => setComplaints([]))
  }, [])

  return (
    <div className="rounded bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-semibold">Complaint Tracking</h2>
      <div className="overflow-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b">
              <th className="p-2">ID</th><th className="p-2">Title</th><th className="p-2">Status</th><th className="p-2">Escalation</th>
            </tr>
          </thead>
          <tbody>
            {complaints.map((c) => (
              <tr key={c.id} className="border-b">
                <td className="p-2">{c.id}</td><td className="p-2">{c.title}</td><td className="p-2">{c.status}</td><td className="p-2">{c.escalation_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
