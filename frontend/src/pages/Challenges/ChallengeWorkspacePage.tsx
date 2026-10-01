import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  Shield,
  ArrowLeft,
  Key,
  HelpCircle,
  Eye,
  FileCode,
  CheckCircle,
  XCircle,
  Save,
  CheckSquare,
  AlertCircle,
  Copy,
} from 'lucide-react';
import { challengeApi } from '../../services/challengeApi';
import type {
  ChallengeAttempt,
  ChallengeDetail,
  FlagSubmissionResponse,
} from '../../types/challenge';
import '../../components/challenges/challenges.css';

export const ChallengeWorkspacePage: React.FC = () => {
  const { challengeId } = useParams<{ challengeId: string }>();
  const navigate = useNavigate();

  const [challenge, setChallenge] = useState<ChallengeDetail | null>(null);
  const [attempt, setAttempt] = useState<ChallengeAttempt | null>(null);
  const [activeEvidenceIndex, setActiveEvidenceIndex] = useState<number>(0);
  const [submittedFlag, setSubmittedFlag] = useState<string>('');
  const [notesText, setNotesText] = useState<string>('');
  const [notesSaved, setNotesSaved] = useState<boolean>(true);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [submissionFeedback, setSubmissionFeedback] = useState<FlagSubmissionResponse | null>(null);
  const [submissionError, setSubmissionError] = useState<string | null>(null);
  const [unlockingHint, setUnlockingHint] = useState<boolean>(false);
  const [revealing, setRevealing] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [copySuccess, setCopySuccess] = useState<boolean>(false);

  const notesTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (challengeId) {
      loadWorkspace(challengeId);
    }
  }, [challengeId]);

  const loadWorkspace = async (id: string) => {
    setLoading(true);
    try {
      const detail = await challengeApi.getChallengeDetail(id);
      setChallenge(detail);

      const att = await challengeApi.startAttempt(detail.challenge_id);
      setAttempt(att);
      setNotesText(att.notes || '');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to initialize workspace.';
      setSubmissionError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleNotesChange = (text: string) => {
    setNotesText(text);
    setNotesSaved(false);

    if (notesTimeoutRef.current) {
      clearTimeout(notesTimeoutRef.current);
    }

    notesTimeoutRef.current = setTimeout(async () => {
      if (!attempt || !challenge) return;
      try {
        await challengeApi.saveNotes(challenge.challenge_id, attempt.attempt_id, text);
        setNotesSaved(true);
      } catch {
        // quiet retry
      }
    }, 1200);
  };

  const handleFlagSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!challenge || !attempt || !submittedFlag.trim()) return;

    setSubmitting(true);
    setSubmissionError(null);
    setSubmissionFeedback(null);

    try {
      const result = await challengeApi.submitFlag(
        challenge.challenge_id,
        attempt.attempt_id,
        submittedFlag.trim()
      );
      setSubmissionFeedback(result);

      if (result.is_correct && result.solved) {
        // Refresh detail to capture solved status
        const updatedDetail = await challengeApi.getChallengeDetail(challenge.challenge_id);
        setChallenge(updatedDetail);
      }
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Flag verification failed.';
      setSubmissionError(message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleUnlockHint = async () => {
    if (!challenge || !attempt) return;
    setUnlockingHint(true);
    try {
      await challengeApi.unlockHint(challenge.challenge_id, attempt.attempt_id);
      // Reload challenge and attempt to see unlocked hint text and updated penalties
      const updatedDetail = await challengeApi.getChallengeDetail(challenge.challenge_id);
      const updatedAttempt = await challengeApi.startAttempt(challenge.challenge_id);
      setChallenge(updatedDetail);
      setAttempt(updatedAttempt);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to unlock hint.';
      setSubmissionError(message);
    } finally {
      setUnlockingHint(false);
    }
  };

  const handleRevealSolution = async () => {
    if (!challenge || !attempt) return;
    const confirmed = window.confirm(
      'Are you sure you want to reveal the solution? This will forfeit points for this challenge (0 pts awarded) but allow you to study the complete walkthrough.'
    );
    if (!confirmed) return;

    setRevealing(true);
    try {
      await challengeApi.revealSolution(challenge.challenge_id, attempt.attempt_id);
      navigate(`/challenges/${challenge.challenge_id}/results`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to reveal walkthrough.';
      setSubmissionError(message);
      setRevealing(false);
    }
  };

  const handleCopyEvidence = (content: string) => {
    navigator.clipboard.writeText(content);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  if (loading) {
    return (
      <div className="challenges-container">
        <div className="text-center py-16 text-gray-400">Loading synthetic investigation sandbox...</div>
      </div>
    );
  }

  if (!challenge || !attempt) {
    return (
      <div className="challenges-container">
        <div className="feedback-banner error">Unable to load workspace.</div>
        <Link to="/challenges" className="inline-flex items-center gap-2 text-sm text-blue-400">
          <ArrowLeft size={16} /> Back to Catalog
        </Link>
      </div>
    );
  }

  const tasks: string[] = (() => {
    try {
      return JSON.parse(challenge.tasks_json);
    } catch {
      return [];
    }
  })();

  const activeEvidence = challenge.evidence[activeEvidenceIndex] || null;

  return (
    <div className="challenges-container">
      {/* Top Bar */}
      <div className="flex items-center justify-between pb-2 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <Link
            to={`/challenges/${challenge.challenge_id}`}
            className="text-gray-400 hover:text-gray-200 text-sm flex items-center gap-1.5"
          >
            <ArrowLeft size={16} /> Briefing
          </Link>
          <span className="text-gray-600">/</span>
          <span className="text-sm font-semibold text-gray-200">{challenge.title}</span>
          <span className="challenge-id-tag">{challenge.challenge_id}</span>
        </div>

        <div className="flex items-center gap-3">
          <div className="simulation-badge">
            <Shield size={14} />
            <span>Simulation Only</span>
          </div>
          {challenge.is_solved && (
            <Link
              to={`/challenges/${challenge.challenge_id}/results`}
              className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded"
            >
              View Walkthrough & Takeaways
            </Link>
          )}
        </div>
      </div>

      {/* 3-Column Workspace Layout */}
      <div className="workspace-layout">
        {/* ================================================================= */}
        {/* LEFT PANEL: Objectives, Tasks & Hints */}
        {/* ================================================================= */}
        <div className="workspace-panel">
          <div className="panel-header">
            <span className="flex items-center gap-1.5">
              <CheckSquare size={16} className="text-blue-400" />
              Investigation Tasks
            </span>
            <span className="text-xs text-gray-400">{tasks.length} steps</span>
          </div>

          <div className="panel-content">
            {/* Tasks Checklist */}
            <div className="space-y-2">
              {tasks.map((task, i) => (
                <div
                  key={i}
                  className="p-2.5 rounded bg-gray-950 border border-gray-800 text-xs text-gray-300 leading-relaxed flex items-start gap-2"
                >
                  <span className="text-blue-400 font-bold mt-0.5">{i + 1}.</span>
                  <span>{task}</span>
                </div>
              ))}
            </div>

            {/* Progressive Hints Section */}
            <div className="mt-4 pt-4 border-t border-gray-800 flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                  <HelpCircle size={14} className="text-yellow-400" />
                  Progressive Hints ({attempt.hints_unlocked} unlocked)
                </span>
                <span className="text-xs text-red-400 font-mono">
                  -{attempt.hints_penalty} pts deducted
                </span>
              </div>

              {challenge.hints.length === 0 ? (
                <div className="text-xs text-gray-500 italic">No hints available for this challenge.</div>
              ) : (
                challenge.hints.map((hint) => (
                  <div key={hint.id} className="hint-item">
                    <div className="hint-header">
                      <span>Hint #{hint.hint_number}</span>
                      {hint.is_unlocked ? (
                        <span className="text-xs text-emerald-400 flex items-center gap-1">
                          <CheckCircle size={12} /> Unlocked
                        </span>
                      ) : (
                        <span className="hint-penalty-tag">
                          Penalty: -{hint.penalty_points} pts
                        </span>
                      )}
                    </div>
                    {hint.is_unlocked ? (
                      <div className="text-gray-300 text-xs bg-gray-900 p-2 rounded border border-gray-700">
                        {hint.hint_text}
                      </div>
                    ) : (
                      <div className="text-gray-500 text-xs italic">
                        Content locked until revealed.
                      </div>
                    )}
                  </div>
                ))
              )}

              {/* Unlock Next Hint Button */}
              {attempt.hints_unlocked < challenge.hints.length && !challenge.is_solved && (
                <button
                  onClick={handleUnlockHint}
                  disabled={unlockingHint}
                  className="hint-unlock-btn w-full"
                >
                  {unlockingHint ? 'Unlocking...' : 'Unlock Next Hint (-Points)'}
                </button>
              )}

              {/* Give Up / Solution Reveal Button */}
              {!challenge.is_solved && !challenge.revealed_solution && (
                <button
                  onClick={handleRevealSolution}
                  disabled={revealing}
                  className="giveup-btn"
                >
                  <Eye size={14} className="inline mr-1" />
                  {revealing ? 'Revealing...' : 'Give Up & Reveal Solution Walkthrough'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* ================================================================= */}
        {/* CENTER PANEL: Synthetic Evidence Explorer */}
        {/* ================================================================= */}
        <div className="workspace-panel">
          <div className="panel-header">
            <span className="flex items-center gap-1.5">
              <FileCode size={16} className="text-emerald-400" />
              Synthetic Evidence Explorer
            </span>
            {activeEvidence && (
              <button
                onClick={() => handleCopyEvidence(activeEvidence.content_json)}
                className="text-xs text-gray-400 hover:text-gray-200 flex items-center gap-1 bg-gray-800 px-2 py-1 rounded"
              >
                <Copy size={12} />
                <span>{copySuccess ? 'Copied!' : 'Copy Evidence'}</span>
              </button>
            )}
          </div>

          <div className="panel-content">
            {/* Evidence Tabs */}
            {challenge.evidence.length > 0 ? (
              <>
                <div className="evidence-tabs-bar">
                  {challenge.evidence.map((ev, idx) => (
                    <button
                      key={ev.id}
                      className={`evidence-tab-btn ${activeEvidenceIndex === idx ? 'active' : ''}`}
                      onClick={() => setActiveEvidenceIndex(idx)}
                    >
                      {ev.title}
                    </button>
                  ))}
                </div>

                {activeEvidence && (
                  <div className="flex flex-col gap-2 flex-1">
                    <div className="text-xs text-gray-400">{activeEvidence.description}</div>
                    <div className="evidence-viewer-box flex-1">
                      {activeEvidence.content_json}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <div className="text-gray-500 text-sm text-center py-12">
                No external evidence attachments for this conceptual drill. Use scenario description.
              </div>
            )}
          </div>
        </div>

        {/* ================================================================= */}
        {/* RIGHT PANEL: Flag Submission & Scratchpad */}
        {/* ================================================================= */}
        <div className="workspace-panel">
          <div className="panel-header">
            <span className="flex items-center gap-1.5">
              <Key size={16} className="text-yellow-400" />
              Flag Verification
            </span>
            <span className="text-xs text-gray-400">
              Potential: {Math.max(challenge.points - attempt.hints_penalty, 10)} pts
            </span>
          </div>

          <div className="panel-content">
            {/* Flag Submission Form */}
            <form onSubmit={handleFlagSubmit} className="flag-submission-card">
              <label className="text-xs font-semibold text-gray-300">
                Submit Flag or Verified Answer:
              </label>
              <input
                type="text"
                className="flag-input"
                placeholder={challenge.flag_format || 'FLAG{...}'}
                value={submittedFlag}
                onChange={(e) => setSubmittedFlag(e.target.value)}
                disabled={submitting || challenge.is_solved}
              />

              <button
                type="submit"
                disabled={submitting || !submittedFlag.trim() || challenge.is_solved}
                className="challenge-action-btn"
              >
                {submitting ? 'Verifying...' : challenge.is_solved ? 'Challenge Completed' : 'Submit Flag'}
              </button>
            </form>

            {/* Error or Rate Limit Alert */}
            {submissionError && (
              <div className="feedback-banner error flex items-start gap-2">
                <AlertCircle size={16} className="shrink-0 mt-0.5" />
                <span>{submissionError}</span>
              </div>
            )}

            {/* Result Feedback Banner */}
            {submissionFeedback && (
              <div
                className={`feedback-banner ${
                  submissionFeedback.is_correct ? 'success' : 'error'
                } flex items-start gap-2`}
              >
                {submissionFeedback.is_correct ? (
                  <CheckCircle size={16} className="shrink-0 mt-0.5" />
                ) : (
                  <XCircle size={16} className="shrink-0 mt-0.5" />
                )}
                <div>
                  <div className="font-semibold">{submissionFeedback.feedback}</div>
                  {submissionFeedback.points_awarded > 0 && (
                    <div className="text-xs mt-1">
                      Score Awarded: +{submissionFeedback.points_awarded} pts!
                    </div>
                  )}
                  {submissionFeedback.solution_explanation && (
                    <Link
                      to={`/challenges/${challenge.challenge_id}/results`}
                      className="inline-block mt-2 text-xs font-semibold text-emerald-400 underline"
                    >
                      View Comprehensive Solution Walkthrough & Takeaways →
                    </Link>
                  )}
                </div>
              </div>
            )}

            {/* Student Scratchpad / Investigation Notes */}
            <div className="mt-4 pt-4 border-t border-gray-800 flex flex-col gap-2 flex-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-gray-300 flex items-center gap-1.5">
                  <Save size={14} className="text-blue-400" />
                  Investigation Scratchpad (Autosaved)
                </span>
                <span className="scratchpad-save-indicator">
                  {notesSaved ? 'Saved' : 'Saving...'}
                </span>
              </div>
              <textarea
                className="scratchpad-textarea flex-1"
                placeholder="Log your hypotheses, observations, IP addresses, and forensic clues here..."
                value={notesText}
                onChange={(e) => handleNotesChange(e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
