/**
 * TypeScript types for Step 13 Threat Intelligence & IOC Investigation.
 */

export type IndicatorType = 'IP_ADDRESS' | 'DOMAIN' | 'URL' | 'FILE_HASH' | 'EMAIL_ADDRESS'
export type HashType = 'MD5' | 'SHA1' | 'SHA256' | 'SHA512'
export type IndicatorClassification = 'BENIGN' | 'SUSPICIOUS' | 'MALICIOUS' | 'FALSE_POSITIVE' | 'UNKNOWN'
export type ThreatIntelConfidence = 'LOW' | 'MEDIUM' | 'HIGH'
export type ThreatIntelSeverity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type IndicatorStatus = 'NEW' | 'ACTIVE' | 'EXPIRED' | 'REVOKED' | 'FALSE_POSITIVE' | 'UNKNOWN'
export type SourceReliability = 'UNKNOWN' | 'LOW' | 'MEDIUM' | 'HIGH'

export interface ThreatIntelSource {
  id: number
  name: string
  source_type: string
  description?: string | null
  reliability: SourceReliability
  enabled: boolean
  is_synthetic: boolean
  created_at: string
}

export interface IndicatorBrief {
  id: number
  indicator_id: string
  indicator_type: IndicatorType
  hash_type?: HashType | null
  value: string
  normalized_value: string
  display_value: string
  source_name: string
  classification: IndicatorClassification
  confidence: ThreatIntelConfidence
  severity: ThreatIntelSeverity
  status: IndicatorStatus
  mitre_attack_id?: string | null
  mitre_technique?: string | null
  is_synthetic: boolean
  first_seen?: string | null
  last_seen?: string | null
  created_at: string
}

export interface IndicatorObservation {
  id: number
  indicator_id: number
  capture_id?: number | null
  packet_number?: number | null
  alert_id?: number | null
  investigation_id?: number | null
  case_id?: number | null
  observation_type: string
  context_data?: string | null
  observed_at?: string | null
  created_at: string
}

export interface IndicatorTimelineEvent {
  id: number
  indicator_id: number
  event_type: string
  title: string
  description?: string | null
  actor_name: string
  event_timestamp: string
  created_at: string
}

export interface IndicatorNote {
  id: number
  indicator_id: number
  user_id?: number | null
  author_name: string
  note: string
  created_at: string
  updated_at: string
}

export interface IndicatorRelationship {
  id: number
  source_indicator_id: number
  target_indicator_id: number
  relationship_type: string
  description?: string | null
  confidence: string
  created_at: string
  target_indicator?: IndicatorBrief | null
}

export interface IndicatorDetail extends IndicatorBrief {
  false_positive_reason?: string | null
  description?: string | null
  tags?: string | null
  is_watched: boolean
  source?: ThreatIntelSource | null
  observations: IndicatorObservation[]
  outgoing_relationships: IndicatorRelationship[]
  incoming_relationships: IndicatorRelationship[]
  timeline_events: IndicatorTimelineEvent[]
  notes: IndicatorNote[]
}

export interface WatchlistItem {
  id: number
  indicator_id: number
  user_id: number
  reason: string
  added_by: string
  expires_at?: string | null
  created_at: string
  indicator?: IndicatorBrief | null
}

export interface ThreatIntelGraphNode {
  id: string
  label: string
  type: string
  severity: string
  details?: Record<string, any>
}

export interface ThreatIntelGraphLink {
  source: string
  target: string
  label: string
}

export interface ThreatIntelGraph {
  root_indicator_id: number
  nodes: ThreatIntelGraphNode[]
  links: ThreatIntelGraphLink[]
}

export interface ThreatIntelChallengeBrief {
  id: number
  slug: string
  title: string
  difficulty: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'
  category: string
  objective: string
  target_indicator_value: string
  expected_classification: string
  created_at: string
}

export interface ThreatIntelChallengeDetail extends ThreatIntelChallengeBrief {
  scenario_description: string
  expected_observations?: string | null
  rubric_description?: string | null
}

export interface ChallengeRubricDimension {
  score: number
  max: number
  feedback: string
}

export interface ChallengeRubricBreakdown {
  ioc_classification: ChallengeRubricDimension
  evidence_review: ChallengeRubricDimension
  threat_intel_interpretation: ChallengeRubricDimension
  correlation_context: ChallengeRubricDimension
  soc_conclusion: ChallengeRubricDimension
}

export interface ChallengeFeedback {
  total_score: number
  max_score: number
  passed: boolean
  passing_threshold: number
  breakdown: ChallengeRubricBreakdown
  educational_takeaway: string
}

export interface ChallengeAttempt {
  id: number
  challenge_id: number
  user_id: number
  selected_classification: string
  hypothesis_text: string
  evidence_notes: string
  conclusion: string
  score: number
  passed: boolean
  feedback?: string | null
  created_at: string
}

export interface ThreatIntelOverview {
  total_indicators: number
  by_classification: Record<string, number>
  by_type: Record<string, number>
  by_severity: Record<string, number>
  active_watchlists: number
  total_challenges: number
  recent_indicators: IndicatorBrief[]
}

export interface IndicatorImportResult {
  total_records: number
  imported: number
  skipped: number
  errors: Array<{ row_index: number; value: string; error: string }>
  sample_imported: Array<{ id: number; indicator_id: string; type: string; value: string; classification: string }>
}

export interface IndicatorCreatePayload {
  raw_value: string
  indicator_type?: IndicatorType | null
  description?: string
  tags?: string[]
  source_name?: string
}

export interface IndicatorClassificationUpdatePayload {
  classification: IndicatorClassification
  reason: string
  status?: IndicatorStatus
}

export interface WatchlistCreatePayload {
  reason: string
  expires_at?: string | null
}

export interface ChallengeSubmitPayload {
  selected_classification: string
  hypothesis_text: string
  evidence_notes: string
  conclusion: string
}
