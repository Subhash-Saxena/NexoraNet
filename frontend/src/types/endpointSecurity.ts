/**
 * Step 16: Endpoint Security & Host Investigation Engine Types
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

export type EndpointPlatform = 'WINDOWS' | 'LINUX' | 'MACOS'

export type EndpointArchitecture = 'X86_64' | 'ARM64'

export type EndpointEnvironment =
  | 'DEVELOPMENT'
  | 'STAGING'
  | 'PRODUCTION'
  | 'WORKSTATION'
  | 'SERVER'

export type EndpointStatus =
  | 'ONLINE'
  | 'OFFLINE'
  | 'SUSPICIOUS'
  | 'ISOLATED_SIMULATED'

export type EndpointRiskLevel = 'NONE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'

export type EndpointEventCategory =
  | 'PROCESS'
  | 'AUTHENTICATION'
  | 'NETWORK'
  | 'DNS'
  | 'FILE'
  | 'REGISTRY'
  | 'SERVICE'
  | 'PERSISTENCE'
  | 'PRIVILEGE'
  | 'SECURITY'

export type EndpointEventType =
  | 'PROCESS_CREATE'
  | 'PROCESS_TERMINATE'
  | 'LOGON_SUCCESS'
  | 'LOGON_FAILED'
  | 'LOGOFF'
  | 'SOCKET_CONNECT'
  | 'SOCKET_LISTEN'
  | 'DNS_QUERY'
  | 'FILE_CREATE'
  | 'FILE_MODIFY'
  | 'FILE_DELETE'
  | 'REGISTRY_KEY_SET'
  | 'SERVICE_INSTALL'
  | 'SERVICE_START'
  | 'SCHEDULED_TASK_CREATE'
  | 'USER_PRIVILEGE_ELEVATION'
  | 'SUDO_COMMAND'
  | 'DEFENSE_EVASION_OBSERVED'

export type ProcessIntegrityLevel =
  | 'UNTRUSTED'
  | 'LOW'
  | 'MEDIUM'
  | 'HIGH'
  | 'SYSTEM'

export type FileAction = 'CREATED' | 'MODIFIED' | 'DELETED' | 'EXECUTED' | 'READ'

export type EvidenceRelevance = 'SUPPORTING' | 'REFUTING' | 'INCONCLUSIVE'

export type ThreatConfidence = 'LOW' | 'MEDIUM' | 'HIGH'

export type EndpointInvestigationStatus =
  | 'OPEN'
  | 'IN_PROGRESS'
  | 'WAITING'
  | 'COMPLETED'
  | 'CANCELLED'

export type EndpointInvestigationPriority = 'P1' | 'P2' | 'P3' | 'P4'

export type EndpointVerdict =
  | 'BENIGN'
  | 'SUSPICIOUS'
  | 'CONFIRMED_COMPROMISE'
  | 'FALSE_POSITIVE'
  | 'INCONCLUSIVE'

export interface EndpointHost {
  id: number
  stable_id: string
  hostname: string
  display_name: string | null
  platform: EndpointPlatform
  platform_version: string
  architecture: EndpointArchitecture
  environment: EndpointEnvironment
  status: EndpointStatus
  risk_level: EndpointRiskLevel
  ip_address: string
  mac_address: string
  os_build: string | null
  description: string | null
  last_activity_at: string | null
  is_synthetic: boolean
  created_at: string
  updated_at: string
}

export interface EndpointHostSummary {
  total_hosts: number
  platforms: Record<string, number>
  risk_levels: Record<string, number>
  environments: Record<string, number>
  total_events: number
  active_investigations: number
}

export interface EndpointHostOverview {
  host: EndpointHost
  counts: {
    processes: number
    network_connections: number
    dns_queries: number
    file_modifications: number
    services: number
    persistence_mechanisms: number
    authentication_events: number
    investigations: number
  }
}

export interface EndpointEvent {
  id: number
  stable_id: string
  event_id: string
  host_id: number
  timestamp: string
  event_category: EndpointEventCategory
  event_type: string
  severity: string
  action: string | null
  result: string | null
  process_name: string | null
  process_id: number | null
  parent_process_name: string | null
  parent_process_id: number | null
  command_line: string | null
  command_summary: string | null
  file_path: string | null
  file_hash: string | null
  username: string | null
  user_domain: string | null
  logon_id: string | null
  logon_type: string | null
  source_ip: string | null
  source_port: number | null
  destination_ip: string | null
  destination_port: number | null
  protocol: string | null
  domain: string | null
  query_type: string | null
  target_object: string | null
  new_value: string | null
  old_value: string | null
  service_name: string | null
  persistence_type: string | null
  integrity_level: ProcessIntegrityLevel | null
  raw_event_reference: string | null
  is_synthetic: boolean
  host_hostname?: string | null
}

export interface ProcessTreeNode {
  process_id: number
  process_name: string
  command_summary: string
  command_line: string
  user: string
  integrity_level: string
  spawned_at: string
  terminated_at: string | null
  file_hash: string | null
  children: ProcessTreeNode[]
}

export interface ProcessDetails {
  host: {
    id: number
    stable_id: string
    hostname: string
    platform: string
  }
  process_id: number
  process_name: string
  command_line: string
  integrity_level: string
  user: string
  parent: {
    process_id: number | null
    process_name: string | null
    command_line: string | null
  }
  children: Array<{
    process_id: number
    process_name: string
    command_line: string
    spawned_at: string
  }>
  network_connections: Array<{
    destination_ip: string
    destination_port: number
    protocol: string
    timestamp: string
  }>
  dns_queries: Array<{
    domain: string
    query_type: string
    timestamp: string
  }>
  file_modifications: Array<{
    file_path: string
    action: string
    file_hash: string
    timestamp: string
  }>
  security_context: {
    is_elevated: boolean
    has_network_activity: boolean
    has_suspicious_arguments: boolean
    flags: string[]
  }
}

export interface AuthenticationAnalysis {
  total_logons: number
  successful_logons: number
  failed_logons: number
  distinct_users: string[]
  distinct_source_ips: string[]
  brute_force_indicators: boolean
  pattern_status: string
  analyst_guidance: string
}

export interface EndpointHypothesis {
  id: number
  investigation_id: number
  statement: string
  status: string
  confidence: string
  analyst_notes: string | null
  created_at: string
  updated_at: string
}

export interface EndpointEvidence {
  id: number
  investigation_id: number
  hypothesis_id: number | null
  event_id: string
  observable_type: string
  observable_value: string
  description: string
  relevance: EvidenceRelevance
  collected_at: string
}

export interface EndpointFinding {
  id: number
  investigation_id: number
  title: string
  description: string
  severity: string
  mitre_technique: string | null
  created_at: string
}

export interface EndpointConclusion {
  id: number
  investigation_id: number
  summary: string
  verdict: EndpointVerdict
  lessons_learned: string | null
  training_score: number
  scored_at: string
}

export interface EndpointInvestigation {
  id: number
  stable_id: string
  host_id: number
  user_id: number
  title: string
  description: string
  status: EndpointInvestigationStatus
  priority: EndpointInvestigationPriority
  scenario_slug: string | null
  created_at: string
  updated_at: string
  completed_at: string | null
  host?: EndpointHost
  hypotheses?: EndpointHypothesis[]
  evidence?: EndpointEvidence[]
  findings?: EndpointFinding[]
  conclusion?: EndpointConclusion | null
}

export interface EndpointScenario {
  id: number
  scenario_id: string
  slug: string
  title: string
  difficulty: string
  category: string
  target_host_stable_id: string
  description: string
  background: string
  objectives: string[]
  hints: string[]
  estimated_minutes: number
  is_published: boolean
}

export interface ScenarioValidationResult {
  passed: boolean
  score: number
  rubric_evaluations: Record<string, boolean>
  feedback: string[]
  recommendations: string[]
}

export interface PivotIntelResponse {
  event_id: string
  host_id: number
  observables: Array<{
    type: string
    value: string
    found_in_threat_intel: boolean
    indicator_id: string | null
    classification: string
    confidence: string
    reputation_score: number
  }>
  analyst_guidance: string
}

export interface PivotHuntResponse {
  hunt_id: string
  title: string
  objective: string
  status: string
  initial_pivot_type: string
  initial_pivot_value: string
}

export interface PivotSocResponse {
  investigation_id: string
  title: string
  priority: string
  status: string
}
