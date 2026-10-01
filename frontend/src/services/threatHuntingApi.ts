/**
 * Threat Hunting & Investigation Workspace API Client for Step 14.
 */

import type {
  DatasetAnalytics,
  EntityGraphResponse,
  HuntDataset,
  HuntEvidence,
  HuntFinding,
  HuntHypothesis,
  HuntNote,
  HuntOverviewResponse,
  HuntQueryRequest,
  HuntQueryResponse,
  HuntScenario,
  HuntScoreResponse,
  HuntTimelineResponse,
  PivotResponse,
  ThreatHunt,
  ThreatHuntDetail,
} from '../types/threat_hunting'
import { getApiBaseUrl } from './apiConfig'

class ThreatHuntingApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  // 1. Overview & Summary
  async getOverview(): Promise<HuntOverviewResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/overview`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch hunting overview (${res.status})`)
    }
    return res.json()
  }

  // 2. Datasets
  async listDatasets(params?: { dataset_type?: string; status?: string }): Promise<HuntDataset[]> {
    const sp = new URLSearchParams()
    if (params?.dataset_type) sp.set('dataset_type', params.dataset_type)
    if (params?.status) sp.set('status', params.status)

    const query = sp.toString() ? `?${sp.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/datasets${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch datasets (${res.status})`)
    }
    return res.json()
  }

  async getDatasetAnalytics(datasetId: number): Promise<DatasetAnalytics> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/datasets/${datasetId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch dataset analytics (${res.status})`)
    }
    return res.json()
  }

  async createDataset(payload: {
    dataset_id: string
    name: string
    description: string
    dataset_type?: string
    source?: string
  }): Promise<HuntDataset> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/datasets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create dataset (${res.status})`)
    }
    return res.json()
  }

  // 3. Scenarios
  async listScenarios(difficulty?: string): Promise<HuntScenario[]> {
    const sp = new URLSearchParams()
    if (difficulty) sp.set('difficulty', difficulty)

    const query = sp.toString() ? `?${sp.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/scenarios${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch scenarios (${res.status})`)
    }
    return res.json()
  }

  async getScenario(slug: string): Promise<HuntScenario> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/scenarios/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch scenario (${res.status})`)
    }
    return res.json()
  }

  async launchScenario(slug: string): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/scenarios/${slug}/launch`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to launch scenario (${res.status})`)
    }
    return res.json()
  }

  // 4. Hunts CRUD & Lifecycle
  async listHunts(params?: {
    status?: string
    difficulty?: string
    limit?: number
    offset?: number
  }): Promise<ThreatHunt[]> {
    const sp = new URLSearchParams()
    if (params?.status) sp.set('status', params.status)
    if (params?.difficulty) sp.set('difficulty', params.difficulty)
    if (params?.limit) sp.set('limit', String(params.limit))
    if (params?.offset) sp.set('offset', String(params.offset))

    const query = sp.toString() ? `?${sp.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list hunts (${res.status})`)
    }
    return res.json()
  }

  async getHuntDetail(huntId: number): Promise<ThreatHuntDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to get hunt details (${res.status})`)
    }
    return res.json()
  }

  async createHunt(payload: {
    title: string
    description: string
    objective: string
    difficulty?: string
    dataset_id?: number | null
    scenario_slug?: string | null
    initial_pivot_type?: string | null
    initial_pivot_value?: string | null
  }): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create hunt (${res.status})`)
    }
    return res.json()
  }

  async launchFromAlert(payload: {
    alert_id: number
    dataset_id?: number | null
    title?: string | null
  }): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/launch-from-alert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to launch hunt from alert (${res.status})`)
    }
    return res.json()
  }

  async launchFromIOC(payload: {
    ioc_id: number
    dataset_id?: number | null
    title?: string | null
  }): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/launch-from-ioc`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to launch hunt from IOC (${res.status})`)
    }
    return res.json()
  }

  async startHunt(huntId: number): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/start`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to start hunt (${res.status})`)
    }
    return res.json()
  }

  async pauseHunt(huntId: number): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/pause`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to pause hunt (${res.status})`)
    }
    return res.json()
  }

  async completeHunt(
    huntId: number,
    payload: { conclusion: string; conclusion_disposition: string },
  ): Promise<ThreatHunt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to complete hunt (${res.status})`)
    }
    return res.json()
  }

  // 5. Query Engine
  async queryTelemetry(huntId: number, payload: HuntQueryRequest): Promise<HuntQueryResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to execute telemetry query (${res.status})`)
    }
    return res.json()
  }

  // 6. Timeline, Graph & Pivoting
  async getTimeline(huntId: number, interval: string = 'minute'): Promise<HuntTimelineResponse> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/timeline?interval=${interval}`,
      { headers: { Accept: 'application/json' } },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch hunt timeline (${res.status})`)
    }
    return res.json()
  }

  async getEntityGraph(
    huntId: number,
    focus?: string,
    maxDepth: number = 2,
    maxNodes: number = 50,
  ): Promise<EntityGraphResponse> {
    const sp = new URLSearchParams()
    if (focus) sp.set('focus', focus)
    sp.set('max_depth', String(maxDepth))
    sp.set('max_nodes', String(maxNodes))

    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/entities?${sp.toString()}`,
      { headers: { Accept: 'application/json' } },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch entity graph (${res.status})`)
    }
    return res.json()
  }

  async pivotEntity(
    huntId: number,
    payload: { entity_type: string; entity_value: string },
  ): Promise<PivotResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/pivot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to pivot entity (${res.status})`)
    }
    return res.json()
  }

  // 7. Hypotheses
  async listHypotheses(huntId: number): Promise<HuntHypothesis[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/hypotheses`,
      { headers: { Accept: 'application/json' } },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list hypotheses (${res.status})`)
    }
    return res.json()
  }

  async createHypothesis(
    huntId: number,
    payload: { title: string; description: string; confidence?: string },
  ): Promise<HuntHypothesis> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/hypotheses`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create hypothesis (${res.status})`)
    }
    return res.json()
  }

  async updateHypothesis(
    hypothesisId: number,
    payload: {
      status?: string
      confidence?: string
      analyst_reasoning?: string
      title?: string
      description?: string
    },
  ): Promise<HuntHypothesis> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hypotheses/${hypothesisId}`,
      {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update hypothesis (${res.status})`)
    }
    return res.json()
  }

  async deleteHypothesis(hypothesisId: number): Promise<void> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hypotheses/${hypothesisId}`,
      { method: 'DELETE' },
    )
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to delete hypothesis (${res.status})`)
    }
  }

  // 8. Evidence
  async listEvidence(huntId: number, hypothesisId?: number): Promise<HuntEvidence[]> {
    const sp = new URLSearchParams()
    if (hypothesisId) sp.set('hypothesis_id', String(hypothesisId))
    const query = sp.toString() ? `?${sp.toString()}` : ''

    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/evidence${query}`,
      { headers: { Accept: 'application/json' } },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list evidence (${res.status})`)
    }
    return res.json()
  }

  async addEvidence(
    huntId: number,
    payload: {
      hypothesis_id?: number | null
      evidence_type: string
      source_id: string
      description: string
      relevance: string
      analyst_note?: string | null
      data_snapshot?: Record<string, any> | null
    },
  ): Promise<HuntEvidence> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/evidence`, {
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

  async updateEvidence(
    evidenceId: number,
    payload: { hypothesis_id?: number | null; relevance?: string; analyst_note?: string | null },
  ): Promise<HuntEvidence> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/evidence/${evidenceId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update evidence (${res.status})`)
    }
    return res.json()
  }

  async deleteEvidence(evidenceId: number): Promise<void> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/evidence/${evidenceId}`, {
      method: 'DELETE',
    })
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to delete evidence (${res.status})`)
    }
  }

  // 9. Findings
  async listFindings(huntId: number): Promise<HuntFinding[]> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/findings`,
      { headers: { Accept: 'application/json' } },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list findings (${res.status})`)
    }
    return res.json()
  }

  async createFinding(
    huntId: number,
    payload: {
      title: string
      description: string
      finding_type: string
      confidence?: string
      evidence_count?: number
      mitigation_recommendation?: string | null
    },
  ): Promise<HuntFinding> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/findings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create finding (${res.status})`)
    }
    return res.json()
  }

  async deleteFinding(findingId: number): Promise<void> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/findings/${findingId}`, {
      method: 'DELETE',
    })
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to delete finding (${res.status})`)
    }
  }

  // 10. Notes
  async listNotes(huntId: number): Promise<HuntNote[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/notes`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list notes (${res.status})`)
    }
    return res.json()
  }

  async addNote(
    huntId: number,
    payload: {
      content: string
      related_event_id?: string | null
      related_alert_id?: number | null
      related_ioc_id?: number | null
      related_hypothesis_id?: number | null
    },
  ): Promise<HuntNote> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add note (${res.status})`)
    }
    return res.json()
  }

  async deleteNote(noteId: number): Promise<void> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/notes/${noteId}`, {
      method: 'DELETE',
    })
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to delete note (${res.status})`)
    }
  }

  // 11. Conclusion & Scoring
  async submitConclusion(
    huntId: number,
    payload: { conclusion: string; conclusion_disposition: string },
  ): Promise<HuntScoreResponse> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/conclusion`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload),
      },
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to submit conclusion (${res.status})`)
    }
    return res.json()
  }

  async getHuntScore(huntId: number): Promise<HuntScoreResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-hunting/hunts/${huntId}/score`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch hunt score (${res.status})`)
    }
    return res.json()
  }
}

export const threatHuntingApi = new ThreatHuntingApiService()
