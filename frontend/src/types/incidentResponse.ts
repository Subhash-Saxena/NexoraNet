/**
 * STEP 17: Incident Response, Case Management & MITRE ATT&CK Investigation Types
 */

export type IncidentStatus =
  | 'NEW'
  | 'TRIAGED'
  | 'INVESTIGATING'
  | 'CONTAINMENT'
  | 'ERADICATION'
  | 'RECOVERY'
  | 'MONITORING'
  | 'RESOLVED'
  | 'CLOSED'
  | 'FALSE_POSITIVE'

export type IncidentSeverity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN'

export type IncidentClassification =
  | 'BENIGN'
  | 'SUSPICIOUS'
  | 'CONFIRMED_INCIDENT'
  | 'FALSE_POSITIVE'
  | 'UNDETERMINED'

export type IncidentType =
  | 'NETWORK_INTRUSION'
  | 'SUSPICIOUS_LOGIN'
  | 'MALWARE_INDICATOR'
  | 'CREDENTIAL_ATTACK'
  | 'PHISHING'
  | 'DATA_EXFILTRATION_PATTERN'
  | 'POLICY_VIOLATION'
  | 'ENDPOINT_COMPROMISE'
  | 'DNS_ANOMALY'
  | 'SUSPICIOUS_PROCESS'
  | 'MULTI_STAGE_ACTIVITY'
  | 'OTHER'

export type IncidentPhase =
  | 'PREPARATION'
  | 'DETECTION_ANALYSIS'
  | 'CONTAINMENT_ERADICATION_RECOVERY'
  | 'POST_INCIDENT_ACTIVITY'

export type ResponseActionCategory = 'CONTAINMENT' | 'ERADICATION' | 'RECOVERY'

export type ResponseActionStatus = 'PROPOSED' | 'APPROVED' | 'EXECUTED' | 'REVERTED' | 'CANCELLED'

export type ResponseActionType =
  | 'SIMULATE_HOST_ISOLATION'
  | 'SIMULATE_ACCOUNT_RESTRICTION'
  | 'SIMULATE_NETWORK_BLOCK'
  | 'SIMULATE_IOC_BLOCK'
  | 'SIMULATE_SESSION_REVOCATION'
  | 'SIMULATE_REMOVE_INDICATOR'
  | 'SIMULATE_REMOVE_PERSISTENCE'
  | 'SIMULATE_RESET_CREDENTIAL'
  | 'SIMULATE_CLEAN_HOST'
  | 'SIMULATE_RESTORE_HOST'
  | 'SIMULATE_RESTORE_SERVICE'
  | 'SIMULATE_REENABLE_ACCOUNT'
  | 'SIMULATE_RESTORE_NETWORK'

export type IncidentEvidenceType =
  | 'ALERT'
  | 'PACKET'
  | 'PCAP'
  | 'FLOW'
  | 'DNS_EVENT'
  | 'HTTP_EVENT'
  | 'TLS_EVENT'
  | 'SIEM_EVENT'
  | 'ENDPOINT_EVENT'
  | 'PROCESS_EVENT'
  | 'FILE_EVENT'
  | 'AUTH_EVENT'
  | 'IOC'
  | 'DETECTION'
  | 'NOTE'
  | 'SCREENSHOT_REFERENCE'
  | 'SIMULATION_EVENT'

export type IncidentEvidenceRelevance = 'SUPPORTING' | 'CONTRADICTING' | 'CONTEXT' | 'INCONCLUSIVE'

export type EvidenceAuditAction =
  | 'ATTACHED'
  | 'VIEWED'
  | 'ANNOTATED'
  | 'LINKED'
  | 'UNLINKED'
  | 'HASH_VERIFIED'

export type MitreMappingConfidence =
  | 'OBSERVED_EVIDENCE'
  | 'HYPOTHESIS_SUGGESTED'
  | 'ANALYST_INFERRED'

// ---------------------------------------------------------------------------
// MITRE ATT&CK
// ---------------------------------------------------------------------------
export interface AttackTechnique {
  id: number
  technique_id: string
  tactic_id: number
  name: string
  description: string
  detection_guidance?: string | null
  mitigation_guidance?: string | null
  is_subtechnique: boolean
  parent_technique_id?: string | null
  platforms?: string | null
  data_sources?: string | null
  external_url?: string | null
}

export interface AttackTactic {
  id: number
  tactic_id: string
  name: string
  description: string
  external_url?: string | null
  display_order: number
  techniques: AttackTechnique[]
}

export interface IncidentTechniqueMapping {
  id: number
  incident_id: number
  technique_id: number
  mapping_confidence: MitreMappingConfidence | string
  evidence_summary?: string | null
  phase?: string | null
  mapped_at: string
  technique?: AttackTechnique
}

export interface MatrixTechniqueCoverage {
  id: number
  technique_id: string
  name: string
  is_subtechnique: boolean
  is_mapped: boolean
}

export interface MatrixTacticColumn {
  tactic_id: string
  name: string
  display_order: number
  techniques: MatrixTechniqueCoverage[]
  mapped_count: number
  total_count: number
}

export interface MatrixCoverageResponse {
  incident_id?: number | null
  tactics: MatrixTacticColumn[]
  total_techniques: number
  covered_techniques: number
  coverage_percentage: number
}

// ---------------------------------------------------------------------------
// Playbooks
// ---------------------------------------------------------------------------
export interface IncidentPlaybook {
  id: number
  playbook_id: string
  title: string
  description: string
  category: string
  severity_guidance: IncidentSeverity | string
  primary_tactic_id?: string | null
  phases_definition: string
  checklist_json: string
  recommended_actions_json: string
  version: string
  is_active: boolean
}

