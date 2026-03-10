import { useState } from 'react'
import { api } from '../api/client'

export default function SubmitComplaintPage() {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [message, setMessage] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    setMessage('')
    try {
      await api.post('/complaints', { title, description })
      setTitle('')
      setDescription('')
      setMessage('Complaint submitted successfully.')
    } catch {
      setMessage('Failed to submit complaint.')
    }
  }

  return (
    <div className="rounded bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-semibold">Submit Complaint</h2>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full rounded border p-2" placeholder="Complaint title" value={title} onChange={(e) => setTitle(e.target.value)} required />
        <textarea className="h-36 w-full rounded border p-2" placeholder="Complaint details" value={description} onChange={(e) => setDescription(e.target.value)} required />
        <button className="rounded bg-blue-600 px-4 py-2 text-white">Submit</button>
      </form>
      {message && <p className="mt-3 text-sm text-slate-700">{message}</p>}
    </div>
  )
}
