/**
 * Step 18: SOAR Automation API Client
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

import type {
  AutomationAuditLog,
  AutomationPlaybook,
  DryRunResponse,
  PlaybookExecution,
  PlaybookRiskLevel,
  PlaybookStatus,
  SoarMetrics,
} from '../types/soar';
import { getApiBaseUrl } from './apiConfig';

class SoarApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl();
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.getBaseUrl()}${endpoint}`;
    const headers = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed with status ${res.status}: ${res.statusText}`);
    }
    if (res.status === 204) {
      return null as unknown as T;
    }
    return res.json();
  }

  // --- Playbooks ---

  async getPlaybooks(params?: {
    status?: PlaybookStatus;
    category?: string;
    risk_level?: PlaybookRiskLevel;
    skip?: number;
    limit?: number;
  }): Promise<AutomationPlaybook[]> {
    const q = new URLSearchParams();
    if (params?.status) q.append('status', params.status);
    if (params?.category) q.append('category', params.category);
    if (params?.risk_level) q.append('risk_level', params.risk_level);
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<AutomationPlaybook[]>(`/api/v1/automation/playbooks${qs}`);
  }

  async getPlaybookDetail(playbookId: string | number): Promise<AutomationPlaybook> {
    return this.request<AutomationPlaybook>(`/api/v1/automation/playbooks/${playbookId}`);
  }

  async createPlaybook(data: Partial<AutomationPlaybook>): Promise<AutomationPlaybook> {
    return this.request<AutomationPlaybook>('/api/v1/automation/playbooks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePlaybookStatus(playbookId: string | number, status: PlaybookStatus): Promise<AutomationPlaybook> {
    return this.request<AutomationPlaybook>(
      `/api/v1/automation/playbooks/${playbookId}/status?status=${encodeURIComponent(status)}`,
      { method: 'PATCH' }
    );
  }

  async dryRunPlaybook(
    playbookId: string | number,
    sampleEvent: Record<string, any>
  ): Promise<DryRunResponse> {
    return this.request<DryRunResponse>(`/api/v1/automation/playbooks/${playbookId}/dry-run`, {
      method: 'POST',
      body: JSON.stringify({ sample_event: sampleEvent }),
    });
  }

  // --- Executions ---

  async getExecutions(params?: {
    status?: string;
    playbook_id?: string;
    skip?: number;
    limit?: number;
  }): Promise<PlaybookExecution[]> {
    const q = new URLSearchParams();
    if (params?.status) q.append('status', params.status);
    if (params?.playbook_id) q.append('playbook_id', params.playbook_id);
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<PlaybookExecution[]>(`/api/v1/automation/executions${qs}`);
  }

  async getExecutionDetail(executionId: string): Promise<PlaybookExecution> {
    return this.request<PlaybookExecution>(`/api/v1/automation/executions/${executionId}`);
  }

  async triggerPlaybook(payload: {
    playbook_identifier: string;
    trigger_source?: string;
    source_id?: string;
    trigger_data?: Record<string, any>;
    requested_by?: string;
  }): Promise<PlaybookExecution> {
    return this.request<PlaybookExecution>('/api/v1/automation/executions/trigger', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async approveExecution(
    executionId: string,
    payload: { approver: string; reason?: string }
  ): Promise<PlaybookExecution> {
    return this.request<PlaybookExecution>(`/api/v1/automation/executions/${executionId}/approve`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async rejectExecution(
    executionId: string,
    payload: { approver: string; reason?: string }
  ): Promise<PlaybookExecution> {
    return this.request<PlaybookExecution>(`/api/v1/automation/executions/${executionId}/reject`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async cancelExecution(executionId: string): Promise<PlaybookExecution> {
    return this.request<PlaybookExecution>(`/api/v1/automation/executions/${executionId}/cancel`, {
      method: 'POST',
    });
  }

  // --- Metrics & Audit ---

  async getSoarMetrics(): Promise<SoarMetrics> {
    return this.request<SoarMetrics>('/api/v1/automation/metrics');
  }

  async getAuditLogs(params?: {
    execution_id?: string;
    limit?: number;
  }): Promise<AutomationAuditLog[]> {
    const q = new URLSearchParams();
    if (params?.execution_id) q.append('execution_id', params.execution_id);
    if (params?.limit !== undefined) q.append('limit', String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<AutomationAuditLog[]>(`/api/v1/automation/audit-logs${qs}`);
  }
}

export const soarApi = new SoarApiService();
