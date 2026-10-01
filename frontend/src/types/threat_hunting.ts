/**
 * Step 14 Threat Hunting & Investigation Workspace TypeScript Definitions
 */

export type HuntStatus = 'DRAFT' | 'READY' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'CANCELLED'

export type HuntDifficulty = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'

export type HuntDatasetType =
  | 'PCAP'
  | 'DETECTION_EVENTS'
  | 'SOC_ALERTS'
  | 'IOC_DATA'
  | 'SIMULATOR_EVENTS'
  | 'COMBINED'

export type HuntEventType =
  | 'NETWORK_CONNECTION'
  | 'DNS_QUERY'
  | 'DNS_RESPONSE'
  | 'HTTP_REQUEST'
  | 'TLS_EVENT'
  | 'TCP_EVENT'
  | 'UDP_EVENT'
  | 'ICMP_EVENT'
  | 'ARP_EVENT'
  | 'DETECTION_ALERT'
  | 'SOC_ALERT'
  | 'IOC_OBSERVATION'
  | 'SIMULATOR_EVENT'

export type HuntHypothesisStatus = 'OPEN' | 'SUPPORTED' | 'NOT_SUPPORTED' | 'INCONCLUSIVE'

export type HuntConfidence = 'LOW' | 'MEDIUM' | 'HIGH'

export type HuntEvidenceType =
  | 'EVENT'
  | 'ALERT'
  | 'IOC'
  | 'TIMELINE'
  | 'PCAP_PACKET'
  | 'DNS_EVENT'
  | 'HTTP_EVENT'
  | 'TLS_EVENT'
  | 'SIMULATOR_EVENT'

export type HuntEvidenceRelevance = 'SUPPORTING' | 'CONTRADICTING' | 'CONTEXT'

export type HuntFindingType =
  | 'OBSERVATION'
  | 'PATTERN'
  | 'ANOMALY'
  | 'IOC_CORRELATION'
  | 'NETWORK_BEHAVIOR'
  | 'DETECTION_GAP'
  | 'INCONCLUSIVE'

export type HuntConclusionDisposition =
  | 'SUPPORTED'
  | 'NOT_SUPPORTED'
  | 'INCONCLUSIVE'
  | 'INSUFFICIENT_DATA'

export interface HuntDataset {
  id: number
  dataset_id: string
  name: string
  description: string
  dataset_type: string
  source: string
  event_count: number
  status: string
  time_start?: string | null
  time_end?: string | null
  metadata_json?: string | null
  created_at: string
}

export interface DatasetAnalytics {
  dataset_id: number
  code: string
  name: string
  total_events: number
  time_range: { start: string | null; end: string | null }
  protocols: Record<string, number>
  event_types: Record<string, number>
  top_source_ips: { ip: string; count: number }[]
  top_destination_ips: { ip: string; count: number }[]
  top_domains: { domain: string; count: number }[]
}

export interface HuntEvent {
  id: number
  event_id: string
  dataset_id: number
  event_type: string
  timestamp: string
  source_ip?: string | null
  destination_ip?: string | null
  source_port?: number | null
  destination_port?: number | null
  protocol?: string | null
  domain?: string | null
  url?: string | null
  ioc_id?: number | null
  alert_id?: number | null
  soc_alert_id?: number | null
  pcap_capture_id?: number | null
  pcap_packet_number?: number | null
  severity?: string | null
  action?: string | null
  status?: string | null
  summary?: string | null
  payload_preview?: string | null
  metadata_json?: string | null
}

export interface EventCondition {
  field: string
  operator: string
  value: any
}

export interface HuntQueryRequest {
  dataset_id?: number | null
  conditions?: EventCondition[]
  query_string?: string | null
  search_text?: string | null
  conjunction?: 'AND' | 'OR'
  limit?: number
  offset?: number
  sort_by?: string
  sort_desc?: boolean
}

export interface HuntQueryResponse {
  total: number
  limit: number
  offset: number
  events: HuntEvent[]
  took_ms: number
  conditions_used: EventCondition[]
  explanation: string
}

