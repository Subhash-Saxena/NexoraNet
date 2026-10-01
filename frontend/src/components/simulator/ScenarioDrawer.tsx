import React, { useState } from 'react'
import {
  X,
  BookOpen,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  Award,
  ChevronRight,
} from 'lucide-react'
import type { Scenario, ScenarioValidationResult, TopologyData } from '../../types/simulator'

interface ScenarioDrawerProps {
  isOpen: boolean
  onClose: () => void
  scenarios: Scenario[]
  activeScenario: Scenario | null
  onSelectScenario: (scenario: Scenario) => void
  currentTopology: TopologyData
  onValidateScenario: (hintsUsed: number) => Promise<ScenarioValidationResult | null>
}

export const ScenarioDrawer: React.FC<ScenarioDrawerProps> = ({
  isOpen,
  onClose,
  scenarios,
  activeScenario,
  onSelectScenario,
  onValidateScenario,
}) => {
  const [hintsRevealed, setHintsRevealed] = useState<number>(0)
  const [isValidating, setIsValidating] = useState<boolean>(false)
  const [validationResult, setValidationResult] = useState<ScenarioValidationResult | null>(null)

  if (!isOpen) return null

  const handleRevealHint = () => {
    if (activeScenario && hintsRevealed < activeScenario.hints.length) {
      setHintsRevealed((h) => h + 1)
    }
  }

  const handleCheck = async () => {
    setIsValidating(true)
    try {
      const res = await onValidateScenario(hintsRevealed)
      setValidationResult(res)
    } finally {
      setIsValidating(false)
    }
  }

  const handleSelect = (sc: Scenario) => {
    onSelectScenario(sc)
    setHintsRevealed(0)
    setValidationResult(null)
  }

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        zIndex: 50,
        display: 'flex',
        justifyContent: 'flex-end',
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: '520px',
          maxWidth: '90vw',
          height: '100%',
          backgroundColor: '#0f172a',
          borderLeft: '1px solid #1e293b',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '-8px 0 25px rgba(0, 0, 0, 0.6)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Drawer Header */}
        <div
          style={{
            padding: '1rem',
            borderBottom: '1px solid #1e293b',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, color: '#f8fafc' }}>
            <BookOpen size={18} color="#38bdf8" /> Guided Scenarios & Challenges
          </div>
          <button
            className="sim-btn sim-btn-secondary"
            style={{ padding: '0.25rem' }}
            onClick={onClose}
          >
            <X size={16} />
          </button>
        </div>

        {/* Drawer Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
          {!activeScenario ? (
            <div>
              <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '1rem' }}>
                Select a guided learning scenario to test and apply your networking skills.
              </div>

              {['BEGINNER', 'INTERMEDIATE', 'ADVANCED'].map((diff) => {
                const filtered = scenarios.filter((s) => s.difficulty === diff)
                if (filtered.length === 0) return null

                return (
                  <div key={diff} style={{ marginBottom: '1.2rem' }}>
                    <div
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        color: diff === 'BEGINNER' ? '#34d399' : diff === 'INTERMEDIATE' ? '#fbbf24' : '#f87171',
                        marginBottom: '0.4rem',
                      }}
                    >
                      {diff} Tracks
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                      {filtered.map((sc) => (
                        <div
                          key={sc.id}
                          style={{
                            background: '#1e293b',
                            border: '1px solid #334155',
                            borderRadius: '0.375rem',
                            padding: '0.65rem 0.85rem',
                            cursor: 'pointer',
                            transition: 'all 0.15s ease',
                          }}
                          onClick={() => handleSelect(sc)}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f1f5f9' }}>
                              {sc.title}
                            </div>
                            <ChevronRight size={14} color="#64748b" />
                          </div>
                          <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.2rem' }}>
                            {sc.description.slice(0, 110)}...
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div>
              <button
                className="sim-btn sim-btn-secondary"
                style={{ marginBottom: '0.75rem', fontSize: '0.75rem', padding: '0.2rem 0.5rem' }}
                onClick={() => handleSelect(null as any)}
              >
                ← Back to All Scenarios
              </button>

              <div style={{ marginBottom: '1rem' }}>
                <span className="simulator-badge" style={{ marginRight: '0.5rem' }}>
                  {activeScenario.difficulty}
                </span>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                  Category: {activeScenario.category}
                </span>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', marginTop: '0.4rem', marginBottom: '0.4rem' }}>
                  {activeScenario.title}
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: 1.45 }}>
                  {activeScenario.description}
                </p>
              </div>

              {/* Tasks Checklist */}
              <div style={{ marginBottom: '1rem', background: '#1e293b', padding: '0.75rem', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#38bdf8', marginBottom: '0.5rem' }}>
                  TASKS & OBJECTIVES
                </div>
                {activeScenario.tasks.map((task, idx) => (
                  <div
                    key={task.id}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.5rem',
                      fontSize: '0.78rem',
                      marginBottom: '0.4rem',
                    }}
                  >
                    <span style={{ color: '#64748b', fontWeight: 'bold' }}>{idx + 1}.</span>
                    <div>
                      <div style={{ fontWeight: 600, color: '#f8fafc' }}>{task.title}</div>
                      <div style={{ color: '#94a3b8', fontSize: '0.73rem' }}>{task.description}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Progressive Hints */}
              <div style={{ marginBottom: '1rem', background: '#131c31', padding: '0.75rem', borderRadius: '0.375rem', border: '1px solid #1e293b' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#fbbf24', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                    <HelpCircle size={14} /> Guided Hints ({hintsRevealed}/{activeScenario.hints.length})
                  </span>
                  {hintsRevealed < activeScenario.hints.length && (
                    <button
                      className="sim-btn sim-btn-secondary"
                      style={{ fontSize: '0.7rem', padding: '0.15rem 0.4rem' }}
                      onClick={handleRevealHint}
                    >
                      Reveal Hint #{hintsRevealed + 1}
                    </button>
                  )}
                </div>

                {hintsRevealed === 0 && (
                  <div style={{ fontSize: '0.74rem', color: '#64748b' }}>
                    Try solving the scenario first. If stuck, click Reveal Hint.
                  </div>
                )}

                {activeScenario.hints.slice(0, hintsRevealed).map((h, i) => (
                  <div key={i} style={{ fontSize: '0.75rem', color: '#e2e8f0', marginTop: '0.3rem', paddingLeft: '0.5rem', borderLeft: '2px solid #fbbf24' }}>
                    <strong>Hint {i + 1}:</strong> {h}
                  </div>
                ))}
              </div>

              {/* Validation Result Box */}
              {validationResult && (
                <div
                  style={{
                    background: validationResult.is_passed ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    border: `1px solid ${validationResult.is_passed ? '#10b981' : '#ef4444'}`,
                    padding: '0.75rem',
                    borderRadius: '0.375rem',
                    marginBottom: '1rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontWeight: 700, color: validationResult.is_passed ? '#34d399' : '#f87171' }}>
                    {validationResult.is_passed ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                    {validationResult.feedback}
                  </div>

                  {validationResult.is_passed && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', marginTop: '0.3rem', fontSize: '0.8rem', color: '#38bdf8' }}>
                      <Award size={14} /> Earned Score: {validationResult.score}/100
                    </div>
                  )}

                  <div style={{ marginTop: '0.5rem' }}>
                    {validationResult.task_results.map((tr, idx) => (
                      <div key={idx} style={{ fontSize: '0.73rem', display: 'flex', gap: '0.3rem', color: tr.passed ? '#34d399' : '#f87171' }}>
                        <span>{tr.passed ? '✓' : '✗'}</span>
                        <span>{tr.message}</span>
                      </div>
                    ))}
                  </div>

                  {validationResult.solution_explanation && (
                    <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', color: '#cbd5e1', borderTop: '1px solid rgba(255, 255, 255, 0.1)', paddingTop: '0.4rem' }}>
                      <strong>Pedagogical Takeaway:</strong> {validationResult.solution_explanation}
                    </div>
                  )}
                </div>
              )}

              {/* Validate Action */}
              <button
                className="sim-btn sim-btn-primary"
                style={{ width: '100%', justifyContent: 'center', padding: '0.6rem', fontSize: '0.85rem' }}
                onClick={handleCheck}
                disabled={isValidating}
              >
                {isValidating ? 'Validating Topology...' : 'Check Solution & Score'}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
