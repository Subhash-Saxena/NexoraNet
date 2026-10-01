import React, { useEffect, useState } from 'react';
import {
  Award,
  CheckCircle2,
  Compass,
  FileCheck,
  FileText,
  Printer,
  RefreshCw,
  Shield,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { AssessmentReport } from '../../types/analytics';
import '../../components/analytics/analytics.css';

export const AssessmentReportPage: React.FC = () => {
  const [report, setReport] = useState<AssessmentReport | null>(null);
  const [_history, setHistory] = useState<AssessmentReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const fetchReports = async () => {
    try {
      setLoading(true);
      const pastReports = await analyticsApi.getReportHistory();
      setHistory(pastReports);
      if (pastReports.length > 0) {
        setReport(pastReports[0]);
      } else {
        // Generate initial report
        const newReport = await analyticsApi.generateAssessmentReport();
        setReport(newReport);
        setHistory([newReport]);
      }
      setLoading(false);
    } catch (err) {
      console.error('Failed to load report:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerateNew = async () => {
    try {
      setGenerating(true);
      const newReport = await analyticsApi.generateAssessmentReport();
      setReport(newReport);
      setHistory((prev) => [newReport, ...prev]);
      setGenerating(false);
    } catch (err) {
      console.error('Failed to generate report:', err);
      setGenerating(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="analytics-container">
      {/* Top Action Bar */}
      <div className="analytics-header">
        <div>
          <h1>
            <FileCheck className="text-cyan-400" size={28} />
            <span>Formal Assessment & Verification Report</span>
          </h1>
          <p className="analytics-tagline">
            Multi-modal evaluation synthesis of conceptual understanding and practical cyber defense execution.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            className="btn-secondary"
            onClick={handleGenerateNew}
            disabled={generating}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <RefreshCw size={16} className={generating ? 'animate-spin' : ''} />
            <span>{generating ? 'Re-evaluating...' : 'Generate Fresh Report'}</span>
          </button>
          <button
            className="btn-primary"
            onClick={handlePrint}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <Printer size={16} />
            <span>Print / Save PDF</span>
          </button>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
          Compiling student assessment telemetry...
        </div>
      ) : !report ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af', background: '#111827', borderRadius: '0.75rem' }}>
          No assessment reports available. Click Generate Fresh Report to build one.
        </div>
      ) : (
        <div className="report-paper">
          {/* Official Document Banner */}
          <div className="report-header-banner">
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#38bdf8', fontWeight: 700, fontSize: '0.9rem', letterSpacing: '0.05em' }}>
                <Shield size={18} />
                <span>NEXORANET CYBERSECURITY EDUCATION PLATFORM</span>
              </div>
              <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc', margin: '0.5rem 0 0.25rem 0' }}>
                Comprehensive Student Progress Assessment
              </h2>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                Issued to: <strong style={{ color: '#e2e8f0' }}>{report.student_name}</strong> | Report ID: <span style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{report.report_code}</span>
              </div>
            </div>

            <div style={{ textAlign: 'right', fontSize: '0.8rem', color: '#64748b' }}>
              <div>Generated: {new Date(report.generated_at).toLocaleDateString()}</div>
              <div>Verification Status: <span style={{ color: '#34d399', fontWeight: 600 }}>SYSTEM VERIFIED</span></div>
            </div>
          </div>

          {/* Mandatory Educational Disclaimer */}
          <div className="disclaimer-banner">
            <Compass size={18} />
            <div>
              <strong>Educational Disclaimer:</strong> {report.disclaimer}
            </div>
          </div>

          {/* Executive Summary */}
          <div className="report-section">
            <h3>Executive Summary</h3>
            <p style={{ fontSize: '0.95rem', lineHeight: '1.6', color: '#cbd5e1', margin: 0 }}>
              {report.executive_summary}
            </p>
          </div>

          {/* Evidence Synthesis */}
          <div className="report-section">
            <h3>Evidence Breakdown</h3>
            <div className="evidence-grid">
              <div className="evidence-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#60a5fa', fontWeight: 600, fontSize: '0.9rem' }}>
                  <FileText size={16} />
                  <span>Knowledge Assessment Evidence</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.5rem' }}>
                  <div>Completed Lessons: <strong style={{ color: '#f1f5f9' }}>{String(report.knowledge_evidence?.lessons_completed ?? 0)}</strong></div>
                  <div>Exam Attempts: <strong style={{ color: '#f1f5f9' }}>{String(report.knowledge_evidence?.tests_attempted ?? 0)}</strong></div>
                  <div>Average Exam Accuracy: <strong style={{ color: '#f1f5f9' }}>{String(report.knowledge_evidence?.average_test_score ?? 0)}%</strong></div>
                </div>
              </div>

              <div className="evidence-card">
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#34d399', fontWeight: 600, fontSize: '0.9rem' }}>
                  <Award size={16} />
                  <span>Practical Simulation Evidence</span>
                </div>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8', display: 'flex', flexDirection: 'column', gap: '0.25rem', marginTop: '0.5rem' }}>
                  <div>Hands-on Labs Completed: <strong style={{ color: '#f1f5f9' }}>{String(report.practical_evidence?.labs_completed ?? 0)}</strong></div>
                  <div>SOC Scenarios Solved: <strong style={{ color: '#f1f5f9' }}>{String(report.practical_evidence?.soc_scenarios_completed ?? 0)}</strong></div>
                  <div>CTF Challenges Solved: <strong style={{ color: '#f1f5f9' }}>{String(report.practical_evidence?.challenges_solved ?? 0)}</strong></div>
                </div>
              </div>
            </div>
          </div>

          {/* Skills Proficiency Matrix Summary */}
          <div className="report-section">
            <h3>Demonstrated Core Proficiencies</h3>
            <div style={{ overflowX: 'auto' }}>
              <table className="admin-table">
                <thead>
                  <tr>
                    <th>Domain</th>
                    <th>Skill Code</th>
                    <th>Proficiency Name</th>
                    <th>Accuracy</th>
                    <th>Evidence Confidence</th>
                  </tr>
                </thead>
                <tbody>
                  {report.skills_summary.slice(0, 8).map((sk) => (
                    <tr key={sk.code}>
                      <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{sk.category.replace('_', ' ')}</td>
                      <td style={{ fontFamily: 'monospace', color: '#38bdf8' }}>{sk.code}</td>
                      <td style={{ fontWeight: 600 }}>{sk.name}</td>
                      <td>{sk.accuracy.toFixed(1)}%</td>
                      <td>
                        <span className={`confidence-badge ${sk.confidence.toLowerCase()}`}>
                          {sk.confidence}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Qualitative Insights: Strengths & Growth */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
            <div className="report-section">
              <h3 style={{ color: '#34d399' }}>Demonstrated Strengths</h3>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {report.strengths.map((s, idx) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            </div>

            <div className="report-section">
              <h3 style={{ color: '#fbbf24' }}>Recommended Practice Areas</h3>
              <ul style={{ margin: 0, paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.9rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {report.growth_areas.map((g, idx) => (
                  <li key={idx}>{g}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* Recommended Next Actions */}
          <div className="report-section">
            <h3>Pedagogical Recommendations</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {report.recommendations.map((rec, idx) => (
                <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: '#1e293b', padding: '0.75rem 1rem', borderRadius: '0.375rem', fontSize: '0.9rem', color: '#e2e8f0' }}>
                  <CheckCircle2 size={16} className="text-cyan-400" />
                  <span>{rec}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Signature / Verification Footer */}
          <div style={{ borderTop: '1px solid #334155', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#64748b' }}>
            <div>
              Generated deterministically by NexoraNet Educational Assessment Engine Step 20.
            </div>
            <div>
              Verification Hash: <span style={{ fontFamily: 'monospace' }}>SHA256-{report.report_code}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
