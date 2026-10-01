# NexoraNet — Analytics & Learning Intelligence Engine

**“Learn. Simulate. Analyze. Defend.”**

## 1. Overview
The Student Analytics Engine transforms activity across Steps 1–19 into educational progress telemetry. Instead of merely displaying raw point totals, the analytics engine follows the pedagogical principle:

$$\text{LEARN} \rightarrow \text{PRACTICE} \rightarrow \text{ANALYZE} \rightarrow \text{APPLY} \rightarrow \text{ASSESS} \rightarrow \text{IMPROVE} \rightarrow \text{DOCUMENT}$$

## 2. Telemetry Architecture
The analytics system consolidates multi-source evidence across all simulation modules:
- **Foundational Learning:** Lesson completions, topic progressions, module coverage.
- **Formative & Summative Testing:** Mock test attempts, adaptive session accuracies.
- **Hands-On Sandboxes:** Lab attempts and step verifications.
- **Cybersecurity Operations:** PCAP investigations, Detection Engine runs, Mini-SOC alert triages and cases.
- **Threat Intelligence & Hunting:** IOC pivots, hunt query executions, hypothesis findings.
- **SIEM & Endpoint Analysis:** Search queries, host timeline reviews, process tree analysis.
- **Incident Response & MITRE ATT&CK:** Incident playbooks, containment simulations.
- **Security Automation & Scenarios:** SOAR playbook executions, 9-stage SOC scenario attempts.
- **Defensive CTF:** Solved synthetic cybersecurity challenges across 4 difficulty tiers.

## 3. Pedagogical Design & Neutral Tone
Analytics in NexoraNet are intentionally **non-judgmental**:
- Never uses labels such as *"You are bad at subnetting."*
- Uses neutral educational phrasing: *"Recent results suggest additional practice with subnetting may be useful."*
- Never makes claims regarding career potential, intelligence, or external professional certification.

## 4. Endpoints
- `GET /api/v1/analytics/overview` — Authoritative student telemetry (time, streak, counts, recent feed).
- `GET /api/v1/analytics/progress` — Granular module and topic completion metrics.
- `GET /api/v1/analytics/trends?days=14` — 14-day rolling activity and accuracy trends.
