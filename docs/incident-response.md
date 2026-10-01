# Incident Response & Case Management Engine (Step 17)

## Overview

The **NexoraNet Incident Response & Case Management Engine** provides an interactive, educational environment simulating enterprise-grade digital forensics and incident handling aligned with **NIST SP 800-61 Rev 2** (*Computer Security Incident Handling Guide*).

The engine links all previously built NexoraNet defensive systems:

```text
ALERT (Detection / SIEM / SOC)
  ↓
TRIAGE (Triage Assessment & Scope)
  ↓
INCIDENT TICKET (Incident Record Creation)
  ↓
CASE COORDINATION (Lead Analyst Assignment & SLA)
  ↓
CROSS-ENGINE EVIDENCE (Pcaps, Flows, Telemetry, IOCs)
  ↓
CHAIN OF CUSTODY (Cryptographic SHA-256 Verification & Audit Logs)
  ↓
UNIFIED TIMELINE (Event Aggregation & Milestone Tagging)
  ↓
HYPOTHESIS & FINDINGS (Scientific Investigation Methodology)
  ↓
MITRE ATT&CK MAPPING (Observed Tactics & Techniques)
  ↓
RESPONSE ACTION SIMULATION (Containment / Eradication / Recovery)
  ↓
EXECUTIVE REPORTING (NIST SP 800-61 Post-Incident Analysis)
```

---

## 1. NIST SP 800-61 Lifecycle Management

NexoraNet structures every incident around four sequential operational phases:

1. **Preparation**: Pre-configured incident response playbooks, detection rules, and telemetry feeds.
2. **Detection & Analysis**: Ingestion of alerts from the Detection Engine, SIEM correlation alerts, and Endpoint telemetry. Scope assessment, affected users, affected hosts, and evidence gathering.
3. **Containment, Eradication & Recovery**: Proposing, reviewing, simulating, and documenting non-destructive defensive actions.
4. **Post-Incident Activity**: Formulating root cause analysis, logging business impact, documenting lessons learned, and compiling executive reports.

### Workflow Statuses
- `NEW`: Freshly escalated from SOC triage or detection alert.
- `TRIAGED`: Initial severity and blast radius established.
- `INVESTIGATING`: Active evidence gathering, hypothesis formulation, and timeline correlation.
- `CONTAINMENT`: Executing containment countermeasures.
- `ERADICATION`: Removing persistence mechanisms, malware artifacts, and attacker access.
- `RECOVERY`: Restoring business services and monitoring for reinfection.
- `MONITORING`: Heightened telemetry observation to confirm threat eradication.
- `RESOLVED`: Incident objectives completed and systems verified clean.
- `CLOSED`: Post-incident review completed, report archived.
- `FALSE_POSITIVE`: Validated as benign activity; detection tuning feedback recorded.

---

## 2. Cross-Engine Evidence Vault & Chain of Custody

The Incident Response workspace features a unified cross-engine evidence collector capable of ingesting artifacts from:
- **Detection Engine**: IDS alerts, rule matches, packet signatures.
- **Packet Analysis Engine (PCAP)**: Raw packet captures, TCP/UDP streams, TLS handshakes.
- **SIEM Engine**: Normalized syslog, Windows Event Logs, CEF events, correlation triggers.
- **Endpoint Security Engine**: Process creation trees, registry modifications, socket connections.
- **Threat Intelligence**: Indicators of compromise (IOCs), reputation scores, threat actor profiles.

### Cryptographic Integrity & Chain of Custody
Every evidence item stored in `IncidentEvidence` maintains:
1. `hash_sha256`: SHA-256 cryptographic digest calculated over the serialized payload.
2. **On-demand Verification**: Analysts can trigger `POST /incidents/{incident_id}/evidence/{evidence_id}/verify-hash` to guarantee tamper resistance.
3. `EvidenceAuditLog`: Immutable ledger tracking every analyst action (`ATTACHED`, `VIEWED`, `ANNOTATED`, `LINKED`, `UNLINKED`, `HASH_VERIFIED`) with timestamps and actor identities.

---

## 3. Incident Timeline Analysis

The `IncidentTimelineEvent` model synchronizes chronological events from multiple disparate log engines:
- Categorization into lifecycle stages: `INITIAL_ACCESS`, `EXECUTION`, `DETECTION`, `TRIAGE`, `CONTAINMENT`, `ERADICATION`, `RECOVERY`, `OBSERVATION`.
- **Milestone Tagging**: Analysts can highlight key turning points in the intrusion (e.g. initial exploitation, privilege escalation, lateral jump).
- **Auto-Sync Engine**: Discovers timestamps across linked alerts and automatically generates timeline milestones.

---

## 4. Standardized IR Playbooks

NexoraNet includes 10 built-in Incident Response Standard Operating Procedures:
1. **PB-IR-001**: Ransomware Outbreak Containment
2. **PB-IR-002**: Credential Stuffing & Password Spray Response
3. **PB-IR-003**: Spear-Phishing Credential Harvest & Session Hijack
4. **PB-IR-004**: Lateral Movement & Pass-the-Hash Remediation
5. **PB-IR-005**: DNS Tunneling & C2 Exfiltration Interception
6. **PB-IR-006**: Web Application Exploitation (SQLi / RCE)
7. **PB-IR-007**: Endpoint Privilege Escalation & Persistence
8. **PB-IR-008**: Data Exfiltration via Encrypted Channels
9. **PB-IR-009**: Insider Threat & Unauthorized File Access
10. **PB-IR-010**: DDoS Flood & Service Degradation

Each playbook provides structured phase instructions, triage checklists, and recommended simulation actions.

---

## 5. Post-Incident Reporting

The reporting engine automatically synthesizes incident telemetry into a formal **NIST SP 800-61 Post-Incident Executive Report**:
- Markdown format with structured sections.
- JSON structured overview with total timelines, affected systems, root cause, and recommendations.
- Interactive export as downloadable `.md` file or direct clipboard copy.
