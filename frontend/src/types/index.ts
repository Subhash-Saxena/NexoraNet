export type BackendHealthState = 'checking' | 'connected' | 'disconnected'

export interface HealthResponse {
  status: string
  service: string
}

export interface StudentDashboardMetrics {
  learningProgress: number // percentage 0-100
  labsCompleted: number
  mockTests: number
  networkingSkills: number // percentage 0-100
  securitySkills: number // percentage 0-100
  currentLevel: string
}

export interface LearningPathStep {
  id: string
  title: string
  subtitle: string
  tag: string
  active?: boolean
}

export interface ModuleFeatureSpec {
  id: string
  title: string
  route: string
  tagline: string
  description: string
  phase: string
  statusLabel: string
  practiceOpportunities: string[]
  keyObjectives: string[]
}

// STEP 2: Database & Content Architecture Types

export type DifficultyLevel = 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'MIXED'

export type QuestionType =
  | 'SINGLE_CHOICE'
  | 'MULTIPLE_CHOICE'
  | 'TRUE_FALSE'
  | 'FILL_BLANK'
  | 'NUMERICAL'
  | 'SUBNETTING'
  | 'SCENARIO'
  | 'PACKET_ANALYSIS'
  | 'MATCHING'

export interface TopicBrief {
  id: number
  module_id: number
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  order_index: number
}

export interface LessonBrief {
  id: number
  topic_id: number
  title: string
  slug: string
  content_type: string
  order_index: number
  estimated_minutes: number
  difficulty: DifficultyLevel
}

export interface TopicDetail extends TopicBrief {
  lessons: LessonBrief[]
}

export interface ModuleDetail {
  id: number
  course_id: number
  title: string
  slug: string
  description?: string | null
  order_index: number
  difficulty: DifficultyLevel
  topics: TopicBrief[]
}

export interface CourseBrief {
  id: number
  title: string
  slug: string
  description?: string | null
  level: DifficultyLevel
  estimated_hours: number
  modules_count: number
}

export interface CourseDetail extends CourseBrief {
  modules: ModuleDetail[]
}

export interface QuestionTag {
  id: number
  name: string
  slug: string
}

export interface StudentQuestionOption {
  id: number
  option_text: string
  order_index: number
}

export interface StudentQuestion {
  id: number
  question_text: string
  question_type: QuestionType
  topic_id: number
  difficulty: DifficultyLevel
  cognitive_level: string
  points: number
  estimated_seconds: number
  options: StudentQuestionOption[]
  tags: QuestionTag[]
}

export type MockTestType =
  | 'TOPIC'
  | 'DIFFICULTY'
  | 'MIXED'
  | 'COMPREHENSIVE'
  | 'PRACTICE'
  | 'FULL_MOCK'

export type AttemptStatus =
  | 'IN_PROGRESS'
  | 'SUBMITTED'
  | 'COMPLETED'
  | 'EXPIRED'
  | 'ABANDONED'

export interface MockTestTopicCount {
  topic: string
  question_count: number
}

export interface StudentOptionBrief {
  id: number
  option_text: string
  order_index: number
}

export interface StudentQuestionPayload {
  id: number
  question_number: number
  question_text: string
  question_type: QuestionType
  points: number
  topic_title: string
  difficulty: DifficultyLevel
  options: StudentOptionBrief[]
}

export interface StudentAnswerBrief {
  question_id: number
  selected_option_ids: number[]
  is_marked_for_review: boolean
  answered_at: string
}

export interface MockTestBrief {
  id: number
  code?: string | null
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  test_type?: MockTestType
  duration_minutes: number
  total_questions: number
  passing_percentage: number
  status: string
  prerequisites?: string | null
  tags?: string[]
  topics_covered?: string[]
  is_ready?: boolean
  shortfall?: number
  latest_attempt_score?: number | null
  latest_attempt_status?: string | null
  active_attempt_id?: number | null
  attempt_count?: number
}

export interface MockTestDetail extends MockTestBrief {
  instructions?: string | null
  what_you_will_practice?: string[]
  blueprint_id?: number | null
  topics_breakdown?: MockTestTopicCount[]
  questions?: StudentQuestionPayload[] | StudentQuestion[]
}

