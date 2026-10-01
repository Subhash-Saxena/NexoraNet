import type {
  AdaptiveOverviewResponse,
  AttemptHistoryItem,
  AttemptStatusResponse,
  BookmarkItem,
  CatalogCategoryItem,
  CatalogDifficultyItem,
  CatalogFilterOptionsResponse,
  CatalogStatisticsResponse,
  CatalogTopicItem,
  CatalogTypeItem,
  CourseBrief,
  CourseDetail,
  HealthResponse,
  LabAttemptBrief,
  LabAttemptDetail,
  LabBrief,
  LabDetail,
  LabStepDetail,
  LabTelemetry,
  LearningProgressResponse,
  LearningSearchResponse,
  LessonActionResponse,
  LessonBrief,
  LessonBriefWithProgress,
  LessonDetailExtended,
  MockTestBrief,
  MockTestDetail,
  MockTestPreviewResponse,
  ModuleDetail,
  RecommendationItem,
  SaveAnswerRequest,
  SaveAnswerResponse,
  StartAdaptiveTestRequest,
  StartAttemptResponse,
  StepSubmitRequest,
  StepSubmitResponse,
  StudentQuestion,
  TestBlueprintResponse,
  TestResultResponse,
  TestReviewResponse,
  TopicBrief,
  TopicDetailExtended,
  TopicPerformanceItem,
} from '../types'
import { getApiBaseUrl } from './apiConfig'

/**
 * Standard API Client for NexoraNet platform services.
 */
class ApiService {
  private getBaseUrl(): string {
    return getApiBaseUrl()
  }

  /**
   * Check backend health status.
   * Target endpoint: GET /api/health
   */
  async checkHealth(): Promise<HealthResponse> {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 4000)

