/**
 * Step 16: Endpoint Security & Host Investigation Engine API Client
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

import type {
  AuthenticationAnalysis,
  EndpointConclusion,
  EndpointEvent,
  EndpointEvidence,
  EndpointFinding,
  EndpointHost,
  EndpointHostOverview,
  EndpointHostSummary,
  EndpointHypothesis,
  EndpointInvestigation,
  EndpointScenario,
  PivotHuntResponse,
  PivotIntelResponse,
  PivotSocResponse,
  ProcessDetails,
  ProcessTreeNode,
  ScenarioValidationResult,
} from '../types/endpointSecurity'
import { getApiBaseUrl } from './apiConfig'

class EndpointSecurityApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  // 1. Overview & Host Inventory
  async getOverview(): Promise<EndpointHostSummary> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/overview`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch overview (${res.status})`)
    }
    return res.json()
  }

  async listHosts(params?: {
    platform?: string
    risk_level?: string
    search?: string
    skip?: number
    limit?: number
  }): Promise<{ items: EndpointHost[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.platform) q.set('platform', params.platform)
    if (params?.risk_level) q.set('risk_level', params.risk_level)
    if (params?.search) q.set('search', params.search)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list hosts (${res.status})`)
    }
    return res.json()
  }

  async getHost(hostId: string | number): Promise<EndpointHost> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch host (${res.status})`)
    }
    return res.json()
  }

  async getHostOverview(hostId: string | number): Promise<EndpointHostOverview> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/overview`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch host overview (${res.status})`)
    }
    return res.json()
  }

  async getHostEvents(
    hostId: string | number,
    params?: {
      category?: string
      severity?: string
      search?: string
      skip?: number
      limit?: number
    }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.category) q.set('category', params.category)
    if (params?.severity) q.set('severity', params.severity)
    if (params?.search) q.set('search', params.search)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/events?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch host events (${res.status})`)
    }
    return res.json()
  }

  // 2. Processes & Telemetry Specialized Views
  async getProcessTree(hostId: string | number): Promise<ProcessTreeNode[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/processes`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch process tree (${res.status})`)
    }
    return res.json()
  }

  async getProcessDetails(hostId: string | number, processId: number): Promise<ProcessDetails> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/processes/${processId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch process details (${res.status})`)
    }
    return res.json()
  }

  async getHostAuthentication(
    hostId: string | number,
    params?: { username?: string; result?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number; summary: AuthenticationAnalysis }> {
    const q = new URLSearchParams()
    if (params?.username) q.set('username', params.username)
    if (params?.result) q.set('result', params.result)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/authentication?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch authentication events (${res.status})`)
    }
    const data = await res.json()
    return {
      items: data.events || [],
      total: data.total,
      summary: data.summary,
    }
  }

  async getHostNetwork(
    hostId: string | number,
    params?: { process_name?: string; destination_ip?: string; protocol?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.process_name) q.set('process_name', params.process_name)
    if (params?.destination_ip) q.set('destination_ip', params.destination_ip)
    if (params?.protocol) q.set('protocol', params.protocol)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/network?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch network activity (${res.status})`)
    }
    return res.json()
  }

  async getHostDns(
    hostId: string | number,
    params?: { domain?: string; process_name?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.domain) q.set('domain', params.domain)
    if (params?.process_name) q.set('process_name', params.process_name)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/dns?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch DNS activity (${res.status})`)
    }
    return res.json()
  }

  async getHostFiles(
    hostId: string | number,
    params?: { action?: string; process_name?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.action) q.set('action', params.action)
    if (params?.process_name) q.set('process_name', params.process_name)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/files?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch file events (${res.status})`)
    }
    return res.json()
  }

  async getHostServices(
    hostId: string | number,
    params?: { service_name?: string; action?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.service_name) q.set('service_name', params.service_name)
    if (params?.action) q.set('action', params.action)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/services?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch services (${res.status})`)
    }
    return res.json()
  }

  async getHostPersistence(
    hostId: string | number,
    params?: { persistence_type?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.persistence_type) q.set('persistence_type', params.persistence_type)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/persistence?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch persistence indicators (${res.status})`)
    }
    return res.json()
  }

  async getHostPrivileges(
    hostId: string | number,
    params?: { username?: string; action?: string; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.username) q.set('username', params.username)
    if (params?.action) q.set('action', params.action)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/privileges?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch privilege events (${res.status})`)
    }
    return res.json()
  }

  async getHostTimeline(
    hostId: string | number,
    params?: { categories?: string[]; skip?: number; limit?: number }
  ): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.categories && params.categories.length > 0) {
      params.categories.forEach((cat) => q.append('categories', cat))
    }
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/hosts/${hostId}/timeline?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch timeline (${res.status})`)
    }
    return res.json()
  }

  // 3. Events Explorer & Cross-Pivots
  async listEvents(params?: {
    category?: string
    severity?: string
    search?: string
    skip?: number
    limit?: number
  }): Promise<{ items: EndpointEvent[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.category) q.set('category', params.category)
    if (params?.severity) q.set('severity', params.severity)
    if (params?.search) q.set('search', params.search)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch events (${res.status})`)
    }
    return res.json()
  }

  async getEvent(eventId: string): Promise<EndpointEvent> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events/${eventId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch event (${res.status})`)
    }
    return res.json()
  }

  async pivotToIntel(eventId: string): Promise<PivotIntelResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events/${eventId}/pivot-intel`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Pivot to Threat Intel failed (${res.status})`)
    }
    return res.json()
  }

  async startThreatHunt(eventId: string): Promise<PivotHuntResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events/${eventId}/start-threat-hunt`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Start Threat Hunt failed (${res.status})`)
    }
    return res.json()
  }

  async investigateInSoc(eventId: string): Promise<PivotSocResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events/${eventId}/investigate-in-soc`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Escalate to SOC failed (${res.status})`)
    }
    return res.json()
  }

  async correlateSiem(eventId: string): Promise<any[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events/${eventId}/correlate-siem`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Correlate with SIEM failed (${res.status})`)
    }
    return res.json()
  }

  async correlatePcap(eventId: string): Promise<any[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/events/${eventId}/correlate-pcap`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Correlate with PCAP failed (${res.status})`)
    }
    return res.json()
  }

  // 4. Investigations Workbench
  async listInvestigations(params?: {
    status?: string
    priority?: string
    host_id?: number
    skip?: number
    limit?: number
  }): Promise<{ items: EndpointInvestigation[]; total: number }> {
    const q = new URLSearchParams()
    if (params?.status) q.set('status', params.status)
    if (params?.priority) q.set('priority', params.priority)
    if (params?.host_id) q.set('host_id', String(params.host_id))
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations?${q.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list investigations (${res.status})`)
    }
    return res.json()
  }

  async createInvestigation(payload: {
    host_id: number
    title: string
    description: string
    priority?: string
    scenario_slug?: string
  }): Promise<EndpointInvestigation> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create investigation (${res.status})`)
    }
    return res.json()
  }

  async getInvestigation(id: number): Promise<EndpointInvestigation> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch investigation (${res.status})`)
    }
    return res.json()
  }

  async updateInvestigation(
    id: number,
    payload: { title?: string; description?: string; status?: string; priority?: string }
  ): Promise<EndpointInvestigation> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update investigation (${res.status})`)
    }
    return res.json()
  }

  async addHypothesis(
    id: number,
    payload: { statement: string; status?: string; confidence?: string; analyst_notes?: string }
  ): Promise<EndpointHypothesis> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}/hypotheses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add hypothesis (${res.status})`)
    }
    return res.json()
  }

  async updateHypothesis(
    id: number,
    hypId: number,
    payload: { status?: string; confidence?: string; analyst_notes?: string }
  ): Promise<EndpointHypothesis> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}/hypotheses/${hypId}`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update hypothesis (${res.status})`)
    }
    return res.json()
  }

  async addEvidence(
    id: number,
    payload: {
      hypothesis_id?: number
      event_id: string
      observable_type: string
      observable_value: string
      description: string
      relevance?: string
    }
  ): Promise<EndpointEvidence> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}/evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add evidence (${res.status})`)
    }
    return res.json()
  }

  async addFinding(
    id: number,
    payload: { title: string; description: string; severity?: string; mitre_technique?: string }
  ): Promise<EndpointFinding> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}/findings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add finding (${res.status})`)
    }
    return res.json()
  }

  async submitConclusion(
    id: number,
    payload: { summary: string; verdict: string; lessons_learned?: string }
  ): Promise<EndpointConclusion> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/investigations/${id}/conclusion`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to submit conclusion (${res.status})`)
    }
    return res.json()
  }

  // 5. Guided Scenarios
  async listScenarios(): Promise<EndpointScenario[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/scenarios`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch scenarios (${res.status})`)
    }
    return res.json()
  }

  async getScenario(slug: string): Promise<EndpointScenario> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/scenarios/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch scenario (${res.status})`)
    }
    return res.json()
  }

  async validateScenario(
    slug: string,
    payload: {
      target_host?: string
      identified_process?: string
      parent_process?: string
      c2_domain_or_ip?: string
      persistence_mechanism?: string
      verdict?: string
      analyst_notes?: string
    }
  ): Promise<ScenarioValidationResult> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/endpoint-security/scenarios/${slug}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to validate scenario (${res.status})`)
    }
    return res.json()
  }
}

export const endpointSecurityApi = new EndpointSecurityApiService()
