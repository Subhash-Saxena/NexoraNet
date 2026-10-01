/**
 * Type definitions for Step 12 SOC Dashboard, Alert Queue, Triage, and Investigations.
 */

export type TrainingPriority = 'P1' | 'P2' | 'P3' | 'P4'

export type TriageClassification =
  | 'UNREVIEWED'
  | 'BENIGN'
  | 'SUSPICIOUS'
  | 'FALSE_POSITIVE'
  | 'REQUIRES_MORE_DATA'
  | 'CLOSED'

export type InvestigationStatus = 'OPEN' | 'INVESTIGATING' | 'PENDING' | 'RESOLVED' | 'CLOSED'

export type InvestigationAlertRelationship = 'PRIMARY' | 'RELATED' | 'CONTEXT'

export type HypothesisStatus = 'UNTESTED' | 'SUPPORTED' | 'NOT_SUPPORTED' | 'INCONCLUSIVE'

export type FindingConfidence = 'LOW' | 'MEDIUM' | 'HIGH'

export type CaseStatus = 'OPEN' | 'INVESTIGATING' | 'PENDING' | 'RESOLVED' | 'CLOSED'

export type NotificationType =
  | 'ALERT_ASSIGNED'
  | 'ALERT_ESCALATED'
  | 'INVESTIGATION_OPENED'
  | 'CASE_CREATED'
  | 'CHALLENGE_EVALUATED'

export interface SocOverviewMetrics {
  total_alerts: number
  open_alerts: number
  investigating_alerts: number
  closed_alerts: number
  p1_alerts: number
  p2_alerts: number
  active_rules_count: number
  open_investigations_count: number
  open_cases_count: number
}

export interface LearningRecommendation {
  title: string
  reason: string
  action_link: string
  category: string
}

export interface SocOverviewResponse {
  platform: string
  environment_status: string
  metrics: SocOverviewMetrics
  learning_recommendations: LearningRecommendation[]
}

export interface SocStatisticsResponse {
  alerts_by_severity: Record<string, number>
  alerts_by_priority: Record<string, number>
  alerts_by_status: Record<string, number>
  alerts_by_classification: Record<string, number>
  alerts_by_category: Record<string, number>
  top_sources: Array<{ ip: string; count: number }>
  top_destinations: Array<{ ip: string; count: number }>
  recent_alert_volume: Array<{ hour: string; count: number }>
}

export interface SocActivityItem {
  id: string
  timestamp: string
  activity_type: string
  title: string
  description: string
  actor_name: string
  entity_type: string
  entity_id: number | string
}

export interface EndpointContext {
  ip: string
  packet_count: number
  byte_count: number
  protocols: string[]
  ports: number[]
  first_seen?: number | null
  last_seen?: number | null
}

export interface NetworkContext {
  source?: EndpointContext | null
  destination?: EndpointContext | null
  conversation_summary?: string | null
}

export interface AlertTimelineEvent {
  timestamp: string
  time_display: string
  event_type: string
  title: string
  description: string
  actor_name: string
}

export interface RelatedAlertItem {
  id: number
  title: string
  severity: string
  priority: string
  correlation_reason: string
}

export interface SocAlertItem {
  id: number
  run_id?: number | null
  rule_id?: number | null
  rule_code?: string | null
  capture_id?: number | null
  title: string
  severity: string
  priority: TrainingPriority
  priority_reason?: string | null
  confidence: string
  status: string
  classification: TriageClassification
  source_ip?: string | null
  source_port?: number | null
  destination_ip?: string | null
  destination_port?: number | null
  protocol?: string | null
  packet_count?: number | null
  byte_count?: number | null
  evidence_count: number
  assigned_to_id?: number | null
  assigned_to_name?: string | null
  created_at: string
  updated_at: string
}

export interface SocAlertDetailResponse extends SocAlertItem {
  explanation: string
  mitre_attack_id?: string | null
  mitre_technique?: string | null
  investigation_steps: string[]
  rule_description?: string | null
  evidence: Array<{
    id: number
    evidence_type: string
    packet_id?: number | null
    packet_number?: number | null
    timestamp?: number | null
    summary?: string | null
    evidence_payload?: Record<string, unknown> | null
    created_at: string
  }>
  notes: Array<{
    id: number
    author: string
    note: string
    created_at: string
  }>
  status_history: Array<{
    id: number
    previous_status?: string | null
    new_status: string
    reason?: string | null
    actor: string
    created_at: string
  }>
  timeline: AlertTimelineEvent[]
  related_alerts: RelatedAlertItem[]
  network_context: NetworkContext
  investigations: InvestigationBriefItem[]
}