    try {
      const response = await fetch(`${this.getBaseUrl()}/api/health`, {
        signal: controller.signal,
        headers: {
          Accept: 'application/json',
        },
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to retrieve health status`)
      }

      const data: HealthResponse = await response.json()
      return data
    } finally {
      clearTimeout(timeoutId)
    }
  }

  /**
   * Introspect backend module status (API v1)
   */
  async getModuleStatus(moduleEndpoint: string): Promise<Record<string, unknown>> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/${moduleEndpoint}`, {
      headers: {
        Accept: 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Module endpoint unavailable`)
    }

    return response.json()
  }

  // --- STEP 2: Content & Assessment Endpoints ---

  async getCourses(): Promise<CourseBrief[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/courses`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load courses`)
    return response.json()
  }

  async getCourse(courseId: string | number): Promise<CourseDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/courses/${courseId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load course ${courseId}`)
    return response.json()
  }

  async getTopics(params?: { moduleId?: number; difficulty?: string }): Promise<TopicBrief[]> {
    const url = new URL(`${this.getBaseUrl()}/api/v1/topics`, window.location.origin)
    if (params?.moduleId) url.searchParams.set('module_id', params.moduleId.toString())
    if (params?.difficulty) url.searchParams.set('difficulty', params.difficulty)

    const response = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load topics`)
    return response.json()
  }

  async getTopic(topicId: string | number): Promise<TopicDetailExtended> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/topics/${topicId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load topic ${topicId}`)
    return response.json()
  }

  async getQuestions(params?: {
    topicId?: number
    difficulty?: string
    questionType?: string
    tag?: string
  }): Promise<StudentQuestion[]> {
    const url = new URL(`${this.getBaseUrl()}/api/v1/questions`, window.location.origin)
    if (params?.topicId) url.searchParams.set('topic_id', params.topicId.toString())
    if (params?.difficulty) url.searchParams.set('difficulty', params.difficulty)
    if (params?.questionType) url.searchParams.set('question_type', params.questionType)
    if (params?.tag) url.searchParams.set('tag', params.tag)

    const response = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load questions`)
    return response.json()
  }

  async getQuestion(questionId: number): Promise<StudentQuestion> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/questions/${questionId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load question ${questionId}`)
    return response.json()
  }

  async getMockTests(
    params?:
      | string
      | {
          category?: string
          difficulty?: string
          test_type?: string
          topic?: string
          duration_min?: number
          duration_max?: number
          status?: string
          q?: string
        }
  ): Promise<MockTestBrief[]> {
    const url = new URL(`${this.getBaseUrl()}/api/v1/mock-tests`, window.location.origin)
    if (typeof params === 'string') {
      url.searchParams.set('difficulty', params)
    } else if (params) {
      if (params.category) url.searchParams.set('category', params.category)
      if (params.difficulty) url.searchParams.set('difficulty', params.difficulty)
      if (params.test_type) url.searchParams.set('test_type', params.test_type)
      if (params.topic) url.searchParams.set('topic', params.topic)
      if (params.duration_min !== undefined) url.searchParams.set('duration_min', params.duration_min.toString())
      if (params.duration_max !== undefined) url.searchParams.set('duration_max', params.duration_max.toString())
      if (params.status) url.searchParams.set('status', params.status)
      if (params.q) url.searchParams.set('q', params.q)
    }

    const response = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load mock tests`)
    return response.json()
  }

  async getCatalogCategories(): Promise<CatalogCategoryItem[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/categories`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load catalog categories`)
    return response.json()
  }

  async getCatalogTopics(): Promise<CatalogTopicItem[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/topics`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load catalog topics`)
    return response.json()
  }

  async getCatalogDifficulties(): Promise<CatalogDifficultyItem[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/difficulties`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load catalog difficulties`)
    return response.json()
  }

  async getCatalogTypes(): Promise<CatalogTypeItem[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/types`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load catalog types`)
    return response.json()
  }

  async getCatalogFilterOptions(): Promise<CatalogFilterOptionsResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/filter-options`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load filter options`)
    return response.json()
  }

  async getCatalogStatistics(): Promise<CatalogStatisticsResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/statistics`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load catalog statistics`)
    return response.json()
  }

  async getMockTestPreview(mockTestId: string | number): Promise<MockTestPreviewResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/${mockTestId}/preview`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load test preview`)
    return response.json()
  }

  async getMockTestAttemptHistory(mockTestId: string | number): Promise<AttemptHistoryItem[]> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-tests/${mockTestId}/attempt-history`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load attempt history`)
    return response.json()
  }

  async getMockTestBlueprint(mockTestId: string | number): Promise<TestBlueprintResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-tests/${mockTestId}/blueprint`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load mock test blueprint`)
    return response.json()
  }

  async getMockTest(mockTestId: string | number): Promise<MockTestDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/mock-tests/${mockTestId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load mock test ${mockTestId}`)
    return response.json()
  }

