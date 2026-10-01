import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, Filter, Sparkles, Zap } from 'lucide-react';
import { soarApi } from '../../services/soarApi';
import type { AutomationPlaybook, PlaybookRiskLevel, PlaybookStatus } from '../../types/soar';
import '../../components/soar/soar.css';

export const SoarPlaybooksPage: React.FC = () => {
  const navigate = useNavigate();
  const [playbooks, setPlaybooks] = useState<AutomationPlaybook[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedRisk, setSelectedRisk] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const loadPlaybooks = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await soarApi.getPlaybooks({
        category: selectedCategory !== 'ALL' ? selectedCategory : undefined,
        risk_level: selectedRisk !== 'ALL' ? (selectedRisk as PlaybookRiskLevel) : undefined,
      });
      setPlaybooks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load playbooks');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlaybooks();
  }, [selectedCategory, selectedRisk]);

  const handleToggleStatus = async (playbook: AutomationPlaybook, e: React.MouseEvent) => {
    e.stopPropagation();
    const newStatus: PlaybookStatus = playbook.status === 'ENABLED' ? 'DISABLED' : 'ENABLED';
    try {
      await soarApi.updatePlaybookStatus(playbook.id, newStatus);
      setPlaybooks((prev) =>
        prev.map((p) => (p.id === playbook.id ? { ...p, status: newStatus } : p))
      );
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update status');
    }
  };

  const filteredPlaybooks = playbooks.filter((p) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      p.name.toLowerCase().includes(query) ||
      p.playbook_id.toLowerCase().includes(query) ||
      p.description.toLowerCase().includes(query)
    );
  });

  return (
    <div className="soar-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Zap size={20} color="#06b6d4" />
          <span>
            <strong>Educational Playbook Catalog:</strong> Automated incident workflows designed for SOC training with step conditions and analyst approval controls.
          </span>
        </div>
        <span className="soar-safety-badge">Simulation Mode Only</span>
      </div>

      {/* Header */}
      <div className="soar-header">
        <div>
          <h1 className="soar-title">
            <BookOpen size={28} color="#06b6d4" /> Automation Playbooks Catalog
          </h1>
          <p className="soar-subtitle">
            Pre-built and custom educational security automation playbooks for standard threat scenarios.
          </p>
        </div>
        <div>
          <Link to="/soc/automation" className="soar-btn">
            &larr; Back to SOAR Dashboard
          </Link>
        </div>
      </div>

      {/* Nav Tabs */}
      <div className="soar-nav-tabs">
        <Link to="/soc/automation" className="soar-tab-btn">
          Overview Dashboard
        </Link>
        <Link to="/soc/automation/playbooks" className="soar-tab-btn active">
          Playbooks Catalog ({playbooks.length})
        </Link>
        <Link to="/soc/automation/executions" className="soar-tab-btn">
          Execution Logs
        </Link>
      </div>

      {/* Filter Bar */}
      <div style={{
        background: '#111827',
        border: '1px solid #334155',
        borderRadius: 10,
        padding: '16px 20px',
        marginBottom: 24,
        display: 'flex',
        gap: 16,
        alignItems: 'center',
        flexWrap: 'wrap'
      }}>
        <div style={{ flex: '1 1 250px' }}>
          <input
            type="text"
            placeholder="Search playbooks by ID, title, or keywords..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '9px 14px',
              borderRadius: 6,
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#fff',
              fontSize: '0.9rem',
            }}
          />
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Filter size={16} /> Category:
          </span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#fff',
              fontSize: '0.85rem',
            }}
          >
            <option value="ALL">All Categories</option>
            <option value="PHISHING">Phishing</option>
            <option value="MALWARE">Malware</option>
            <option value="RANSOMWARE">Ransomware</option>
            <option value="CREDENTIAL_ACCESS">Credential Access</option>
            <option value="DATA_EXFILTRATION">Data Exfiltration</option>
            <option value="SUSPICIOUS_LOGIN">Suspicious Login</option>
            <option value="LATERAL_MOVEMENT">Lateral Movement</option>
          </select>

          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Risk:</span>
          <select
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 6,
              background: '#1e293b',
              border: '1px solid #334155',
              color: '#fff',
              fontSize: '0.85rem',
            }}
          >
            <option value="ALL">All Risks</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ padding: 14, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5', marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Playbook Cards Grid */}
      {loading ? (
        <div style={{ padding: 48, textAlign: 'center', color: '#94a3b8' }}>Loading playbook catalog...</div>
      ) : filteredPlaybooks.length === 0 ? (
        <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>
          No playbooks matched the current filters.
        </div>
      ) : (
        <div className="soar-playbook-grid">
          {filteredPlaybooks.map((pb) => (
            <div
              key={pb.id}
              className="soar-playbook-card"
              onClick={() => navigate(`/soc/automation/playbooks/${pb.playbook_id}`)}
              style={{ cursor: 'pointer' }}
            >
              <div>
                <div className="soar-playbook-card-header">
                  <span style={{ fontSize: '0.8rem', fontFamily: 'monospace', color: '#06b6d4', fontWeight: 700 }}>
                    {pb.playbook_id}
                  </span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <span className={`soar-badge ${pb.risk_level}`}>{pb.risk_level}</span>
                    <span
                      onClick={(e) => handleToggleStatus(pb, e)}
                      title="Click to toggle Enabled / Disabled"
                      style={{
                        fontSize: '0.75rem',
                        padding: '2px 8px',
                        borderRadius: 4,
                        background: pb.status === 'ENABLED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(100, 116, 139, 0.2)',
                        color: pb.status === 'ENABLED' ? '#34d399' : '#94a3b8',
                        fontWeight: 600,
                        cursor: 'pointer',
                      }}
                    >
                      {pb.status}
                    </span>
                  </div>
                </div>

                <h3 className="soar-playbook-card-title">{pb.name}</h3>
                <p className="soar-playbook-card-desc">{pb.description}</p>
              </div>

              <div>
                <div style={{
                  padding: '10px 12px',
                  background: '#1e293b',
                  borderRadius: 6,
                  fontSize: '0.8rem',
                  color: '#94a3b8',
                  marginBottom: 16,
                  display: 'flex',
                  justifyContent: 'space-between',
                }}>
                  <span>Trigger: <strong>{pb.trigger_type}</strong></span>
                  <span>Steps: <strong>{pb.steps_count ?? pb.steps?.length ?? 4}</strong></span>
                  {pb.requires_approval && (
                    <span style={{ color: '#fbbf24', fontWeight: 600 }}>&bull; Approval Gate</span>
                  )}
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10 }}>
                  <button
                    className="soar-btn"
                    style={{ flex: 1, justifyContent: 'center' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/soc/automation/playbooks/${pb.playbook_id}`);
                    }}
                  >
                    View Steps
                  </button>
                  <button
                    className="soar-btn soar-btn-primary"
                    style={{ flex: 1, justifyContent: 'center' }}
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate(`/soc/automation/playbooks/${pb.playbook_id}?tab=dry-run`);
                    }}
                  >
                    <Sparkles size={14} /> Dry-Run
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
