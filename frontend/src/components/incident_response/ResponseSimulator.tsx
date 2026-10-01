import React, { useState } from 'react'
import type { ResponseAction } from '../../types/incidentResponse'

interface ResponseSimulatorProps {
  actions: ResponseAction[]
  onProposeAction: (data: {
    category: string
    action_type: string
    target_type: string
    target_identifier: string
    reason: string
    risk_assessment?: string
    expected_impact?: string
  }) => Promise<void>
  onExecuteAction: (actionId: string | number) => Promise<void>
  onRevertAction: (actionId: string | number) => Promise<void>
}

export const ResponseSimulator: React.FC<ResponseSimulatorProps> = ({
  actions,
  onProposeAction,
  onExecuteAction,
  onRevertAction,
}) => {
  const [showProposeModal, setShowProposeModal] = useState(false)
  const [loadingActionId, setLoadingActionId] = useState<string | null>(null)

  // Form states
  const [category, setCategory] = useState('CONTAINMENT')
  const [actionType, setActionType] = useState('SIMULATE_HOST_ISOLATION')
  const [targetType, setTargetType] = useState('HOST')
  const [targetIdentifier, setTargetIdentifier] = useState('')
  const [reason, setReason] = useState('')
  const [riskAssessment, setRiskAssessment] = useState('')
  const [expectedImpact, setExpectedImpact] = useState('')

  const handleExecute = async (action: ResponseAction) => {
    setLoadingActionId(action.action_id)
    try {
      await onExecuteAction(action.id)
    } finally {
      setLoadingActionId(null)
    }
  }

  const handleRevert = async (action: ResponseAction) => {
    setLoadingActionId(action.action_id)
    try {
      await onRevertAction(action.id)
    } finally {
      setLoadingActionId(null)
    }
  }

  const handlePropose = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!targetIdentifier.trim() || !reason.trim()) return
    await onProposeAction({
      category,
      action_type: actionType,
      target_type: targetType,
      target_identifier: targetIdentifier,
      reason,
      risk_assessment: riskAssessment || undefined,
      expected_impact: expectedImpact || undefined,
    })
    setShowProposeModal(false)
    setTargetIdentifier('')
    setReason('')
    setRiskAssessment('')
    setExpectedImpact('')
  }

  return (
    <div>
      {/* Strict Educational Safety Banner */}
      <div className="ir-safety-banner">
        <div>
          <span className="shield-icon">🛡️</span>
          <strong>NexoraNet Incident Response Lab — Synthetic Training Environment</strong>
          <div style={{ fontSize: '0.78rem', color: '#67e8f9', marginTop: '3px' }}>
            All response actions are executed strictly within the educational simulator. Zero commands are run on live systems. Zero accounts or firewalls are modified.
          </div>
        </div>
        <span className="ir-safety-badge">Simulation Mode Only</span>
      </div>

      {/* Action Header */}
      <div className="ir-filter-bar">
        <div style={{ fontSize: '0.9rem', color: '#9ca3af' }}>
          Evaluate operational impact and safely test containment, eradication, and recovery strategies.
        </div>
        <div style={{ marginLeft: 'auto' }}>
          <button className="ir-btn-primary" onClick={() => setShowProposeModal(true)}>
            + Propose Response Action
          </button>
        </div>
      </div>

      {/* Actions Table */}
      <div className="ir-table-wrapper">
        <table className="ir-table">
          <thead>
            <tr>
              <th>Action ID</th>
              <th>Category</th>
              <th>Simulated Action Type</th>
              <th>Target</th>
              <th>Status</th>
              <th>Simulated Outcome</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {actions.map((act) => {
              const isLoading = loadingActionId === act.action_id

              return (
                <tr key={act.id}>
                  <td>
                    <span className="ir-table-id">{act.action_id}</span>
                  </td>
                  <td>
                    <span
                      className={`ir-pill ${
                        act.category === 'CONTAINMENT'
                          ? 'badge-crit'
                          : act.category === 'ERADICATION'
                          ? 'badge-high'
                          : 'badge-emerald'
                      }`}
                    >
                      {act.category}
                    </span>
                  </td>
                  <td>
                    <code style={{ color: '#38bdf8', fontSize: '0.8rem' }}>{act.action_type}</code>
                  </td>
                  <td>
                    <strong>{act.target_identifier}</strong>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>({act.target_type})</div>
                  </td>
                  <td>
                    <span
                      className={`ir-pill ${
                        act.status === 'EXECUTED'
                          ? 'badge-emerald'
                          : act.status === 'REVERTED'
                          ? 'badge-low'
                          : 'badge-med'
                      }`}
                    >
                      {act.status}
                    </span>
                  </td>
                  <td style={{ maxWidth: '300px' }}>
                    <div style={{ fontSize: '0.8rem', color: '#cbd5e1', lineHeight: '1.4' }}>
                      {act.simulated_outcome || act.reason}
                    </div>
                    {act.executed_at && (
                      <div style={{ fontSize: '0.72rem', color: '#06b6d4', marginTop: '4px' }}>
                        Executed: {new Date(act.executed_at).toLocaleTimeString()}
                      </div>
                    )}
                  </td>
                  <td>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {act.status === 'PROPOSED' && (
                        <button
                          className="ir-btn-primary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem' }}
                          onClick={() => handleExecute(act)}
                          disabled={isLoading}
                        >
                          {isLoading ? 'Simulating...' : '▶ Simulate Action'}
                        </button>
                      )}

                      {act.status === 'EXECUTED' && (
                        <button
                          className="ir-btn-secondary"
                          style={{ padding: '4px 10px', fontSize: '0.75rem', borderColor: '#f97316', color: '#f97316' }}
                          onClick={() => handleRevert(act)}
                          disabled={isLoading}
                        >
                          {isLoading ? 'Reverting...' : '↩ Revert'}
                        </button>
                      )}

                      {act.status === 'REVERTED' && (
                        <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Reverted in Sim</span>
                      )}
                    </div>
                  </td>
                </tr>
              )
            })}

            {actions.length === 0 && (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '32px', color: '#6b7280' }}>
                  No defensive actions formulated yet. Click "Propose Response Action" to simulate containment or eradication.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Propose Action Modal */}
      {showProposeModal && (
        <div className="ir-modal-backdrop" onClick={() => setShowProposeModal(false)}>
          <div className="ir-modal-box" onClick={(e) => e.stopPropagation()}>
            <div className="ir-modal-header">
              <h3>Formulate Response Simulation Action</h3>
              <button className="ir-modal-close" onClick={() => setShowProposeModal(false)}>
                &times;
              </button>
            </div>

            <form onSubmit={handlePropose}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Category</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  >
                    <option value="CONTAINMENT">Containment</option>
                    <option value="ERADICATION">Eradication</option>
                    <option value="RECOVERY">Recovery</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Simulated Action Type</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={actionType}
                    onChange={(e) => setActionType(e.target.value)}
                  >
                    <optgroup label="Containment">
                      <option value="SIMULATE_HOST_ISOLATION">Simulate Host Isolation (VLAN Quarantine)</option>
                      <option value="SIMULATE_ACCOUNT_RESTRICTION">Simulate Account Restriction / Lockout</option>
                      <option value="SIMULATE_NETWORK_BLOCK">Simulate Perimeter IP Block</option>
                      <option value="SIMULATE_IOC_BLOCK">Simulate IOC Sinkhole / Proxy Block</option>
                      <option value="SIMULATE_SESSION_REVOCATION">Simulate VPN Session Revocation</option>
                    </optgroup>
                    <optgroup label="Eradication">
                      <option value="SIMULATE_REMOVE_INDICATOR">Simulate EDR Malicious File Quarantine</option>
                      <option value="SIMULATE_REMOVE_PERSISTENCE">Simulate Scheduled Task / Run Key Cleanup</option>
                      <option value="SIMULATE_RESET_CREDENTIAL">Simulate Forced Password Reset</option>
                      <option value="SIMULATE_CLEAN_HOST">Simulate Endpoint Memory Scrubbing</option>
                    </optgroup>
                    <optgroup label="Recovery">
                      <option value="SIMULATE_RESTORE_HOST">Simulate Restoring Host to Production VLAN</option>
                      <option value="SIMULATE_RESTORE_SERVICE">Simulate Restarting Application Service</option>
                      <option value="SIMULATE_REENABLE_ACCOUNT">Simulate Re-enabling Account</option>
                    </optgroup>
                  </select>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '12px', marginBottom: '12px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Target Type</label>
                  <select
                    className="ir-select"
                    style={{ width: '100%' }}
                    value={targetType}
                    onChange={(e) => setTargetType(e.target.value)}
                  >
                    <option value="HOST">Host / Machine</option>
                    <option value="USER">User Account</option>
                    <option value="IP">IP Address</option>
                    <option value="DOMAIN">Domain Name</option>
                    <option value="PROCESS">Process / Binary</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Target Identifier</label>
                  <input
                    type="text"
                    className="ir-search-input"
                    style={{ width: '100%' }}
                    placeholder="e.g. FIN-SRV-01 (10.0.4.15) or svc_backup"
                    value={targetIdentifier}
                    onChange={(e) => setTargetIdentifier(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div style={{ marginBottom: '12px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Analytical Justification / Reason</label>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '60px' }}
                  placeholder="Why is this defensive action required based on collected evidence?"
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  required
                />
              </div>

              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', marginBottom: '4px' }}>Operational Risk & Side Effect Assessment</label>
                <textarea
                  className="ir-search-input"
                  style={{ width: '100%', height: '50px' }}
                  placeholder="What business process might be impacted? (e.g. Finance batch processing delayed)"
                  value={riskAssessment}
                  onChange={(e) => setRiskAssessment(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button type="button" className="ir-btn-secondary" onClick={() => setShowProposeModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="ir-btn-primary">
                  Propose Simulated Action
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
