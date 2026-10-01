/**
 * Threat Intelligence & IOC Investigation API client for Step 13.
 */

import type {
  ChallengeAttempt,
  ChallengeSubmitPayload,
  IndicatorBrief,
  IndicatorClassificationUpdatePayload,
  IndicatorCreatePayload,
  IndicatorDetail,
  IndicatorImportResult,
  IndicatorNote,
  IndicatorObservation,
  IndicatorRelationship,
  IndicatorTimelineEvent,
  ThreatIntelChallengeBrief,
  ThreatIntelChallengeDetail,
  ThreatIntelGraph,
  ThreatIntelOverview,
  ThreatIntelSource,
  WatchlistCreatePayload,
  WatchlistItem,
} from '../types/threat_intel'
import { getApiBaseUrl } from './apiConfig'

class ThreatIntelApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  // 1. Overview & Metrics
  async getOverview(): Promise<ThreatIntelOverview> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/overview`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch threat intel overview (${res.status})`)
    }
    return res.json()
  }

  // 2. Indicators List & CRUD
  async listIndicators(params?: {
    indicator_type?: string
    classification?: string
    confidence?: string
    severity?: string
    status?: string
    search?: string
    limit?: number
    offset?: number
  }): Promise<IndicatorBrief[]> {
    const query = new URLSearchParams()
    if (params?.indicator_type) query.set('indicator_type', params.indicator_type)
    if (params?.classification) query.set('classification', params.classification)
    if (params?.confidence) query.set('confidence', params.confidence)
    if (params?.severity) query.set('severity', params.severity)
    if (params?.status) query.set('status', params.status)
    if (params?.search) query.set('search', params.search)
    if (params?.limit) query.set('limit', String(params.limit))
    if (params?.offset) query.set('offset', String(params.offset))

    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators?${query.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list indicators (${res.status})`)
    }
    return res.json()
  }

  async getIndicator(id: number): Promise<IndicatorDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch indicator #${id} (${res.status})`)
    }
    return res.json()
  }

  async createIndicator(payload: IndicatorCreatePayload): Promise<IndicatorDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create indicator (${res.status})`)
    }
    return res.json()
  }

  async enrichIndicator(id: number): Promise<IndicatorDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/enrich`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to enrich indicator #${id} (${res.status})`)
    }
    return res.json()
  }

  async updateClassification(id: number, payload: IndicatorClassificationUpdatePayload): Promise<IndicatorDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/classification`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update indicator #${id} classification (${res.status})`)
    }
    return res.json()
  }

  // 3. Observations & Correlated Entities
  async getEvidence(id: number): Promise<IndicatorObservation[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/evidence`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch evidence for indicator #${id} (${res.status})`)
    }
    return res.json()
  }

  async getCorrelatedAlerts(id: number): Promise<{ indicator_id: number; total_alerts: number; alerts: any[] }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/alerts`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch correlated alerts for #${id} (${res.status})`)
    }
    return res.json()
  }

  async getCorrelatedInvestigations(id: number): Promise<{ indicator_id: number; total_investigations: number; investigations: any[] }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/investigations`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch correlated investigations for #${id} (${res.status})`)
    }
    return res.json()
  }

  async getCorrelatedCases(id: number): Promise<{ indicator_id: number; total_cases: number; cases: any[] }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/cases`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch correlated cases for #${id} (${res.status})`)
    }
    return res.json()
  }

  // 4. Relationships & Graph
  async getRelationships(id: number): Promise<IndicatorRelationship[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/relationships`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch relationships for #${id} (${res.status})`)
    }
    return res.json()
  }

  async createRelationship(id: number, payload: { target_indicator_id: number; relationship_type: string; description?: string; confidence?: string }): Promise<IndicatorRelationship> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/relationships`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create relationship for #${id} (${res.status})`)
    }
    return res.json()
  }

  async getGraph(id: number): Promise<ThreatIntelGraph> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/graph`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch graph for #${id} (${res.status})`)
    }
    return res.json()
  }

  // 5. Timeline & Notes
  async getTimeline(id: number): Promise<IndicatorTimelineEvent[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/timeline`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch timeline for #${id} (${res.status})`)
    }
    return res.json()
  }

  async getNotes(id: number): Promise<IndicatorNote[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/notes`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch notes for #${id} (${res.status})`)
    }
    return res.json()
  }

  async createNote(id: number, note: string): Promise<IndicatorNote> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/indicators/${id}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ note }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add note to #${id} (${res.status})`)
    }
    return res.json()
  }

  // 6. Search & Sources
  async search(query: string, indicator_type?: string, classification?: string): Promise<IndicatorBrief[]> {
    const params = new URLSearchParams({ q: query })
    if (indicator_type) params.set('indicator_type', indicator_type)
    if (classification) params.set('classification', classification)

    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/search?${params.toString()}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Search failed (${res.status})`)
    }
    return res.json()
  }

  async getSources(): Promise<ThreatIntelSource[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/sources`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch threat intel sources (${res.status})`)
    }
    return res.json()
  }

  // 7. Watchlist
  async getWatchlist(includeExpired = false): Promise<WatchlistItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/watchlist?include_expired=${includeExpired}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch watchlist (${res.status})`)
    }
    return res.json()
  }

  async addToWatchlist(indicatorId: number, payload: WatchlistCreatePayload): Promise<WatchlistItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/watchlist/${indicatorId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add indicator #${indicatorId} to watchlist (${res.status})`)
    }
    return res.json()
  }

  async removeFromWatchlist(watchlistId: number): Promise<void> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/watchlist/${watchlistId}`, {
      method: 'DELETE',
    })
    if (!res.ok && res.status !== 204) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to remove watchlist entry #${watchlistId} (${res.status})`)
    }
  }

  // 8. Safe Import / Export
  async importIndicators(file: File): Promise<IndicatorImportResult> {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/import`, {
      method: 'POST',
      body: formData,
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to import indicators (${res.status})`)
    }
    return res.json()
  }

  async exportIndicators(fileFormat: 'csv' | 'json' = 'json', classification?: string, indicatorType?: string): Promise<Blob> {
    const params = new URLSearchParams({ file_format: fileFormat })
    if (classification) params.set('classification', classification)
    if (indicatorType) params.set('indicator_type', indicatorType)

    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/export?${params.toString()}`)
    if (!res.ok) {
      throw new Error(`Failed to export indicators (${res.status})`)
    }
    return res.blob()
  }

  // 9. Challenges
  async listChallenges(): Promise<ThreatIntelChallengeBrief[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/challenges`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to list challenges (${res.status})`)
    }
    return res.json()
  }

  async getChallenge(slug: string): Promise<ThreatIntelChallengeDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/challenges/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch challenge '${slug}' (${res.status})`)
    }
    return res.json()
  }

  async submitChallengeAttempt(slug: string, payload: ChallengeSubmitPayload): Promise<ChallengeAttempt> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/challenges/${slug}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to submit challenge attempt (${res.status})`)
    }
    return res.json()
  }

  async getChallengeAttempts(slug: string): Promise<ChallengeAttempt[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/threat-intel/challenges/${slug}/attempts`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch challenge attempts (${res.status})`)
    }
    return res.json()
  }
}

export const threatIntelApi = new ThreatIntelApiService()
