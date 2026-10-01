import React from 'react'
import type { SafeInputConfig } from '../../../types'

interface TextInputProps {
  config?: SafeInputConfig
  value: string
  onChange: (val: string) => void
  disabled?: boolean
  placeholder?: string
}

export const TextInput: React.FC<TextInputProps> = ({
  config = { validation_type: 'TEXT' },
  value,
  onChange,
  disabled = false,
  placeholder,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      {config.label && (
        <label style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-main)' }}>
          {config.label}
        </label>
      )}
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
        placeholder={placeholder || config.placeholder || 'Enter your observation or parameter...'}
        style={{
          width: '100%',
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
