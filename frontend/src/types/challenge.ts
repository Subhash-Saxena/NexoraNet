/**
 * Types for Step 19 CTF Challenges & Advanced Cybersecurity Training Engine.
 * Non-destructive, educational offline simulation.
 */

export type ChallengeCategory =
  | 'NETWORKING'
  | 'PACKET_ANALYSIS'
  | 'SOC_ANALYSIS'
  | 'SIEM'
  | 'DETECTION_ENGINEERING'
  | 'THREAT_INTELLIGENCE'
  | 'THREAT_HUNTING'
  | 'INCIDENT_RESPONSE'
  | 'MITRE_ATTACK'
  | 'ENDPOINT_SECURITY'
  | 'FORENSICS'
  | 'CYBERSECURITY_REASONING';

export type ChallengeDifficulty =
  | 'BEGINNER'
  | 'INTERMEDIATE'
  | 'ADVANCED'
  | 'EXPERT';

export type ChallengeType =
  | 'FLAG_CHALLENGE'
  | 'MULTIPLE_CHOICE'
  | 'MULTI_SELECT'
  | 'SHORT_ANSWER'
  | 'NUMERICAL'
  | 'IP_ADDRESS'
  | 'CIDR_CALCULATION'
  | 'PACKET_INSPECTION'
  | 'LOG_DECODER'
  | 'ALERT_TRIAGE'
  | 'IOC_IDENTIFICATION'
  | 'CORRELATION_CHAIN'
  | 'PROCESS_TREE_ANALYSIS'
  | 'TIMELINE_RECONSTRUCTION'
  | 'MITRE_MAPPING'
  | 'CONTAINMENT_REASONING'
  | 'AUTOMATION_VALIDATION'
  | 'MULTI_STAGE_INVESTIGATION';

export type ChallengeAttemptStatus =
  | 'NOT_STARTED'
  | 'IN_PROGRESS'
  | 'SOLVED'
  | 'FAILED'
  | 'ABANDONED'
  | 'EXPIRED';

export interface ChallengeSummary {
  id: number;
  challenge_id: string;
  title: string;
  category: ChallengeCategory;
  difficulty: ChallengeDifficulty;
  challenge_type: ChallengeType;
  points: number;
  estimated_minutes: number;
  description: string;
  is_multi_stage: boolean;
  flag_format: string;
  status: 'NOT_STARTED' | 'IN_PROGRESS' | 'SOLVED';
  created_at: string;
}

export interface ChallengeStage {
  id: number;
  stage_order: number;
  title: string;
  description: string;
  tasks_json: string;
  points: number;
  is_terminal: boolean;
}

export interface ChallengeHint {
  id: number;
  hint_number: number;
  penalty_percent: number;
  penalty_points: number;
  is_unlocked: boolean;
  hint_text: string | null;
}

export interface ChallengeEvidence {
  id: number;
  evidence_type: string;
  title: string;
  description: string;
  order_index: number;
  content_json: string;
}

export interface ChallengeDetail {
  id: number;
  challenge_id: string;
  title: string;
  category: ChallengeCategory;
  difficulty: ChallengeDifficulty;
  challenge_type: ChallengeType;
  points: number;
  estimated_minutes: number;
  description: string;
  scenario: string;
  learning_objectives: string;
  prerequisites: string;
  environment_description: string;
  tasks_json: string;
  skills_tested_json: string;
  related_lesson_slug?: string | null;
  related_lab_slug?: string | null;
  related_mitre_technique?: string | null;
  flag_format: string;
  is_multi_stage: boolean;
  simulation_only: boolean;
  stages: ChallengeStage[];
  hints: ChallengeHint[];
  evidence: ChallengeEvidence[];
  solution_explanation?: string | null;
  common_mistakes?: string | null;
  is_solved: boolean;
  revealed_solution: boolean;
  active_attempt_id?: string | null;
}

export interface ChallengeAttempt {
  id: number;
  attempt_id: string;
  challenge_id: number;
  user_id?: number | null;
  status: ChallengeAttemptStatus;
  current_stage_order: number;
  stage_progress_json: string;
  hints_unlocked: number;
  hints_penalty: number;
  attempts_count: number;
  score: number;
  max_score: number;
  solved: boolean;
  revealed_solution: boolean;
  started_at: string;
  completed_at?: string | null;
  last_activity_at: string;
  notes: string;
}

export interface FlagSubmissionResponse {
  is_correct: boolean;
  solved: boolean;
  points_awarded: number;
  current_score: number;
  current_stage: number;
  feedback: string;
  attempts_used: number;
  solution_explanation?: string | null;
}

export interface HintUnlockResponse {
  message: string;
  hint_number: number;
  hint_text?: string | null;
  penalty_applied: number;
  total_penalty: number;
  remaining_hints: number;
}

export interface RevealSolutionResponse {
  revealed: boolean;
  score: number;
  solution_explanation: string;
  common_mistakes: string;
  message: string;
}

export interface ChallengeTrackItem {
  order_index: number;
  is_required: boolean;
  challenge: {
    id: number;
    challenge_id: string;
    title: string;
    category: ChallengeCategory;
    difficulty: ChallengeDifficulty;
    points: number;
    estimated_minutes: number;
  };
}

export interface ChallengeTrack {
  id: number;
  track_id: string;
  title: string;
  description: string;
  target_role: string;
  difficulty: ChallengeDifficulty;
  badge_name: string;
  challenges_count: number;
}

export interface ChallengeTrackDetail {
  id: number;
  track_id: string;
  title: string;
  description: string;
  target_role: string;
  difficulty: ChallengeDifficulty;
  badge_name: string;
  items: ChallengeTrackItem[];
}

export interface ChallengeMetrics {
  total_challenges: number;
  difficulty_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  user_solved: number;
  user_in_progress: number;
  total_points_earned: number;
  completion_rate_percent: number;
}

export interface ChallengeRecommendation {
  type: string;
  title: string;
  challenge_id: string;
  category: ChallengeCategory;
  difficulty: ChallengeDifficulty;
  points: number;
  reason: string;
  action_url: string;
  related_lesson_slug?: string | null;
  related_lab_slug?: string | null;
}

export type CtfChallengeAttempt = ChallengeAttempt;
