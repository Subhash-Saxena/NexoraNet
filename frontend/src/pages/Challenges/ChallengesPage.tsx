import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Trophy,
  Shield,
  Search,
  CheckCircle,
  Clock,
  Sparkles,
  Layers,
  ArrowRight,
  Filter,
  BarChart2,
  BookOpen,
} from 'lucide-react';
import { challengeApi } from '../../services/challengeApi';
import type {
  ChallengeMetrics,
  ChallengeRecommendation,
  ChallengeSummary,
  ChallengeTrack,
} from '../../types/challenge';
import '../../components/challenges/challenges.css';

export const ChallengesPage: React.FC = () => {
  const [challenges, setChallenges] = useState<ChallengeSummary[]>([]);
  const [metrics, setMetrics] = useState<ChallengeMetrics | null>(null);
  const [tracks, setTracks] = useState<ChallengeTrack[]>([]);
  const [recommendations, setRecommendations] = useState<ChallengeRecommendation[]>([]);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedTrack, setSelectedTrack] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedDifficulty, selectedCategory, searchQuery]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [chalData, metData, trackData, recData] = await Promise.all([
        challengeApi.getChallenges({
          difficulty: selectedDifficulty !== 'ALL' ? selectedDifficulty : undefined,
          category: selectedCategory !== 'ALL' ? selectedCategory : undefined,
          search: searchQuery.trim() || undefined,
        }),
        challengeApi.getMetrics().catch(() => null),
        challengeApi.getTracks().catch(() => []),
        challengeApi.getRecommendations().catch(() => []),
      ]);

      setChallenges(chalData || []);
      if (metData) setMetrics(metData);
      if (trackData) setTracks(trackData);
      if (recData) setRecommendations(recData);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load challenges.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    'ALL',
    'NETWORKING',
    'PACKET_ANALYSIS',
    'SOC_ANALYSIS',
    'SIEM',
    'DETECTION_ENGINEERING',
    'THREAT_INTELLIGENCE',
    'THREAT_HUNTING',
    'INCIDENT_RESPONSE',
    'MITRE_ATTACK',
    'ENDPOINT_SECURITY',
    'FORENSICS',
    'CYBERSECURITY_REASONING',
  ];

  return (
    <div className="challenges-container">
      {/* Header */}
      <div className="challenges-header">
        <div>
          <h1>
            <Trophy className="text-yellow-500" size={32} />
            CTF Challenges & Advanced Defensive Training
          </h1>
          <p className="challenges-tagline">
            Learn. Simulate. Analyze. Defend. — 40 Offline Educational Challenges Across 5 Skill Tracks
          </p>
        </div>
        <div className="simulation-badge">
          <Shield size={14} />
          <span>100% Offline Simulation Invariant</span>
        </div>
      </div>

      {/* Metrics Banner */}
      {metrics && (
        <div className="challenges-metrics-grid">
          <div className="metric-card">
            <div className="metric-icon-wrap" style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}>
              <Layers size={22} />
            </div>
            <div>
              <div className="metric-value">{metrics.total_challenges}</div>
              <div className="metric-label">Total Challenges</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon-wrap" style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#34d399' }}>
              <CheckCircle size={22} />
            </div>
            <div>
              <div className="metric-value">{metrics.user_solved}</div>
              <div className="metric-label">Challenges Solved</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon-wrap" style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#fbbf24' }}>
              <Clock size={22} />
            </div>
            <div>
              <div className="metric-value">{metrics.user_in_progress}</div>
              <div className="metric-label">In Progress</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon-wrap" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
              <Trophy size={22} />
            </div>
            <div>
              <div className="metric-value">{metrics.total_points_earned}</div>
              <div className="metric-label">Points Earned</div>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon-wrap" style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171' }}>
              <BarChart2 size={22} />
            </div>
            <div>
              <div className="metric-value">{metrics.completion_rate_percent}%</div>
              <div className="metric-label">Completion Rate</div>
            </div>
          </div>
        </div>
      )}

      {/* Recommended Next Actions */}
      {recommendations.length > 0 && (
        <div className="recommendations-box">
          <div className="recommendations-header">
            <Sparkles size={18} />
            <span>Adaptive Training Recommendations</span>
          </div>
          <div className="recommendations-list">
            {recommendations.map((rec, i) => (
              <div key={i} className="rec-item-card">
                <div>
                  <div className="rec-item-title">{rec.title}</div>
                  <div className="rec-item-reason">{rec.reason}</div>
                </div>
                <Link
                  to={rec.action_url}
                  className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 font-semibold"
                >
                  <span>{rec.type === 'CHALLENGE' ? 'Solve Challenge' : 'Review Concepts'}</span>
                  <ArrowRight size={12} />
                </Link>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Curriculum Tracks */}
      {tracks.length > 0 && (
        <div className="tracks-section">
          <h2>
            <BookOpen size={20} className="text-blue-400" />
            Curated Defensive Training Pathways
          </h2>
          <div className="tracks-grid">
            {tracks.map((track) => (
              <div
                key={track.track_id}
                className={`track-card ${selectedTrack === track.track_id ? 'active' : ''}`}
                onClick={() => setSelectedTrack(selectedTrack === track.track_id ? null : track.track_id)}
              >
                <div>
                  <div className="track-card-header">
                    <span className="track-badge-tag">{track.difficulty}</span>
                    <span className="text-xs text-gray-400 font-medium">{track.challenges_count} drills</span>
                  </div>
                  <div className="track-title">{track.title}</div>
                  <div className="track-desc">{track.description}</div>
                </div>
                <div className="track-footer">
                  <span>Badge: {track.badge_name}</span>
                  <span className="text-blue-400 font-medium">Role: {track.target_role}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="challenges-filter-bar">
        <div className="flex items-center gap-2 flex-1">
          <Search size={18} className="text-gray-400" />
          <input
            type="text"
            className="filter-search-input"
            placeholder="Search challenges by keyword, technique, or ID (e.g., DNS, SYN, CHAL-001)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter size={16} className="text-gray-400" />
          <select
            className="filter-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat.replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>

        <div className="difficulty-pill-group">
          {['ALL', 'BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'EXPERT'].map((diff) => (
            <button
              key={diff}
              className={`diff-pill ${diff.toLowerCase()} ${selectedDifficulty === diff ? 'active' : ''}`}
              onClick={() => setSelectedDifficulty(diff)}
            >
              {diff}
            </button>
          ))}
        </div>
      </div>

      {/* Challenges List Grid */}
      {error && <div className="feedback-banner error">{error}</div>}

      {loading ? (
        <div className="text-center py-12 text-gray-400 font-medium">Loading synthetic CTF challenges...</div>
      ) : challenges.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No challenges matched your active filters. Try adjusting your search query or difficulty level.
        </div>
      ) : (
        <div className="challenges-grid">
          {challenges.map((ch) => (
            <div key={ch.id} className="challenge-card">
              <div>
                <div className="challenge-card-header">
                  <span className="challenge-id-tag">{ch.challenge_id}</span>
                  <div className="flex items-center gap-2">
                    <span className={`difficulty-badge ${ch.difficulty.toLowerCase()}`}>
                      {ch.difficulty}
                    </span>
                    <span
                      className={`status-badge ${
                        ch.status === 'SOLVED'
                          ? 'solved'
                          : ch.status === 'IN_PROGRESS'
                          ? 'in-progress'
                          : 'not-started'
                      }`}
                    >
                      {ch.status === 'SOLVED' ? 'Solved' : ch.status === 'IN_PROGRESS' ? 'In Progress' : 'New'}
                    </span>
                  </div>
                </div>

                <h3 className="challenge-card-title">{ch.title}</h3>
                <p className="challenge-card-desc">{ch.description}</p>
              </div>

              <div>
                <div className="challenge-card-meta">
                  <div className="meta-item">
                    <Trophy size={14} className="text-yellow-400" />
                    <span>+{ch.points} pts</span>
                  </div>
                  <div className="meta-item">
                    <Clock size={14} />
                    <span>~{ch.estimated_minutes}m</span>
                  </div>
                  <div className="meta-item">
                    <Shield size={14} className="text-blue-400" />
                    <span>{ch.category.replace('_', ' ')}</span>
                  </div>
                  {ch.is_multi_stage && (
                    <div className="meta-item">
                      <Layers size={14} className="text-purple-400" />
                      <span>Multi-Stage</span>
                    </div>
                  )}
                </div>

                <div className="mt-4">
                  <Link
                    to={`/challenges/${ch.challenge_id}`}
                    className={`challenge-action-btn ${ch.status === 'SOLVED' ? 'solved-btn' : ''}`}
                  >
                    {ch.status === 'SOLVED' ? (
                      <>
                        <CheckCircle size={16} />
                        <span>Review Solution</span>
                      </>
                    ) : ch.status === 'IN_PROGRESS' ? (
                      <>
                        <Clock size={16} />
                        <span>Resume Challenge</span>
                      </>
                    ) : (
                      <>
                        <Trophy size={16} />
                        <span>Start Challenge</span>
                      </>
                    )}
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
