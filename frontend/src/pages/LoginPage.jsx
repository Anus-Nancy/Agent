import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api/client'

export default function LoginPage() {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ full_name: '', email: '', password: '', role: 'student' })
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const onChange = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      if (mode === 'signup') {
        await api.post('/signup', form)
      }
      const res = await api.post('/login', { email: form.email, password: form.password })
      localStorage.setItem('token', res.data.access_token)
      localStorage.setItem('user', JSON.stringify({ email: form.email, role: form.role }))
      navigate('/student')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Authentication failed')
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded bg-white p-6 shadow">
        <h2 className="mb-4 text-2xl font-bold">{mode === 'login' ? 'Login' : 'Sign up'}</h2>
        {mode === 'signup' && (
          <input name="full_name" className="mb-3 w-full rounded border p-2" placeholder="Full name" onChange={onChange} required />
        )}
        <input name="email" type="email" className="mb-3 w-full rounded border p-2" placeholder="Email" onChange={onChange} required />
        <input name="password" type="password" className="mb-3 w-full rounded border p-2" placeholder="Password" onChange={onChange} required />
        {mode === 'signup' && (
          <select name="role" className="mb-3 w-full rounded border p-2" onChange={onChange} value={form.role}>
            <option value="student">Student</option>
            <option value="staff">Staff</option>
            <option value="admin">Admin</option>
          </select>
        )}
        {error && <p className="mb-3 text-sm text-rose-600">{error}</p>}
        <button className="w-full rounded bg-blue-600 py-2 text-white">{mode === 'login' ? 'Login' : 'Create account'}</button>
        <button type="button" className="mt-2 w-full text-sm text-blue-700" onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}>
          {mode === 'login' ? 'Need an account? Sign up' : 'Already have an account? Login'}
        </button>
      </form>
    </div>
  )
}
