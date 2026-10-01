import React from 'react'
import type { SafeInputConfig } from '../../../types'

interface SubnetInputProps {
  config?: SafeInputConfig
  value: string | Record<string, string>
  onChange: (val: string | Record<string, string>) => void
  disabled?: boolean
  placeholder?: string
}

export const SubnetInput: React.FC<SubnetInputProps> = ({
  config = { validation_type: 'SUBNET' },
  value,
  onChange,
  disabled = false,
  placeholder,
}) => {
  // If structured fields are requested (e.g., network, broadcast, usable hosts)
  const isMultiField = config.fields && config.fields.length > 0

  if (isMultiField) {
    const valObj = typeof value === 'object' && value !== null ? value : {}

    const handleFieldChange = (field: string, text: string) => {
      onChange({ ...valObj, [field]: text })
    }

    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {config.label && (
          <label style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-main)' }}>
            {config.label}
          </label>
        )}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
          {config.fields?.map((fieldKey) => (
            <div key={fieldKey} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'capitalize' }}>
                {fieldKey.replace('_', ' ')}
              </span>
              <input
                type="text"
                value={valObj[fieldKey] || ''}
                onChange={(e) => handleFieldChange(fieldKey, e.target.value)}
                disabled={disabled}
                placeholder={`e.g. 192.168.10.x`}
                style={{
                  padding: '8px 12px',
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-main)',
                  fontSize: '0.86rem',
                  fontFamily: 'monospace',
                  outline: 'none',
                }}
              />
            </div>
          ))}
        </div>
      </div>
    )
  }

  // Single string subnet / network input fallback
  const strVal = typeof value === 'string' ? value : ''
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
        value={strVal}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder || config.placeholder || 'e.g. 192.168.10.0 or 255.255.255.192'}
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
