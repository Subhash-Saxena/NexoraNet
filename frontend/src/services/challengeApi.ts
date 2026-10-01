/**
 * Step 19: CTF Challenges & Advanced Cybersecurity Training Engine API Client
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

import type {
  ChallengeAttempt,
  ChallengeCategory,
  ChallengeDetail,
  ChallengeDifficulty,
  ChallengeMetrics,
  ChallengeRecommendation,
  ChallengeSummary,
  ChallengeTrack,
  ChallengeTrackDetail,
  FlagSubmissionResponse,
  HintUnlockResponse,
  RevealSolutionResponse,
} from '../types/challenge';
import { getApiBaseUrl } from './apiConfig';

class ChallengeApiService {
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

  // --- Catalog & Filters ---

  async getChallenges(params?: {
    category?: ChallengeCategory | string;
    difficulty?: ChallengeDifficulty | string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<ChallengeSummary[]> {
    const q = new URLSearchParams();
    if (params?.category) q.append('category', params.category);
    if (params?.difficulty) q.append('difficulty', params.difficulty);
    if (params?.search) q.append('search', params.search);
    if (params?.skip !== undefined) q.append('skip', String(params.skip));
    if (params?.limit !== undefined) q.append('limit', String(params.limit));

    const qs = q.toString() ? `?${q.toString()}` : '';
    return this.request<ChallengeSummary[]>(`/api/v1/challenges${qs}`);
  }

  async getMetrics(): Promise<ChallengeMetrics> {
    return this.request<ChallengeMetrics>('/api/v1/challenges/metrics');
  }

  async getTracks(): Promise<ChallengeTrack[]> {
    return this.request<ChallengeTrack[]>('/api/v1/challenges/tracks');
  }

  async getTrackDetail(trackId: string): Promise<ChallengeTrackDetail> {
    return this.request<ChallengeTrackDetail>(`/api/v1/challenges/tracks/${trackId}`);
  }

  async getRecommendations(limit: number = 5): Promise<ChallengeRecommendation[]> {
    return this.request<ChallengeRecommendation[]>(`/api/v1/challenges/recommendations?limit=${limit}`);
  }

  // --- Challenge Detail & Solving Workflows ---

  async getChallengeDetail(challengeId: string | number): Promise<ChallengeDetail> {
    return this.request<ChallengeDetail>(`/api/v1/challenges/${challengeId}`);
  }

  async startAttempt(challengeId: string | number): Promise<ChallengeAttempt> {
    return this.request<ChallengeAttempt>(`/api/v1/challenges/${challengeId}/start`, {
      method: 'POST',
      body: JSON.stringify({}),
    });
  }

  async submitFlag(
    challengeId: string | number,
    attemptId: string,
    flag: string
  ): Promise<FlagSubmissionResponse> {
    return this.request<FlagSubmissionResponse>(`/api/v1/challenges/${challengeId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ attempt_id: attemptId, flag }),
    });
  }

  async unlockHint(
    challengeId: string | number,
    attemptId: string
  ): Promise<HintUnlockResponse> {
    return this.request<HintUnlockResponse>(`/api/v1/challenges/${challengeId}/hint`, {
      method: 'POST',
      body: JSON.stringify({ attempt_id: attemptId }),
    });
  }

  async revealSolution(
    challengeId: string | number,
    attemptId: string
  ): Promise<RevealSolutionResponse> {
    return this.request<RevealSolutionResponse>(`/api/v1/challenges/${challengeId}/reveal`, {
      method: 'POST',
      body: JSON.stringify({ attempt_id: attemptId }),
    });
  }

  async saveNotes(
    challengeId: string | number,
    attemptId: string,
    notes: string
  ): Promise<ChallengeAttempt> {
    return this.request<ChallengeAttempt>(`/api/v1/challenges/${challengeId}/notes`, {
      method: 'POST',
      body: JSON.stringify({ attempt_id: attemptId, notes }),
    });
  }
}

export const challengeApi = new ChallengeApiService();