  async startAttempt(mockTestId: string | number, retake = false): Promise<StartAttemptResponse> {
    const url = new URL(
      `${this.getBaseUrl()}/api/v1/mock-tests/${mockTestId}/start`,
      window.location.origin
    )
    if (retake) url.searchParams.set('retake', 'true')

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to start mock test attempt`)
    return response.json()
  }

  async getAttemptStatus(attemptId: number): Promise<AttemptStatusResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/status`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch attempt status`)
    return response.json()
  }

  async saveAnswer(attemptId: number, data: SaveAnswerRequest): Promise<SaveAnswerResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/save-answer`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(data),
      }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to save answer`)
    return response.json()
  }

  async clearAnswer(attemptId: number, questionId: number): Promise<SaveAnswerResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/clear-answer/${questionId}`,
      {
        method: 'POST',
        headers: { Accept: 'application/json' },
      }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to clear answer`)
    return response.json()
  }

  async markQuestion(
    attemptId: number,
    questionId: number,
    isMarked: boolean
  ): Promise<SaveAnswerResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/mark-question/${questionId}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ is_marked_for_review: isMarked }),
      }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to mark question`)
    return response.json()
  }

  async submitAttempt(attemptId: number): Promise<TestResultResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/submit`,
      {
        method: 'POST',
        headers: { Accept: 'application/json' },
      }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to submit exam attempt`)
    return response.json()
  }

  async getAttemptResult(attemptId: number): Promise<TestResultResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/result`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch attempt results`)
    return response.json()
  }

  async getAttemptReview(attemptId: number): Promise<TestReviewResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/review`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch test review`)
    return response.json()
  }

  async getAttemptHistory(): Promise<AttemptHistoryItem[]> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/history`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to fetch attempt history`)
    return response.json()
  }

  async createPracticeSession(
    attemptId: number,
    mode = 'incorrect_or_unanswered'
  ): Promise<StartAttemptResponse> {
    const url = new URL(
      `${this.getBaseUrl()}/api/v1/mock-test-attempts/${attemptId}/practice`,
      window.location.origin
    )
    url.searchParams.set('mode', mode)

    const response = await fetch(url.toString(), {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to create practice session`)
    return response.json()
  }

  async getTestBlueprints(): Promise<TestBlueprintResponse[]> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/mock-tests/blueprints/list`,
      { headers: { Accept: 'application/json' } }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load blueprints`)
    return response.json()
  }

  // --- STEP 3: Learning System Endpoints ---

  async getModule(moduleId: string | number): Promise<ModuleDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/modules/${moduleId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load module ${moduleId}`)
    return response.json()
  }

  async getTopicDetail(topicIdOrSlug: string | number): Promise<TopicDetailExtended> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/topics/${topicIdOrSlug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load topic ${topicIdOrSlug}`)
    return response.json()
  }

  async getTopicLessons(topicIdOrSlug: string | number): Promise<LessonBriefWithProgress[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/topics/${topicIdOrSlug}/lessons`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lessons for topic ${topicIdOrSlug}`)
    return response.json()
  }

  async getLesson(lessonIdOrSlug: string | number): Promise<LessonDetailExtended> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonIdOrSlug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lesson ${lessonIdOrSlug}`)
    return response.json()
  }

  async getNextLesson(lessonIdOrSlug: string | number): Promise<LessonBrief | null> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonIdOrSlug}/next`, {
      headers: { Accept: 'application/json' },
    })
    if (response.status === 404) return null
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to get next lesson`)
    return response.json()
  }

  async getPreviousLesson(lessonIdOrSlug: string | number): Promise<LessonBrief | null> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonIdOrSlug}/previous`, {
      headers: { Accept: 'application/json' },
    })
    if (response.status === 404) return null
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to get previous lesson`)
    return response.json()
  }

  async startLesson(lessonId: number): Promise<LessonActionResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonId}/start`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to start lesson ${lessonId}`)
    return response.json()
  }

  async completeLesson(lessonId: number): Promise<LessonActionResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonId}/complete`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to complete lesson ${lessonId}`)
    return response.json()
  }

  async getLearningProgress(): Promise<LearningProgressResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/learning/progress`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load learning progress`)
    return response.json()
  }

  async searchCurriculum(params: {
    q: string
    difficulty?: string
    type?: string
    limit?: number
  }): Promise<LearningSearchResponse> {
    const url = new URL(`${this.getBaseUrl()}/api/v1/learning/search`, window.location.origin)
    url.searchParams.set('q', params.q)
    if (params.difficulty) url.searchParams.set('difficulty', params.difficulty)
    if (params.type) url.searchParams.set('type', params.type)
    if (params.limit) url.searchParams.set('limit', params.limit.toString())

    const response = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to search curriculum`)
    return response.json()
  }

  async getBookmarks(): Promise<BookmarkItem[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/learning/bookmarks`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load bookmarks`)
    return response.json()
  }

  async bookmarkLesson(lessonId: number): Promise<{ message: string; bookmarked: boolean }> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonId}/bookmark`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to bookmark lesson ${lessonId}`)
    return response.json()
  }

  async unbookmarkLesson(lessonId: number): Promise<{ message: string; bookmarked: boolean }> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lessons/${lessonId}/bookmark`, {
      method: 'DELETE',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to unbookmark lesson ${lessonId}`)
    return response.json()
  }

  // --- STEP 4: Hands-on Networking Lab Engine Endpoints ---

  async getLabs(params?: {
    difficulty?: string
    topicId?: number
    environment?: string
    status?: string
    q?: string
  }): Promise<LabBrief[]> {
    const url = new URL(`${this.getBaseUrl()}/api/v1/labs`, window.location.origin)
    if (params?.difficulty) url.searchParams.set('difficulty', params.difficulty)
    if (params?.topicId) url.searchParams.set('topic_id', params.topicId.toString())
    if (params?.environment) url.searchParams.set('environment', params.environment)
    if (params?.status) url.searchParams.set('status', params.status)
    if (params?.q) url.searchParams.set('q', params.q)

    const response = await fetch(url.toString(), {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load labs`)
    return response.json()
  }

  async getLab(labIdOrSlug: string | number): Promise<LabDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/labs/${labIdOrSlug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lab ${labIdOrSlug}`)
    return response.json()
  }

  async getLabBySlug(slug: string): Promise<LabDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/labs/slug/${slug}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lab ${slug}`)
    return response.json()
  }

  async getLabSteps(labIdOrSlug: string | number): Promise<LabStepDetail[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/labs/${labIdOrSlug}/steps`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load steps for lab ${labIdOrSlug}`)
    return response.json()
  }

  async startLab(labIdOrSlug: string | number): Promise<LabDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/labs/${labIdOrSlug}/start`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to start lab ${labIdOrSlug}`)
    return response.json()
  }

  async submitLabStep(
    attemptId: number,
    stepId: number,
    payload: StepSubmitRequest
  ): Promise<StepSubmitResponse> {
    const response = await fetch(
      `${this.getBaseUrl()}/api/v1/lab-attempts/${attemptId}/steps/${stepId}/submit`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify(payload),
      }
    )
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to submit step answer`)
    return response.json()
  }

  async retryLab(attemptId: number): Promise<LabDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lab-attempts/${attemptId}/retry`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to retry lab`)
    return response.json()
  }

  async getLabAttempts(): Promise<LabAttemptBrief[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lab-attempts`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lab attempts`)
    return response.json()
  }

  async getLabAttemptDetail(attemptId: number): Promise<LabAttemptDetail> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/lab-attempts/${attemptId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lab attempt ${attemptId}`)
    return response.json()
  }

  async getLabTelemetry(): Promise<LabTelemetry> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/labs/telemetry`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) throw new Error(`HTTP ${response.status}: Failed to load lab telemetry`)
    return response.json()
  }

  // --- STEP 8: Adaptive Testing & Personalized Practice ---

  async getAdaptiveOverview(): Promise<AdaptiveOverviewResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive/overview`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to retrieve adaptive overview`)
    }
    return response.json()
  }

  async getTopicPerformance(activeOnly: boolean = false): Promise<TopicPerformanceItem[]> {
    const query = activeOnly ? '?active_only=true' : ''
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive/topic-performance${query}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to retrieve topic performance`)
    }
    return response.json()
  }

  async getRecommendations(): Promise<RecommendationItem[]> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive/recommendations`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to retrieve recommendations`)
    }
    return response.json()
  }

  async getNextRecommendation(): Promise<RecommendationItem | null> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive/recommendations/next`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to retrieve next recommendation`)
    }
    return response.json()
  }

  async startAdaptiveTest(payload?: StartAdaptiveTestRequest): Promise<StartAttemptResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive-tests/start`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: JSON.stringify(payload || { question_count: 20, duration_minutes: 20 }),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || `HTTP ${response.status}: Failed to launch adaptive test`)
    }
    return response.json()
  }

  async getAdaptiveTestSession(attemptId: number): Promise<StartAttemptResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive-tests/${attemptId}`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to load adaptive test session`)
    }
    return response.json()
  }

  async getAdaptiveTestStatus(attemptId: number): Promise<AttemptStatusResponse> {
    const response = await fetch(`${this.getBaseUrl()}/api/v1/adaptive-tests/${attemptId}/status`, {
      headers: { Accept: 'application/json' },
    })
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: Failed to sync adaptive test timer`)
    }
    return response.json()
  }

  async trackAdaptiveEvent(payload: {
    recommendation_type: string
    title: string
    reason: string
    action_url: string
    event_type?: string
  }): Promise<void> {
    try {
      await fetch(`${this.getBaseUrl()}/api/v1/adaptive/events`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
    } catch {
      // Telemetry failure is non-blocking
    }
  }
}

export const apiService = new ApiService()
