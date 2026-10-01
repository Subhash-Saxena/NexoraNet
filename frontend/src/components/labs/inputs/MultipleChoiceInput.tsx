import React from 'react'
import type { SafeInputConfig, SafeInputOption } from '../../../types'

interface MultipleChoiceInputProps {
  config?: SafeInputConfig
  options?: SafeInputOption[]
  value: string[] | string
  onChange: (val: string[]) => void
  disabled?: boolean
}

export const MultipleChoiceInput: React.FC<MultipleChoiceInputProps> = ({
  config = { validation_type: 'MULTIPLE_CHOICE' },
  options: optionsProp,
  value,
  onChange,
  disabled = false,
}) => {
  const options = optionsProp || config.options || []
  const selectedList = Array.isArray(value)
    ? value
    : typeof value === 'string' && value.trim()
    ? value.split(',').map((s) => s.trim())
    : []

  const toggleOption = (text: string) => {
    if (disabled) return
    const exists = selectedList.includes(text)
    if (exists) {
      onChange(selectedList.filter((v) => v !== text))
    } else {
      onChange([...selectedList, text])
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {config.label && (
        <label style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--text-main)' }}>
          {config.label}
        </label>
      )}
      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
        {config.helper_text || 'Select all that apply'}
      </span>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '4px' }}>
        {options.map((opt) => {
          const isSelected = selectedList.includes(opt.text)
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
                type="checkbox"
                value={opt.text}
                checked={isSelected}
                onChange={() => toggleOption(opt.text)}
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
