import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import type { LoginCredentials, RegisterCredentials, UserProfile } from '../types/auth'
import { authApi } from '../services/authApi'
import {
  clearAuth,
  getAuthToken,
  getStoredUser,
} from '../services/apiConfig'

interface AuthContextType {
  user: UserProfile | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => Promise<void>
  loginDemo: () => Promise<void>
  clearError: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(() => getStoredUser())
  const [token, setToken] = useState<string | null>(() => getAuthToken())
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [error, setError] = useState<string | null>(null)

  // Validate session on boot
  useEffect(() => {
    let isMounted = true
    const initAuth = async () => {
      const existingToken = getAuthToken()
      if (existingToken) {
        try {
          const profile = await authApi.getCurrentUser()
          if (isMounted) {
            setUser(profile)
            setToken(existingToken)
          }
        } catch {
          if (isMounted) {
            clearAuth()
            setUser(null)
            setToken(null)
          }
        }
      }
      if (isMounted) {
        setIsLoading(false)
      }
    }

    initAuth()

    const handleUnauthorized = () => {
      clearAuth()
      setUser(null)
      setToken(null)
    }

    window.addEventListener('nexora:unauthorized', handleUnauthorized)
    return () => {
      isMounted = false
      window.removeEventListener('nexora:unauthorized', handleUnauthorized)
    }
  }, [])

  const login = useCallback(async (credentials: LoginCredentials) => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await authApi.login(credentials)
      setUser(res.user)
      setToken(res.access_token)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Login failed'
      setError(msg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const register = useCallback(async (credentials: RegisterCredentials) => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await authApi.register(credentials)
      setUser(res.user)
      setToken(res.access_token)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Registration failed'
      setError(msg)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(async () => {
    setIsLoading(true)
    try {
      await authApi.logout()
    } finally {
      setUser(null)
      setToken(null)
      setIsLoading(false)
    }
  }, [])

  const loginDemo = useCallback(async () => {
    // Quick demo student login
    return login({
      username: 'student1',
      password: 'ProductionPassword2026!',
    })
  }, [login])

  const clearError = useCallback(() => {
    setError(null)
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        error,
        login,
        register,
        logout,
        loginDemo,
        clearError,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
