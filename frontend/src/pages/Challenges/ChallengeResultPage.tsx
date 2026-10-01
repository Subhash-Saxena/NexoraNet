import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Trophy,
  AlertTriangle,
  ArrowLeft,
  Shield,
  BookOpen,
  ArrowRight,
  Sparkles,
} from 'lucide-react';
import { challengeApi } from '../../services/challengeApi';
import type { ChallengeDetail, ChallengeRecommendation } from '../../types/challenge';
import '../../components/challenges/challenges.css';

export const ChallengeResultPage: React.FC = () => {
  const { challengeId } = useParams<{ challengeId: string }>();
  const [challenge, setChallenge] = useState<ChallengeDetail | null>(null);
  const [recommendations, setRecommendations] = useState<ChallengeRecommendation[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (challengeId) {
      loadResults(challengeId);
    }
  }, [challengeId]);

  const loadResults = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const [detail, recs] = await Promise.all([
        challengeApi.getChallengeDetail(id),
        challengeApi.getRecommendations(3).catch(() => []),
      ]);
      setChallenge(detail);
      setRecommendations(recs);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load challenge results.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="challenges-container">
        <div className="text-center py-16 text-gray-400">Loading educational walkthrough...</div>
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div className="challenges-container">
        <div className="feedback-banner error mb-4">{error || 'Challenge not found.'}</div>
        <Link to="/challenges" className="inline-flex items-center gap-2 text-sm text-blue-400">
          <ArrowLeft size={16} /> Back to Challenges Catalog
        </Link>
      </div>
    );
  }

  const commonMistakes: string[] = (() => {
    try {
      return JSON.parse(challenge.common_mistakes || '[]');
    } catch {
      return [];
    }
  })();

  const isSolved = challenge.is_solved;
  const isRevealed = challenge.revealed_solution;

  return (
    <div className="challenges-container">
      {/* Top Nav */}
      <div className="flex items-center justify-between pb-2 border-b border-gray-800">
        <Link to="/challenges" className="text-gray-400 hover:text-gray-200 text-sm flex items-center gap-1.5">
          <ArrowLeft size={16} /> Back to Catalog
        </Link>
        <div className="simulation-badge">
          <Shield size={14} />
          <span>Non-Destructive Simulation Only</span>
        </div>
      </div>

      {/* Outcome Banner */}
      <div
        className={`p-6 rounded-xl border flex flex-col md:flex-row items-center justify-between gap-4 ${
          isSolved
            ? 'bg-emerald-950/40 border-emerald-700/50 text-emerald-200'
            : isRevealed
            ? 'bg-amber-950/40 border-amber-700/50 text-amber-200'
            : 'bg-gray-900 border-gray-800 text-gray-200'
        }`}
      >
        <div className="flex items-center gap-4">
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${
              isSolved ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'
            }`}
          >
            {isSolved ? <Trophy size={28} /> : <AlertTriangle size={28} />}
          </div>
          <div>
            <h1 className="text-xl font-bold">
              {isSolved
                ? `Challenge Completed: ${challenge.title}`
                : isRevealed
                ? `Walkthrough Revealed: ${challenge.title}`
                : challenge.title}
            </h1>
            <p className="text-sm opacity-80 mt-1">
              {isSolved
                ? `Congratulations! Flag verified successfully.`
                : isRevealed
                ? 'Educational walkthrough unlocked for study review (0 points awarded).'
                : 'Review the challenge analysis and recommendations.'}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to={`/challenges/${challenge.challenge_id}/workspace`}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-semibold rounded"
          >
            Revisit Sandbox
          </Link>
          <Link
            to="/challenges"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded"
          >
            Catalog
          </Link>
        </div>
      </div>

      {/* Walkthrough & Common Mistakes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 flex flex-col gap-6">
          {/* Detailed Solution Walkthrough */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <h2 className="text-base font-semibold text-gray-100 flex items-center gap-2 mb-3">
              <BookOpen size={18} className="text-blue-400" />
              Comprehensive Technical Walkthrough
            </h2>
            <div className="text-gray-300 text-sm leading-relaxed whitespace-pre-line bg-gray-950 p-4 rounded-lg border border-gray-800">
              {challenge.solution_explanation || 'Walkthrough is hidden until the challenge is solved or revealed.'}
            </div>
          </div>

          {/* Common Mistakes */}
          {commonMistakes.length > 0 && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-base font-semibold text-gray-100 flex items-center gap-2 mb-3">
                <AlertTriangle size={18} className="text-amber-400" />
                Common Pitfalls & Mistakes
              </h2>
              <ul className="space-y-2">
                {commonMistakes.map((mistake, i) => (
                  <li key={i} className="text-xs text-gray-300 flex items-start gap-2 bg-gray-950 p-3 rounded border border-gray-800">
                    <span className="text-amber-400 font-bold">•</span>
                    <span>{mistake}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Right Sidebar: Recommended Next Steps */}
        <div className="flex flex-col gap-6">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 flex flex-col gap-4">
            <h2 className="text-sm font-semibold text-gray-200 flex items-center gap-1.5">
              <Sparkles size={16} className="text-blue-400" />
              Recommended Next Practice
            </h2>
            <div className="space-y-3">
              {recommendations.map((rec, i) => (
                <div key={i} className="p-3 bg-gray-950 border border-gray-800 rounded-lg flex flex-col gap-1.5">
                  <div className="text-xs font-semibold text-gray-200">{rec.title}</div>
                  <div className="text-[11px] text-gray-400">{rec.reason}</div>
                  <Link
                    to={rec.action_url}
                    className="inline-flex items-center gap-1 text-[11px] text-blue-400 hover:text-blue-300 font-semibold mt-1"
                  >
                    <span>Proceed</span>
                    <ArrowRight size={10} />
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
