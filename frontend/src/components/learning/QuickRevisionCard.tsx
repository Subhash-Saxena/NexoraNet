import React from 'react'
import { BookmarkCheck, Hash, Key } from 'lucide-react'

export interface QuickRevisionCardProps {
  keyTakeaways: string[]
  formulaOrPorts?: { label: string; value: string }[]
  commonTraps?: string[]
}

export const QuickRevisionCard: React.FC<QuickRevisionCardProps> = ({
  keyTakeaways,
  formulaOrPorts,
  commonTraps,
}) => {
  return (
    <div className="revision-box">
      <div className="revision-title">
        <BookmarkCheck size={18} />
        <span>Quick Revision & Exam Cheat Sheet</span>
      </div>

      <div style={{ marginBottom: '14px' }}>
        <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px' }}>
          Core Takeaways
        </div>
        <ul style={{ margin: '0 0 0 18px', color: '#cbd5e1', fontSize: '0.88rem' }}>
          {keyTakeaways.map((item, idx) => (
            <li key={idx} style={{ marginBottom: '6px', lineHeight: 1.5 }}>
              {item}
            </li>
          ))}
        </ul>
      </div>

      {formulaOrPorts && formulaOrPorts.length > 0 && (
        <div style={{ marginBottom: '14px' }}>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700, marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Hash size={14} color="var(--cyan-primary)" />
            <span>Key Ports & Constants</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '8px' }}>
            {formulaOrPorts.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '6px 10px',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{item.label}</span>
                <code style={{ fontSize: '0.82rem', color: 'var(--cyan-primary)', fontWeight: 600 }}>
                  {item.value}
                </code>
              </div>
            ))}
          </div>
        </div>
      )}

      {commonTraps && commonTraps.length > 0 && (
        <div>
          <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--amber-warning)', fontWeight: 700, marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Key size={14} />
            <span>Common Exam & Interview Traps</span>
          </div>
          <ul style={{ margin: '0 0 0 18px', color: '#e2e8f0', fontSize: '0.84rem' }}>
            {commonTraps.map((trap, idx) => (
              <li key={idx} style={{ marginBottom: '4px' }}>
                {trap}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
