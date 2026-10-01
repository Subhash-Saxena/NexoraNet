export type CaptureStatus = 'UPLOADED' | 'PARSING' | 'READY' | 'FAILED' | 'DELETED'
export type ObservationSeverity = 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH'
export type TcpHandshakeState = 'COMPLETE' | 'INCOMPLETE' | 'RESET' | 'UNKNOWN'

export interface CaptureSummary {
  id: number
  name: string
  filename: string
  file_size: number
  format: string
  packet_count: number
  start_time: string | null
  end_time: string | null
  duration: number
  status: CaptureStatus | string
  error_message: string | null
  is_sample: boolean
  sample_category: string | null
  description: string | null
  created_at: string
}

export interface CaptureDetail extends CaptureSummary {
  summary_metadata: {
    total_bytes?: number
    protocol_distribution?: Record<string, number>
    unique_ips_count?: number
    unique_macs_count?: number
    unique_ports_count?: number
    [key: string]: unknown
  } | null
  safety_disclaimer: string
  privacy_disclaimer: string
}

export interface ParsedPacketSummary {
  packet_number: number
  timestamp: number
  relative_time: number
  captured_length: number
  protocol: string
  source_mac?: string | null
  destination_mac?: string | null
  source_ip?: string | null
  destination_ip?: string | null
  source_port?: number | null
  destination_port?: number | null
  info: string
}

export interface ParsedPacketDetail extends ParsedPacketSummary {
  original_length: number
  transport_protocol?: string | null
  application_protocol?: string | null
  tcp_flags: string[]
  tcp_seq?: number | null
  tcp_ack?: number | null
  layers: string[]
  layer_details: Record<string, Record<string, unknown>>
}

export interface PacketListResponse {
  capture_id: number
  total_matched: number
  page: number
  page_size: number
  total_pages: number
  filter_applied: string | null
  packets: ParsedPacketSummary[]
}

export interface FlowLadderItem {
  step: number
  relative_time: number
  source: string
  destination: string
  protocol: string
  info: string
  tcp_flags: string[]
}

export interface ConversationItem {
  id: string
  client_endpoint: string
  server_endpoint: string
  protocol: string
  packet_count: number
  byte_count: number
  total_bytes: number
  start_time: number
  duration: number
  handshake_state: TcpHandshakeState | string
  ladder: FlowLadderItem[]
}

export interface EndpointItem {
  ip: string
  mac?: string | null
  packets_sent: number
  packets_received: number
  total_packets: number
  bytes_sent: number
  bytes_received: number
  total_bytes: number
  protocols: string[]
  first_seen: number
  last_seen: number
}

export interface PortItem {
  port: number
  protocol: string
  service_hint: string
  packet_count: number
  byte_count: number
  client_count: number
  server_count: number
}

export interface TimelineBucketItem {
  bucket_index: number
  start_offset_seconds: number
  end_offset_seconds: number
  packet_count: number
  byte_count: number
  protocols: Record<string, number>
}

export interface CaptureStatistics {
  capture_id: number
  total_packets: number
  total_bytes: number
  duration_seconds: number
  packets_per_second: number
  bytes_per_second: number
  avg_packet_rate_pps?: number | null
  avg_bit_rate_bps?: number | null
  unique_ips: number
  unique_macs: number
  unique_ports: number
  protocol_distribution: Record<string, number>
  top_protocols: Array<{ protocol: string; count: number; percentage: number }>
  top_talkers: Array<{ ip: string; packet_count: number; byte_count: number; destinations: string[] }>
}

export interface ObservationItem {
  id: string
  type: string
  severity: ObservationSeverity
  title: string
  description: string
  why_it_matters: string
  cyber_relevance: string
  evidence_packets: number[]
}

export interface BookmarkCreateRequest {
  packet_number: number
  note?: string
  tags?: string[]
}

export interface BookmarkItem {
  id: number
  capture_id: number
  packet_number: number
  note: string | null
  tags: string[]
  created_at: string
}

export interface NoteCreateRequest {
  target_type?: string
  target_id?: string
  title?: string
  content: string
}

export interface NoteItem {
  id: number
  capture_id: number
  target_type: string
  target_id: string | null
  title: string | null
  content: string
  created_at: string
}

export interface FindingCreateRequest {
  title: string
  description: string
  severity?: ObservationSeverity | string
  evidence_packets?: number[]
  source_endpoint?: string
  destination_endpoint?: string
  hypothesis?: string
  conclusion?: string
}

export interface FindingItem {
  id: number
  capture_id: number
  title: string
  description: string
  severity: string
  evidence_packets: number[]
  source_endpoint?: string | null
  destination_endpoint?: string | null
  hypothesis?: string | null
  conclusion?: string | null
  created_at: string
}

export interface InvestigationReport {
  capture: CaptureSummary
  statistics: CaptureStatistics
  top_endpoints: EndpointItem[]
  conversations: ConversationItem[]
  observations: ObservationItem[]
  bookmarks: BookmarkItem[]
  notes: NoteItem[]
  findings: FindingItem[]
  disclaimer: string
}
