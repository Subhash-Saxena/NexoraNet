import React, { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Award,
  CheckCircle,
  GraduationCap,
  Lightbulb,
  Search,
  Target,
  XCircle,
} from 'lucide-react'
import { SiemNav } from '../components/siem/SiemNav'
import { siemApi } from '../services/siemApi'
import type {
  SIEMLabScenario,
  SIEMLabValidateResponse,
} from '../types/siem'
import '../components/siem/siem.css'

export const SiemLabsPage: React.FC = () => {
  const { slug } = useParams<{ slug?: string }>()
  const navigate = useNavigate()

  const [labs, setLabs] = useState<SIEMLabScenario[]>([])
  const [selectedLab, setSelectedLab] = useState<SIEMLabScenario | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Validation submission form
  const [identifiedEntity, setIdentifiedEntity] = useState<string>('')
  const [findingsNotes, setFindingsNotes] = useState<string>('')
  const [showHints, setShowHints] = useState<boolean>(false)

  const [validating, setValidating] = useState<boolean>(false)
  const [validationResult, setValidationResult] = useState<SIEMLabValidateResponse | null>(null)

  useEffect(() => {
    const fetchLabs = async () => {
      try {
        setError(null)
        const list = await siemApi.listLabs()
        setLabs(list)

        if (slug) {
          const match = list.find((l) => l.slug === slug)
          if (match) {
            setSelectedLab(match)
          } else {
            const specific = await siemApi.getLab(slug)
            setSelectedLab(specific)
          }
        } else if (list.length > 0) {
          setSelectedLab(list[0])
        }
      } catch (err: unknown) {
        setError(err instanceof Error ? err.message : 'Failed to load SIEM lab scenarios')
      }
    }
    fetchLabs()
  }, [slug])

  const handleSelectLab = (lab: SIEMLabScenario) => {
    setSelectedLab(lab)
    setValidationResult(null)
    setIdentifiedEntity('')
    setFindingsNotes('')
    setShowHints(false)
    navigate(`/siem/labs/${lab.slug}`)
  }

  const handleValidate = async () => {
    if (!selectedLab) return
    try {
      setValidating(true)
      const res = await siemApi.validateLab(selectedLab.slug, {
        executed_query: {
          conditions: [{ field: 'action', operator: '=', value: 'LOGIN_FAILURE' }],
        },
        identified_entity: identifiedEntity.trim() || undefined,
        findings_notes: findingsNotes.trim() || undefined,
      })
      setValidationResult(res)
    } catch (err: unknown) {
      alert(`Validation error: ${err instanceof Error ? err.message : 'Unknown error'}`)
    } finally {
      setValidating(false)
    }
  }

  const handleOpenInSearch = () => {
    if (!selectedLab) return
    navigate('/siem/search')
  }

  return (
    <div className="siem-container">
      {/* Header */}
      <div className="siem-header">
        <div className="siem-header-left">
          <div className="siem-title-row">
            <h1>
              <GraduationCap className="text-cyan-400" size={26} />
              SIEM Log Analysis Practice Labs
            </h1>
            <span className="siem-tag">HANDS-ON LABS</span>
          </div>
          <p className="siem-subtitle">
            Guided investigation scenarios. Formulate SIEM queries, isolate suspicious observables, and test your findings.
          </p>
        </div>
      </div>

      <SiemNav />

      {error && (
        <div style={{ padding: '0.75rem 1rem', background: 'rgba(239,68,68,0.1)', border: '1px solid #ef4444', borderRadius: '0.5rem', color: '#f87171' }}>
          {error}
        </div>
      )}

      {/* Main Two-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '1.5rem', alignItems: 'start' }}>
        {/* Lab Selector Sidebar */}
        <div className="siem-table-container" style={{ display: 'flex', flexDirection: 'column' }}>
          <div className="siem-table-toolbar">
            <span style={{ fontWeight: 600, color: '#f8fafc' }}>Scenarios ({labs.length})</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', maxHeight: '70vh', overflowY: 'auto' }}>
            {labs.map((lab) => {
              const isSelected = selectedLab?.id === lab.id
              return (
                <div
                  key={lab.id}
                  style={{
                    padding: '0.875rem 1rem',
                    borderBottom: '1px solid #1e293b',
                    cursor: 'pointer',
                    background: isSelected ? 'rgba(14, 165, 233, 0.12)' : 'transparent',
                    borderLeft: isSelected ? '3px solid #38bdf8' : '3px solid transparent',
                    transition: 'background 0.1s',
                  }}
                  onClick={() => handleSelectLab(lab)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                    <span className={`sev-badge sev-${lab.difficulty === 'ADVANCED' ? 'HIGH' : lab.difficulty === 'INTERMEDIATE' ? 'MEDIUM' : 'LOW'}`}>
                      {lab.difficulty}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      ~{lab.expected_event_count} events
                    </span>
                  </div>
                  <div style={{ fontWeight: 600, fontSize: '0.875rem', color: isSelected ? '#38bdf8' : '#f1f5f9' }}>
                    {lab.title}
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Lab Execution Workspace */}
        {selectedLab ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {/* Scenario Overview */}
            <div className="siem-kpi-card" style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h2 style={{ fontSize: '1.25rem', color: '#f8fafc', margin: '0 0 0.5rem 0' }}>
                    {selectedLab.title}
                  </h2>
                  <div style={{ fontSize: '0.8125rem', color: '#94a3b8', lineHeight: 1.5 }}>
                    {selectedLab.description}
                  </div>
                </div>
                <button
                  className="siem-btn-secondary"
                  onClick={handleOpenInSearch}
                  title="Open Search Workspace to run queries"
                >
                  <Search size={14} /> Open Search Engine &rarr;
                </button>
              </div>

              {/* Objectives */}
              <div style={{ marginTop: '1.25rem', background: '#0f172a', border: '1px solid #1e293b', borderRadius: '0.375rem', padding: '1rem' }}>
                <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.375rem' }}>
                  <Target size={14} /> Investigation Objectives
                </div>
                <div style={{ fontSize: '0.8125rem', color: '#cbd5e1', lineHeight: 1.5, whiteSpace: 'pre-line' }}>
                  {selectedLab.objectives}
                </div>
              </div>

              {/* Hints Accordion */}
              {selectedLab.hints && (
                <div style={{ marginTop: '1rem' }}>
                  <button
                    className="siem-btn-secondary"
                    style={{ padding: '0.3rem 0.6rem', fontSize: '0.75rem' }}
                    onClick={() => setShowHints(!showHints)}
                  >
                    <Lightbulb size={12} /> {showHints ? 'Hide Hints' : 'Show Analyst Hints'}
                  </button>

                  {showHints && (
                    <div style={{ marginTop: '0.5rem', background: '#1c1917', border: '1px solid #44403c', borderRadius: '0.375rem', padding: '0.75rem', fontSize: '0.8125rem', color: '#fde047' }}>
                      {selectedLab.hints}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Student Findings & Submission Form */}
            <div className="siem-kpi-card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', color: '#f8fafc', margin: '0 0 1rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Award size={18} color="#10b981" />
                Submit Findings & Validate
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ fontSize: '0.8125rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>
                    Identified Malicious / Suspicious Observable (IP, Hostname, or User Account):
                  </label>
                  <input
                    type="text"
                    className="siem-input-main"
                    style={{ width: '100%' }}
                    placeholder="e.g. 198.51.100.45 or bad_actor"
                    value={identifiedEntity}
                    onChange={(e) => setIdentifiedEntity(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8125rem', color: '#94a3b8', display: 'block', marginBottom: '0.25rem' }}>
                    Analyst Findings & Evidence Summary:
                  </label>
                  <textarea
                    className="siem-input-main"
                    style={{ width: '100%', height: '90px', resize: 'vertical' }}
                    placeholder="Summarize your query results, observed volume, and reason for identifying the observable..."
                    value={findingsNotes}
                    onChange={(e) => setFindingsNotes(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                  <button
                    className="siem-btn-primary"
                    onClick={handleValidate}
                    disabled={validating}
                  >
                    {validating ? 'Verifying Telemetry...' : 'Validate My Findings'}
                  </button>
                </div>
              </div>

              {/* Validation Result Box */}
              {validationResult && (
                <div
                  style={{
                    marginTop: '1.25rem',
                    background: validationResult.success ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${validationResult.success ? '#10b981' : '#ef4444'}`,
                    borderRadius: '0.5rem',
                    padding: '1.25rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      {validationResult.success ? (
                        <CheckCircle size={20} color="#10b981" />
                      ) : (
                        <XCircle size={20} color="#ef4444" />
                      )}
                      <span style={{ fontWeight: 700, color: validationResult.success ? '#34d399' : '#f87171' }}>
                        {validationResult.success ? 'Lab Validation Passed!' : 'Lab Validation Incomplete'}
                      </span>
                    </div>

                    <span className="sev-badge" style={{ fontSize: '0.875rem', background: '#0f172a' }}>
                      Score: {validationResult.score}/100
                    </span>
                  </div>

                  <p style={{ fontSize: '0.875rem', color: '#e2e8f0', margin: '0 0 0.75rem 0', lineHeight: 1.5 }}>
                    {validationResult.feedback}
                  </p>

                  <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '0.75rem' }}>
                    {Object.entries(validationResult.criteria).map(([crit, passed]) => (
                      <div key={crit} style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem', color: passed ? '#34d399' : '#94a3b8' }}>
                        {passed ? '✓' : '✗'} <span style={{ textTransform: 'capitalize' }}>{crit.replace('_', ' ')}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '4rem', color: '#64748b' }}>
            Select a scenario to begin investigation.
          </div>
        )}
      </div>
    </div>
  )
}
