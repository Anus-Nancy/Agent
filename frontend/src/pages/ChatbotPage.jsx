import { useState } from 'react'
import { api } from '../api/client'

export default function ChatbotPage() {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])

  const ask = async (e) => {
    e.preventDefault()
    const q = question
    setQuestion('')
    setMessages((prev) => [...prev, { role: 'user', text: q }])
    try {
      const res = await api.post('/chatbot/ask', { question: q, top_k: 3 })
      setMessages((prev) => [...prev, { role: 'bot', text: res.data.answer, contexts: res.data.contexts }])
    } catch {
      setMessages((prev) => [...prev, { role: 'bot', text: 'Chatbot unavailable right now.' }])
    }
  }

  return (
    <div className="rounded bg-white p-6 shadow">
      <h2 className="mb-4 text-xl font-semibold">AI Chatbot</h2>
      <div className="mb-4 h-96 overflow-y-auto rounded border p-3">
        {messages.map((m, idx) => (
          <div key={idx} className={`mb-3 ${m.role === 'user' ? 'text-right' : 'text-left'}`}>
            <p className={`inline-block rounded px-3 py-2 text-sm ${m.role === 'user' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-800'}`}>{m.text}</p>
            {m.contexts && (
              <div className="mt-1 text-xs text-slate-500">
                Sources: {m.contexts.map((c) => c.title).join(', ')}
              </div>
            )}
          </div>
        ))}
      </div>
      <form onSubmit={ask} className="flex gap-2">
        <input className="flex-1 rounded border p-2" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask anything about fees, scholarships, admissions..." required />
        <button className="rounded bg-blue-600 px-4 py-2 text-white">Send</button>
      </form>
    </div>
  )
}
