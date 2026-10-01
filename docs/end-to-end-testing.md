# NexoraNet — End-to-End (E2E) Testing Guide & Verification

## 1. Scope & Objective
This document outlines the end-to-end integration and regression testing architecture of NexoraNet. The primary verification goal is to validate that all 22 steps operate as an integrated platform without regressions, state leakage, or orphaned workflows.

---

## 2. Test Suites Overview

### 2.1 Backend Pytest Suite
- **Location**: `backend/tests/`
- **Total Test Cases**: 279 automated tests across 30 test modules
- **Execution Command**:
  ```bash
  cd backend
  pytest tests -v
  ```
- **Coverage Areas**:
  - `test_security.py`, `test_security_hardening.py`, `test_step22_security_audit.py`: Authentication, token revocation, rate limiting, IDOR, SSRF, XSS, and production flags.
  - `test_e2e_student_journey.py`: End-to-end student lifecycle (Registration -> Learning -> Labs -> Simulators -> SOC Triage -> Threat Intel -> Hunting -> SIEM -> Endpoint -> Incident Response -> SOAR -> CTF -> Portfolio -> Logout).
  - `test_curriculum_api.py`, `test_learning_system.py`, `test_questions_api.py`: Structured learning paths, progress telemetry, question bank queries.
  - `test_mock_test_engine.py`, `test_adaptive_engine.py`: Exam timing, adaptive Bayesian scoring, anti-repetition guards.
  - `test_network_simulator.py`, `test_pcap_engine.py`, `test_detection_engine.py`: Packet parsing, graph routing, detection rule execution.
  - `test_soc_engine.py`, `test_threat_intel_engine.py`, `test_threat_hunting_engine.py`: Alert triage, IOC correlations, hypothesis trees, hunting syntax.
  - `test_siem_engine.py`, `test_endpoint_security.py`: Log normalization, correlation alerts, process trees, timeline graphs.
  - `test_incident_response.py`, `test_soar_engine.py`: IR workbench, evidence tracking, MITRE mappings, dry-run playbooks, multi-stage SOC scenarios.
  - `test_challenge_engine.py`, `test_analytics_and_admin.py`: CTF challenges, progressive hints, skill matrix assessments, student portfolios.

### 2.2 Frontend Vitest Suite
- **Location**: `frontend/src/test/`
- **Total Test Cases**: 139 automated tests across 18 test suites
- **Execution Command**:
  ```bash
  cd frontend
  npm test
  ```
- **Coverage Areas**:
  - UI routing, responsive sidebars, theme toggles (`App.test.tsx`)
  - Curriculum diagrams, OSI stack interactive layers, TCP handshake stepper (`LearningSystem.test.tsx`)
  - Lab workbench, split-screen instructions, packet trace inspector (`LabEngine.test.tsx`)
  - Mock test timers, answer selections, result reviews (`MockTestEngine.test.tsx`)
  - Network canvas, drag-and-drop node placement, interface config panels (`NetworkSimulator.test.tsx`)
  - PCAP filter bar, packet hex stream dissector (`PacketAnalysis.test.tsx`)
  - Mini SOC dashboard, alert triage cards, severity badges (`SocDashboard.test.tsx`)
  - Threat intelligence graphs, IOC details, watchlist drawers (`ThreatIntel.test.tsx`)
  - Hunting query editor, hypothesis notes, timeline charts (`ThreatHunting.test.tsx`)
  - SIEM aggregations, correlation rule builder (`Siem.test.tsx`)
  - Endpoint host lists, process tree rendering, event filters (`EndpointSecurity.test.tsx`)
  - Incident response workbench tabs, MITRE matrix navigator, response simulator (`IncidentResponse.test.tsx`)
  - SOAR visual playbook canvas, execution logs, dry-run triggers (`SoarAndScenarios.test.tsx`)
  - CTF catalog, challenge workspace, evidence inspect tabs (`Challenges.test.tsx`)
  - Skill assessment radar cards, recommendations, portfolio editor (`AnalyticsAndAdmin.test.tsx`)

---

## 3. End-to-End Student Journey Scenario

The end-to-end workflow verified in `backend/tests/test_e2e_student_journey.py` proves that a new student can complete the full curriculum and investigative training workflow seamlessly:

```
[Student Registration]
        ↓
[JWT Issuance & Identity Verification]
        ↓
[Curriculum Topic Browsing & Lesson Progression]
        ↓
[Network Simulation & Packet Analysis]
        ↓
[Detection Rule Inspection & SOC Alert Triage]
        ↓
[Threat Intel IOC Correlation & Threat Hunting]
        ↓
[SIEM Aggregation & Endpoint Host Investigation]
        ↓
[Incident Response Workbench & MITRE Mapping]
        ↓
[SOAR Playbook Dry-Run & SOC Scenario Experience]
        ↓
[CTF Defensive Challenge & Zero-Knowledge Validation]
        ↓
[Competency Skill Matrix Assessment & Recommendations]
        ↓
[Student Portfolio Project Creation & Showcase]
        ↓
[Logout & Server-Side Token Revocation]
```

---

## 4. Regression & Boundary Stability

1. **Pagination Limits**: All paginated APIs enforce `limit <= 100` and `skip >= 0`. Out-of-bounds queries reject with `HTTP 422 Unprocessable Content`.
2. **Missing Token Rejection**: Protected endpoints strictly return `HTTP 401 Unauthorized` when accessed without authorization tokens.
3. **Database Concurrency**: Seeded models and dynamic runtime tables remain consistent across rapid read/write sequences with zero orphaned keys.
