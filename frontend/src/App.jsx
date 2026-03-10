import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import ProtectedRoute from './components/layout/ProtectedRoute'
import AdminDashboard from './pages/AdminDashboard'
import ChatbotPage from './pages/ChatbotPage'
import ComplaintTrackingPage from './pages/ComplaintTrackingPage'
import LoginPage from './pages/LoginPage'
import QueryPage from './pages/QueryPage'
import StaffDashboard from './pages/StaffDashboard'
import StudentDashboard from './pages/StudentDashboard'
import SubmitComplaintPage from './pages/SubmitComplaintPage'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Routes>
                <Route path="student" element={<StudentDashboard />} />
                <Route path="complaints/new" element={<SubmitComplaintPage />} />
                <Route path="complaints/track" element={<ComplaintTrackingPage />} />
                <Route path="queries" element={<QueryPage />} />
                <Route path="chatbot" element={<ChatbotPage />} />
                <Route path="admin" element={<AdminDashboard />} />
                <Route path="staff" element={<StaffDashboard />} />
                <Route path="*" element={<Navigate to="/student" replace />} />
              </Routes>
            </AppLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
