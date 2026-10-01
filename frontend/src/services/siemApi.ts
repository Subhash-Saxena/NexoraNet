/**
 * Step 15 SIEM & Security Log Analysis Engine API Client.
 */

import type {
  CorrelationAlert,
  DatasetImportRequest,
  EscalationResult,
  LogCorrelationRule,
  LogSource,
  RuleEvaluationResult,
  SavedSearch,
  SearchHistoryItem,
  SecurityEvent,
  SecurityEventDetail,
  SecurityLogDataset,
  SIEMLabScenario,
  SIEMLabValidateRequest,
  SIEMLabValidateResponse,
  SiemAggregations,
  SiemSearchRequest,
  SiemSearchResponse,
} from '../types/siem'
import { getApiBaseUrl } from './apiConfig'

class SiemApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  // 1. Sources & Datasets
  async listSources(): Promise<LogSource[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/sources`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch log sources (${res.status})`)
    }
    return res.json()
  }

  async listDatasets(): Promise<SecurityLogDataset[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/datasets`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch datasets (${res.status})`)
    }
    return res.json()
  }

  async getDataset(id: number): Promise<SecurityLogDataset> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/datasets/${id}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch dataset (${res.status})`)
    }
    return res.json()
  }

  async importLogs(payload: DatasetImportRequest): Promise<{ imported_events: number; dataset_total: number }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/datasets/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to import logs (${res.status})`)
    }
    return res.json()
  }

  // 2. Search & Aggregations
  async searchEvents(req: SiemSearchRequest): Promise<SiemSearchResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(req),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to search logs (${res.status})`)
    }
    return res.json()
  }

  async getAggregations(params?: { dataset_id?: number; time_preset?: string }): Promise<SiemAggregations> {
    const sp = new URLSearchParams()
    if (params?.dataset_id) sp.set('dataset_id', String(params.dataset_id))
    if (params?.time_preset) sp.set('time_preset', params.time_preset)
    const query = sp.toString() ? `?${sp.toString()}` : ''

    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/aggregations${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch aggregations (${res.status})`)
    }
    return res.json()
  }

  async getEvent(eventId: string): Promise<SecurityEventDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/events/${eventId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch event detail (${res.status})`)
    }
    return res.json()
  }

  async getRelatedEvents(eventId: string): Promise<SecurityEvent[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/events/${eventId}/related`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch related events (${res.status})`)
    }
    return res.json()
  }

  // 3. Correlation Rules & Alerts
  async listRules(params?: { category?: string; status?: string }): Promise<LogCorrelationRule[]> {
    const sp = new URLSearchParams()
    if (params?.category) sp.set('category', params.category)
    if (params?.status) sp.set('status', params.status)
    const query = sp.toString() ? `?${sp.toString()}` : ''

    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/rules${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch correlation rules (${res.status})`)
    }
    return res.json()
  }

  async evaluateRule(ruleId: number, datasetId?: number): Promise<RuleEvaluationResult> {
    const sp = new URLSearchParams()
    if (datasetId) sp.set('dataset_id', String(datasetId))
    const query = sp.toString() ? `?${sp.toString()}` : ''

    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/rules/${ruleId}/evaluate${query}`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to evaluate correlation rule (${res.status})`)
    }
    return res.json()
  }

  async listAlerts(params?: { dataset_id?: number; status?: string; severity?: string }): Promise<CorrelationAlert[]> {
    const sp = new URLSearchParams()
    if (params?.dataset_id) sp.set('dataset_id', String(params.dataset_id))
    if (params?.status) sp.set('status', params.status)
    if (params?.severity) sp.set('severity', params.severity)
    const query = sp.toString() ? `?${sp.toString()}` : ''

    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/alerts${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch correlation alerts (${res.status})`)
    }
    return res.json()
  }

  async updateAlertStatus(alertId: number, status: string): Promise<CorrelationAlert> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/alerts/${alertId}/status`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ status }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update alert status (${res.status})`)
    }
    return res.json()
  }

  // 4. Saved Searches & History
  async listSavedSearches(): Promise<SavedSearch[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/search/saved`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch saved searches (${res.status})`)
    }
    return res.json()
  }

  async createSavedSearch(payload: {
    name: string
    description?: string
    query_definition: Record<string, unknown>
    is_public?: boolean
  }): Promise<SavedSearch> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/search/saved`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to save search (${res.status})`)
    }
    return res.json()
  }

  async deleteSavedSearch(id: number): Promise<{ success: boolean; message: string }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/search/saved/${id}`, {
      method: 'DELETE',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to delete saved search (${res.status})`)
    }
    return res.json()
  }

  async listSearchHistory(limit = 20): Promise<SearchHistoryItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/search/history?limit=${limit}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch search history (${res.status})`)
    }
    return res.json()
  }

  // 5. Educational Labs & Scenarios
  async listLabs(): Promise<SIEMLabScenario[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/labs`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch labs (${res.status})`)
    }
    return res.json()
  }

  async getLab(slug: string): Promise<SIEMLabScenario> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/labs/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch lab scenario (${res.status})`)
    }
    return res.json()
  }

  async validateLab(slug: string, payload: SIEMLabValidateRequest): Promise<SIEMLabValidateResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/labs/${slug}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to validate lab (${res.status})`)
    }
    return res.json()
  }

  // 6. Cross-Platform Escalations
  async investigateInSoc(eventId?: string, alertId?: number): Promise<EscalationResult> {
    const url = alertId
      ? `${this.getBaseUrl()}/api/v1/siem/alerts/${alertId}/investigate`
      : `${this.getBaseUrl()}/api/v1/siem/events/${eventId}/investigate`

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({}),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to escalate to SOC (${res.status})`)
    }
    return res.json()
  }

  async startThreatHunt(
    eventId?: string,
    alertId?: number,
    hypothesisStatement?: string
  ): Promise<EscalationResult> {
    const url = alertId
      ? `${this.getBaseUrl()}/api/v1/siem/alerts/${alertId}/start-hunt`
      : `${this.getBaseUrl()}/api/v1/siem/events/${eventId}/start-hunt`

    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ hypothesis_statement: hypothesisStatement }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to start threat hunt (${res.status})`)
    }
    return res.json()
  }

  async extractIoc(eventId: string): Promise<EscalationResult> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/siem/events/${eventId}/extract-ioc`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to extract IOC (${res.status})`)
    }
    return res.json()
  }
}

export const siemApi = new SiemApiService()
