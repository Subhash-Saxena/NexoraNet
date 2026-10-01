import React from 'react'
import type { SafeInputConfig, SafeInputOption } from '../../../types'

interface SingleChoiceInputProps {
  config?: SafeInputConfig
  options?: SafeInputOption[]
  value: string
  onChange: (val: string) => void
  disabled?: boolean
}

export const SingleChoiceInput: React.FC<SingleChoiceInputProps> = ({
  config = { validation_type: 'SINGLE_CHOICE' },
  options: optionsProp,
  value,
  onChange,
  disabled = false,
}) => {
  const options = optionsProp || config.options || []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
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
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
        {options.map((opt) => {
          const isSelected = value.toLowerCase() === opt.text.toLowerCase()
          return (
            <label
              key={opt.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '10px 14px',
                background: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                border: isSelected ? '1px solid var(--cyan-primary)' : '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                cursor: disabled ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <input
                type="radio"
                name="single_choice_group"
                value={opt.text}
                checked={isSelected}
                onChange={() => onChange(opt.text)}
                disabled={disabled}
                style={{ accentColor: 'var(--cyan-primary)', cursor: 'pointer' }}
              />
              <span style={{ fontSize: '0.88rem', color: isSelected ? 'var(--cyan-primary)' : 'var(--text-secondary)' }}>
                {opt.text}
              </span>
            </label>
          )
        })}
      </div>
    </div>
  )
}
