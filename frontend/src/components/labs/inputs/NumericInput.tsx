import React from 'react'
import type { SafeInputConfig } from '../../../types'

interface NumericInputProps {
  config?: SafeInputConfig
  value: string | number
  onChange: (val: string | number) => void
  disabled?: boolean
  placeholder?: string
}

export const NumericInput: React.FC<NumericInputProps> = ({
  config = { validation_type: 'NUMERICAL' },
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
        type="number"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder || config.placeholder || 'Enter numeric value (e.g. 62)'}
        style={{
          width: '100%',
          maxWidth: '300px',
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
