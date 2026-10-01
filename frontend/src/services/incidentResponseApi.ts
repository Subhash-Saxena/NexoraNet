/**
 * Step 17: Incident Response, Case Management & MITRE ATT&CK API Client
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

import type {
  AttackTactic,
  AttackTechnique,
  Incident,
  IncidentEvidence,
  IncidentFinding,
  IncidentHypothesis,
  IncidentListResponse,
  IncidentMetrics,
  IncidentNote,
  IncidentPlaybook,
  IncidentReport,
  IncidentTechniqueMapping,
  IncidentTimelineEvent,
  MatrixCoverageResponse,
  ResponseAction,
} from '../types/incidentResponse'
import { getApiBaseUrl } from './apiConfig'

class IncidentResponseApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.getBaseUrl()}${endpoint}`
    const headers = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
    }

    const res = await fetch(url, { ...options, headers })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Request failed with status ${res.status}: ${res.statusText}`)
    }
    if (res.status === 204) {
      return null as unknown as T
    }
    return res.json()
  }

  // -------------------------------------------------------------------------
  // 1. Incidents Core
  // -------------------------------------------------------------------------
  async listIncidents(params?: {
    status?: string
    severity?: string
    classification?: string
    incident_type?: string
    search?: string
    skip?: number
    limit?: number
  }): Promise<IncidentListResponse> {
    const q = new URLSearchParams()
    if (params?.status) q.set('status', params.status)
    if (params?.severity) q.set('severity', params.severity)
    if (params?.classification) q.set('classification', params.classification)
    if (params?.incident_type) q.set('incident_type', params.incident_type)
    if (params?.search) q.set('search', params.search)
    if (params?.skip !== undefined) q.set('skip', String(params.skip))
    if (params?.limit !== undefined) q.set('limit', String(params.limit))

    const queryStr = q.toString() ? `?${q.toString()}` : ''
    return this.request<IncidentListResponse>(`/api/v1/incidents${queryStr}`)
  }

  async getIncident(incidentId: string | number): Promise<Incident> {
    return this.request<Incident>(`/api/v1/incidents/${incidentId}`)
  }

  async createIncident(data: {
    title: string
    description: string
    incident_type?: string
    severity?: string
    priority?: string
    playbook_id?: number | null
    lead_analyst?: string | null
  }): Promise<Incident> {
    return this.request<Incident>('/api/v1/incidents', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateIncident(
    incidentId: string | number,
    updates: Partial<Incident>
  ): Promise<Incident> {
    return this.request<Incident>(`/api/v1/incidents/${incidentId}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  }

  async escalateAlert(data: {
    alert_id: number
    title?: string
    severity?: string
    playbook_id?: number | null
  }): Promise<Incident> {
    return this.request<Incident>('/api/v1/incidents/escalate-alert', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async addNote(incidentId: string | number, note: string): Promise<IncidentNote> {
    return this.request<IncidentNote>(`/api/v1/incidents/${incidentId}/notes`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    })
  }

  async getMetrics(): Promise<IncidentMetrics> {
    return this.request<IncidentMetrics>('/api/v1/incidents/metrics')
  }

  async getIncidentReport(incidentId: string | number): Promise<IncidentReport> {
    return this.request<IncidentReport>(`/api/v1/incidents/${incidentId}/report`)
  }

  // -------------------------------------------------------------------------
  // 2. Evidence & Chain of Custody
  // -------------------------------------------------------------------------
  async listEvidence(
    incidentId: string | number,
    params?: { evidence_type?: string; source_engine?: string }
  ): Promise<IncidentEvidence[]> {
    const q = new URLSearchParams()
    if (params?.evidence_type) q.set('evidence_type', params.evidence_type)
    if (params?.source_engine) q.set('source_engine', params.source_engine)
    const queryStr = q.toString() ? `?${q.toString()}` : ''
    return this.request<IncidentEvidence[]>(`/api/v1/incidents/${incidentId}/evidence${queryStr}`)
  }

  async addEvidence(
    incidentId: string | number,
    data: {
      title: string
      description: string
      evidence_type: string
      source_engine: string
      source_id?: string | null
      source_ref?: string | null
      data_payload?: unknown
      relevance?: string
    }
  ): Promise<IncidentEvidence> {
    return this.request<IncidentEvidence>(`/api/v1/incidents/${incidentId}/evidence`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async verifyEvidenceHash(
    incidentId: string | number,
    evidenceId: string | number
  ): Promise<{
    evidence_id: string
    stored_hash: string
    computed_hash: string
    is_valid: boolean
    verified_at: string
  }> {
    return this.request(`/api/v1/incidents/${incidentId}/evidence/${evidenceId}/verify-hash`, {
      method: 'POST',
    })
  }

  async updateEvidence(
    incidentId: string | number,
    evidenceId: string | number,
    data: { relevance?: string; is_contained?: boolean; description?: string }
  ): Promise<IncidentEvidence> {
    return this.request<IncidentEvidence>(`/api/v1/incidents/${incidentId}/evidence/${evidenceId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  // -------------------------------------------------------------------------
  // 3. Timeline
  // -------------------------------------------------------------------------
  async listTimeline(
    incidentId: string | number,
    params?: { category?: string; is_milestone?: boolean }
  ): Promise<IncidentTimelineEvent[]> {
    const q = new URLSearchParams()
    if (params?.category) q.set('category', params.category)
    if (params?.is_milestone !== undefined) q.set('is_milestone', String(params.is_milestone))
    const queryStr = q.toString() ? `?${q.toString()}` : ''
    return this.request<IncidentTimelineEvent[]>(`/api/v1/incidents/${incidentId}/timeline${queryStr}`)
  }

  async addTimelineEvent(
    incidentId: string | number,
    data: {
      timestamp: string
      title: string
      description: string
      event_category: string
      source?: string
      source_id?: string | null
      mitre_technique_id?: string | null
      is_milestone?: boolean
    }
  ): Promise<IncidentTimelineEvent> {
    return this.request<IncidentTimelineEvent>(`/api/v1/incidents/${incidentId}/timeline`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async syncTimeline(incidentId: string | number): Promise<{ incident_id: string; events_synced: number }> {
    return this.request(`/api/v1/incidents/${incidentId}/timeline/sync`, {
      method: 'POST',
    })
  }

  // -------------------------------------------------------------------------
  // 4. Hypotheses & Findings
  // -------------------------------------------------------------------------
  async createHypothesis(
    incidentId: string | number,
    data: { statement: string; confidence?: string; rationale?: string }
  ): Promise<IncidentHypothesis> {
    return this.request<IncidentHypothesis>(`/api/v1/incidents/${incidentId}/hypotheses`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async updateHypothesis(
    incidentId: string | number,
    hypothesisId: string | number,
    data: { status: string; confidence?: string; rationale?: string }
  ): Promise<IncidentHypothesis> {
    return this.request<IncidentHypothesis>(`/api/v1/incidents/${incidentId}/hypotheses/${hypothesisId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    })
  }

  async recordFinding(
    incidentId: string | number,
    data: {
      title: string
      description: string
      severity?: string
      confidence?: string
      affected_systems?: string
      affected_accounts?: string
      indicators_observed?: string
      mitre_technique?: string
      mitre_tactic?: string
    }
  ): Promise<IncidentFinding> {
    return this.request<IncidentFinding>(`/api/v1/incidents/${incidentId}/findings`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // -------------------------------------------------------------------------
  // 5. Response Simulation (Simulation-Only)
  // -------------------------------------------------------------------------
  async listActions(
    incidentId: string | number,
    params?: { category?: string; status?: string }
  ): Promise<ResponseAction[]> {
    const q = new URLSearchParams()
    if (params?.category) q.set('category', params.category)
    if (params?.status) q.set('status', params.status)
    const queryStr = q.toString() ? `?${q.toString()}` : ''
    return this.request<ResponseAction[]>(`/api/v1/incidents/${incidentId}/actions${queryStr}`)
  }

  async proposeAction(
    incidentId: string | number,
    data: {
      category: string
      action_type: string
      target_type: string
      target_identifier: string
      reason: string
      risk_assessment?: string
      expected_impact?: string
    }
  ): Promise<ResponseAction> {
    return this.request<ResponseAction>(`/api/v1/incidents/${incidentId}/actions`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async executeAction(
    incidentId: string | number,
    actionId: string | number
  ): Promise<ResponseAction> {
    return this.request<ResponseAction>(`/api/v1/incidents/${incidentId}/actions/${actionId}/execute`, {
      method: 'POST',
    })
  }

  async revertAction(
    incidentId: string | number,
    actionId: string | number
  ): Promise<ResponseAction> {
    return this.request<ResponseAction>(`/api/v1/incidents/${incidentId}/actions/${actionId}/revert`, {
      method: 'POST',
    })
  }

  // -------------------------------------------------------------------------
  // 6. MITRE ATT&CK Framework
  // -------------------------------------------------------------------------
  async listTactics(): Promise<AttackTactic[]> {
    return this.request<AttackTactic[]>('/api/v1/mitre/tactics')
  }

  async listTechniques(params?: { tactic_id?: string; search?: string }): Promise<AttackTechnique[]> {
    const q = new URLSearchParams()
    if (params?.tactic_id) q.set('tactic_id', params.tactic_id)
    if (params?.search) q.set('search', params.search)
    const queryStr = q.toString() ? `?${q.toString()}` : ''
    return this.request<AttackTechnique[]>(`/api/v1/mitre/techniques${queryStr}`)
  }

  async getTechnique(techniqueId: string): Promise<AttackTechnique> {
    return this.request<AttackTechnique>(`/api/v1/mitre/techniques/${techniqueId}`)
  }

  async getMatrixCoverage(incidentId?: number): Promise<MatrixCoverageResponse> {
    const queryStr = incidentId ? `?incident_id=${incidentId}` : ''
    return this.request<MatrixCoverageResponse>(`/api/v1/mitre/coverage${queryStr}`)
  }

  async mapTechnique(
    incidentId: string | number,
    data: {
      technique_id_or_code: string | number
      mapping_confidence?: string
      evidence_summary?: string
      phase?: string
    }
  ): Promise<IncidentTechniqueMapping> {
    return this.request<IncidentTechniqueMapping>(`/api/v1/incidents/${incidentId}/mitre/map`, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async unmapTechnique(
    incidentId: string | number,
    techniqueId: string
  ): Promise<void> {
    return this.request<void>(`/api/v1/incidents/${incidentId}/mitre/map/${techniqueId}`, {
      method: 'DELETE',
    })
  }

  // -------------------------------------------------------------------------
  // 7. Playbooks
  // -------------------------------------------------------------------------
  async listPlaybooks(params?: { category?: string; search?: string }): Promise<IncidentPlaybook[]> {
    const q = new URLSearchParams()
    if (params?.category) q.set('category', params.category)
    if (params?.search) q.set('search', params.search)
    const queryStr = q.toString() ? `?${q.toString()}` : ''
    return this.request<IncidentPlaybook[]>(`/api/v1/playbooks${queryStr}`)
  }

  async getPlaybook(playbookId: string | number): Promise<IncidentPlaybook> {
    return this.request<IncidentPlaybook>(`/api/v1/playbooks/${playbookId}`)
  }

  async attachPlaybook(
    incidentId: string | number,
    playbookId: string | number
  ): Promise<Incident> {
    return this.request<Incident>(`/api/v1/incidents/${incidentId}/playbooks/attach?playbook_id=${playbookId}`, {
      method: 'POST',
    })
  }
}

export const incidentResponseApi = new IncidentResponseApiService()