export interface ThreatHunt {
  id: number
  hunt_id: string
  title: string
  description: string
  objective: string
  status: HuntStatus
  difficulty: HuntDifficulty
  dataset_id?: number | null
  user_id: number
  scenario_slug?: string | null
  initial_pivot_type?: string | null
  initial_pivot_value?: string | null
  query_history?: string | null
  conclusion?: string | null
  conclusion_disposition?: HuntConclusionDisposition | null
  score?: number | null
  score_breakdown?: string | null
  started_at?: string | null
  completed_at?: string | null
  created_at: string
  updated_at: string
}

export interface HuntHypothesis {
  id: number
  hunt_id: number
  title: string
  description: string
  status: HuntHypothesisStatus
  confidence: HuntConfidence
  analyst_reasoning?: string | null
  created_at: string
  updated_at: string
}

export interface HuntEvidence {
  id: number
  hunt_id: number
  hypothesis_id?: number | null
  evidence_type: string
  source_id: string
  description: string
  relevance: HuntEvidenceRelevance
  analyst_note?: string | null
  data_snapshot?: string | null
  created_at: string
}

export interface HuntFinding {
  id: number
  hunt_id: number
  title: string
  description: string
  finding_type: string
  confidence: HuntConfidence
  evidence_count: number
  mitigation_recommendation?: string | null
  created_at: string
}

export interface HuntNote {
  id: number
  hunt_id: number
  user_id: number
  author_name: string
  content: string
  related_event_id?: string | null
  related_alert_id?: number | null
  related_ioc_id?: number | null
  related_hypothesis_id?: number | null
  created_at: string
}

export interface ThreatHuntDetail extends ThreatHunt {
  dataset?: HuntDataset | null
  hypotheses: HuntHypothesis[]
  evidence: HuntEvidence[]
  findings: HuntFinding[]
  notes: HuntNote[]
}

export interface TimelineBucket {
  time_slot: string
  event_count: number
  alert_count: number
  ioc_count: number
  breakdown: Record<string, number>
}

export interface TimelineMilestone {
  event_id: string
  timestamp: string
  event_type: string
  summary?: string | null
  severity: string
  source_ip?: string | null
  destination_ip?: string | null
}

export interface HuntTimelineResponse {
  total_events: number
  interval: string
  buckets: TimelineBucket[]
  milestones: TimelineMilestone[]
}

export interface GraphNode {
  id: string
  label: string
  type: string
  severity: string
  metadata: Record<string, any>
}

export interface GraphEdge {
  source: string
  target: string
  relationship: string
  label: string
}

export interface EntityGraphResponse {
  nodes: GraphNode[]
  edges: GraphEdge[]
  focus?: string | null
}

export interface PivotResponse {
  entity_type: string
  entity_value: string
  matched_events_count: number
  matched_events: {
    event_id: string
    timestamp: string
    event_type: string
    protocol?: string | null
    source_ip?: string | null
    destination_ip?: string | null
    summary?: string | null
  }[]
  matched_iocs: {
    id: number
    indicator_id: string
    type: string
    value: string
    severity: string
    classification: string
  }[]
  matched_alerts: {
    id: number
    alert_id: string
    title: string
    severity: string
    created_at: string
  }[]
  suggested_questions: string[]
}

export interface RubricDimension {
  score: number
  max: number
  feedback: string[]
}

export interface HuntScoreResponse {
  hunt_id: string
  total_score: number
  max_score: number
  grade: 'A' | 'B' | 'C' | 'D' | 'F'
  breakdown: {
    evidence_quality?: RubricDimension
    correlation_and_pivoting?: RubricDimension
    hypothesis_testing?: RubricDimension
    documentation_and_findings?: RubricDimension
    conclusion_soundness?: RubricDimension
  }
}

export interface HuntScenario {
  slug: string
  title: string
  difficulty: HuntDifficulty
  category: string
  estimated_minutes: number
  mitre_tactics: string[]
  mitre_techniques: string[]
  brief: string
  objective: string
  background: string
  dataset_code: string
  initial_pivot_type?: string | null
  initial_pivot_value?: string | null
  guided_questions: string[]
  suggested_hypotheses: { title: string; description: string }[]
  expected_findings: { title: string; description: string; finding_type: string; mitigation_recommendation?: string }[]
}

export interface HuntOverviewResponse {
  total_hunts: number
  active_hunts: number
  completed_hunts: number
  total_datasets: number
  total_events: number
  total_scenarios: number
  recent_hunts: ThreatHunt[]
}
