/**
 * Step 15 SIEM & Security Log Analysis Engine TypeScript Definitions.
 */

export type LogSourceType =
  | 'WINDOWS_SECURITY'
  | 'WINDOWS_SYS'
  | 'LINUX_AUTH'
  | 'LINUX_SYSLOG'
  | 'LINUX_SSH'
  | 'FIREWALL'
  | 'DNS'
  | 'WEB_SERVER'
  | 'APPLICATION'
  | 'IDS'
  | 'DATABASE'
  | 'IDENTITY_PROVIDER'

export type LogSourceStatus = 'ACTIVE' | 'DEGRADED' | 'INACTIVE' | 'ARCHIVED'

export type RawLogFormat =
  | 'JSON'
  | 'CSV'
  | 'SYSLOG'
  | 'WINDOWS_EVENT_XML'
  | 'CEF_LIKE'
  | 'GENERIC_TEXT'

export type SecurityEventCategory =
  | 'AUTHENTICATION'
  | 'FIREWALL'
  | 'NETWORK'
  | 'DNS'
  | 'WEB'
  | 'PROCESS'
  | 'FILE'
  | 'REGISTRY'
  | 'ACCOUNT'
  | 'PRIVILEGE'
  | 'SYSTEM'

export type SecurityEventAction =
  | 'LOGIN'
  | 'LOGIN_FAILURE'
  | 'LOGOUT'
  | 'CONNECTION'
  | 'CONNECTION_BLOCKED'
  | 'DNS_QUERY'
  | 'PROCESS_START'
  | 'FILE_READ'
  | 'FILE_WRITE'
  | 'ACCOUNT_CREATED'
  | 'ACCOUNT_DISABLED'
  | 'PRIVILEGE_CHANGE'
  | 'SERVICE_START'

export type SecurityEventSeverity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type SecurityLogDatasetType =
  | 'AUTHENTICATION_FOCUS'
  | 'NETWORK_FOCUS'
  | 'MIXED_SOC_INCIDENT'
  | 'LATERAL_MOVEMENT'
  | 'EXFILTRATION'
  | 'BRUTE_FORCE'

export type LogCorrelationRuleStatus = 'ENABLED' | 'DISABLED' | 'TESTING'

export type CorrelationAlertStatus =
  | 'NEW'
  | 'ACKNOWLEDGED'
  | 'ESCALATED'
  | 'RESOLVED'
  | 'FALSE_POSITIVE'

export interface LogSource {
  id: number
  stable_id: string
  name: string
  description: string
  source_type: LogSourceType | string
  platform: string
  vendor: string
  version?: string | null
  status: LogSourceStatus | string
  is_synthetic: boolean
  created_at: string
  updated_at: string
}

export interface SecurityLogDataset {
  id: number
  stable_id: string
  name: string
  description: string
  dataset_type: SecurityLogDatasetType | string
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | string
  event_count: number
  start_time?: string | null
  end_time?: string | null
  is_synthetic: boolean
  created_at: string
}

export interface SecurityEvent {
  id: number
  event_id: string
  timestamp: string
  event_type: string
  event_category: SecurityEventCategory | string
  source_type: LogSourceType | string
  host?: string | null
  username?: string | null
  source_ip?: string | null
  source_port?: number | null
  destination_ip?: string | null
  destination_port?: number | null
  protocol?: string | null
  action?: SecurityEventAction | string | null
  status?: string | null
  severity: SecurityEventSeverity | string
  process_name?: string | null
  domain?: string | null
  message?: string | null
  dataset_id: number
}

export interface SecurityEventDetail extends SecurityEvent {
  parent_process?: string | null
  command_summary?: string | null
  file_name?: string | null
  file_hash?: string | null
  url?: string | null
  authentication_method?: string | null
  result?: string | null
  metadata_json?: string | null
  raw_event_id?: number | null
  source_id?: number | null
  raw_message?: string | null
}

export interface QueryCondition {
  field: string
  operator: '=' | '!=' | 'CONTAINS' | 'STARTSWITH' | '>' | '<' | '>=' | '<='
  value: string | number
}

export interface SiemSearchRequest {
  dataset_id?: number | null
  conditions?: QueryCondition[] | null
  logical_op?: 'AND' | 'OR'
  not_conditions?: QueryCondition[] | null
  search_text?: string | null
  time_preset?: 'ALL' | 'LAST_15M' | 'LAST_1H' | 'LAST_24H' | 'LAST_7D' | string | null
  start_time?: string | null
  end_time?: string | null
  quick_filter?: string | null
  limit?: number
  offset?: number
  sort_by?: string
  sort_asc?: boolean
}

export interface SiemSearchResponse {
  total: number
  limit: number
  offset: number
  execution_time_ms: number
  human_readable: string
  events: SecurityEvent[]
}

export interface TopEntityItem {
  name: string
  count: number
}

export interface TimeSeriesBucket {
  bucket: string
  timestamp: string
  total: number
  auth_failures: number
  firewall_blocks: number
  dns_queries: number
}

export interface SiemAggregations {
  total_events: number
  auth_failures: number
  firewall_blocks: number
  dns_queries: number
  high_severity_count: number
  by_severity: Record<string, number>
  by_source_type: Record<string, number>
  by_category: Record<string, number>
  top_source_ips: TopEntityItem[]
  top_dest_ports: TopEntityItem[]
  top_hosts: TopEntityItem[]
  top_users: TopEntityItem[]
  top_domains: TopEntityItem[]
  timeline: TimeSeriesBucket[]
}

export interface LogCorrelationRule {
  id: number
  stable_id: string
  name: string
  description: string
  category: string
  severity: SecurityEventSeverity | string
  confidence: string
  status: LogCorrelationRuleStatus | string
  version: string
  logic: string
  time_window_seconds: number
  explanation: string
  created_at: string
  updated_at: string
}

export interface CorrelationAlert {
  id: number
  alert_id: string
  rule_id: number
  dataset_id: number
  timestamp: string
  title: string
  category: string
  severity: SecurityEventSeverity | string
  confidence: string
  status: CorrelationAlertStatus | string
  event_count: number
  source_context?: string | null
  evidence_summary: string
  matched_event_ids?: string | null
  soc_alert_id?: number | null
  created_at: string
}

export interface SavedSearch {
  id: number
  name: string
  description?: string | null
  query_definition: string
  owner_id?: number | null
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface SearchHistoryItem {
  id: number
  user_id?: number | null
  query_definition: string
  timestamp: string
  dataset_id?: number | null
  result_count: number
  execution_time_ms: number
}

export interface SIEMLabScenario {
  id: number
  slug: string
  title: string
  description: string
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | string
  dataset_id: number
  objectives: string
  expected_event_count: number
  hints?: string | null
  recommended_query?: string | null
}

export interface SIEMLabValidateRequest {
  executed_query: Record<string, unknown>
  findings_notes?: string | null
  identified_entity?: string | null
}

export interface SIEMLabValidateResponse {
  success: boolean
  score: number
  feedback: string
  criteria: Record<string, boolean>
}

export interface DatasetImportRequest {
  dataset_id: number
  content: string
  format: string
  source_id?: number | null
}

export interface RuleEvaluationResult {
  rule_id: number
  rule_code: string
  rule_name: string
  matching_events_count: number
  sample_events: SecurityEvent[]
  evaluation_message: string
}

export interface EscalationResult {
  status: string
  investigation_code?: string
  hunt_code?: string
  redirect_url: string
  extracted_iocs?: Array<{ ioc_type: string; value: string; indicator_id: number }>
}
