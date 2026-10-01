import type {
  AlertNoteItem,
  AlertSeverity,
  AlertStatus,
  DetectionAlertDetail,
  DetectionAlertListItem,
  DetectionRule,
  DetectionRuleTestRequest,
  DetectionRuleTestResponse,
  DetectionRunResponse,
  DetectionStats,
  RuleCategory,
  RuleStatus,
} from '../types/detection'
import { getApiBaseUrl } from './apiConfig'

class DetectionApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  /**
   * Fetch aggregate detection engine statistics.
   */
  async getStats(): Promise<DetectionStats> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/stats`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch detection statistics (${res.status})`)
    }
    return res.json()
  }

  /**
   * List all detection rules with optional filters.
   */
  async listRules(filters?: {
    category?: RuleCategory
    status?: RuleStatus
    severity?: AlertSeverity
  }): Promise<DetectionRule[]> {
    const params = new URLSearchParams()
    if (filters?.category) params.append('category', filters.category)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.severity) params.append('severity', filters.severity)

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/rules${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch rules (${res.status})`)
    }
    return res.json()
  }

  /**
   * Get single detection rule by rule ID code (e.g. NET-TCP-001).
   */
  async getRule(ruleId: string): Promise<DetectionRule> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/rules/${encodeURIComponent(ruleId)}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch rule ${ruleId} (${res.status})`)
    }
    return res.json()
  }

  /**
   * Dry-run simulation of a rule without persisting alerts.
   */
  async testRule(payload: DetectionRuleTestRequest): Promise<DetectionRuleTestResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/rules/test`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to simulate rule test (${res.status})`)
    }
    return res.json()
  }

  /**
   * Launch a synchronous detection run on a PCAP or simulator trace.
   */
  async createRun(payload: {
    source_type?: 'PCAP' | 'SIMULATOR'
    capture_id?: number
    rule_ids?: string[]
  }): Promise<DetectionRunResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/runs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Detection run execution failed (${res.status})`)
    }
    return res.json()
  }

  /**
   * List recent detection runs.
   */
  async listRuns(filters?: { capture_id?: number; limit?: number }): Promise<DetectionRunResponse[]> {
    const params = new URLSearchParams()
    if (filters?.capture_id) params.append('capture_id', String(filters.capture_id))
    if (filters?.limit) params.append('limit', String(filters.limit))

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/runs${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch detection runs (${res.status})`)
    }
    return res.json()
  }

  /**
   * Get single detection run details.
   */
  async getRun(runId: number): Promise<DetectionRunResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/runs/${runId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch run ${runId} (${res.status})`)
    }
    return res.json()
  }

  /**
   * List detection alerts with filtering.
   */
  async listAlerts(filters?: {
    run_id?: number
    capture_id?: number
    status?: AlertStatus
    severity?: AlertSeverity
    category?: RuleCategory
    limit?: number
  }): Promise<DetectionAlertListItem[]> {
    const params = new URLSearchParams()
    if (filters?.run_id) params.append('run_id', String(filters.run_id))
    if (filters?.capture_id) params.append('capture_id', String(filters.capture_id))
    if (filters?.status) params.append('status', filters.status)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.category) params.append('category', filters.category)
    if (filters?.limit) params.append('limit', String(filters.limit))

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/alerts${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch alerts (${res.status})`)
    }
    return res.json()
  }

  /**
   * Get full details of an alert including explanation, steps, evidence, notes, and history.
   */
  async getAlert(alertId: number): Promise<DetectionAlertDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/alerts/${alertId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch alert ${alertId} (${res.status})`)
    }
    return res.json()
  }

  /**
   * Update triage status of an alert.
   */
  async updateAlertStatus(
    alertId: number,
    payload: { status: AlertStatus; reason?: string }
  ): Promise<DetectionAlertDetail> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/alerts/${alertId}/status`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update alert status (${res.status})`)
    }
    return res.json()
  }

  /**
   * Add analyst investigation note to an alert.
   */
  async addAlertNote(alertId: number, note: string): Promise<AlertNoteItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/detection/alerts/${alertId}/notes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify({ note }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add alert note (${res.status})`)
    }
    return res.json()
  }
}

export const detectionApi = new DetectionApiService()
