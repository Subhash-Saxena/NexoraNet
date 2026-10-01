# NexoraNet SOAR Simulation Engine

> **Tagline:** Learn. Simulate. Analyze. Defend.  
> **Subsystem:** Security Orchestration, Automation & Response (SOAR)  
> **Step:** 18

---

## 1. Executive Overview

The **NexoraNet SOAR Simulation Engine** provides students and security analysts with an authentic, deterministic, and safe environment to build, test, and execute security automation playbooks.

Modern Security Operations Centers (SOCs) depend heavily on automation to triage alerts, enrich suspicious indicators of compromise (IOCs), reduce Mean Time to Detect (MTTD), and minimize Mean Time to Respond (MTTR). NexoraNet teaches these concepts through a **declarative state machine** that simulates automated workflows without ever issuing live system commands or modifying physical infrastructure.

---

## 2. Core Educational Architecture

```text
ALERT / INCIDENT / IOC TRIGGER
             ↓
    AUTOMATION PLAYBOOK
             ↓
  STEP 1: ENRICHMENT (IP, Domain, Hash)
             ↓
  STEP 2: CORRELATION & THREAT SCORING
             ↓
  STEP 3: DECISION GATE (Condition Evaluator)
             ↓
  STEP 4: HUMAN APPROVAL (High-Risk Gating)
             ↓
  STEP 5: SIMULATED CONTAINMENT (Safe Sandbox)
             ↓
  STEP 6: NOTIFICATION & CASE AUDIT
```

### Key Architectural Tenets
1. **Deterministic Execution:** Playbooks follow predictable steps with explicit conditions and outputs.
2. **Whitelist Condition Evaluator:** Conditions are evaluated strictly using 13 safe operators (`eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `contains`, `not_contains`, `in`, `not_in`, `regex_match`, `is_empty`, `is_not_empty`). Neither `eval()` nor `exec()` is ever utilized.
3. **Analyst Approval Gates:** Any step tagged with `requires_approval=True` pauses execution in `WAITING_APPROVAL` status until a human analyst reviews the telemetry and issues an approval or rejection.
4. **Failure Strategies:** Individual steps declare `on_failure="STOP"` or `on_failure="CONTINUE"`, with up to 2 automated retries on simulated transient failures.
5. **Deduplication & Idempotency:** Executions generate deterministic idempotency keys (`{playbook_id}:{source_id}:{date}`) preventing duplicate automated actions from running against the same incident entity concurrently.

---

## 3. Pre-Built Educational Playbooks

NexoraNet includes 8 official pre-built educational playbooks:

| Playbook ID | Name | Category | Trigger Type | Risk Level | Human Approval |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `SOAR-PB-001` | Phishing Email Triage & Safe Quarantine | `PHISHING` | `ALERT_CREATED` | `MEDIUM` | No |
| `SOAR-PB-002` | Malware Endpoint Host Containment | `MALWARE` | `ALERT_CREATED` | `HIGH` | Yes (Analyst Gate) |
| `SOAR-PB-003` | Ransomware Rapid Containment & Snapshot | `RANSOMWARE` | `DETECTION_MATCH` | `CRITICAL` | Yes (Analyst Gate) |
| `SOAR-PB-004` | Credential Access & User Account Revocation | `CREDENTIAL_ACCESS` | `ALERT_THRESHOLD` | `HIGH` | Yes (Analyst Gate) |
| `SOAR-PB-005` | Data Exfiltration Perimeter IP Block | `DATA_EXFILTRATION` | `DETECTION_MATCH` | `HIGH` | Yes (Analyst Gate) |
| `SOAR-PB-006` | Suspicious Geo-Login Investigation & MFA Reset | `SUSPICIOUS_LOGIN` | `ALERT_CREATED` | `MEDIUM` | No |
| `SOAR-PB-007` | Lateral Movement Isolation & Evidence Capture | `LATERAL_MOVEMENT` | `CORRELATION_MATCH`| `HIGH` | Yes (Analyst Gate) |
| `SOAR-PB-008` | Automated Threat Intelligence IOC Enrichment | `THREAT_INTEL` | `IOC_OBSERVED` | `LOW` | No |

---

## 4. Supported Action Handlers

All action handlers are declared in `action_handlers.py` and run exclusively within the NexoraNet sandbox:

- **Enrichment Actions:**
  - `ENRICH_IOC`: Queries local synthetic threat intelligence database.
  - `ENRICH_ENDPOINT`: Gathers synthetic endpoint telemetry and running processes.
  - `ENRICH_USER`: Retrieves directory role, privileges, and MFA status.
- **Investigation Actions:**
  - `QUERY_SIEM_LOGS`: Searches synthetic SIEM datasets for related events.
  - `CHECK_THREAT_REPUTATION`: Evaluates reputation scores from synthetic feed items.
  - `CALCULATE_RISK_SCORE`: Aggregates alert weights into a unified threat metric.
- **Case Management Actions:**
  - `CREATE_INCIDENT_CASE`: Automatically generates a tracked SOC case.
  - `UPDATE_CASE_STATUS`: Updates case priority, status, and assigned analyst.
  - `ATTACH_EVIDENCE`: Links IOCs, hashes, and process traces to the case.
  - `ADD_TIMELINE_EVENT`: Records milestone events in the incident timeline.
- **Simulated Containment Actions:**
  - `SIMULATED_ISOLATE_HOST`: Flags the endpoint as isolated in synthetic telemetry.
  - `SIMULATED_BLOCK_IP`: Adds synthetic firewall perimeter drop rule.
  - `SIMULATED_BLOCK_DOMAIN`: Adds synthetic DNS sinkhole / blackhole entry.
  - `SIMULATED_DISABLE_ACCOUNT`: Flags user identity as disabled in directory sandbox.
  - `SIMULATED_REVOKE_SESSIONS`: Invalidates active synthetic OAuth/session tokens.
  - `SIMULATED_KILL_PROCESS`: Flags suspicious process PID as terminated in telemetry.
  - `SIMULATED_QUARANTINE_EMAIL`: Flags malicious phishing message as quarantined.
- **Notification & Audit Actions:**
  - `SEND_ANALYST_NOTIFICATION`: Adds in-app SOC notification for the tier 1/2 team.
  - `SEND_SLACK_ALERT`: Formats simulated webhook alert payload for study.
  - `RECORD_AUDIT_LOG`: Logs immutable SOAR action trace with timestamp and actor.

---

## 5. Dry-Run Simulator

Students can test conditions and parameter substitution using the **Dry-Run Simulator** (`POST /api/v1/automation/playbooks/{id}/dry-run`):
- Provides arbitrary sample event JSON.
- Evaluates condition expressions for every step without state mutations.
- Returns step-by-step status preview (`Condition Passed` vs `Condition Skipped`) and highlights steps that will pause for analyst signoff.
