/**
 * Step 20: Analytics, Skill Assessment, Portfolio & Admin API Client
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

import type {
  AchievementItem,
  AchievementsResponse,
  AdminAuditLog,
  AdminContentItem,
  AdminDashboardMetrics,
  AssessmentReport,
  CertificateVerification,
  EducationalCertificate,
  LearningProgressSummary,
  PortfolioDetail,
  PortfolioExportResponse,
  PortfolioProject,
  PublicPortfolioResponse,
  RecommendationItem,
  SkillAssessment,
  StudentOverview,
  TrendsResponse,
} from '../types/analytics';
import { getApiBaseUrl } from './apiConfig';

class AnalyticsApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl();
  }

  private getAuthHeaders(): Record<string, string> {
    const role = localStorage.getItem('nexoranet_role') || 'STUDENT';
    const userId = localStorage.getItem('nexoranet_user_id') || '2';
    return {
      'X-User-Role': role,
      'X-User-Id': userId,
    };
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.getBaseUrl()}${endpoint}`;
    const headers = {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...this.getAuthHeaders(),
      ...options.headers,
    };

    const res = await fetch(url, { ...options, headers });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || `Request failed (${res.status}): ${res.statusText}`);
    }
    if (res.status === 204) {
      return null as unknown as T;
    }
    return res.json();
  }

  // --- Student Telemetry ---

  async getOverview(): Promise<StudentOverview> {
    return this.request<StudentOverview>('/api/v1/analytics/overview');
  }

  async getLearningProgress(): Promise<LearningProgressSummary> {
    return this.request<LearningProgressSummary>('/api/v1/analytics/progress');
  }

  async getTrends(days = 14): Promise<TrendsResponse> {
    return this.request<TrendsResponse>(`/api/v1/analytics/trends?days=${days}`);
  }

  // --- Skill Assessment ---

  async getSkills(category?: string): Promise<SkillAssessment[]> {
    const q = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.request<SkillAssessment[]>(`/api/v1/skills${q}`);
  }

  async getSkillDetail(skillId: number): Promise<SkillAssessment> {
    return this.request<SkillAssessment>(`/api/v1/skills/${skillId}`);
  }

  async getSkillMatrix(): Promise<Record<string, SkillAssessment[]>> {
    return this.request<Record<string, SkillAssessment[]>>('/api/v1/skills/matrix');
  }

  // --- Recommendations ---

  async getRecommendations(): Promise<RecommendationItem[]> {
    return this.request<RecommendationItem[]>('/api/v1/recommendations');
  }

  async dismissRecommendation(id: number): Promise<void> {
    return this.request<void>(`/api/v1/recommendations/${id}/dismiss`, { method: 'POST' });
  }

  // --- Achievements ---

  async getAchievements(): Promise<AchievementsResponse> {
    return this.request<AchievementsResponse>('/api/v1/achievements');
  }

  async evaluateAchievements(): Promise<{ newly_unlocked: AchievementItem[]; total_unlocked: number }> {
    return this.request<{ newly_unlocked: AchievementItem[]; total_unlocked: number }>(
      '/api/v1/achievements/evaluate',
      { method: 'POST' }
    );
  }

  // --- Reports & Certificates ---

  async generateAssessmentReport(): Promise<AssessmentReport> {
    return this.request<AssessmentReport>('/api/v1/reports/assessment', { method: 'POST' });
  }

  async getReportHistory(): Promise<AssessmentReport[]> {
    return this.request<AssessmentReport[]>('/api/v1/reports/history');
  }

  async getCertificates(): Promise<EducationalCertificate[]> {
    return this.request<EducationalCertificate[]>('/api/v1/certificates');
  }

  async verifyCertificate(code: string): Promise<CertificateVerification> {
    return this.request<CertificateVerification>(`/api/v1/certificates/verify/${encodeURIComponent(code)}`);
  }

  // --- Portfolio ---

  async getMyPortfolio(): Promise<PortfolioDetail> {
    return this.request<PortfolioDetail>('/api/v1/portfolio');
  }

  async updatePortfolio(payload: Partial<PortfolioDetail>): Promise<PortfolioDetail> {
    return this.request<PortfolioDetail>('/api/v1/portfolio', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async addPortfolioProject(payload: Partial<PortfolioProject>): Promise<PortfolioProject> {
    return this.request<PortfolioProject>('/api/v1/portfolio/projects', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async updatePortfolioProject(projectId: number, payload: Partial<PortfolioProject>): Promise<PortfolioProject> {
    return this.request<PortfolioProject>(`/api/v1/portfolio/projects/${projectId}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async deletePortfolioProject(projectId: number): Promise<void> {
    return this.request<void>(`/api/v1/portfolio/projects/${projectId}`, {
      method: 'DELETE',
    });
  }

  async getPublicPortfolio(slug: string): Promise<PublicPortfolioResponse> {
    return this.request<PublicPortfolioResponse>(`/api/v1/portfolio/public/${encodeURIComponent(slug)}`);
  }

  async exportPortfolioJson(): Promise<PortfolioExportResponse> {
    return this.request<PortfolioExportResponse>('/api/v1/portfolio/export/json');
  }

  // --- Administration & Content Management ---

  async getAdminDashboard(): Promise<AdminDashboardMetrics> {
    return this.request<AdminDashboardMetrics>('/api/v1/admin/dashboard');
  }

  async getAdminContent(params?: { type?: string; status?: string }): Promise<AdminContentItem[]> {
    const q = new URLSearchParams();
    if (params?.type) q.append('type', params.type);
    if (params?.status) q.append('status', params.status);
    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<AdminContentItem[]>(`/api/v1/admin/content${qs}`);
  }

  async updateContentStatus(
    contentType: string,
    contentId: number,
    newStatus: string
  ): Promise<{ success: boolean; message: string; content_id: number; new_status: string }> {
    return this.request<{ success: boolean; message: string; content_id: number; new_status: string }>(
      `/api/v1/admin/content/${contentType}/${contentId}/status`,
      {
        method: 'PUT',
        body: JSON.stringify({ status: newStatus }),
      }
    );
  }

  async getAdminAuditLogs(limit = 50): Promise<AdminAuditLog[]> {
    return this.request<AdminAuditLog[]>(`/api/v1/admin/audit?limit=${limit}`);
  }
}

export const analyticsApi = new AnalyticsApiService();
