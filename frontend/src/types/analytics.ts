/**
 * Step 20: Analytics, Skill Assessment, Portfolio & Admin Types
 * NexoraNet - "Learn. Simulate. Analyze. Defend."
 */

export type SkillConfidence = 'LOW' | 'MEDIUM' | 'HIGH';
export type PortfolioVisibility = 'PRIVATE' | 'UNLISTED' | 'PUBLIC';
export type ContentStatus = 'DRAFT' | 'REVIEW' | 'PUBLISHED' | 'ARCHIVED';

export interface StudentActivity {
  id: number;
  activity_type: string;
  reference_id?: string;
  title: string;
  summary?: string;
  score?: number;
  points_earned: number;
  status?: string;
  occurred_at: string;
}

export interface StudentOverview {
  user_id: number;
  username: string;
  display_name: string;
  current_level: string;
  total_learning_time_minutes: number;
  lessons_completed: number;
  total_lessons: number;
  labs_completed: number;
  total_labs: number;
  tests_attempted: number;
  tests_completed: number;
  challenges_attempted: number;
  challenges_solved: number;
  total_challenges: number;
  total_challenge_points: number;
  soc_scenarios_completed: number;
  total_scenarios: number;
  incidents_investigated: number;
  pcap_investigations_completed: number;
  siem_investigations_completed: number;
  endpoint_investigations_completed: number;
  current_learning_streak: number;
  recent_activity: StudentActivity[];
}

export interface LearningProgressModule {
  module_id: number;
  title: string;
  slug: string;
  category: string;
  total_lessons: number;
  completed_lessons: number;
  completion_percentage: number;
}

export interface LearningProgressSummary {
  overall_completion_percentage: number;
  total_lessons: number;
  completed_lessons: number;
  modules: LearningProgressModule[];
}

export interface TrendPoint {
  date: string;
  learning_minutes: number;
  activities_count: number;
  average_accuracy: number;
}

export interface TrendsResponse {
  history: TrendPoint[];
}

export interface SkillAssessment {
  skill_id: number;
  skill_code: string;
  name: string;
  category: string;
  description?: string;
  accuracy: number;
  evidence_count: number;
  confidence: SkillConfidence;
  confidence_score: number;
  confidence_rationale: string;
  recent_performance: number;
  historical_performance: number;
  practical_performance: number;
  last_evaluated?: string;
  recommended_next_step?: string;
}

export interface RecommendationItem {
  id: number;
  rec_type: string;
  target_id?: string;
  title: string;
  rationale: string;
  priority: number;
  action_url?: string;
  created_at: string;
  completed: boolean;
}

export interface AchievementItem {
  id: number;
  slug: string;
  title: string;
  description: string;
  badge_icon: string;
  unlocked: boolean;
  unlocked_at?: string;
}

export interface AchievementsResponse {
  achievements: AchievementItem[];
  unlocked_count: number;
  total_count: number;
}

export interface AssessmentReport {
  id?: number;
  report_code: string;
  student_name: string;
  generated_at: string;
  executive_summary: string;
  disclaimer: string;
  knowledge_evidence: Record<string, unknown>;
  practical_evidence: Record<string, unknown>;
  skills_summary: Array<{
    code: string;
    name: string;
    category: string;
    accuracy: number;
    confidence: SkillConfidence;
  }>;
  strengths: string[];
  growth_areas: string[];
  recommendations: string[];
}

export interface EducationalCertificate {
  id: number;
  certificate_code: string;
  title: string;
  track_code: string;
  issued_at: string;
  hours_invested: number;
  summary?: string;
  verification_url: string;
}

export interface CertificateVerification {
  is_valid: boolean;
  certificate_code: string;
  title: string;
  track_code: string;
  student_name: string;
  issued_at: string;
  hours_invested: number;
  disclaimer: string;
}

export interface PortfolioProject {
  id: number;
  title: string;
  description: string;
  technologies: string[];
  skills: string[];
  learning_outcome?: string;
  repository_url?: string;
  demo_url?: string;
  completed_date?: string;
  is_featured: boolean;
}

export interface PortfolioDetail {
  id: number;
  user_id: number;
  public_slug: string;
  visibility: PortfolioVisibility;
  display_name: string;
  bio?: string;
  learning_focus?: string;
  social_links: Record<string, string>;
  show_stats: boolean;
  show_skills: boolean;
  show_certifications: boolean;
  no_index: boolean;
  projects: PortfolioProject[];
}

export interface PublicPortfolioResponse {
  display_name: string;
  bio?: string;
  learning_focus?: string;
  social_links: Record<string, string>;
  projects: PortfolioProject[];
  stats?: {
    lessons_completed?: number;
    labs_completed?: number;
    challenges_solved?: number;
    scenarios_completed?: number;
    total_learning_time_minutes?: number;
  };
  skills?: Array<{
    name: string;
    category: string;
    confidence: string;
    accuracy: number;
  }>;
  certifications?: Array<{
    code: string;
    title: string;
    track: string;
    issued_at: string;
  }>;
}

export interface PortfolioExportResponse {
  export_version: string;
  generated_at: string;
  display_name: string;
  bio?: string;
  visibility: string;
  projects: PortfolioProject[];
  verified_certificates: Array<Record<string, unknown>>;
  disclaimer: string;
}

export interface AdminDashboardMetrics {
  total_users: number;
  active_students_7d: number;
  catalog_counts: Record<string, number>;
  publication_status: {
    published: number;
    draft: number;
    review: number;
    archived: number;
  };
  audit_count: number;
}

export interface AdminContentItem {
  type: string;
  id: number;
  title: string;
  slug?: string;
  category?: string;
  status: string;
  updated_at?: string;
}

export interface AdminAuditLog {
  id: number;
  actor_id?: number;
  actor_role: string;
  action: string;
  target_type: string;
  target_id: string;
  details?: string;
  created_at: string;
}
