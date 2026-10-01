import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Trophy,
  Shield,
  Clock,
  BookOpen,
  ArrowLeft,
  CheckCircle2,
  FileText,
  AlertTriangle,
  Play,
  Key,
} from 'lucide-react';
import { challengeApi } from '../../services/challengeApi';
import type { ChallengeDetail } from '../../types/challenge';
import '../../components/challenges/challenges.css';

export const ChallengeDetailPage: React.FC = () => {
  const { challengeId } = useParams<{ challengeId: string }>();
  const navigate = useNavigate();
  const [challenge, setChallenge] = useState<ChallengeDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [starting, setStarting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (challengeId) {
      loadDetail(challengeId);
    }
  }, [challengeId]);

  const loadDetail = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await challengeApi.getChallengeDetail(id);
      setChallenge(data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load challenge details.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleStart = async () => {
    if (!challenge) return;
    setStarting(true);
    try {
      await challengeApi.startAttempt(challenge.challenge_id);
      navigate(`/challenges/${challenge.challenge_id}/workspace`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to initialize attempt.';
      setError(message);
      setStarting(false);
    }
  };

  if (loading) {
    return (
      <div className="challenges-container">
        <div className="text-center py-16 text-gray-400">Loading challenge specifications...</div>
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div className="challenges-container">
        <div className="feedback-banner error mb-4">
          {error || 'Challenge not found.'}
        </div>
        <Link to="/challenges" className="inline-flex items-center gap-2 text-sm text-blue-400">
          <ArrowLeft size={16} /> Back to Challenges Catalog
        </Link>
      </div>
    );
  }

  const parseJsonArray = (str: string): string[] => {
    try {
      return JSON.parse(str);
    } catch {
      return [];
    }
  };

  const learningObjectives = parseJsonArray(challenge.learning_objectives);
  const prerequisites = parseJsonArray(challenge.prerequisites);
  const skillsTested = parseJsonArray(challenge.skills_tested_json);

  return (
    <div className="challenges-container">
      {/* Top Navigation */}
      <div className="flex items-center justify-between mb-2">
        <Link to="/challenges" className="inline-flex items-center gap-2 text-sm text-gray-400 hover:text-gray-200">
          <ArrowLeft size={16} /> Back to Catalog
        </Link>
        <div className="simulation-badge">
          <Shield size={14} />
          <span>Non-Destructive Simulation Only</span>
        </div>
      </div>

      {/* Main Card */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 flex flex-col gap-6">
        {/* Header Section */}
        <div className="flex flex-wrap items-start justify-between gap-4 border-b border-gray-800 pb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <span className="challenge-id-tag">{challenge.challenge_id}</span>
              <span className={`difficulty-badge ${challenge.difficulty.toLowerCase()}`}>
                {challenge.difficulty}
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-blue-900/40 text-blue-300 font-semibold border border-blue-700/50">
                {challenge.category.replace('_', ' ')}
              </span>
              {challenge.is_solved && (
                <span className="status-badge solved">
                  <CheckCircle2 size={12} /> Solved
                </span>
              )}
            </div>
            <h1 className="text-2xl font-bold text-gray-100">{challenge.title}</h1>
            <p className="text-gray-400 mt-2 max-w-3xl leading-relaxed">{challenge.description}</p>
          </div>

          <div className="flex flex-col gap-3 min-w-[200px]">
            <div className="bg-gray-800/80 p-4 rounded-lg border border-gray-700 flex flex-col gap-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400 flex items-center gap-1.5">
                  <Trophy size={14} className="text-yellow-400" /> Max Score:
                </span>
                <span className="font-bold text-yellow-400">{challenge.points} pts</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400 flex items-center gap-1.5">
                  <Clock size={14} /> Est. Time:
                </span>
                <span className="text-gray-200 font-medium">~{challenge.estimated_minutes} min</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-400 flex items-center gap-1.5">
                  <Key size={14} /> Flag Format:
                </span>
                <span className="font-mono text-xs text-blue-300">{challenge.flag_format}</span>
              </div>
            </div>

            <button
              onClick={handleStart}
              disabled={starting}
              className="challenge-action-btn py-3 text-base"
            >
              <Play size={18} />
              <span>{starting ? 'Initializing...' : challenge.is_solved ? 'Open Workspace (Review)' : 'Launch Challenge Workspace'}</span>
            </button>
          </div>
        </div>

        {/* Scenario Briefing */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 flex flex-col gap-6">
            <div>
              <h2 className="text-base font-semibold text-gray-200 flex items-center gap-2 mb-2">
                <FileText size={18} className="text-blue-400" />
                Scenario Investigation Brief
              </h2>
              <div className="bg-gray-950 p-4 rounded-lg border border-gray-800 text-gray-300 text-sm leading-relaxed whitespace-pre-line">
                {challenge.scenario}
              </div>
            </div>

            <div>
              <h2 className="text-base font-semibold text-gray-200 flex items-center gap-2 mb-2">
                <Shield size={18} className="text-emerald-400" />
                Synthetic Environment Details
              </h2>
              <div className="bg-gray-950 p-4 rounded-lg border border-gray-800 text-gray-400 text-sm leading-relaxed">
                {challenge.environment_description}
              </div>
            </div>
          </div>

          {/* Right Meta Column */}
          <div className="flex flex-col gap-6">
            {/* Learning Objectives */}
            <div>
              <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-1.5 mb-2">
                <BookOpen size={16} className="text-blue-400" /> Learning Objectives
              </h3>
              <ul className="space-y-1.5 text-xs text-gray-400">
                {learningObjectives.map((obj, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-blue-500 font-bold">•</span>
                    <span>{obj}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Prerequisites */}
            <div>
              <h3 className="text-sm font-semibold text-gray-300 flex items-center gap-1.5 mb-2">
                <AlertTriangle size={16} className="text-yellow-400" /> Prerequisites
              </h3>
              <ul className="space-y-1.5 text-xs text-gray-400">
                {prerequisites.map((req, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-yellow-500 font-bold">•</span>
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Skills Tested */}
            <div>
              <h3 className="text-sm font-semibold text-gray-300 mb-2">Skills Tested</h3>
              <div className="flex flex-wrap gap-1.5">
                {skillsTested.map((skill, i) => (
                  <span
                    key={i}
                    className="text-xs px-2.5 py-1 rounded bg-gray-800 text-gray-300 border border-gray-700"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
