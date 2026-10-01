/**
 * Types for Step 18 Advanced SOC Scenario Engine.
 */

export type ScenarioDifficulty = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'EXPERT';

export type ScenarioCategory =
  | 'MALWARE_INFECTION'
  | 'RANSOMWARE_OUTBREAK'
  | 'CREDENTIAL_ACCESS'
  | 'LATERAL_MOVEMENT'
  | 'DATA_EXFILTRATION'
  | 'WEB_COMPROMISE'
  | 'SUPPLY_CHAIN'
  | 'INSIDER_THREAT'
  | 'APT_CAMPAIGN';

export type ScenarioStage =
  | 'INITIAL_SIGNAL'
  | 'EVIDENCE_SELECTION'
  | 'CORRELATION'
  | 'HYPOTHESIS'
  | 'VALIDATION'
  | 'MITRE_MAPPING'
  | 'RESPONSE_DECISION'
  | 'OUTCOME'
  | 'LESSONS_LEARNED';

export type ScenarioAttemptStatus = 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';

export interface SocScenarioSummary {
  id: number;
  scenario_id: string;
  title: string;
  description: string;
  difficulty: ScenarioDifficulty;
  category: ScenarioCategory;
  estimated_duration_minutes: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface SocScenarioDetail extends SocScenarioSummary {
  learning_objectives: string;
  initial_signal_json: string;
  available_evidence_json: string;
  correlation_targets_json: string;
  hypotheses_options_json: string;
  mitre_techniques_json: string;
  response_options_json: string;
  scoring_rubric_json: string;
  hints_json: string;
  solution_explanation: string;
}

export interface ScenarioAttempt {
  id: number;
  attempt_id: string;
  scenario_id: number;
  scenario_identifier: string;
  scenario_title: string;
  user_id?: number | null;
  status: ScenarioAttemptStatus;
  current_stage: ScenarioStage;
  stage_data_json: string;
  hints_used: number;
  score: number;
  score_breakdown_json?: string | null;
  started_at: string;
  completed_at?: string | null;
}

export interface StageUpdateRequest {
  stage_name: string;
  data: Record<string, any>;
  advance_stage?: boolean;
}

export interface ScenarioHintResponse {
  hint: string;
  hints_used: number;
  remaining: number;
  penalty_applied: number;
  message?: string | null;
}

export interface ScenarioEvaluationResponse {
  attempt_id: string;
  scenario_id: string;
  scenario_title: string;
  status: string;
  score: number;
  max_score: number;
  passed: boolean;
  breakdown: Record<string, number>;
  feedback: string[];
  solution_explanation: string;
  completed_at?: string | null;
}

export interface ScenarioMetrics {
  total_scenarios: number;
  total_attempts: number;
  completed_attempts: number;
  avg_score: number;
  user_completed: number;
  difficulty_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
}
