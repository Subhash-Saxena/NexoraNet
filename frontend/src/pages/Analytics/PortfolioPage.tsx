import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Award,
  Check,
  Copy,
  Download,
  ExternalLink,
  Eye,
  EyeOff,
  Globe,
  Lock,
  Plus,
  Save,
  Trash2,
} from 'lucide-react';
import { analyticsApi } from '../../services/analyticsApi';
import type { PortfolioDetail, PortfolioVisibility } from '../../types/analytics';
import '../../components/analytics/analytics.css';

export const PortfolioPage: React.FC = () => {
  const [portfolio, setPortfolio] = useState<PortfolioDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);
  const [savingBio, setSavingBio] = useState(false);
  const [bioInput, setBioInput] = useState('');
  const [focusInput, setFocusInput] = useState('');

  // New project modal state
  const [showAddProject, setShowAddProject] = useState(false);
  const [projectTitle, setProjectTitle] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [projectTechs, setProjectTechs] = useState('');
  const [projectSkills, setProjectSkills] = useState('');
  const [projectOutcome, setProjectOutcome] = useState('');
  const [projectRepo, setProjectRepo] = useState('');
  const [projectDemo, setProjectDemo] = useState('');
  const [urlError, setUrlError] = useState('');
  const [addingProject, setAddingProject] = useState(false);

  const fetchPortfolio = async () => {
    try {
      setLoading(true);
      const data = await analyticsApi.getMyPortfolio();
      setPortfolio({ ...data, projects: data.projects || [] });
      setBioInput(data.bio || '');
      setFocusInput(data.learning_focus || '');
      setLoading(false);
    } catch (err) {
      console.error('Failed to load portfolio:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleVisibilityChange = async (newVis: PortfolioVisibility) => {
    if (!portfolio) return;
    try {
      const updated = await analyticsApi.updatePortfolio({ visibility: newVis });
      setPortfolio((prev) => (prev ? { ...updated, projects: updated.projects || prev.projects || [] } : updated));
    } catch (err) {
      console.error('Failed to update visibility:', err);
    }
  };

  const handleSaveBio = async () => {
    if (!portfolio) return;
    try {
      setSavingBio(true);
      const updated = await analyticsApi.updatePortfolio({
        bio: bioInput,
        learning_focus: focusInput,
      });
      setPortfolio((prev) => (prev ? { ...updated, projects: updated.projects || prev.projects || [] } : updated));
      setSavingBio(false);
    } catch (err) {
      console.error('Failed to save bio:', err);
      setSavingBio(false);
    }
  };

  const handleCopyLink = () => {
    if (!portfolio) return;
    const publicUrl = `${window.location.origin}/portfolio/public/${portfolio.public_slug}`;
    navigator.clipboard.writeText(publicUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleExportJson = async () => {
    try {
      const data = await analyticsApi.exportPortfolioJson();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `nexoranet-portfolio-${portfolio?.public_slug || 'export'}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to export JSON:', err);
    }
  };

  const validateUrl = (urlStr: string): boolean => {
    if (!urlStr) return true;
    const lower = urlStr.trim().toLowerCase();
    if (lower.startsWith('javascript:') || lower.startsWith('data:') || lower.startsWith('vbscript:')) {
      return false;
    }
    return lower.startsWith('http://') || lower.startsWith('https://');
  };

  const handleAddProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setUrlError('');

    if (projectRepo && !validateUrl(projectRepo)) {
      setUrlError('Repository URL must be a valid http:// or https:// link.');
      return;
    }
    if (projectDemo && !validateUrl(projectDemo)) {
      setUrlError('Demo URL must be a valid http:// or https:// link.');
      return;
    }

    try {
      setAddingProject(true);
      const newProj = await analyticsApi.addPortfolioProject({
        title: projectTitle,
        description: projectDesc,
        technologies: projectTechs.split(',').map((s) => s.trim()).filter(Boolean),
        skills: projectSkills.split(',').map((s) => s.trim()).filter(Boolean),
        learning_outcome: projectOutcome,
        repository_url: projectRepo || undefined,
        demo_url: projectDemo || undefined,
      });

      if (portfolio) {
        setPortfolio({
          ...portfolio,
          projects: [...portfolio.projects, newProj],
        });
      }
      setShowAddProject(false);
      setProjectTitle('');
      setProjectDesc('');
      setProjectTechs('');
      setProjectSkills('');
      setProjectOutcome('');
      setProjectRepo('');
      setProjectDemo('');
      setAddingProject(false);
    } catch (err: any) {
      setUrlError(err.message || 'Failed to add project');
      setAddingProject(false);
    }
  };

  const handleDeleteProject = async (projId: number) => {
    if (!portfolio) return;
    try {
      await analyticsApi.deletePortfolioProject(projId);
      setPortfolio({
        ...portfolio,
        projects: portfolio.projects.filter((p) => p.id !== projId),
      });
    } catch (err) {
      console.error('Failed to delete project:', err);
    }
  };

  return (
    <div className="analytics-container">
      {/* Header */}
      <div className="analytics-header">
        <div>
          <h1>
            <Award className="text-cyan-400" size={28} />
            <span>Cybersecurity Student Portfolio</span>
          </h1>
          <p className="analytics-tagline">
            Showcase hands-on investigation artifacts, verified lab accomplishments, and practical defensive projects.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <button
            className="btn-secondary"
            onClick={handleExportJson}
            style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <Download size={16} />
            <span>Export JSON</span>
          </button>
          {portfolio && (
            <Link
              to={`/portfolio/public/${portfolio.public_slug}`}
              className="btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}
            >
              <Eye size={16} />
              <span>Preview Public View</span>
            </Link>
          )}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af' }}>
          Loading portfolio workspace...
        </div>
      ) : !portfolio ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#9ca3af', background: '#111827', borderRadius: '0.75rem' }}>
          Unable to load portfolio details.
        </div>
      ) : (
        <>
          {/* Visibility & Link Controls */}
          <div className="portfolio-header-box">
            <div>
              <div style={{ fontSize: '0.8rem', color: '#9ca3af', textTransform: 'uppercase', fontWeight: 600 }}>
                Portfolio Visibility Status
              </div>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                <button
                  className={`tab-btn ${portfolio.visibility === 'PRIVATE' ? 'active' : ''}`}
                  onClick={() => handleVisibilityChange('PRIVATE')}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  <Lock size={14} />
                  <span>Private</span>
                </button>
                <button
                  className={`tab-btn ${portfolio.visibility === 'UNLISTED' ? 'active' : ''}`}
                  onClick={() => handleVisibilityChange('UNLISTED')}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  <EyeOff size={14} />
                  <span>Unlisted</span>
                </button>
                <button
                  className={`tab-btn ${portfolio.visibility === 'PUBLIC' ? 'active' : ''}`}
                  onClick={() => handleVisibilityChange('PUBLIC')}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                >
                  <Globe size={14} />
                  <span>Public</span>
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <div style={{ fontSize: '0.85rem', color: '#9ca3af' }}>
                Public Slug: <code style={{ color: '#38bdf8' }}>{portfolio.public_slug}</code>
              </div>
              <button
                className="btn-secondary"
                onClick={handleCopyLink}
                style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}
              >
                {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                <span>{copied ? 'Copied URL!' : 'Share Link'}</span>
              </button>
            </div>
          </div>

          {/* Profile & Bio Editor */}
          <div className="admin-card">
            <h3 style={{ fontSize: '1.15rem', color: '#f3f4f6', margin: '0 0 1rem 0' }}>Profile & Learning Direction</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.85rem', color: '#9ca3af', display: 'block', marginBottom: '4px' }}>
                  Student Bio / Summary
                </label>
                <textarea
                  value={bioInput}
                  onChange={(e) => setBioInput(e.target.value)}
                  placeholder="Summarize your cybersecurity background and learning goals..."
                  rows={3}
                  style={{
                    width: '100%',
                    padding: '0.75rem',
                    background: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.375rem',
                    color: '#f9fafb',
                    fontSize: '0.875rem',
                  }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.85rem', color: '#9ca3af', display: 'block', marginBottom: '4px' }}>
                  Current Learning Focus
                </label>
                <input
                  type="text"
                  value={focusInput}
                  onChange={(e) => setFocusInput(e.target.value)}
                  placeholder="e.g. Network Detection, PCAP Analysis, SOC Triage"
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.75rem',
                    background: '#1f2937',
                    border: '1px solid #374151',
                    borderRadius: '0.375rem',
                    color: '#f9fafb',
                    fontSize: '0.875rem',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  className="btn-primary"
                  onClick={handleSaveBio}
                  disabled={savingBio}
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <Save size={16} />
                  <span>{savingBio ? 'Saving...' : 'Save Profile'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Showcase Projects */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '0.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', color: '#f3f4f6', margin: 0 }}>Showcase Projects & Artifacts</h2>
            <button
              className="btn-primary"
              onClick={() => setShowAddProject(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <Plus size={16} />
              <span>Add Project</span>
            </button>
          </div>

          {(portfolio.projects || []).length === 0 ? (
            <div style={{ textAlign: 'center', padding: '2.5rem', color: '#9ca3af', background: '#111827', borderRadius: '0.75rem', border: '1px dashed #374151' }}>
              No projects added yet. Click &quot;Add Project&quot; to showcase your defensive tooling, forensics walkthroughs, or lab investigations.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '1.25rem' }}>
              {(portfolio.projects || []).map((proj) => (
                <div key={proj.id} className="project-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#f9fafb', margin: 0 }}>{proj.title}</h3>
                    <button
                      onClick={() => handleDeleteProject(proj.id)}
                      style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', padding: '0.2rem' }}
                      title="Delete Project"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>

                  <p style={{ fontSize: '0.85rem', color: '#9ca3af', margin: '0.25rem 0', lineHeight: 1.5 }}>
                    {proj.description}
                  </p>

                  {proj.learning_outcome && (
                    <div style={{ fontSize: '0.8rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.08)', padding: '0.4rem 0.6rem', borderRadius: '0.25rem' }}>
                      <strong>Outcome:</strong> {proj.learning_outcome}
                    </div>
                  )}

                  {proj.technologies && proj.technologies.length > 0 && (
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
                        <span>Live Demo</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Add Project Modal */}
          {showAddProject && (
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
              onClick={() => setShowAddProject(false)}
            >
              <div
                style={{
                  background: '#111827',
                  border: '1px solid #374151',
                  borderRadius: '0.75rem',
                  maxWidth: '550px',
                  width: '100%',
                  padding: '2rem',
                }}
                onClick={(e) => e.stopPropagation()}
              >
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f9fafb', margin: '0 0 1rem 0' }}>
                  Add Showcase Project
                </h2>

                {urlError && (
                  <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#f87171', padding: '0.5rem 0.75rem', borderRadius: '0.375rem', fontSize: '0.85rem', marginBottom: '1rem' }}>
                    {urlError}
                  </div>
                )}

                <form onSubmit={handleAddProject} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Project Title *
                    </label>
                    <input
                      type="text"
                      required
                      value={projectTitle}
                      onChange={(e) => setProjectTitle(e.target.value)}
                      placeholder="e.g. PCAP Beaconing Detection Engine"
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Description *
                    </label>
                    <textarea
                      required
                      value={projectDesc}
                      onChange={(e) => setProjectDesc(e.target.value)}
                      placeholder="Explain what the project simulates or defends against..."
                      rows={3}
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Technologies (comma separated)
                    </label>
                    <input
                      type="text"
                      value={projectTechs}
                      onChange={(e) => setProjectTechs(e.target.value)}
                      placeholder="e.g. Python, Scapy, Suricata"
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Demonstrated Skills (comma separated)
                    </label>
                    <input
                      type="text"
                      value={projectSkills}
                      onChange={(e) => setProjectSkills(e.target.value)}
                      placeholder="e.g. PACKET_ANALYSIS, NETWORK_TRAFFIC_ANALYSIS"
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Learning Outcome
                    </label>
                    <input
                      type="text"
                      value={projectOutcome}
                      onChange={(e) => setProjectOutcome(e.target.value)}
                      placeholder="e.g. Reconstructed HTTP streams and detected exfiltration."
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Repository URL (https://)
                    </label>
                    <input
                      type="text"
                      value={projectRepo}
                      onChange={(e) => setProjectRepo(e.target.value)}
                      placeholder="https://github.com/example/repo"
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '2px' }}>
                      Demo URL (https://)
                    </label>
                    <input
                      type="text"
                      value={projectDemo}
                      onChange={(e) => setProjectDemo(e.target.value)}
                      placeholder="https://example.com/demo"
                      style={{ width: '100%', padding: '0.5rem', background: '#1f2937', border: '1px solid #374151', borderRadius: '0.375rem', color: '#fff' }}
                    />
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => setShowAddProject(false)}
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="btn-primary"
                      disabled={addingProject}
                    >
                      {addingProject ? 'Adding...' : 'Save Project'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};
