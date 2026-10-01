/**
 * SOC API client for Step 12 SOC Dashboard, Alert Queue, Triage, and Investigations.
 */

import type {
  CaseDetailResponse,
  CaseNoteItem,
  CaseStatus,
  DetectionCoverageResponse,
  HypothesisStatus,
  InvestigationBriefItem,
  InvestigationDetailResponse,
  InvestigationEvidenceItem,
  InvestigationFindingItem,
  InvestigationHypothesisItem,
  InvestigationNoteItem,
  InvestigationStatus,
  SocActivityItem,
  SocAlertDetailResponse,
  SocAlertItem,
  SocAuditLogItem,
  SocChallengeDetailResponse,
  SocChallengeEvaluation,
  SocChallengeItem,
  SocNotificationItem,
  SocOverviewResponse,
  SocStatisticsResponse,
  TrainingDatasetItem,
  TrainingPriority,
  TriageClassification,
} from '../types/soc'
import { getApiBaseUrl } from './apiConfig'

class SocApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  // 1. Overview & Statistics
  async getOverview(): Promise<SocOverviewResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/overview`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC overview (${res.status})`)
    }
    return res.json()
  }

  async getStatistics(): Promise<SocStatisticsResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/statistics`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC statistics (${res.status})`)
    }
    return res.json()
  }

  async getActivityStream(): Promise<SocActivityItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/activity`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC activity stream (${res.status})`)
    }
    return res.json()
  }

  // 2. Alert Queue & Details
  async listAlerts(filters?: {
    priority?: TrainingPriority | string
    severity?: string
    status?: string
    classification?: TriageClassification | string
    category?: string
    q?: string
    limit?: number
    offset?: number
  }): Promise<SocAlertItem[]> {
    const params = new URLSearchParams()
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.severity) params.append('severity', filters.severity)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.classification) params.append('classification', filters.classification)
    if (filters?.category) params.append('category', filters.category)
    if (filters?.q) params.append('q', filters.q)
    if (filters?.limit) params.append('limit', String(filters.limit))
    if (filters?.offset) params.append('offset', String(filters.offset))

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/alerts${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC alerts (${res.status})`)
    }
    return res.json()
  }

  async getAlertDetail(alertId: number): Promise<SocAlertDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/alerts/${alertId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch alert detail (${res.status})`)
    }
    return res.json()
  }

  // 3. Triage Actions
  async acknowledgeAlert(alertId: number, reason?: string): Promise<SocAlertItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ reason: reason || 'Acknowledged by analyst for triage.' }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to acknowledge alert (${res.status})`)
    }
    return res.json()
  }

  async updateClassification(
    alertId: number,
    classification: TriageClassification,
    reason: string,
    status?: string
  ): Promise<SocAlertItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/alerts/${alertId}/classification`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ classification, reason, status }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update alert classification (${res.status})`)
    }
    return res.json()
  }

  async bulkAlertAction(data: {
    alert_ids: number[]
    action: 'ACKNOWLEDGE' | 'ASSIGN' | 'CLOSE' | 'SET_CLASSIFICATION'
    assigned_to_id?: number
    classification?: TriageClassification
    status?: string
    reason?: string
  }): Promise<{ message: string; modified_count: number }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/alerts/bulk-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Bulk alert action failed (${res.status})`)
    }
    return res.json()
  }

  async addAlertNote(alertId: number, note: string): Promise<{ id: number; note: string }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/alerts/${alertId}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ note }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add alert note (${res.status})`)
    }
    return res.json()
  }

  // 4. Investigations
  async listInvestigations(filters?: {
    status?: InvestigationStatus | string
    priority?: TrainingPriority | string
    limit?: number
    offset?: number
  }): Promise<InvestigationBriefItem[]> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.limit) params.append('limit', String(filters.limit))
    if (filters?.offset) params.append('offset', String(filters.offset))

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch investigations (${res.status})`)
    }
    return res.json()
  }

  async createInvestigation(data: {
    title: string
    description: string
    priority?: TrainingPriority
    alert_ids?: number[]
    case_id?: number
  }): Promise<InvestigationDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create investigation (${res.status})`)
    }
    return res.json()
  }

  async getInvestigation(id: number): Promise<InvestigationDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${id}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch investigation detail (${res.status})`)
    }
    return res.json()
  }

  async updateInvestigation(
    id: number,
    data: {
      title?: string
      description?: string
      status?: InvestigationStatus
      priority?: TrainingPriority
      classification?: TriageClassification
      conclusion?: string
      recommendations?: string
    }
  ): Promise<InvestigationDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update investigation (${res.status})`)
    }
    return res.json()
  }

  async addHypothesis(
    investigationId: number,
    data: {
      hypothesis_text: string
      reasoning?: string
      supporting_evidence_ids?: string[]
    }
  ): Promise<InvestigationHypothesisItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/hypotheses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add hypothesis (${res.status})`)
    }
    return res.json()
  }

  async updateHypothesis(
    investigationId: number,
    hypothesisId: number,
    data: {
      status?: HypothesisStatus
      reasoning?: string
      supporting_evidence_ids?: string[]
    }
  ): Promise<InvestigationHypothesisItem> {
    const res = await fetch(
      `${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/hypotheses/${hypothesisId}`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(data),
      }
    )
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update hypothesis (${res.status})`)
    }
    return res.json()
  }

  async addInvestigationEvidence(
    investigationId: number,
    data: {
      evidence_type: string
      reference_id?: string
      capture_id?: number
      packet_number?: number
      description: string
      evidence_data?: Record<string, unknown>
    }
  ): Promise<InvestigationEvidenceItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/evidence`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to attach evidence to investigation (${res.status})`)
    }
    return res.json()
  }

  async addInvestigationFinding(
    investigationId: number,
    data: {
      title: string
      description: string
      evidence_summary?: string
      confidence?: string
    }
  ): Promise<InvestigationFindingItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/findings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to record finding (${res.status})`)
    }
    return res.json()
  }

  async addInvestigationNote(investigationId: number, note: string): Promise<InvestigationNoteItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ note }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to record investigation note (${res.status})`)
    }
    return res.json()
  }

  async linkAlertToInvestigation(
    investigationId: number,
    alertId: number,
    relationshipType: string = 'PRIMARY'
  ): Promise<{ message: string; alert_id: number }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/alerts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ alert_id: alertId, relationship_type: relationshipType }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to link alert (${res.status})`)
    }
    return res.json()
  }

  async exportInvestigationReport(investigationId: number): Promise<Record<string, unknown>> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/investigations/${investigationId}/report`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to export investigation report (${res.status})`)
    }
    return res.json()
  }

  // 5. Cases
  async listCases(filters?: {
    status?: CaseStatus | string
    priority?: TrainingPriority | string
    limit?: number
    offset?: number
  }): Promise<CaseDetailResponse[]> {
    const params = new URLSearchParams()
    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)
    if (filters?.limit) params.append('limit', String(filters.limit))
    if (filters?.offset) params.append('offset', String(filters.offset))

    const query = params.toString() ? `?${params.toString()}` : ''
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/cases${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch cases (${res.status})`)
    }
    return res.json()
  }

  async createCase(data: {
    title: string
    description: string
    priority?: TrainingPriority
    alert_ids?: number[]
    investigation_ids?: number[]
  }): Promise<CaseDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/cases`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to create case (${res.status})`)
    }
    return res.json()
  }

  async getCase(id: number): Promise<CaseDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/cases/${id}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch case detail (${res.status})`)
    }
    return res.json()
  }

  async updateCase(
    id: number,
    data: {
      title?: string
      description?: string
      status?: CaseStatus
      priority?: TrainingPriority
    }
  ): Promise<CaseDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/cases/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to update case (${res.status})`)
    }
    return res.json()
  }

  async addCaseNote(caseId: number, note: string): Promise<CaseNoteItem> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/cases/${caseId}/notes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ note }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to add case note (${res.status})`)
    }
    return res.json()
  }

  // 6. Detection Coverage
  async getDetectionCoverage(): Promise<DetectionCoverageResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/detection-coverage`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch detection coverage matrix (${res.status})`)
    }
    return res.json()
  }

  // 7. Challenges & Scenarios
  async listChallenges(): Promise<SocChallengeItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/challenges`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC challenges (${res.status})`)
    }
    return res.json()
  }

  async getChallenge(slug: string): Promise<SocChallengeDetailResponse> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/challenges/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC challenge (${res.status})`)
    }
    return res.json()
  }

  async submitChallenge(
    slug: string,
    submission: {
      selected_classification: TriageClassification
      hypothesis_text: string
      evidence_packet_numbers: number[]
      conclusion: string
    }
  ): Promise<SocChallengeEvaluation> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/challenges/${slug}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(submission),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to evaluate challenge attempt (${res.status})`)
    }
    return res.json()
  }

  // 8. Training Datasets & Reset
  async listDatasets(): Promise<TrainingDatasetItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/datasets`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch training datasets (${res.status})`)
    }
    return res.json()
  }

  async resetTrainingDataset(datasetId: string): Promise<{ message: string; dataset: string; new_run_id: number }> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/datasets/reset`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ dataset_id: datasetId }),
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to reset training dataset (${res.status})`)
    }
    return res.json()
  }

  // 9. Audit Logs & Notifications
  async listAuditLogs(limit: number = 50): Promise<SocAuditLogItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/audit-logs?limit=${limit}`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch SOC audit logs (${res.status})`)
    }
    return res.json()
  }

  async listNotifications(): Promise<SocNotificationItem[]> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/notifications`, {
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to fetch notifications (${res.status})`)
    }
    return res.json()
  }

  async markNotificationRead(id: number): Promise<void> {
    const res = await fetch(`${this.getBaseUrl()}/api/v1/soc/notifications/${id}/read`, {
      method: 'PATCH',
      headers: { Accept: 'application/json' },
    })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || `Failed to mark notification read (${res.status})`)
    }
  }
}

export const socApi = new SocApiService()
