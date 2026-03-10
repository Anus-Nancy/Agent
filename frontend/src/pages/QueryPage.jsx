import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function QueryPage() {
  const [queryText, setQueryText] = useState('')
  const [items, setItems] = useState([])

  const load = () => api.get('/queries').then((r) => setItems(r.data)).catch(() => setItems([]))
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    await api.post('/queries', { query_text: queryText })
    setQueryText('')
    load()
  }

  return (
    <div className="space-y-4">
      <div className="rounded bg-white p-6 shadow">
        <h2 className="mb-3 text-xl font-semibold">Submit Query</h2>
        <form onSubmit={submit} className="flex gap-2">
          <input className="flex-1 rounded border p-2" value={queryText} onChange={(e) => setQueryText(e.target.value)} placeholder="Ask your query" required />
          <button className="rounded bg-blue-600 px-4 py-2 text-white">Submit</button>
        </form>
      </div>
      <div className="rounded bg-white p-6 shadow">
        <h3 className="mb-3 font-semibold">Query History</h3>
        {items.map((q) => (
          <div key={q.id} className="mb-2 rounded border p-2 text-sm">
            <p><strong>Q:</strong> {q.query_text}</p>
            <p><strong>Status:</strong> {q.status}</p>
            {q.answer_text && <p><strong>A:</strong> {q.answer_text}</p>}
          </div>
        ))}
      </div>
    </div>
  )
}
