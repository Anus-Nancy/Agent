import { Link, useNavigate } from 'react-router-dom'
import { getCurrentUser, logout } from '../../utils/auth'

export default function AppLayout({ children }) {
  const user = getCurrentUser()
  const navigate = useNavigate()

  const onLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <h1 className="text-lg font-semibold text-slate-800">TCF Complaint System</h1>
          <div className="flex items-center gap-4 text-sm">
            <span className="rounded bg-slate-100 px-2 py-1">{user?.role || 'guest'}</span>
            <button className="rounded bg-rose-600 px-3 py-1 text-white" onClick={onLogout}>Logout</button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 px-4 py-4 md:grid-cols-[240px_1fr]">
        <aside className="rounded bg-white p-3 shadow">
          <nav className="space-y-2 text-sm">
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/student">Student Dashboard</Link>
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/complaints/new">Submit Complaint</Link>
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/complaints/track">Complaint Tracking</Link>
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/queries">Query Page</Link>
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/chatbot">Chatbot</Link>
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/admin">Admin Dashboard</Link>
            <Link className="block rounded px-2 py-1 hover:bg-slate-100" to="/staff">Staff Dashboard</Link>
          </nav>
        </aside>
        <main>{children}</main>
      </div>
    </div>
  )
}
