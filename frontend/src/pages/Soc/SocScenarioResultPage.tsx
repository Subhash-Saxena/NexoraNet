import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle2, XCircle, ArrowLeft, RotateCcw, BookOpen } from 'lucide-react';
import { socScenarioApi } from '../../services/socScenarioApi';
import type { ScenarioEvaluationResponse } from '../../types/socScenario';
import '../../components/soc_scenarios/socScenarios.css';

export const SocScenarioResultPage: React.FC = () => {
  const { attemptId } = useParams<{ attemptId: string }>();

  const [evaluation, setEvaluation] = useState<ScenarioEvaluationResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!attemptId) return;
    const fetchResults = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await socScenarioApi.submitAttempt(attemptId);
        setEvaluation(res);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load evaluation results');
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [attemptId]);

  if (loading) {
    return (
      <div className="scen-container" style={{ textAlign: 'center', padding: 60, color: '#94a3b8' }}>
        Calculating rubric score breakdown and analyst feedback...
      </div>
    );
  }

  if (error || !evaluation) {
    return (
      <div className="scen-container">
        <div style={{ padding: 20, background: 'rgba(239, 68, 68, 0.1)', border: '1px solid #ef4444', borderRadius: 8, color: '#fca5a5' }}>
          {error || 'Evaluation not available.'}
        </div>
        <div style={{ marginTop: 16 }}>
          <Link to="/soc/scenarios" className="soar-btn">
            &larr; Back to Scenarios Catalog
          </Link>
        </div>
      </div>
    );
  }

  const passed = evaluation.passed;
  const scoreColor = evaluation.score >= 80 ? '#34d399' : evaluation.score >= 60 ? '#fbbf24' : '#f87171';

  return (
    <div className="scen-container">
      {/* Simulation Banner */}
      <div className="soar-safety-banner">
        <span>
          <strong>Scenario Investigation Complete:</strong> Transparent 7-factor educational rubric score and structured post-incident feedback.
        </span>
        <span className="soar-safety-badge">Evaluation Results</span>
      </div>

      {/* Header */}
      <div style={{ marginBottom: 20 }}>
        <Link to="/soc/scenarios" style={{ color: '#06b6d4', textDecoration: 'none', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
          <ArrowLeft size={16} /> Back to Scenarios Catalog
        </Link>
        <h1 className="scen-title">Investigation Evaluation: {evaluation.scenario_title}</h1>
      </div>

      {/* Score Hero */}
      <div className="scen-score-hero">
        <div className="scen-score-circle" style={{ color: scoreColor }}>
          {Math.round(evaluation.score)}%
        </div>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 14px',
          borderRadius: 999,
          background: passed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
          color: passed ? '#34d399' : '#f87171',
          fontWeight: 700,
          fontSize: '0.9rem',
          marginBottom: 10,
        }}>
          {passed ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
          {passed ? 'INVESTIGATION MASTERED' : 'REQUIRES ADDITIONAL PRACTICE'}
        </div>
        <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.9rem' }}>
          Final score calculated using NexoraNet transparent 7-factor rubric with partial credit and progressive hint deductions.
        </p>
      </div>

      {/* 7-Factor Rubric Breakdown */}
      <div className="soar-card">
        <div className="soar-card-title">
          <span>7-Factor Rubric Score Breakdown</span>
        </div>

        <div className="scen-breakdown-grid">
          {Object.entries(evaluation.breakdown).map(([key, val]) => {
            const formattedLabel = key
              .replace(/_/g, ' ')
              .replace(/\b\w/g, (c) => c.toUpperCase());
            const isPenalty = val < 0;

            return (
              <div key={key} className="scen-breakdown-card">
                <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: 4 }}>
                  {formattedLabel}
                </div>
                <div style={{ fontSize: '1.4rem', fontWeight: 700, color: isPenalty ? '#f87171' : '#38bdf8' }}>
                  {isPenalty ? `${val}` : `+${val}`} pts
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Feedback & Observations */}
      {evaluation.feedback && evaluation.feedback.length > 0 && (
        <div className="soar-card">
          <div className="soar-card-title">Analyst Feedback &amp; Rubric Observations</div>
          <ul style={{ paddingLeft: 20, margin: 0, color: '#cbd5e1', lineHeight: 1.6, fontSize: '0.9rem' }}>
            {evaluation.feedback.map((item, idx) => (
              <li key={idx} style={{ marginBottom: 6 }}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Solution Explanation Walkthrough */}
      {evaluation.solution_explanation && (
        <div className="soar-card">
          <div className="soar-card-title">
            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <BookOpen size={18} color="#06b6d4" /> Solution &amp; Root-Cause Walkthrough
            </span>
          </div>
          <div style={{ color: '#cbd5e1', fontSize: '0.92rem', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
            {evaluation.solution_explanation}
          </div>
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 14, marginTop: 24 }}>
        <Link to="/soc/scenarios" className="soar-btn soar-btn-primary">
          Explore Other Scenarios
        </Link>
        <button
          className="soar-btn"
          onClick={() => {
            if (window.confirm('Start a fresh investigation attempt for this scenario?')) {
              socScenarioApi.startAttempt(evaluation.scenario_id).then((newAttempt) => {
                window.location.href = `/soc/scenarios/workspace/${newAttempt.attempt_id}`;
              });
            }
          }}
        >
          <RotateCcw size={16} /> Retry Scenario
        </button>
      </div>
    </div>
  );
};
