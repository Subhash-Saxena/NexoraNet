import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { MainLayout } from './layouts/MainLayout'
import { DashboardPage } from './pages/Dashboard/DashboardPage'
import { LearningPage } from './pages/Learning/LearningPage'
import { TopicPage } from './pages/Learning/TopicPage'
import { LessonPage } from './pages/Learning/LessonPage'
import { BookmarksPage } from './pages/Learning/BookmarksPage'
import { LabsPage } from './pages/Labs/LabsPage'
import { LabDetailPage } from './pages/Labs/LabDetailPage'
import { LabHistoryPage } from './pages/Labs/LabHistoryPage'
import { MockTestsPage } from './pages/MockTests/MockTestsPage'
import { MockTestDetailPage } from './pages/MockTests/MockTestDetailPage'
import { MockTestWorkspacePage } from './pages/MockTests/MockTestWorkspacePage'
import { MockTestResultPage } from './pages/MockTests/MockTestResultPage'
import { MockTestReviewPage } from './pages/MockTests/MockTestReviewPage'
import { MockTestHistoryPage } from './pages/MockTests/MockTestHistoryPage'
import { ChallengesPage } from './pages/Challenges/ChallengesPage'
import { ChallengeDetailPage } from './pages/Challenges/ChallengeDetailPage'
import { ChallengeWorkspacePage } from './pages/Challenges/ChallengeWorkspacePage'
import { ChallengeResultPage } from './pages/Challenges/ChallengeResultPage'
import { PacketAnalysisPage } from './pages/PacketAnalysis/PacketAnalysisPage'
import { CaptureInspectionPage } from './pages/PacketAnalysis/CaptureInspectionPage'
import { InvestigationReportPage } from './pages/PacketAnalysis/InvestigationReportPage'
import { NetworkSimulatorPage } from './pages/NetworkSimulator/NetworkSimulatorPage'
import { SocDashboardPage } from './pages/Soc/SocDashboardPage'
import { AlertQueuePage } from './pages/Soc/AlertQueuePage'
import { AlertDetailPage } from './pages/Soc/AlertDetailPage'
import { AlertTriagePage } from './pages/Soc/AlertTriagePage'
import { AnalystQueuePage } from './pages/Soc/AnalystQueuePage'
import { InvestigationListPage } from './pages/Soc/InvestigationListPage'
import { InvestigationWorkspacePage } from './pages/Soc/InvestigationWorkspacePage'
import { CaseListPage } from './pages/Soc/CaseListPage'
import { CaseDetailPage } from './pages/Soc/CaseDetailPage'
import { DetectionCoveragePage } from './pages/Soc/DetectionCoveragePage'
import { SocChallengesPage } from './pages/Soc/SocChallengesPage'
import { SocChallengeDetailPage } from './pages/Soc/SocChallengeDetailPage'
import { IncidentsPage } from './pages/Soc/IncidentsPage'
import { IncidentDetailPage } from './pages/Soc/IncidentDetailPage'
import { MitreCoveragePage } from './pages/Soc/MitreCoveragePage'
import { PlaybooksPage } from './pages/Soc/PlaybooksPage'
import { ProgressPage } from './pages/Progress/ProgressPage'
import { SettingsPage } from './pages/Settings/SettingsPage'
import { AdaptivePage } from './pages/Adaptive/AdaptivePage'
import { DetectionDashboardPage } from './pages/Detection/DetectionDashboardPage'
import { DetectionRunPage } from './pages/Detection/DetectionRunPage'
import { AlertDetailsPage } from './pages/Detection/AlertDetailsPage'
import { DetectionRulesPage } from './pages/Detection/DetectionRulesPage'
import { ThreatIntelDashboardPage } from './pages/ThreatIntel/ThreatIntelDashboardPage'
import { IndicatorListPage } from './pages/ThreatIntel/IndicatorListPage'
import { IndicatorDetailPage } from './pages/ThreatIntel/IndicatorDetailPage'
import { IndicatorGraphPage } from './pages/ThreatIntel/IndicatorGraphPage'
import { ThreatIntelSearchPage } from './pages/ThreatIntel/ThreatIntelSearchPage'
import { WatchlistPage } from './pages/ThreatIntel/WatchlistPage'
import { ThreatIntelChallengesPage } from './pages/ThreatIntel/ThreatIntelChallengesPage'
import { ThreatIntelChallengeDetailPage } from './pages/ThreatIntel/ThreatIntelChallengeDetailPage'
import { ThreatHuntingDashboardPage } from './pages/ThreatHuntingDashboardPage'
import { HuntScenariosPage } from './pages/HuntScenariosPage'
import { HuntWorkspacePage } from './pages/HuntWorkspacePage'
import { SiemDashboardPage } from './pages/SiemDashboardPage'
import { SiemSearchPage } from './pages/SiemSearchPage'
import { SiemDatasetsPage } from './pages/SiemDatasetsPage'
import { SiemRulesPage } from './pages/SiemRulesPage'
import { SiemLabsPage } from './pages/SiemLabsPage'
import { EndpointDashboardPage } from './pages/EndpointDashboardPage'
import { EndpointHostsPage } from './pages/EndpointHostsPage'
import { EndpointHostDetailPage } from './pages/EndpointHostDetailPage'
import { EndpointEventsPage } from './pages/EndpointEventsPage'
import { EndpointInvestigationsPage } from './pages/EndpointInvestigationsPage'
import { EndpointScenariosPage } from './pages/EndpointScenariosPage'
import { SoarDashboardPage } from './pages/Soc/SoarDashboardPage'
import { SoarPlaybooksPage } from './pages/Soc/SoarPlaybooksPage'
import { SoarPlaybookDetailPage } from './pages/Soc/SoarPlaybookDetailPage'
import { SoarExecutionsPage } from './pages/Soc/SoarExecutionsPage'
import { SoarExecutionDetailPage } from './pages/Soc/SoarExecutionDetailPage'
import { SocScenariosPage } from './pages/Soc/SocScenariosPage'
import { SocScenarioWorkspacePage } from './pages/Soc/SocScenarioWorkspacePage'
import { SocScenarioResultPage } from './pages/Soc/SocScenarioResultPage'
import { SkillCatalogPage } from './pages/Analytics/SkillCatalogPage'
import { AssessmentReportPage } from './pages/Analytics/AssessmentReportPage'
import { PortfolioPage } from './pages/Analytics/PortfolioPage'
import { PublicPortfolioPage } from './pages/Analytics/PublicPortfolioPage'
import { AdminDashboardPage } from './pages/Analytics/AdminDashboardPage'
import { AdminContentPage } from './pages/Analytics/AdminContentPage'
import { AdminAuditPage } from './pages/Analytics/AdminAuditPage'
import { NotFoundPage } from './pages/NotFound/NotFoundPage'
import { AuthProvider } from './context/AuthContext'
import { LoginPage } from './pages/Auth/LoginPage'
import { ErrorBoundary } from './components/common/ErrorBoundary'


