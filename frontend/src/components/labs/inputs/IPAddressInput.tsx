import React from 'react'
import type { SafeInputConfig } from '../../../types'

interface IPAddressInputProps {
  config?: SafeInputConfig
  value: string
  onChange: (val: string) => void
  disabled?: boolean
  placeholder?: string
}

export const IPAddressInput: React.FC<IPAddressInputProps> = ({
  config = { validation_type: 'IP_ADDRESS' },
  value,
  onChange,
  disabled = false,
  placeholder,
}) => {
  // Simple format validation indicator
  const isIPv4 = /^(\d{1,3}\.){3}\d{1,3}$/.test(value.trim())
  const isIPv6 = value.includes(':') && value.trim().length >= 2

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {config.label && (
          <label style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-main)' }}>
            {config.label}
          </label>
        )}
        {value.trim().length > 0 && (
          <span
            style={{
              fontSize: '0.72rem',
              padding: '2px 6px',
              borderRadius: '3px',
              background: isIPv4 || isIPv6 ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              color: isIPv4 || isIPv6 ? 'var(--emerald-success)' : 'var(--crimson-danger)',
              border: `1px solid ${isIPv4 || isIPv6 ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            }}
          >
            {isIPv4 ? 'IPv4 Format' : isIPv6 ? 'IPv6 Format' : 'Invalid IP Format'}
          </span>
        )}
      </div>
      {config.helper_text && (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          {config.helper_text}
        </span>
      )}
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder || config.placeholder || 'e.g. 192.168.1.1 or ::1'}
        style={{
          width: '100%',
          maxWidth: '380px',
          padding: '10px 14px',
          background: 'rgba(0, 0, 0, 0.25)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)',
          color: 'var(--text-main)',
          fontSize: '0.9rem',
          fontFamily: 'monospace',
          outline: 'none',
        }}
      />
    </div>
  )
}
