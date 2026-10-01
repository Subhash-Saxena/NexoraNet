import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Compass, Filter, Play, Clock, Target } from 'lucide-react';
import { socScenarioApi } from '../../services/socScenarioApi';
import type {
  ScenarioCategory,
  ScenarioDifficulty,
  ScenarioMetrics,
  SocScenarioSummary,
} from '../../types/socScenario';
import '../../components/soc_scenarios/socScenarios.css';

export const SocScenariosPage: React.FC = () => {
  const navigate = useNavigate();
  const [scenarios, setScenarios] = useState<SocScenarioSummary[]>([]);
  const [metrics, setMetrics] = useState<ScenarioMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [startingScenarioId, setStartingScenarioId] = useState<number | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [scenRes, metRes] = await Promise.all([
        socScenarioApi.getScenarios({
          difficulty: selectedDifficulty !== 'ALL' ? (selectedDifficulty as ScenarioDifficulty) : undefined,
          category: selectedCategory !== 'ALL' ? (selectedCategory as ScenarioCategory) : undefined,
        }),
        socScenarioApi.getScenarioMetrics(),
      ]);
      setScenarios(scenRes);
      setMetrics(metRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenarios');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedDifficulty, selectedCategory]);

  const handleStartScenario = async (scenario: SocScenarioSummary) => {
    setStartingScenarioId(scenario.id);
    try {
      const attempt = await socScenarioApi.startAttempt(scenario.id);
      navigate(`/soc/scenarios/workspace/${attempt.attempt_id}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to start scenario attempt');
    } finally {
      setStartingScenarioId(null);
    }
  };

  const filteredScenarios = scenarios.filter((sc) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      sc.title.toLowerCase().includes(q) ||
      sc.scenario_id.toLowerCase().includes(q) ||
      sc.description.toLowerCase().includes(q)
    );
  });

  return (
    <div className="scen-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <Compass size={20} color="#06b6d4" />
          <span>
            <strong>Advanced SOC Scenario Engine:</strong> Multi-stage guided investigations covering realistic incident handling, triage, MITRE mapping, and response decision-making.
          </span>
        </div>
        <span className="soar-safety-badge">Offline Simulation</span>
      </div>

      {/* Header */}
      <div className="scen-header">
        <div>
          <h1 className="scen-title">
            <Target size={28} color="#06b6d4" /> Advanced SOC Investigation Scenarios
          </h1>
          <p className="scen-subtitle">
            Master real-world SOC workflows across 28 synthetic scenarios spanning Beginner to Expert tier attacks.
          </p>
        </div>
        <div>
          <Link to="/soc" className="soar-btn">
            &larr; Back to SOC Center
          </Link>
        </div>
      </div>

      {/* KPI Overview Metrics */}
      <div className="soar-metrics-grid">
        <div className="soar-metric-card">
          <div className="soar-metric-label">Total Scenarios</div>
          <div className="soar-metric-value">{metrics ? metrics.total_scenarios : 28}</div>
          <div className="soar-metric-subtext">Across 4 difficulty tiers</div>
        </div>
        <div className="soar-metric-card">
          <div className="soar-metric-label">Investigation Attempts</div>
          <div className="soar-metric-value">{metrics ? metrics.total_attempts : 0}</div>
          <div className="soar-metric-subtext">{metrics ? `${metrics.completed_attempts} completed` : '0 completed'}</div>
        </div>
        <div className="soar-metric-card">
          <div className="soar-metric-label">Average Score</div>
          <div className="soar-metric-value" style={{ color: '#34d399' }}>
            {metrics ? `${metrics.avg_score}%` : '--'}
          </div>
          <div className="soar-metric-subtext">Transparent 7-factor rubric</div>
        </div>
        <div className="soar-metric-card">
          <div className="soar-metric-label">Scenarios Mastered</div>
          <div className="soar-metric-value" style={{ color: '#38bdf8' }}>
            {metrics ? metrics.user_completed : 0}
          </div>
          <div className="soar-metric-subtext">Completed by student</div>
        </div>
      </div>

      {/* Filters Bar */}
      <div className="scen-filter-bar">
        <div style={{ flex: '1 1 280px' }}>
          <input
            type="text"
            className="scen-input"
            style={{ width: '100%' }}
            placeholder="Search scenarios by title, attack ID, or concept..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 6 }}>
            <Filter size={16} /> Difficulty:
          </span>
          <select
            className="scen-input"
            value={selectedDifficulty}
            onChange={(e) => setSelectedDifficulty(e.target.value)}
          >
            <option value="ALL">All Difficulties</option>
            <option value="BEGINNER">Beginner (5)</option>
            <option value="INTERMEDIATE">Intermediate (8)</option>
            <option value="ADVANCED">Advanced (10)</option>
            <option value="EXPERT">Expert (5)</option>
          </select>

          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Category:</span>
          <select
            className="scen-input"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="ALL">All Categories</option>
            <option value="MALWARE_INFECTION">Malware Infection</option>
            <option value="RANSOMWARE_OUTBREAK">Ransomware Outbreak</option>
            <option value="CREDENTIAL_ACCESS">Credential Access</option>
            <option value="LATERAL_MOVEMENT">Lateral Movement</option>
            <option value="DATA_EXFILTRATION">Data Exfiltration</option>
            <option value="WEB_COMPROMISE">Web Compromise</option>
            <option value="SUPPLY_CHAIN">Supply Chain</option>
            <option value="INSIDER_THREAT">Insider Threat</option>
            <option value="APT_CAMPAIGN">APT Campaign</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ padding: 14, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5', marginBottom: 20 }}>
          {error}
        </div>
      )}

      {/* Scenario Grid */}
      {loading ? (
        <div style={{ padding: 60, textAlign: 'center', color: '#94a3b8' }}>Loading SOC scenarios...</div>
      ) : filteredScenarios.length === 0 ? (
        <div style={{ padding: 60, textAlign: 'center', color: '#64748b' }}>
          No scenarios found matching your filters.
        </div>
      ) : (
        <div className="soar-playbook-grid">
          {filteredScenarios.map((sc) => (
            <div key={sc.id} className="soar-playbook-card">
              <div>
                <div className="soar-playbook-card-header">
                  <span style={{ fontFamily: 'monospace', color: '#06b6d4', fontWeight: 700, fontSize: '0.85rem' }}>
                    {sc.scenario_id}
                  </span>
                  <div style={{ display: 'flex', gap: 6 }}>
                    <span className={`scen-diff-badge ${sc.difficulty}`}>{sc.difficulty}</span>
                  </div>
                </div>

                <h3 className="soar-playbook-card-title">{sc.title}</h3>
                <p className="soar-playbook-card-desc">{sc.description}</p>
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
                  alignItems: 'center'
                }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Clock size={14} /> ~{sc.estimated_duration_minutes} mins
                  </span>
                  <span style={{ color: '#cbd5e1' }}>{sc.category.replace(/_/g, ' ')}</span>
                </div>

                <button
                  className="soar-btn soar-btn-primary"
                  style={{ width: '100%', justifyContent: 'center' }}
                  onClick={() => handleStartScenario(sc)}
                  disabled={startingScenarioId === sc.id}
                >
                  <Play size={16} />
                  {startingScenarioId === sc.id ? 'Initializing Workspace...' : 'Start Investigation'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
