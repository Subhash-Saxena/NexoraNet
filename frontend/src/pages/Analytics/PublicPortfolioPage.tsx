import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Award,
  ExternalLink,
  Lock,
  Shield,
  Terminal,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { PublicPortfolioResponse } from '../../types/analytics';
import '../../components/analytics/analytics.css';

export const PublicPortfolioPage: React.FC = () => {
  const { publicSlug } = useParams<{ publicSlug: string }>();
  const [data, setData] = useState<PublicPortfolioResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const fetchPublicPortfolio = async () => {
      if (!publicSlug) return;
      try {
        setLoading(true);
        const res = await analyticsApi.getPublicPortfolio(publicSlug);
        if (mounted) {
          setData(res);
          setLoading(false);
        }
      } catch (err: any) {
        if (mounted) {
          setError('This portfolio is currently private or not found.');
          setLoading(false);
        }
      }
    };
    fetchPublicPortfolio();
    return () => {
      mounted = false;
    };
  }, [publicSlug]);

  if (loading) {
    return (
      <div className="analytics-container" style={{ textAlign: 'center', padding: '4rem' }}>
        <p style={{ color: '#9ca3af' }}>Loading portfolio presentation...</p>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="analytics-container" style={{ maxWidth: '600px', margin: '4rem auto', textAlign: 'center' }}>
        <div className="admin-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', padding: '3rem' }}>
          <Lock size={40} className="text-gray-500" />
          <h2 style={{ fontSize: '1.4rem', color: '#f3f4f6', margin: 0 }}>Portfolio Not Available</h2>
          <p style={{ color: '#9ca3af', fontSize: '0.9rem', lineHeight: 1.5 }}>
            This student portfolio is set to Private by its owner or the requested link is invalid.
          </p>
          <Link to="/" className="btn-primary" style={{ textDecoration: 'none', marginTop: '0.5rem' }}>
            Return to NexoraNet Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-container" style={{ maxWidth: '1100px' }}>
      {/* Public Profile Hero */}
      <div className="portfolio-paper" style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '0.75rem', padding: '2.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', borderBottom: '1px solid #1e293b', paddingBottom: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#38bdf8', fontSize: '0.85rem', fontWeight: 600 }}>
              <Shield size={16} />
              <span>NEXORANET VERIFIED CADET PORTFOLIO</span>
            </div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc', margin: '0.5rem 0' }}>
              {data.display_name}
            </h1>
            {data.learning_focus && (
              <div style={{ fontSize: '0.95rem', color: '#38bdf8' }}>
                Specialization: <strong>{data.learning_focus}</strong>
              </div>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <span className="confidence-badge high">
              VERIFIED PORTFOLIO
            </span>
          </div>
        </div>

        {data.bio && (
          <div style={{ marginTop: '1.25rem' }}>
            <h3 style={{ fontSize: '0.9rem', textTransform: 'uppercase', color: '#94a3b8', letterSpacing: '0.05em' }}>About</h3>
            <p style={{ color: '#cbd5e1', lineHeight: 1.6, fontSize: '0.95rem', margin: '0.25rem 0 0 0' }}>
              {data.bio}
            </p>
          </div>
        )}

        {/* Public Telemetry Stats */}
        {data.stats && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem', marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid #1e293b' }}>
            <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Labs Completed</span>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#38bdf8', margin: '0.25rem 0 0 0' }}>
                {data.stats.labs_completed ?? 0}
              </p>
            </div>
            <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Challenges Solved</span>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#34d399', margin: '0.25rem 0 0 0' }}>
                {data.stats.challenges_solved ?? 0}
              </p>
            </div>
            <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>SOC Scenarios</span>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#fbbf24', margin: '0.25rem 0 0 0' }}>
                {data.stats.scenarios_completed ?? 0}
              </p>
            </div>
            <div style={{ background: '#1e293b', padding: '1rem', borderRadius: '0.5rem', textAlign: 'center' }}>
              <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Lessons Mastered</span>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: '#a78bfa', margin: '0.25rem 0 0 0' }}>
                {data.stats.lessons_completed ?? 0}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Showcase Projects */}
      <div style={{ marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.35rem', color: '#f3f4f6', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Terminal size={20} className="text-cyan-400" />
          <span>Showcased Cyber Defense Projects</span>
        </h2>

        {(data.projects || []).length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af', background: '#111827', borderRadius: '0.75rem' }}>
            No public projects displayed.
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
            {(data.projects || []).map((proj) => (
              <div key={proj.id} className="project-card">
                <h3 style={{ fontSize: '1.15rem', color: '#f9fafb', margin: 0 }}>{proj.title}</h3>
                <p style={{ fontSize: '0.85rem', color: '#9ca3af', lineHeight: 1.5, margin: '0.25rem 0' }}>
                  {proj.description}
                </p>

                {proj.learning_outcome && (
                  <div style={{ fontSize: '0.8rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.08)', padding: '0.4rem 0.6rem', borderRadius: '0.25rem' }}>
                    <strong>Demonstrated Outcome:</strong> {proj.learning_outcome}
                  </div>
                )}

                {proj.technologies && (proj.technologies || []).length > 0 && (
                  <div className="tag-list">
                    {(proj.technologies || []).map((t, idx) => (
                      <span key={idx} className="tech-tag">{t}</span>
                    ))}
                  </div>
                )}

                <div style={{ display: 'flex', gap: '1rem', marginTop: 'auto', paddingTop: '0.5rem', borderTop: '1px solid #1f2937' }}>
                  {proj.repository_url && (
                    <a
                      href={proj.repository_url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: '0.8rem', color: '#60a5fa', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                    >
                      <ExternalLink size={14} />
                      <span>Repository</span>
                    </a>
                  )}
                  {proj.demo_url && (
                    <a
                      href={proj.demo_url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: '0.8rem', color: '#34d399', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                    >
                      <ExternalLink size={14} />
                      <span>Live Demonstration</span>
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Verified Certificates */}
      {data.certifications && (data.certifications || []).length > 0 && (
        <div style={{ marginTop: '2.5rem' }}>
          <h2 style={{ fontSize: '1.35rem', color: '#f3f4f6', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Award size={20} className="text-yellow-400" />
            <span>Verified Educational Completion Certificates</span>
          </h2>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
            {(data.certifications || []).map((cert) => (
              <div key={cert.code} style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: '0.5rem', padding: '1rem' }}>
                <div style={{ fontSize: '0.75rem', color: '#fbbf24', fontWeight: 600 }}>{cert.track}</div>
                <h4 style={{ fontSize: '1rem', color: '#f9fafb', margin: '0.25rem 0' }}>{cert.title}</h4>
                <div style={{ fontSize: '0.8rem', color: '#6b7280', fontFamily: 'monospace' }}>
                  Code: {cert.code}
                </div>
                <div style={{ fontSize: '0.75rem', color: '#9ca3af', marginTop: '0.5rem' }}>
                  Issued: {new Date(cert.issued_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer Disclaimer */}
      <div style={{ marginTop: '3rem', textAlign: 'center', fontSize: '0.8rem', color: '#64748b', borderTop: '1px solid #1e293b', paddingTop: '1.5rem' }}>
        Verified by NexoraNet Learning Platform. Work accomplishments represent simulations within controlled safe educational environments.
      </div>
    </div>
  );
};
