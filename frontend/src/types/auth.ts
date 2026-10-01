/**
 * Authentication and User Identity Types.
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

export type UserRole = 'STUDENT' | 'INSTRUCTOR' | 'ADMIN'

export interface UserProfile {
  id: number
  username: string
  email: string
  display_name: string | null
  role: UserRole
  current_level: string
  is_active: boolean
}

export interface AuthTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: UserProfile
}

export interface LoginCredentials {
  username: string // can be username or email
  password: string
}

export interface RegisterCredentials {
  username: string
  email: string
  password: string
  display_name?: string
}
