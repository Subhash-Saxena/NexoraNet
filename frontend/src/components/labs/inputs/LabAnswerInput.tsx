import React from 'react'
import type { SafeInputConfig } from '../../../types'
import { SingleChoiceInput } from './SingleChoiceInput'
import { MultipleChoiceInput } from './MultipleChoiceInput'
import { TextInput } from './TextInput'
import { NumericInput } from './NumericInput'
import { IPAddressInput } from './IPAddressInput'
import { CIDRInput } from './CIDRInput'
import { PortInput } from './PortInput'
import { SubnetInput } from './SubnetInput'

interface LabAnswerInputProps {
  validationType: string
  config: SafeInputConfig
  value: any
  onChange: (val: any) => void
  disabled?: boolean
}

export const LabAnswerInput: React.FC<LabAnswerInputProps> = ({
  validationType,
  config,
  value,
  onChange,
  disabled = false,
}) => {
  const vtype = (validationType || config.validation_type || 'TEXT').toUpperCase().trim()

  switch (vtype) {
    case 'SINGLE_CHOICE':
      return (
        <SingleChoiceInput
          config={config}
          value={typeof value === 'string' ? value : ''}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'MULTIPLE_CHOICE':
      return (
        <MultipleChoiceInput
          config={config}
          value={Array.isArray(value) ? value : []}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'IP_ADDRESS':
      return (
        <IPAddressInput
          config={config}
          value={typeof value === 'string' ? value : ''}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'CIDR':
      return (
        <CIDRInput
          config={config}
          value={typeof value === 'string' ? value : ''}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'PORT':
      return (
        <PortInput
          config={config}
          value={typeof value === 'string' || typeof value === 'number' ? String(value) : ''}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'NUMERICAL':
      return (
        <NumericInput
          config={config}
          value={typeof value === 'string' || typeof value === 'number' ? String(value) : ''}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'SUBNET':
    case 'SUBNETTING':
      return (
        <SubnetInput
          config={config}
          value={value || ''}
          onChange={onChange}
          disabled={disabled}
        />
      )

    case 'TEXT':
    case 'SHORT_ANSWER':
    default:
      return (
        <TextInput
          config={config}
          value={typeof value === 'string' ? value : ''}
          onChange={onChange}
          disabled={disabled}
        />
      )
  }
}
