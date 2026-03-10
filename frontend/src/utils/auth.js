export const getCurrentUser = () => {
  const raw = localStorage.getItem('user')
  return raw ? JSON.parse(raw) : null
}

export const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}
