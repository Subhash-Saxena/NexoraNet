export type RuleStatus = 'ENABLED' | 'DISABLED' | 'TESTING'

export type RuleCategory =
  | 'TCP'
  | 'UDP'
  | 'DNS'
  | 'ARP'
  | 'ICMP'
  | 'HTTP'
  | 'RECON'
  | 'SUSPICIOUS_PORT'
  | 'TRAFFIC'

export type AlertSeverity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type AlertConfidence = 'LOW' | 'MEDIUM' | 'HIGH'

export type AlertStatus = 'NEW' | 'ACKNOWLEDGED' | 'INVESTIGATING' | 'CLOSED' | 'FALSE_POSITIVE'

export type DetectionRunStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'

export type EvidenceType =
  | 'PACKET'
  | 'FLOW'
  | 'STATISTIC'
  | 'DNS_QUERY'
  | 'TCP_FLAG'
  | 'ARP_ENTRY'

export interface DetectionRule {
  id: number
  rule_id: string
  name: string
  description: string
  category: RuleCategory | string
  severity: AlertSeverity | string
  status: RuleStatus | string
  logic_type: string
  threshold_config: Record<string, unknown>
  mitre_attack_id?: string | null
  mitre_technique?: string | null
  explanation_template?: string | null
  investigation_steps?: string[] | null
  is_builtin: boolean
  created_at?: string
  updated_at?: string
}

export interface AlertEvidenceItem {
  id: number
  alert_id: number
  evidence_type: EvidenceType | string
  packet_number?: number | null
  timestamp?: number | null
  protocol?: string | null
  source_ip?: string | null
  destination_ip?: string | null
  source_port?: number | null
  destination_port?: number | null
  evidence_payload?: Record<string, unknown> | null
  summary: string
  created_at?: string
}

export interface AlertNoteItem {
  id: number
  alert_id: number
  user_id?: number | null
  author_name?: string | null
  note: string
  created_at: string
  updated_at?: string
}

export interface AlertStatusHistoryItem {
  id: number
  alert_id: number
  user_id?: number | null
  old_status?: AlertStatus | string | null
  new_status: AlertStatus | string
  reason?: string | null
  created_at: string
}

export interface DetectionAlertListItem {
  id: number
  run_id: number
  rule_id: number
  rule_code?: string | null
  capture_id?: number | null
  title: string
  category: RuleCategory | string
  severity: AlertSeverity | string
  confidence: AlertConfidence | string
  status: AlertStatus | string
  source_ip?: string | null
  source_port?: number | null
  destination_ip?: string | null
  destination_port?: number | null
  protocol?: string | null
  first_seen_timestamp?: number | null
  last_seen_timestamp?: number | null
  packet_count: number
  created_at: string
}

export interface DetectionAlertDetail extends DetectionAlertListItem {
  explanation: string
  mitre_attack_id?: string | null
  mitre_technique?: string | null
  investigation_steps: string[]
  evidence: AlertEvidenceItem[]
  notes: AlertNoteItem[]
  status_history: AlertStatusHistoryItem[]
}

export interface DetectionRunResponse {
  id: number
  source_type: string
  capture_id?: number | null
  status: DetectionRunStatus | string
  packets_analyzed: number
  alerts_generated: number
  execution_time_ms: number
  rule_ids_evaluated?: string[] | null
  summary_metadata?: Record<string, unknown> | null
  error_message?: string | null
  created_at: string
  completed_at?: string | null
}

export interface DetectionStats {
  total_runs: number
  total_alerts: number
  active_alerts: number
  alerts_by_severity: Record<AlertSeverity, number>
  alerts_by_category: Record<string, number>
  alerts_by_status: Record<AlertStatus, number>
  total_rules: number
  active_rules: number
}

export interface DetectionRuleTestRequest {
  rule_id: string
  capture_id?: number | null
  threshold_config?: Record<string, unknown> | null
}

export interface DetectionRuleTestResponse {
  rule_id: string
  matches_found: number
  simulated_alerts: Array<{
    title: string
    category: string
    severity: string
    confidence: string
    explanation: string
    source_ip?: string | null
    destination_ip?: string | null
    packet_count: number
    evidence_count: number
    investigation_steps: string[]
  }>
  execution_time_ms: number
}