export interface InvestigationBriefItem {
  id: number
  investigation_id: string
  title: string
  status: string
  priority: string
  classification: string
  created_at: string
}

export interface InvestigationEvidenceItem {
  id: number
  investigation_id: number
  evidence_type: string
  reference_id?: string | null
  capture_id?: number | null
  packet_number?: number | null
  description: string
  evidence_data?: Record<string, unknown> | null
  created_at: string
}

export interface InvestigationHypothesisItem {
  id: number
  investigation_id: number
  hypothesis_text: string
  status: HypothesisStatus
  reasoning?: string | null
  supporting_evidence_ids: string[]
  created_by_name?: string | null
  created_at: string
  updated_at: string
}

export interface InvestigationFindingItem {
  id: number
  investigation_id: number
  title: string
  description: string
  evidence_summary?: string | null
  confidence: FindingConfidence
  created_by_name?: string | null
  created_at: string
}

export interface InvestigationNoteItem {
  id: number
  investigation_id: number
  user_id?: number | null
  author_name?: string | null
  note: string
  created_at: string
  updated_at: string
}

export interface InvestigationDetailResponse {
  id: number
  investigation_id: string
  title: string
  description: string
  status: InvestigationStatus
  priority: TrainingPriority
  classification: TriageClassification
  created_by_id?: number | null
  created_by_name?: string | null
  assigned_to_id?: number | null
  assigned_to_name?: string | null
  started_at: string
  closed_at?: string | null
  conclusion?: string | null
  recommendations?: string | null
  created_at: string
  updated_at: string
  alerts: SocAlertItem[]
  evidence: InvestigationEvidenceItem[]
  hypotheses: InvestigationHypothesisItem[]
  findings: InvestigationFindingItem[]
  notes: InvestigationNoteItem[]
  cases: Array<{
    id: number
    case_id: string
    title: string
    status: string
  }>
}

export interface CaseAlertItem {
  id: number
  alert_id: number
  title: string
  severity: string
  priority: string
  status: string
  classification: string
}

export interface CaseInvestigationItem {
  id: number
  investigation_id: number
  investigation_code: string
  title: string
  status: string
  priority: string
}

export interface CaseNoteItem {
  id: number
  user_id?: number | null
  author_name?: string | null
  note: string
  created_at: string
}

export interface CaseDetailResponse {
  id: number
  case_id: string
  title: string
  description: string
  status: CaseStatus
  priority: TrainingPriority
  created_by_id?: number | null
  created_by_name?: string | null
  assigned_to_id?: number | null
  assigned_to_name?: string | null
  created_at: string
  updated_at: string
  alerts: CaseAlertItem[]
  investigations: CaseInvestigationItem[]
  notes: CaseNoteItem[]
}

export interface CategoryCoverageItem {
  category: string
  rule_count: number
  rules: Array<{
    id: number
    rule_id: string
    name: string
    severity: string
    status: string
  }>
  mitre_tactics: string[]
  alert_count: number
}

export interface DetectionCoverageResponse {
  categories: CategoryCoverageItem[]
  total_rules: number
  total_categories: number
  total_alerts: number
}

export interface SocChallengeItem {
  id: number
  slug: string
  title: string
  difficulty: string
  category: string
  objective: string
  scenario_description: string
  capture_id?: number | null
  capture_name?: string | null
  mitre_attack_id?: string | null
  rubric_description?: string | null
}

export interface SocChallengeDetailResponse extends SocChallengeItem {
  expected_observations: string[]
  sample_alerts: SocAlertItem[]
}

export interface SocChallengeEvaluation {
  alert_triaged_score: number
  classification_accuracy_score: number
  hypothesis_validity_score: number
  evidence_linking_score: number
  conclusion_depth_score: number
  total_score: number
  percentage: number
  passed: boolean
  feedback_summary: string
  specific_tips: string[]
}

export interface TrainingDatasetItem {
  dataset_id: string
  name: string
  category: string
  description: string
  target_capture_name: string
}

export interface SocAuditLogItem {
  id: number
  actor_name: string
  action: string
  object_type: string
  object_id?: string | null
  details?: Record<string, unknown> | null
  created_at: string
}

export interface SocNotificationItem {
  id: number
  notification_type: NotificationType
  title: string
  message: string
  is_read: boolean
  action_link?: string | null
  created_at: string
}
