/**
 * Step 18: Advanced SOC Scenarios API Client
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

import type {
  ScenarioAttempt,
  ScenarioCategory,
  ScenarioDifficulty,
  ScenarioEvaluationResponse,
  ScenarioHintResponse,
  ScenarioMetrics,
  SocScenarioDetail,
  SocScenarioSummary,
  StageUpdateRequest,
} from '../types/socScenario';
import { getApiBaseUrl } from './apiConfig';

class SocScenarioApiService {
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

  // --- Catalog & Detail ---

  async getScenarios(params?: {
    difficulty?: ScenarioDifficulty;
    category?: ScenarioCategory;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<SocScenarioSummary[]> {
    const q = new URLSearchParams();
    if (params?.difficulty) q.append('difficulty', params.difficulty);
    if (params?.category) q.append('category', params.category);
    if (params?.search) q.append('search', params.search);
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<SocScenarioSummary[]>(`/api/v1/soc-scenarios${qs}`);
  }

  async getScenarioMetrics(): Promise<ScenarioMetrics> {
    return this.request<ScenarioMetrics>('/api/v1/soc-scenarios/metrics');
  }

  async getScenarioDetail(scenarioId: string | number): Promise<SocScenarioDetail> {
    return this.request<SocScenarioDetail>(`/api/v1/soc-scenarios/${scenarioId}`);
  }

  // --- Workspace & Attempts ---

  async startAttempt(scenarioId: string | number): Promise<ScenarioAttempt> {
    return this.request<ScenarioAttempt>(`/api/v1/soc-scenarios/${scenarioId}/attempts`, {
      method: 'POST',
    });
  }

  async getAttempt(attemptId: string): Promise<ScenarioAttempt> {
    return this.request<ScenarioAttempt>(`/api/v1/soc-scenarios/attempts/${attemptId}`);
  }

  async updateStage(
    attemptId: string,
    payload: StageUpdateRequest
  ): Promise<ScenarioAttempt> {
    return this.request<ScenarioAttempt>(`/api/v1/soc-scenarios/attempts/${attemptId}/stage`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async unlockHint(attemptId: string): Promise<ScenarioHintResponse> {
    return this.request<ScenarioHintResponse>(`/api/v1/soc-scenarios/attempts/${attemptId}/hint`, {
      method: 'POST',
    });
  }

  async submitAttempt(attemptId: string): Promise<ScenarioEvaluationResponse> {
    return this.request<ScenarioEvaluationResponse>(
      `/api/v1/soc-scenarios/attempts/${attemptId}/submit`,
      {
        method: 'POST',
      }
    );
  }
}

export const socScenarioApi = new SocScenarioApiService();
