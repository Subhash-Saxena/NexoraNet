import type {
  AuthTokenResponse,
  LoginCredentials,
  RegisterCredentials,
  UserProfile,
} from '../types/auth'
import {
  clearAuth,
  getApiBaseUrl,
  getAuthHeaders,
  setAuthToken,
  setStoredUser,
} from './apiConfig'

class AuthApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  /**
   * Authenticate with username or email address and password.
   * Target endpoint: POST /api/v1/auth/login
   */
  async login(credentials: LoginCredentials): Promise<AuthTokenResponse> {
    const url = `${this.getBaseUrl()}/api/v1/auth/login`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        username: credentials.username.trim(),
        password: credentials.password,
      }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `Login failed (HTTP ${response.status})`)
    }

    const data: AuthTokenResponse = await response.json()
    setAuthToken(data.access_token)
    setStoredUser(data.user)
    return data
  }

  /**
   * Register a new student account.
   * Target endpoint: POST /api/v1/auth/register
   */
  async register(credentials: RegisterCredentials): Promise<AuthTokenResponse> {
    const url = `${this.getBaseUrl()}/api/v1/auth/register`
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({
        username: credentials.username.trim(),
        email: credentials.email.trim().toLowerCase(),
        password: credentials.password,
        display_name: credentials.display_name?.trim() || undefined,
      }),
    })

    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `Registration failed (HTTP ${response.status})`)
    }

    const data: AuthTokenResponse = await response.json()
    setAuthToken(data.access_token)
    setStoredUser(data.user)
    return data
  }

  /**
   * Fetch current authenticated user profile using active JWT.
   * Target endpoint: GET /api/v1/auth/me
   */
  async getCurrentUser(): Promise<UserProfile> {
    const url = `${this.getBaseUrl()}/api/v1/auth/me`
    const response = await fetch(url, {
      headers: getAuthHeaders(),
    })

    if (!response.ok) {
      throw new Error(`Session expired or unauthorized (HTTP ${response.status})`)
    }

    const user: UserProfile = await response.json()
    setStoredUser(user)
    return user
  }

  /**
   * Revoke current session token on the backend and clear local storage.
   * Target endpoint: POST /api/v1/auth/logout
   */
  async logout(): Promise<void> {
    const url = `${this.getBaseUrl()}/api/v1/auth/logout`
    try {
      await fetch(url, {
        method: 'POST',
        headers: getAuthHeaders(),
      })
    } catch (e) {
      // Ignore network errors on logout
      console.warn('Backend logout notification failed:', e)
    } finally {
      clearAuth()
    }
  }
}

export const authApi = new AuthApiService()
