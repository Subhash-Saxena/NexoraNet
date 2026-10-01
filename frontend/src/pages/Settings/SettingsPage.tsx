import React from 'react'
import { Settings, ShieldCheck, Server, AlertTriangle } from 'lucide-react'
import { useHealthCheck } from '../../hooks/useHealthCheck'
import { StatusDot } from '../../components/common/StatusDot'

export const SettingsPage: React.FC = () => {
  const { status, data, error, lastChecked, checkNow } = useHealthCheck(15000)

  return (
    <div className="placeholder-view">
      <div className="placeholder-badge-row">
        <span className="badge badge-phase">Configuration</span>
        <span className="badge badge-ready">Step 1 Foundation</span>
      </div>

      <div className="placeholder-title">
        <div className="module-icon-wrap">
          <Settings size={24} />
        </div>
        <span>Platform Settings & Security Boundaries</span>
      </div>

      <div style={{ color: 'var(--cyan-primary)', fontWeight: 600, fontSize: '1.05rem', marginBottom: '8px' }}>
        &ldquo;System Defaults, Safe Execution Boundaries, and Service Telemetry&rdquo;
      </div>

      <p className="placeholder-summary">
        NexoraNet is architected with strict defensive security principles from the ground up.
        This panel displays current system boundaries, API connectivity parameters, and safety enforcement rules.
      </p>

      {/* Backend API Connection Diagnostic */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Server size={20} color="var(--cyan-primary)" />
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Backend API Diagnostics (GET /api/health)
            </h3>
          </div>
          <StatusDot status={status} onClick={checkNow} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '12px', fontSize: '0.84rem' }}>
          <div className="practice-card">
            <span style={{ color: 'var(--text-muted)' }}>Connection Status:</span>
            <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '4px' }}>
              {status.toUpperCase()}
            </div>
          </div>
          <div className="practice-card">
            <span style={{ color: 'var(--text-muted)' }}>Service Identity:</span>
            <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '4px' }}>
              {data?.service || 'Connecting...'}
            </div>
          </div>
          <div className="practice-card">
            <span style={{ color: 'var(--text-muted)' }}>Last Health Check:</span>
            <div style={{ fontWeight: 600, color: 'var(--text-main)', marginTop: '4px' }}>
              {lastChecked ? lastChecked.toLocaleTimeString() : 'Pending'}
            </div>
          </div>
        </div>

        {error && (
          <div style={{ marginTop: '14px', color: 'var(--rose-danger)', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <AlertTriangle size={14} />
            <span>Connection diagnostic message: {error}</span>
          </div>
        )}
      </div>

      {/* Lab Safety & Security Guard Rails */}
      <div className="placeholder-section-title">
        Platform Security Guard Rails (Design Guarantee)
      </div>

      <div className="practice-cards-grid">
        <div className="practice-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <ShieldCheck size={18} color="var(--emerald-success)" />
            <h4>Strict Target Isolation</h4>
          </div>
          <p>
            Lab commands and simulated scanners are strictly restricted to <code>localhost (127.0.0.1)</code> and isolated lab virtual subnets (<code>10.99.0.0/16</code>). Unrestricted targeting of public WAN networks is prohibited by architectural design.
          </p>
        </div>

        <div className="practice-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <ShieldCheck size={18} color="var(--emerald-success)" />
            <h4>Safe Subprocess Execution</h4>
          </div>
          <p>
            No dynamic <code>eval()</code>, unsafe command concatenation, or arbitrary shell invocations are permitted anywhere in the NexoraNet codebase.
          </p>
        </div>

        <div className="practice-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <ShieldCheck size={18} color="var(--emerald-success)" />
            <h4>Zero Leaked Stack Traces</h4>
          </div>
          <p>
            All backend exceptions pass through centralized error handlers. In production mode, internal server stack traces are never exposed to API consumers.
          </p>
        </div>

        <div className="practice-card">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <ShieldCheck size={18} color="var(--emerald-success)" />
            <h4>Pydantic Input Validation</h4>
          </div>
          <p>
            Every client payload is strictly validated and sanitized through Pydantic type schemas before processing.
          </p>
        </div>
      </div>
    </div>
  )
}