// Step 7: Mock Test Catalog Interfaces
export interface CatalogCategoryItem {
  key: string
  title: string
  description: string
  test_count: number
  icon: string
}

export interface CatalogTopicItem {
  topic_id: number
  topic_title: string
  topic_slug: string
  test_count: number
}

export interface CatalogDifficultyItem {
  difficulty: DifficultyLevel
  label: string
  test_count: number
}

export interface CatalogTypeItem {
  test_type: MockTestType
  label: string
  test_count: number
}

export interface CatalogDurationOption {
  label: string
  min_minutes: number
  max_minutes?: number | null
}

export interface CatalogFilterOptionsResponse {
  categories: CatalogCategoryItem[]
  topics: CatalogTopicItem[]
  difficulties: CatalogDifficultyItem[]
  types: CatalogTypeItem[]
  duration_ranges: CatalogDurationOption[]
}

export interface CatalogStatisticsResponse {
  total_tests: number
  ready_tests: number
  draft_tests: number
  beginner_tests: number
  intermediate_tests: number
  advanced_tests: number
  full_mock_tests: number
  total_questions_represented: number
}

export interface MockTestPreviewTopicRule {
  topic_title: string
  topic_slug: string
  difficulty?: DifficultyLevel | null
  question_count: number
  available_in_bank: number
  is_met: boolean
}

export interface MockTestPreviewResponse {
  id: number
  code?: string | null
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  test_type: MockTestType
  duration_minutes: number
  total_questions: number
  passing_percentage: number
  status: string
  prerequisites?: string | null
  tags: string[]
  is_ready: boolean
  shortfall: number
  topics_covered: string[]
  what_you_will_practice: string[]
  syllabus_rules: MockTestPreviewTopicRule[]
}

export interface StartAttemptResponse {
  attempt_id: number
  test_id: number
  test_title: string
  test_slug: string
  duration_minutes: number
  passing_percentage: number
  started_at: string
  expires_at: string
  remaining_seconds: number
  status: AttemptStatus
  questions: StudentQuestionPayload[]
  saved_answers: StudentAnswerBrief[]
}

export interface SaveAnswerRequest {
  question_id: number
  selected_option_ids: number[]
  is_marked_for_review?: boolean
}

export interface SaveAnswerResponse {
  success: boolean
  question_id: number
  selected_option_ids: number[]
  is_marked_for_review: boolean
  message: string
}

export interface AttemptStatusResponse {
  attempt_id: number
  status: AttemptStatus
  started_at: string
  expires_at: string
  remaining_seconds: number
  is_expired: boolean
  answered_count: number
  marked_count: number
  total_questions: number
}

export interface TopicPerformanceResponse {
  topic_id: number
  topic_title: string
  total_questions: number
  correct_questions: number
  points_earned: number
  total_points: number
  percentage: number
}

export interface DifficultyPerformanceResponse {
  difficulty: string
  total_questions: number
  correct_questions: number
  percentage: number
}

export interface TestResultResponse {
  attempt_id: number
  test_id: number
  test_title: string
  test_slug: string
  status: AttemptStatus
  score: number
  percentage: number
  total_points: number
  earned_points: number
  passing_percentage: number
  passed: boolean
  total_questions: number
  attempted_questions: number
  unanswered_questions: number
  correct_answers: number
  incorrect_answers: number
  time_taken_seconds: number
  started_at: string
  submitted_at?: string | null
  topic_breakdown: TopicPerformanceResponse[]
  difficulty_breakdown: DifficultyPerformanceResponse[]
}

export interface ReviewOptionItem {
  id: number
  option_text: string
  is_correct: boolean
}

export interface QuestionReviewItem {
  question_id: number
  question_number: number
  question_text: string
  question_type: QuestionType
  points: number
  topic_title: string
  difficulty: DifficultyLevel
  options: ReviewOptionItem[]
  selected_option_ids: number[]
  is_correct: boolean
  points_earned: number
  is_marked_for_review: boolean
  explanation: string
}

