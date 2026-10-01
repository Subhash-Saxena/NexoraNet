/**
 * Types for Step 18 SOAR Security Automation Engine.
 */

export type PlaybookStatus = 'ENABLED' | 'DISABLED' | 'DRAFT' | 'ARCHIVED';

export type PlaybookRiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type PlaybookTriggerType =
  | 'ALERT_CREATED'
  | 'ALERT_THRESHOLD'
  | 'IOC_OBSERVED'
  | 'INCIDENT_CREATED'
  | 'INCIDENT_ESCALATED'
  | 'CASE_UPDATED'
  | 'DETECTION_MATCH'
  | 'CORRELATION_MATCH'
  | 'SCHEDULED_TIMER'
  | 'MANUAL';

export type PlaybookExecutionStatus =
  | 'QUEUED'
  | 'RUNNING'
  | 'WAITING_APPROVAL'
  | 'APPROVED'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED';

export type StepExecutionStatus =
  | 'PENDING'
  | 'RUNNING'
  | 'WAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'SKIPPED';

export type ApprovalStatus = 'PENDING' | 'APPROVED' | 'REJECTED' | 'CANCELLED';

export interface AutomationStep {
  id: number;
  playbook_id: number;
  step_order: number;
  name: string;
  description?: string | null;
  action_type: string;
  parameters_json?: string | null;
  condition_json?: string | null;
  requires_approval: boolean;
  timeout_seconds: number;
  enabled: boolean;
  on_failure: 'STOP' | 'CONTINUE';
  retry_count: number;
  created_at: string;
  updated_at: string;
}

export interface AutomationPlaybook {
  id: number;
  playbook_id: string;
  name: string;
  description: string;
  category: string;
  version: string;
  status: PlaybookStatus;
  trigger_type: PlaybookTriggerType;
  trigger_filter_json?: string | null;
  risk_level: PlaybookRiskLevel;
  requires_approval: boolean;
  is_system: boolean;
  simulation_only: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  steps_count?: number;
  steps?: AutomationStep[];
}

export interface ExecutionStepLog {
  id: number;
  execution_id: number;
  step_id?: number | null;
  step_order: number;
  step_name: string;
  action_type: string;
  status: StepExecutionStatus;
  started_at: string;
  completed_at?: string | null;
  input_summary?: string | null;
  output_summary?: string | null;
  error_code?: string | null;
  error_message?: string | null;
  retry_attempt: number;
  simulation_only: boolean;
}

export interface PlaybookExecution {
  id: number;
  execution_id: string;
  playbook_id: number;
  playbook_identifier: string;
  playbook_name: string;
  trigger_source: string;
  source_id: string;
  status: PlaybookExecutionStatus;
  current_step_order: number;
  total_steps: number;
  requested_by: string;
  approved_by?: string | null;
  approval_status?: ApprovalStatus | null;
  approval_reason?: string | null;
  started_at: string;
  completed_at?: string | null;
  simulation_only: boolean;
  result_summary?: string | null;
  error_message?: string | null;
  artifacts_json?: string | null;
  step_logs?: ExecutionStepLog[];
}

export interface AutomationAuditLog {
  id: number;
  execution_id: string;
  action: string;
  actor: string;
  target_type: string;
  target_id: string;
  previous_state?: string | null;
  new_state?: string | null;
  reason?: string | null;
  simulation_only: boolean;
  timestamp: string;
}

export interface DryRunStepResult {
  step_order: number;
  step_name: string;
  action_type: string;
  condition_met: boolean;
  requires_approval: boolean;
  status_preview: string;
  parameters_preview: Record<string, any>;
}

export interface DryRunResponse {
  playbook_id: string;
  playbook_name: string;
  dry_run: boolean;
  total_steps: number;
  executable_steps: number;
  simulated_steps: DryRunStepResult[];
}

export interface SoarMetrics {
  total_playbooks: number;
  enabled_playbooks: number;
  total_executions: number;
  completed_executions: number;
  waiting_approval: number;
  failed_executions: number;
  success_rate_percent: number;
  analyst_hours_saved: number;
  top_playbooks: Array<{
    name: string;
    playbook_id: string;
    executions: number;
  }>;
}