// ---------------------------------------------------------------------------
// Evidence & Chain of Custody
// ---------------------------------------------------------------------------
export interface EvidenceAuditLog {
  id: number
  evidence_id: number
  action: EvidenceAuditAction | string
  details?: string | null
  timestamp: string
}

export interface IncidentEvidence {
  id: number
  evidence_id: string
  incident_id: number
  title: string
  description: string
  evidence_type: IncidentEvidenceType | string
  source_engine: string
  source_id?: string | null
  source_ref?: string | null
  hash_sha256?: string | null
  relevance: IncidentEvidenceRelevance | string
  is_contained: boolean
  collected_at: string
  data_payload?: string | null
  audit_logs?: EvidenceAuditLog[]
}

// ---------------------------------------------------------------------------
// Timeline
// ---------------------------------------------------------------------------
export interface IncidentTimelineEvent {
  id: number
  incident_id: number
  timestamp: string
  title: string
  description: string
  event_category: string
  source: string
  source_id?: string | null
  mitre_technique_id?: string | null
  is_milestone: boolean
}

// ---------------------------------------------------------------------------
// Response Actions (Simulation Only)
// ---------------------------------------------------------------------------
export interface ResponseAction {
  id: number
  action_id: string
  incident_id: number
  category: ResponseActionCategory | string
  action_type: ResponseActionType | string
  target_type: string
  target_identifier: string
  status: ResponseActionStatus | string
  simulation_only: boolean
  reason: string
  risk_assessment?: string | null
  expected_impact?: string | null
  simulated_outcome?: string | null
  executed_at?: string | null
  reverted_at?: string | null
}

// ---------------------------------------------------------------------------
// Hypotheses & Findings
// ---------------------------------------------------------------------------
export interface IncidentHypothesis {
  id: number
  hypothesis_id: string
  incident_id: number
  statement: string
  status: 'PROPOSED' | 'SUPPORTED' | 'NOT_SUPPORTED' | 'INCONCLUSIVE' | string
  confidence: 'LOW' | 'MEDIUM' | 'HIGH' | string
  rationale?: string | null
  tested_at?: string | null
  concluded_at?: string | null
}

export interface IncidentFinding {
  id: number
  finding_id: string
  incident_id: number
  title: string
  description: string
  severity: IncidentSeverity | string
  confidence: 'LOW' | 'MEDIUM' | 'HIGH' | string
  affected_systems?: string | null
  affected_accounts?: string | null
  indicators_observed?: string | null
  mitre_technique?: string | null
  mitre_tactic?: string | null
}

export interface IncidentNote {
  id: number
  incident_id: number
  user_id?: number | null
  note: string
  created_at: string
}

export interface IncidentAlertLink {
  id: number
  incident_id: number
  alert_id: number
  role: string
  added_at: string
}

// ---------------------------------------------------------------------------
// Incident Ticket & Detailed Workbench State
// ---------------------------------------------------------------------------
export interface Incident {
  id: number
  incident_id: string
  title: string
  description: string
  incident_type: IncidentType | string
  severity: IncidentSeverity
  priority: string
  status: IncidentStatus
  phase: IncidentPhase
  classification: IncidentClassification
  case_id?: number | null
  assigned_to_id?: number | null
  playbook_id?: number | null
  lead_analyst?: string | null
  detected_at: string
  contained_at?: string | null
  eradicated_at?: string | null
  recovered_at?: string | null
  closed_at?: string | null
  summary?: string | null
  impact_assessment?: string | null
  root_cause?: string | null
  lessons_learned?: string | null
  recommendations?: string | null
  simulation_mode: boolean
  playbook?: IncidentPlaybook | null
  alerts?: IncidentAlertLink[]
  evidence?: IncidentEvidence[]
  timeline_events?: IncidentTimelineEvent[]
  hypotheses?: IncidentHypothesis[]
  findings?: IncidentFinding[]
  response_actions?: ResponseAction[]
  technique_mappings?: IncidentTechniqueMapping[]
  notes?: IncidentNote[]
}

export interface IncidentListResponse {
  items: Incident[]
  total: number
  skip: number
  limit: number
}

export interface IncidentMetrics {
  total_incidents: number
  active_incidents: number
  closed_incidents: number
  by_status: Record<string, number>
  by_severity: Record<string, number>
  by_type: Record<string, number>
}

export interface IncidentReport {
  incident_id: string
  title: string
  severity: string
  status: string
  phase: string
  classification: string
  lead_analyst?: string | null
  detected_at: string
  contained_at?: string | null
  closed_at?: string | null
  tactics_observed: string[]
  techniques_observed: Array<{
    technique_id: string
    name: string
    confidence: string
    evidence?: string | null
  }>
  evidence_count: number
  evidence_items: Array<{
    evidence_id: string
    title: string
    type: string
    source: string
    hash_sha256?: string | null
    relevance: string
  }>
  timeline_entries: Array<{
    timestamp: string
    title: string
    category: string
    is_milestone: boolean
  }>
  actions_taken: Array<{
    action_id: string
    type: string
    category: string
    target: string
    status: string
    executed_at?: string | null
    outcome?: string | null
  }>
  hypotheses_tested: Array<{
    id: string
    statement: string
    status: string
    confidence: string
    rationale?: string | null
  }>
  findings: Array<{
    id: string
    title: string
    severity: string
    affected_systems?: string | null
    mitre_technique?: string | null
  }>
  markdown_report: string
  generated_at: string
}