export interface TestReviewResponse {
  attempt_id: number
  test_id: number
  test_title: string
  test_slug: string
  status: AttemptStatus
  result: TestResultResponse
  questions: QuestionReviewItem[]
}

export interface AttemptHistoryItem {
  attempt_id: number
  test_id: number
  test_title: string
  test_slug: string
  difficulty: DifficultyLevel
  test_type: MockTestType
  status: AttemptStatus
  score: number
  total_points: number
  percentage: number
  passed: boolean
  started_at: string
  submitted_at?: string | null
  time_taken_seconds: number
}

export interface TestBlueprintRuleBrief {
  id: number
  topic_id: number
  topic_title?: string | null
  difficulty?: DifficultyLevel | null
  question_count: number
  question_type?: QuestionType | null
}

export interface TestBlueprintResponse {
  id: number
  title: string
  slug: string
  description?: string | null
  total_questions: number
  duration_minutes: number
  difficulty: DifficultyLevel
  rules: TestBlueprintRuleBrief[]
}

// STEP 3: Learning System & Curriculum Types

export type ProgressStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED'

export interface PrerequisiteTopic {
  id: number
  title: string
  slug: string
  difficulty: DifficultyLevel
  is_completed: boolean
}

export interface LessonBriefWithProgress extends LessonBrief {
  status: ProgressStatus
  is_bookmarked: boolean
}

export interface RelatedItemBrief {
  id: number
  title: string
  slug: string
  difficulty: DifficultyLevel
  status: string
  description?: string | null
}

export interface TopicDetailExtended {
  id: number
  module_id: number
  module_title: string
  module_slug: string
  course_id: number
  course_title: string
  course_slug: string
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  order_index: number
  estimated_minutes: number
  learning_objectives: string[]
  security_relevance?: string | null
  prerequisites: PrerequisiteTopic[]
  lessons: LessonBriefWithProgress[]
  lessons_count: number
  completed_lessons_count: number
  completion_percentage: number
  related_labs: RelatedItemBrief[]
  related_mock_tests: RelatedItemBrief[]
  next_topic?: TopicBrief | null
  previous_topic?: TopicBrief | null
}

export interface LessonDetailExtended {
  id: number
  topic_id: number
  topic_title: string
  topic_slug: string
  module_id: number
  module_title: string
  module_slug: string
  course_id: number
  course_title: string
  course_slug: string
  title: string
  slug: string
  description?: string | null
  content: string
  content_type: string
  order_index: number
  estimated_minutes: number
  difficulty: DifficultyLevel
  status: ProgressStatus
  started_at?: string | null
  completed_at?: string | null
  last_accessed_at?: string | null
  is_bookmarked: boolean
  next_lesson?: LessonBrief | null
  previous_lesson?: LessonBrief | null
  related_lab?: RelatedItemBrief | null
  related_mock_test?: RelatedItemBrief | null
}

export interface LevelProgress {
  level: DifficultyLevel
  total_lessons: number
  completed_lessons: number
  percentage: number
}

export interface ContinueLearningItem {
  lesson_id: number
  lesson_title: string
  lesson_slug: string
  topic_title: string
  topic_slug: string
  module_title: string
  module_slug: string
  difficulty: DifficultyLevel
  estimated_minutes: number
  lesson_index: number
  total_topic_lessons: number
}

export interface LearningProgressResponse {
  overall_percentage: number
  total_lessons: number
  completed_lessons: number
  in_progress_lessons: number
  remaining_lessons: number
  current_level: string
  beginner_progress: LevelProgress
  intermediate_progress: LevelProgress
  advanced_progress: LevelProgress
  continue_learning?: ContinueLearningItem | null
}

export interface SearchResultItem {
  type: string
  id: number
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  parent_title?: string | null
  url: string
}

export interface LearningSearchResponse {
  query: string
  total_results: number
  results: SearchResultItem[]
}

export interface BookmarkItem {
  id: number
  lesson_id: number
  lesson_title: string
  lesson_slug: string
  topic_title: string
  topic_slug: string
  module_title: string
  module_slug: string
  difficulty: DifficultyLevel
  estimated_minutes: number
  created_at: string
}