export const App: React.FC = () => {
  return (
    <ErrorBoundary label="NexoraNet Application">
      <BrowserRouter>
        <AuthProvider>
          <Routes>
          <Route element={<MainLayout />}>
            <Route path="/login" element={<LoginPage initialTab="login" />} />
            <Route path="/register" element={<LoginPage initialTab="register" />} />
            <Route path="/" element={<DashboardPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/learning" element={<LearningPage />} />
            <Route path="/learning/topics/:topicSlug" element={<TopicPage />} />
            <Route path="/learning/lessons/:lessonSlug" element={<LessonPage />} />
            <Route path="/learning/bookmarks" element={<BookmarksPage />} />
            <Route path="/labs" element={<LabsPage />} />
          <Route path="/labs/history" element={<LabHistoryPage />} />
          <Route path="/labs/:labSlug" element={<LabDetailPage />} />
          <Route path="/mock-tests" element={<MockTestsPage />} />
          <Route path="/mock-tests/history" element={<MockTestHistoryPage />} />
          <Route path="/mock-tests/:slug" element={<MockTestDetailPage />} />
          <Route path="/mock-tests/attempt/:attemptId" element={<MockTestWorkspacePage />} />
          <Route path="/mock-tests/attempt/:attemptId/result" element={<MockTestResultPage />} />
          <Route path="/mock-tests/attempt/:attemptId/review" element={<MockTestReviewPage />} />
          <Route path="/challenges" element={<ChallengesPage />} />
          <Route path="/challenges/:challengeId" element={<ChallengeDetailPage />} />
          <Route path="/challenges/:challengeId/workspace" element={<ChallengeWorkspacePage />} />
          <Route path="/challenges/:challengeId/results" element={<ChallengeResultPage />} />
          <Route path="/packet-analysis" element={<PacketAnalysisPage />} />
          <Route path="/packet-analysis/inspect/:captureId" element={<CaptureInspectionPage />} />
          <Route path="/packet-analysis/report/:captureId" element={<InvestigationReportPage />} />
          <Route path="/detection" element={<DetectionDashboardPage />} />
          <Route path="/detection/run" element={<DetectionRunPage />} />
          <Route path="/detection/alerts/:alertId" element={<AlertDetailsPage />} />
          <Route path="/detection/rules" element={<DetectionRulesPage />} />
          <Route path="/network-simulator" element={<NetworkSimulatorPage />} />
          <Route path="/network-simulator/topology/:topologyId" element={<NetworkSimulatorPage />} />
          {/* STEP 12: SOC Dashboard, Alert Queue, Triage & Investigations */}
          <Route path="/soc" element={<SocDashboardPage />} />
          <Route path="/soc/alerts" element={<AlertQueuePage />} />
          <Route path="/soc/alerts/:alertId" element={<AlertDetailPage />} />
          <Route path="/soc/alerts/:alertId/triage" element={<AlertTriagePage />} />
          <Route path="/soc/queue" element={<AnalystQueuePage />} />
          <Route path="/soc/investigations" element={<InvestigationListPage />} />
          <Route path="/soc/investigations/:investigationId" element={<InvestigationWorkspacePage />} />
          <Route path="/soc/cases" element={<CaseListPage />} />
          <Route path="/soc/cases/:caseId" element={<CaseDetailPage />} />
          <Route path="/soc/detection-coverage" element={<DetectionCoveragePage />} />
          <Route path="/soc/challenges" element={<SocChallengesPage />} />
          <Route path="/soc/challenges/:challengeSlug" element={<SocChallengeDetailPage />} />
          {/* STEP 17: Incident Response, Case Management & MITRE ATT&CK */}
          <Route path="/soc/incidents" element={<IncidentsPage />} />
          <Route path="/soc/incidents/:incidentId" element={<IncidentDetailPage />} />
          <Route path="/soc/mitre" element={<MitreCoveragePage />} />
          <Route path="/soc/playbooks" element={<PlaybooksPage />} />
          <Route path="/incidents" element={<IncidentsPage />} />
          <Route path="/incidents/:incidentId" element={<IncidentDetailPage />} />
          <Route path="/mitre" element={<MitreCoveragePage />} />
          <Route path="/playbooks" element={<PlaybooksPage />} />
          {/* STEP 18: SOAR Automation & Advanced SOC Scenario Engine */}
          <Route path="/soc/automation" element={<SoarDashboardPage />} />
          <Route path="/soc/automation/playbooks" element={<SoarPlaybooksPage />} />
          <Route path="/soc/automation/playbooks/:playbookId" element={<SoarPlaybookDetailPage />} />
          <Route path="/soc/automation/executions" element={<SoarExecutionsPage />} />
          <Route path="/soc/automation/executions/:executionId" element={<SoarExecutionDetailPage />} />
          <Route path="/automation" element={<SoarDashboardPage />} />
          <Route path="/automation/playbooks" element={<SoarPlaybooksPage />} />
          <Route path="/automation/playbooks/:playbookId" element={<SoarPlaybookDetailPage />} />
          <Route path="/automation/executions" element={<SoarExecutionsPage />} />
          <Route path="/automation/executions/:executionId" element={<SoarExecutionDetailPage />} />

          <Route path="/soc/scenarios" element={<SocScenariosPage />} />
          <Route path="/soc/scenarios/workspace/:attemptId" element={<SocScenarioWorkspacePage />} />
          <Route path="/soc/scenarios/results/:attemptId" element={<SocScenarioResultPage />} />
          {/* STEP 13: Threat Intelligence & IOC Investigation */}
          <Route path="/threat-intelligence" element={<ThreatIntelDashboardPage />} />
          <Route path="/threat-intelligence/indicators" element={<IndicatorListPage />} />
          <Route path="/threat-intelligence/indicators/:indicatorId" element={<IndicatorDetailPage />} />
          <Route path="/threat-intelligence/graph" element={<IndicatorGraphPage />} />
          <Route path="/threat-intelligence/search" element={<ThreatIntelSearchPage />} />
          <Route path="/threat-intelligence/watchlist" element={<WatchlistPage />} />
          <Route path="/threat-intelligence/challenges" element={<ThreatIntelChallengesPage />} />
          <Route path="/threat-intelligence/challenges/:slug" element={<ThreatIntelChallengeDetailPage />} />
          {/* STEP 14: Threat Hunting & Investigation Workspace */}
          <Route path="/threat-hunting" element={<ThreatHuntingDashboardPage />} />
          <Route path="/threat-hunting/scenarios" element={<HuntScenariosPage />} />
          <Route path="/threat-hunting/hunts/:huntId" element={<HuntWorkspacePage />} />
          {/* STEP 15: SIEM & Security Log Analysis Engine */}
          <Route path="/siem" element={<SiemDashboardPage />} />
          <Route path="/siem/search" element={<SiemSearchPage />} />
          <Route path="/siem/datasets" element={<SiemDatasetsPage />} />
          <Route path="/siem/rules" element={<SiemRulesPage />} />
          <Route path="/siem/labs" element={<SiemLabsPage />} />
          <Route path="/siem/labs/:slug" element={<SiemLabsPage />} />
          {/* STEP 16: Endpoint Security & Host Investigation Engine */}
          <Route path="/endpoint-security" element={<EndpointDashboardPage />} />
          <Route path="/endpoint-security/hosts" element={<EndpointHostsPage />} />
          <Route path="/endpoint-security/hosts/:hostId" element={<EndpointHostDetailPage />} />
          <Route path="/endpoint-security/events" element={<EndpointEventsPage />} />
          <Route path="/endpoint-security/investigations" element={<EndpointInvestigationsPage />} />
          <Route path="/endpoint-security/investigations/:investigationId" element={<EndpointInvestigationsPage />} />
          <Route path="/endpoint-security/scenarios" element={<EndpointScenariosPage />} />
          <Route path="/endpoint-security/scenarios/:slug" element={<EndpointScenariosPage />} />
          <Route path="/progress" element={<ProgressPage />} />
          <Route path="/progress/skills" element={<SkillCatalogPage />} />
          <Route path="/skills" element={<SkillCatalogPage />} />
          <Route path="/progress/assessment" element={<AssessmentReportPage />} />
          <Route path="/assessment" element={<AssessmentReportPage />} />
          <Route path="/portfolio" element={<PortfolioPage />} />
          <Route path="/portfolio/public/:publicSlug" element={<PublicPortfolioPage />} />
          <Route path="/admin" element={<AdminDashboardPage />} />
          <Route path="/admin/content" element={<AdminContentPage />} />
          <Route path="/admin/audit" element={<AdminAuditPage />} />
          <Route path="/adaptive-test" element={<AdaptivePage />} />

          <Route path="/adaptive-test/session/:attemptId" element={<MockTestWorkspacePage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </AuthProvider>
  </BrowserRouter>
  </ErrorBoundary>
  )
}

export default App
