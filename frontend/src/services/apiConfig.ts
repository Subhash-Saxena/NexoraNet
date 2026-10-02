import type { UserProfile } from '../types/auth'

const TOKEN_KEY = 'nexora_token'
const USER_KEY = 'nexora_user'

/**
 * Centralized API Configuration for NexoraNet Frontend.
 *
 * Resolves the backend API base URL from Vite environment variables:
 * - VITE_API_URL or VITE_API_BASE_URL (e.g., "https://nexoranet-api.onrender.com")
 * - If unset, defaults to empty string '' (enabling relative requests to Vite proxy, Nginx proxy, or Cloudflare Pages _redirects).
 */
export const getApiBaseUrl = (): string => {
  const envUrl =
    (import.meta.env.VITE_API_URL as string | undefined) ||
    (import.meta.env.VITE_API_BASE_URL as string | undefined) ||
    ''
  return envUrl ? envUrl.replace(/\/+$/, '') : ''
}

export const getAuthToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY)
}

export const setAuthToken = (token: string | null): void => {
  if (token) {
    localStorage.setItem(TOKEN_KEY, token)
  } else {
    localStorage.removeItem(TOKEN_KEY)
  }
}

export const getStoredUser = (): UserProfile | null => {
  const raw = localStorage.getItem(USER_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserProfile
  } catch {
    return null
  }
}

export const setStoredUser = (user: UserProfile | null): void => {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
    // Also sync legacy developer testing keys for backward compatibility
    localStorage.setItem('nexoranet_role', user.role)
    localStorage.setItem('nexoranet_user_id', String(user.id))
  } else {
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem('nexoranet_role')
    localStorage.removeItem('nexoranet_user_id')
  }
}

export const clearAuth = (): void => {
  setAuthToken(null)
  setStoredUser(null)
}

/**
 * Constructs standard headers, automatically injecting Bearer JWT token if available.
 */
export const getAuthHeaders = (extraHeaders: Record<string, string> = {}): Record<string, string> => {
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...extraHeaders,
  }
  const token = getAuthToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const role = localStorage.getItem('nexoranet_role')
  const userId = localStorage.getItem('nexoranet_user_id')
  if (role && !headers['X-User-Role']) headers['X-User-Role'] = role
  if (userId && !headers['X-User-Id']) headers['X-User-Id'] = userId
  return headers
}

let interceptorInstalled = false

/**
 * Transparent fetch interceptor that automatically attaches Authorization: Bearer <token>
 * to all outgoing API requests toward the NexoraNet backend.
 */
export const installFetchInterceptor = (): void => {
  if (interceptorInstalled || typeof window === 'undefined') return
  interceptorInstalled = true

  const originalFetch = window.fetch
  window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    let url = ''
    if (typeof input === 'string') {
      url = input
    } else if (input instanceof URL) {
      url = input.href
    } else if (input && typeof input === 'object' && 'url' in input) {
      url = (input as Request).url
    }

    const baseUrl = getApiBaseUrl()
    const isApiRequest = url.startsWith(baseUrl) || url.startsWith('/api')

    if (isApiRequest) {
      const token = getAuthToken()
      const modifiedInit: RequestInit = { ...(init || {}) }
      const headers = new Headers(modifiedInit.headers || {})

      if (!headers.has('Accept')) {
        headers.set('Accept', 'application/json')
      }

      if (token && !headers.has('Authorization')) {
        headers.set('Authorization', `Bearer ${token}`)
      }

      const role = localStorage.getItem('nexoranet_role')
      const userId = localStorage.getItem('nexoranet_user_id')
      if (role && !headers.has('X-User-Role')) headers.set('X-User-Role', role)
      if (userId && !headers.has('X-User-Id')) headers.set('X-User-Id', userId)

      modifiedInit.headers = headers
      const response = await originalFetch(input, modifiedInit)

      // Notify application if a 401 is received so it can update auth state
      if (response.status === 401 && !url.includes('/auth/login') && !url.includes('/auth/register')) {
        window.dispatchEvent(new CustomEvent('nexora:unauthorized'))
      }

      return response
    }

    return originalFetch(input, init)
  }
}