export interface LessonActionResponse {
  message: string
  lesson_id: number
  status: ProgressStatus
  updated_at: string
}

// STEP 4: Hands-on Networking Lab Engine Types

export type LabEnvironmentType =
  | 'LOCAL_SYSTEM'
  | 'CONCEPTUAL'
  | 'CONTAINER'
  | 'PCAP'
  | 'SIMULATOR'
  | 'LOG_ANALYSIS'

export interface SafeInputOption {
  id: number | string
  text: string
}

export interface SafeInputConfig {
  validation_type: string
  input_type?: string
  placeholder?: string
  label?: string
  helper_text?: string
  options?: SafeInputOption[]
  fields?: string[]
}

export interface LabQuestionBrief {
  id: number
  step_id?: number | null
  question_text: string
  question_type: string
  points: number
  order_index: number
  safe_input_config: SafeInputConfig
}

export interface LabStepSubmissionBrief {
  id: number
  step_id: number
  submitted_answer: string
  is_correct: boolean
  points_earned: number
  hint_used: boolean
  feedback?: string | null
  submitted_at: string
}

export interface LabStepDetail {
  id: number
  step_number: number
  title: string
  description?: string | null
  instructions: string
  hint?: string | null
  expected_observation?: string | null
  validation_type: string
  points: number
  is_required: boolean
  safe_input_config: SafeInputConfig
  questions: LabQuestionBrief[]
  is_completed: boolean
  points_earned: number
  latest_submission?: LabStepSubmissionBrief | null
}

export interface LabBrief {
  id: number
  topic_id: number
  topic_title: string
  topic_slug: string
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  estimated_minutes: number
  environment_type: string
  status: string
  is_published: boolean
  total_steps: number
  total_points: number
  user_status: 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED'
  latest_score_percentage?: number | null
}

export interface LabDetail {
  id: number
  topic_id: number
  topic_title: string
  topic_slug: string
  title: string
  slug: string
  description?: string | null
  difficulty: DifficultyLevel
  estimated_minutes: number
  environment_type: string
  instructions?: string | null
  objectives: string[]
  prerequisites: string[]
  status: string
  is_published: boolean
  total_steps: number
  total_points: number
  steps: LabStepDetail[]
  active_attempt_id?: number | null
  active_attempt_status?: string | null
  active_attempt_score: number
  active_attempt_percentage: number
  active_attempt_time_taken?: number | null
  attempt_number: number
}

export interface StepSubmitRequest {
  submitted_answer: unknown
  hint_used?: boolean
}

export interface StepSubmitResponse {
  step_id: number
  attempt_id: number
  is_correct: boolean
  points_earned: number
  max_points: number
  feedback: string
  explanation?: string | null
  attempt_score: number
  attempt_total_points: number
  attempt_percentage: number
  is_lab_completed: boolean
}

export interface LabAttemptBrief {
  id: number
  lab_id: number
  lab_title: string
  lab_slug: string
  lab_difficulty: string
  lab_environment: string
  attempt_number: number
  status: 'IN_PROGRESS' | 'SUBMITTED' | 'COMPLETED' | 'EXPIRED' | 'ABANDONED'
  score: number
  total_points: number
  percentage: number
  started_at: string
  completed_at?: string | null
  time_taken_seconds?: number | null
}

export interface LabStepSubmissionDetail {
  step_id: number
  step_number: number
  step_title: string
  submitted_answer: string
  is_correct: boolean
  points_earned: number
  max_points: number
  hint_used: boolean
  feedback?: string | null
  explanation?: string | null
  submitted_at: string
}

export interface LabAttemptDetail {
  id: number
  lab_id: number
  lab_title: string
  lab_slug: string
  lab_difficulty: string
  attempt_number: number
  status: 'IN_PROGRESS' | 'SUBMITTED' | 'COMPLETED' | 'EXPIRED' | 'ABANDONED'
  score: number
  total_points: number
  percentage: number
  started_at: string
  completed_at?: string | null
  time_taken_seconds?: number | null
  submissions: LabStepSubmissionDetail[]
}

