import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Shield, Lock, User, Mail, AlertCircle, ArrowRight, CheckCircle2, Sparkles } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

interface LoginPageProps {
  initialTab?: 'login' | 'register'
}

export const LoginPage: React.FC<LoginPageProps> = ({ initialTab = 'login' }) => {
  const [tab, setTab] = useState<'login' | 'register'>(initialTab)
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const { login, register, loginDemo, isAuthenticated, user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard'

  // If already logged in, show status with continue or logout
  if (isAuthenticated && user) {
    return (
      <div style={{ maxWidth: '480px', margin: '4rem auto', padding: '2rem', background: 'var(--card-bg, #1e293b)', borderRadius: '12px', border: '1px solid var(--border-color, #334155)', textAlign: 'center' }}>
        <CheckCircle2 size={48} style={{ color: '#10b981', margin: '0 auto 1rem' }} />
        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem', color: '#f8fafc' }}>Already Signed In</h2>
        <p style={{ color: '#94a3b8', marginBottom: '1.5rem' }}>
          Signed in as <strong>{user.display_name || user.username}</strong> ({user.email})
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <button
            onClick={() => navigate(from)}
            style={{ padding: '0.75rem 1.5rem', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 600 }}
          >
            Go to Platform
          </button>
          <button
            onClick={() => logout()}
            style={{ padding: '0.75rem 1.5rem', background: '#334155', color: '#f8fafc', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
          >
            Sign Out
          </button>
        </div>
      </div>
    )
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)
    if (!identifier.trim() || !password) {
      setFormError('Please enter both your username/email and password.')
      return
    }

    setIsSubmitting(true)
    try {
      await login({ username: identifier.trim(), password })
      navigate(from, { replace: true })
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Invalid credentials.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)
    if (!username.trim() || !email.trim() || !password) {
      setFormError('Please fill in all required fields.')
      return
    }
    if (password.length < 8) {
      setFormError('Password must be at least 8 characters long.')
      return
    }

    setIsSubmitting(true)
    try {
      await register({
        username: username.trim(),
        email: email.trim(),
        password,
        display_name: displayName.trim() || undefined,
      })
      navigate(from, { replace: true })
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Registration failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleQuickDemo = async () => {
    setIsSubmitting(true)
    setFormError(null)
    try {
      await loginDemo()
      navigate(from, { replace: true })
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Demo login failed.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div style={{ maxWidth: '460px', margin: '3rem auto', padding: '0 1rem' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <div style={{ display: 'inline-flex', padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '16px', color: '#60a5fa', marginBottom: '1rem', border: '1px solid rgba(59, 130, 246, 0.2)' }}>
          <Shield size={36} />
        </div>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: '#f8fafc', margin: '0 0 0.5rem' }}>NexoraNet</h1>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', margin: 0 }}>“Learn. Simulate. Analyze. Defend.”</p>
      </div>

      <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '16px', padding: '2rem', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.5)' }}>
        {/* Tab Controls */}
        <div style={{ display: 'flex', borderBottom: '1px solid #334155', marginBottom: '1.5rem' }}>
          <button
            type="button"
            onClick={() => { setTab('login'); setFormError(null) }}
            style={{
              flex: 1,
              padding: '0.75rem',
              background: 'none',
              border: 'none',
              borderBottom: tab === 'login' ? '2px solid #3b82f6' : '2px solid transparent',
              color: tab === 'login' ? '#60a5fa' : '#94a3b8',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.95rem',
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            onClick={() => { setTab('register'); setFormError(null) }}
            style={{
              flex: 1,
              padding: '0.75rem',
              background: 'none',
              border: 'none',
              borderBottom: tab === 'register' ? '2px solid #3b82f6' : '2px solid transparent',
              color: tab === 'register' ? '#60a5fa' : '#94a3b8',
              fontWeight: 600,
              cursor: 'pointer',
              fontSize: '0.95rem',
            }}
          >
            Create Account
          </button>
        </div>

        {formError && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1rem', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', color: '#f87171', fontSize: '0.85rem', marginBottom: '1.25rem' }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{formError}</span>
          </div>
        )}

        {tab === 'login' ? (
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Email or Username
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="text"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
                  placeholder="student1 or student@nexoranet.com"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.9rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.9rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '0.85rem',
                background: '#2563eb',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.95rem',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                opacity: isSubmitting ? 0.7 : 1,
                marginTop: '0.5rem',
                transition: 'background 0.2s',
              }}
            >
              {isSubmitting ? 'Authenticating...' : 'Sign In'}
              <ArrowRight size={16} />
            </button>
          </form>
        ) : (
          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Username (3-32 characters)
              </label>
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="johndoe"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.9rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="student@example.com"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.9rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Full / Display Name (Optional)
              </label>
              <input
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="John Doe"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f8fafc',
                  fontSize: '0.9rem',
                  outline: 'none',
                  boxSizing: 'border-box',
                }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
                Password (min 8 characters)
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  style={{
                    width: '100%',
                    padding: '0.75rem 0.75rem 0.75rem 2.5rem',
                    background: '#1e293b',
                    border: '1px solid #334155',
                    borderRadius: '8px',
                    color: '#f8fafc',
                    fontSize: '0.9rem',
                    outline: 'none',
                    boxSizing: 'border-box',
                  }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '0.85rem',
                background: '#10b981',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.95rem',
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                opacity: isSubmitting ? 0.7 : 1,
                marginTop: '0.5rem',
              }}
            >
              {isSubmitting ? 'Creating Account...' : 'Register Account'}
              <ArrowRight size={16} />
            </button>
          </form>
        )}

        <div style={{ margin: '1.5rem 0', display: 'flex', alignItems: 'center', gap: '1rem', color: '#64748b', fontSize: '0.8rem' }}>
          <div style={{ flex: 1, height: '1px', background: '#334155' }} />
          <span>OR</span>
          <div style={{ flex: 1, height: '1px', background: '#334155' }} />
        </div>

        {/* 1-Click Quick Demo Student Sign In */}
        <button
          type="button"
          onClick={handleQuickDemo}
          disabled={isSubmitting}
          style={{
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            padding: '0.75rem',
            background: 'rgba(59, 130, 246, 0.12)',
            color: '#60a5fa',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '8px',
            fontWeight: 600,
            fontSize: '0.88rem',
            cursor: isSubmitting ? 'not-allowed' : 'pointer',
            transition: 'all 0.2s',
          }}
        >
          <Sparkles size={16} />
          <span>1-Click Sign In as Pilot Student (student1)</span>
        </button>
      </div>

      <p style={{ textAlign: 'center', marginTop: '1.5rem', color: '#64748b', fontSize: '0.8rem' }}>
        Protected by Argon2/PBKDF2-HMAC-SHA256 & JWT Bearer authentication.
      </p>
    </div>
  )
}
