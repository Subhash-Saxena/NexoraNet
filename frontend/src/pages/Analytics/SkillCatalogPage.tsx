import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Award,
  Compass,
  FileText,
  Search,
  Shield,
  Zap,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { SkillAssessment, SkillConfidence } from '../../types/analytics';
import '../../components/analytics/analytics.css';

const CATEGORIES = [
  'ALL',
  'NETWORKING',
  'PACKET_ANALYSIS',
  'SOC_ANALYSIS',
  'THREAT_INTEL',
  'THREAT_HUNTING',
  'SIEM_LOGS',
  'ENDPOINT_SECURITY',
  'INCIDENT_RESPONSE',
  'DETECTION_AUTOMATION',
];

export const SkillCatalogPage: React.FC = () => {
  const navigate = useNavigate();
  const [skills, setSkills] = useState<SkillAssessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCategory, setActiveCategory] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSkill, setSelectedSkill] = useState<SkillAssessment | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchSkills = async () => {
      try {
        setLoading(true);
        const data = await analyticsApi.getSkills(activeCategory === 'ALL' ? undefined : activeCategory);
        if (mounted) {
          setSkills(data);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to load skills:', err);
        if (mounted) setLoading(false);
      }
    };
    fetchSkills();
    return () => {
      mounted = false;
    };
  }, [activeCategory]);

  const filteredSkills = skills.filter((s) => {
    const q = searchQuery.toLowerCase();
    return (
      s.name.toLowerCase().includes(q) ||
      s.skill_code.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q)
    );
  });

  const getConfidenceBadgeClass = (conf: SkillConfidence) => {
    switch (conf) {
      case 'HIGH':
        return 'confidence-badge high';
      case 'MEDIUM':
        return 'confidence-badge medium';
      default:
        return 'confidence-badge low';
    }
  };

  const highCount = skills.filter((s) => s.confidence === 'HIGH').length;
  const mediumCount = skills.filter((s) => s.confidence === 'MEDIUM').length;
  const lowCount = skills.filter((s) => s.confidence === 'LOW').length;

  return (
    <div className="analytics-container">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <h1>
            <Shield className="text-cyan-400" size={28} />
            <span>Cybersecurity Skill Assessment Matrix</span>
          </h1>
          <p className="analytics-tagline">
            Continuous multi-source evidence evaluation across 28 fundamental cybersecurity proficiencies.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <Link to="/progress/assessment" className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
            <FileText size={16} />
            <span>Formal Assessment Report</span>
          </Link>
          <Link to="/portfolio" className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
            <Award size={16} />
            <span>Showcase Portfolio</span>
          </Link>
        </div>
      </div>

      {/* Educational Banner */}
      <div className="disclaimer-banner">
        <Compass size={18} />
        <div>
          <strong>Educational Assessment Philosophy:</strong> Assessments represent practical learning progress across synthetic simulated environments. Confidence ratings reflect evidence volume and recency rather than permanent abilities.
        </div>
      </div>

      {/* Metrics Row */}
      <div className="analytics-metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Assessed Skills</span>
          <span className="metric-value">{skills.length}</span>
          <span className="metric-subtext">Across 8 Core Domains</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">High Confidence</span>
          <span className="metric-value" style={{ color: '#34d399' }}>{highCount}</span>
          <span className="metric-subtext">Extensive Practical Evidence</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Moderate Evidence</span>
          <span className="metric-value" style={{ color: '#fbbf24' }}>{mediumCount}</span>
          <span className="metric-subtext">Developing Practice History</span>
        </div>
        <div className="metric-card">
          <span className="metric-label">Initial Assessment</span>
          <span className="metric-value" style={{ color: '#9ca3af' }}>{lowCount}</span>
          <span className="metric-subtext">Recommended For Practice</span>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="filter-tabs">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={`tab-btn ${activeCategory === cat ? 'active' : ''}`}
              onClick={() => setActiveCategory(cat)}
            >
              {(cat || '').replace(/_/g, ' ')}
            </button>
          ))}
        </div>

        <div style={{ position: 'relative', minWidth: '260px' }}>
          <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#6b7280' }} />
          <input
            type="text"
            placeholder="Search skills..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '0.5rem 0.75rem 0.5rem 2rem',
              background: '#111827',
              border: '1px solid #1f2937',
              borderRadius: '0.375rem',
              color: '#f9fafb',
              fontSize: '0.875rem',
            }}
          />
        </div>
      </div>

      {/* Skills Grid */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
          Loading skill evidence telemetry...
        </div>
      ) : filteredSkills.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af', background: '#111827', borderRadius: '0.75rem' }}>
          No skills matched the current filter.
        </div>
      ) : (
        <div className="skills-grid">
          {filteredSkills.map((skill) => (
            <div
              key={skill.skill_id}
              className="skill-card"
              onClick={() => setSelectedSkill(skill)}
              style={{ cursor: 'pointer' }}
            >
              <div className="skill-card-header">
                <div>
                  <h3 className="skill-card-title">{skill.name}</h3>
                  <span style={{ fontSize: '0.75rem', color: '#6b7280', fontFamily: 'monospace' }}>
                    {skill.skill_code}
                  </span>
                </div>
                <span className={getConfidenceBadgeClass(skill.confidence)}>
                  {skill.confidence} CONFIDENCE
                </span>
              </div>

              <span className="skill-category-badge" style={{ alignSelf: 'flex-start' }}>
                {(skill.category || '').replace(/_/g, ' ')}
              </span>

              {skill.description && (
                <p style={{ fontSize: '0.85rem', color: '#9ca3af', margin: '0.25rem 0' }}>
                  {skill.description}
                </p>
              )}

              {/* Progress and Accuracy */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#9ca3af', marginBottom: '4px' }}>
                  <span>Demonstrated Accuracy</span>
                  <span style={{ fontWeight: 600, color: '#f3f4f6' }}>{skill.accuracy.toFixed(1)}%</span>
                </div>
                <div className="progress-bar-container">
                  <div
                    className="progress-bar-fill"
                    style={{
                      width: `${Math.min(100, Math.max(0, skill.accuracy))}%`,
                      backgroundColor: skill.accuracy >= 75 ? '#34d399' : skill.accuracy >= 50 ? '#38bdf8' : '#6b7280',
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#6b7280' }}>
                <span>Evidence: {skill.evidence_count} sessions</span>
                <span>Recency: {skill.recent_performance.toFixed(0)}%</span>
              </div>

              {skill.recommended_next_step && (
                <div style={{ fontSize: '0.8rem', color: '#93c5fd', background: 'rgba(59, 130, 246, 0.08)', padding: '0.4rem 0.6rem', borderRadius: '0.375rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                  <Zap size={14} className="text-yellow-400" />
                  <span>Next: {skill.recommended_next_step}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal / Drawer */}
      {selectedSkill && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 999,
            padding: '1rem',
          }}
          onClick={() => setSelectedSkill(null)}
        >
          <div
            style={{
              background: '#111827',
              border: '1px solid #374151',
              borderRadius: '0.75rem',
              maxWidth: '600px',
              width: '100%',
              padding: '2rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '1.25rem',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f9fafb', margin: 0 }}>
                  {selectedSkill.name}
                </h2>
                <span style={{ fontSize: '0.8rem', color: '#6b7280', fontFamily: 'monospace' }}>
                  {selectedSkill.skill_code}
                </span>
              </div>
              <button
                className="btn-secondary"
                onClick={() => setSelectedSkill(null)}
                style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
              >
                Close
              </button>
            </div>

            <div className="disclaimer-banner">
              <strong>Assessment Rationale:</strong> {selectedSkill.confidence_rationale}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem' }}>
              <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Recent (50%)</span>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, margin: '4px 0 0 0', color: '#38bdf8' }}>
                  {selectedSkill.recent_performance.toFixed(1)}%
                </p>
              </div>
              <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Historical (30%)</span>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, margin: '4px 0 0 0', color: '#fbbf24' }}>
                  {selectedSkill.historical_performance.toFixed(1)}%
                </p>
              </div>
              <div style={{ background: '#1f2937', padding: '0.75rem', borderRadius: '0.5rem', textAlign: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>Practical (20%)</span>
                <p style={{ fontSize: '1.2rem', fontWeight: 700, margin: '4px 0 0 0', color: '#34d399' }}>
                  {selectedSkill.practical_performance.toFixed(1)}%
                </p>
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.95rem', color: '#e5e7eb', marginBottom: '0.5rem' }}>Next Recommended Action</h4>
              <p style={{ fontSize: '0.85rem', color: '#9ca3af', background: '#1f2937', padding: '0.75rem', borderRadius: '0.375rem' }}>
                {selectedSkill.recommended_next_step || 'Continue varied practice across labs and mock exams.'}
              </p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                className="btn-primary"
                onClick={() => {
                  setSelectedSkill(null);
                  navigate('/challenges');
                }}
              >
                Practice in Challenges
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