export interface LabTelemetry {
  total_labs: number
  completed_labs: number
  in_progress_labs: number
  average_score: number
  beginner_completed: number
  beginner_total: number
  intermediate_completed: number
  intermediate_total: number
  advanced_completed: number
  advanced_total: number
}

// STEP 8: Adaptive Testing & Personalized Practice Types

export type TopicPerformanceStatus =
  | 'INSUFFICIENT_DATA'
  | 'NEEDS_PRACTICE'
  | 'DEVELOPING'
  | 'SOLID'
  | 'STRONG'

export type RecommendationType =
  | 'LESSON'
  | 'LAB'
  | 'MOCK_TEST'
  | 'ADAPTIVE_TEST'
  | 'TOPIC_PRACTICE'
  | 'DIFFICULTY_REINFORCEMENT'
  | 'REVIEW'

export type RecommendationPriority = 'HIGH' | 'MEDIUM' | 'LOW'

export type ConfidenceLevel = 'INSUFFICIENT' | 'PRELIMINARY' | 'DEVELOPING' | 'STRONG'

export interface DifficultyStats {
  seen: number
  correct: number
  accuracy: number
}

export interface DifficultyPerformanceSummary {
  BEGINNER: DifficultyStats
  INTERMEDIATE: DifficultyStats
  ADVANCED: DifficultyStats
}

export interface TopicPerformanceItem {
  topic_id: number
  topic_title: string
  topic_slug: string
  status: TopicPerformanceStatus
  questions_seen: number
  questions_answered: number
  correct_answers: number
  incorrect_answers: number
  unanswered: number
  accuracy: number
  recent_accuracy: number
  confidence_level: ConfidenceLevel
  recommended_action: string
  last_attempt_at: string | null
  difficulty_distribution: Record<string, DifficultyStats>
}

export interface RecommendationItem {
  id: string
  type: RecommendationType
  title: string
  reason: string
  priority: RecommendationPriority
  topic_id?: number | null
  topic_slug?: string | null
  recommended_difficulty?: DifficultyLevel | null
  action_label: string
  action_url: string
}

export interface AdaptiveOverviewResponse {
  user_id: number
  has_sufficient_data: boolean
  data_message: string
  overall_accuracy: number
  total_questions_analyzed: number
  total_attempts_analyzed: number
  recommended_difficulty: DifficultyLevel
  difficulty_reason: string
  difficulty_performance: DifficultyPerformanceSummary
  top_topics_needing_practice: TopicPerformanceItem[]
  strongest_topics: TopicPerformanceItem[]
  all_topics: TopicPerformanceItem[]
  next_action: RecommendationItem | null
  recommendations: RecommendationItem[]
}

export interface StartAdaptiveTestRequest {
  question_count?: number
  duration_minutes?: number
  focus_topic_ids?: number[]
}

// STEP 11: Network Detection Engine Types
export * from './detection'

// STEP 12: SOC Dashboard & Alert Triage Types
export * from './soc'

// STEP 13: Threat Intelligence & IOC Investigation Types
export * from './threat_intel'

// STEP 14: Threat Hunting & Investigation Workspace Types
export * from './threat_hunting'

// STEP 15: SIEM & Security Log Analysis Engine Types
export * from './siem'

// STEP 16: Endpoint Security & Host Investigation Engine Types
export * from './endpointSecurity'

// STEP 17: Incident Response, Case Management & MITRE ATT&CK Types
export * from './incidentResponse'

// STEP 18: SOAR Automation & Advanced SOC Scenarios Types
export * from './soar'
export * from './socScenario'

// STEP 19: CTF Challenges & Advanced Training Types
export type {
  ChallengeCategory,
  ChallengeDifficulty,
  ChallengeType,
  ChallengeAttemptStatus,
  ChallengeSummary,
  ChallengeStage,
  ChallengeHint,
  ChallengeEvidence,
  ChallengeDetail,
  CtfChallengeAttempt,
  FlagSubmissionResponse,
  HintUnlockResponse,
  RevealSolutionResponse,
  ChallengeTrackItem,
  ChallengeTrack,
  ChallengeTrackDetail,
  ChallengeMetrics,
  ChallengeRecommendation,
} from './challenge'

