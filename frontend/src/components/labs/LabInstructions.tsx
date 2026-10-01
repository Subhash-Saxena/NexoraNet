import React, { useState } from 'react'
import { Shield, Copy, Check, Monitor, Laptop, Server } from 'lucide-react'
import type { LabStepDetail } from '../../types'

interface LabInstructionsProps {
  step: LabStepDetail
  environmentType: string
}

export const LabInstructions: React.FC<LabInstructionsProps> = ({
  step,
  environmentType,
}) => {
  const [copied, setCopied] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState<'windows' | 'linux' | 'macos'>('windows')

  // Extract commands for Windows, Linux, macOS if present in markdown instructions
  const extractPlatformCommands = (text: string) => {
    const commands: { windows?: string; linux?: string; macos?: string } = {}

    const winMatch = text.match(/Windows[^\n`]*?`([^`]+)`/i)
    if (winMatch) commands.windows = winMatch[1]

    const linMatch = text.match(/Linux[^\n`]*?`([^`]+)`/i)
    if (linMatch) commands.linux = linMatch[1]

    const macMatch = text.match(/macOS[^\n`]*?`([^`]+)`/i)
    if (macMatch) commands.macos = macMatch[1]

    return commands
  }

  const commands = extractPlatformCommands(step.instructions || '')
  const hasCommands = !!(commands.windows || commands.linux || commands.macos)

  const activeCommand =
    selectedPlatform === 'windows'
      ? commands.windows || 'ipconfig'
      : selectedPlatform === 'linux'
      ? commands.linux || 'ip addr'
      : commands.macos || 'ifconfig'

  const handleCopy = () => {
    if (!activeCommand) return
    navigator.clipboard.writeText(activeCommand)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  // Format simple markdown into paragraphs and formatted items
  const renderFormattedInstructions = (text: string) => {
    const lines = text.split('\n')
    return lines.map((line, idx) => {
      if (!line.trim()) {
        return <div key={idx} style={{ height: 8 }} />
      }

      // Format bold and inline code
      const parts = line.split(/(`[^`]+`|\*\*[^*]+\*\*)/g)
      const formattedContent = parts.map((part, pIdx) => {
        if (part.startsWith('`') && part.endsWith('`')) {
          return <code key={pIdx}>{part.slice(1, -1)}</code>
        }
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={pIdx}>{part.slice(2, -2)}</strong>
        }
        return part
      })

      if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
        return (
          <li key={idx} style={{ marginLeft: 20, marginBottom: 4 }}>
            {formattedContent}
          </li>
        )
      }

      return (
        <p key={idx} style={{ marginBottom: 8 }}>
          {formattedContent}
        </p>
      )
    })
  }

  return (
    <div className="lab-step-instructions-container">
      {environmentType === 'LOCAL_SYSTEM' && (
        <div className="lab-safety-banner" style={{ marginBottom: 18 }}>
          <Shield size={20} color="var(--cyan-primary)" style={{ flexShrink: 0 }} />
          <div>
            <strong>Local Terminal Drill:</strong> Execute the commands in your local operating
            system terminal. Inspect the real output and answer the validation question below. No
            commands run on the NexoraNet server.
          </div>
        </div>
      )}

      {hasCommands && (
        <div className="lab-command-box" style={{ marginBottom: 20 }}>
          <div className="lab-platform-tabs">
            <button
              type="button"
              className={`lab-platform-tab ${selectedPlatform === 'windows' ? 'active' : ''}`}
              onClick={() => setSelectedPlatform('windows')}
            >
              <Monitor size={14} /> Windows (CMD / PowerShell)
            </button>
            <button
              type="button"
              className={`lab-platform-tab ${selectedPlatform === 'linux' ? 'active' : ''}`}
              onClick={() => setSelectedPlatform('linux')}
            >
              <Server size={14} /> Linux (Bash / Zsh)
            </button>
            <button
              type="button"
              className={`lab-platform-tab ${selectedPlatform === 'macos' ? 'active' : ''}`}
              onClick={() => setSelectedPlatform('macos')}
            >
              <Laptop size={14} /> macOS (Terminal)
            </button>
          </div>

          <div className="lab-command-body">
            <div>
              <span style={{ color: 'var(--text-muted)', marginRight: 10, userSelect: 'none' }}>
                {selectedPlatform === 'windows' ? 'PS C:\\Users>' : '$'}
              </span>
              <span>{activeCommand}</span>
            </div>

            <button
              type="button"
              className={`lab-copy-btn ${copied ? 'copied' : ''}`}
              onClick={handleCopy}
              title="Copy command to clipboard"
            >
              {copied ? (
                <>
                  <Check size={14} /> Copied
                </>
              ) : (
                <>
                  <Copy size={14} /> Copy Command
                </>
              )}
            </button>
          </div>
        </div>
      )}

      <div className="lab-instruction-text">
        {step.description && (
          <p style={{ fontSize: '1rem', color: 'var(--text-main)', marginBottom: 14 }}>
            <strong>{step.description}</strong>
          </p>
        )}
        {renderFormattedInstructions(step.instructions || '')}
      </div>
    </div>
  )
}
