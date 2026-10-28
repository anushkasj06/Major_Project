import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { authAPI } from '../services/api'

export function useAuth() {
  const { user, isAuthenticated, setAuth, logout, updateLanguage } = useAuthStore()
  const navigate = useNavigate()

  const login = useCallback(async (email: string, password: string) => {
    const res = await authAPI.login(email, password)
    const { user, access_token, refresh_token } = res.data
    setAuth(user, access_token, refresh_token)
    return user
  }, [setAuth])

  const register = useCallback(async (name: string, email: string, password: string) => {
    const res = await authAPI.register({ name, email, password })
    const { user, access_token, refresh_token } = res.data
    setAuth(user, access_token, refresh_token)
    return user
  }, [setAuth])

  const handleLogout = useCallback(async () => {
    try { await authAPI.logout() } catch {}
    logout()
    navigate('/login')
  }, [logout, navigate])

  const changeLanguage = useCallback(async (lang: string) => {
    try {
      await authAPI.me() // just to verify auth
      updateLanguage(lang)
    } catch {}
  }, [updateLanguage])

  return { user, isAuthenticated, login, register, logout: handleLogout, changeLanguage }
}
