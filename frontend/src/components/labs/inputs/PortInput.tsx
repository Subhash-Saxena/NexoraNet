import React from 'react'
import type { SafeInputConfig } from '../../../types'

interface PortInputProps {
  config?: SafeInputConfig
  value: string | number
  onChange: (val: string | number) => void
  disabled?: boolean
  placeholder?: string
}

export const PortInput: React.FC<PortInputProps> = ({
  config = { validation_type: 'PORT' },
  value,
  onChange,
  disabled = false,
  placeholder,
}) => {
  const strVal = String(value)
  const numVal = parseInt(strVal, 10)
  const isValidPort = !isNaN(numVal) && numVal >= 1 && numVal <= 65535

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {config.label && (
          <label style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-main)' }}>
            {config.label}
          </label>
        )}
        {strVal.trim().length > 0 && (
          <span
            style={{
              fontSize: '0.72rem',
              padding: '2px 6px',
              borderRadius: '3px',
              background: isValidPort ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
              color: isValidPort ? 'var(--emerald-success)' : 'var(--crimson-danger)',
              border: `1px solid ${isValidPort ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
            }}
          >
            {isValidPort ? (numVal <= 1023 ? 'Well-Known (0-1023)' : numVal <= 49151 ? 'Registered (1024-49151)' : 'Dynamic/Private (49152-65535)') : 'Out of Range (1-65535)'}
          </span>
        )}
      </div>
      {config.helper_text && (
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          {config.helper_text}
        </span>
      )}
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder || config.placeholder || 'e.g. 53, 80, 443'}
        min={1}
        max={65535}
        style={{
          width: '100%',
          maxWidth: '240px',
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
