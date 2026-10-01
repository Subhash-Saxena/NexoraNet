# Step 16: Endpoint Security & Host Investigation Engine

**NexoraNet** — *"Learn. Simulate. Analyze. Defend."*

---

## 1. Overview & Educational Philosophy

The **Endpoint Security & Host Investigation Engine** introduces realistic, interactive host-level security analysis to NexoraNet. While network sensors (PCAP, IDS, SIEM) provide visibility across transit boundaries, modern adversaries execute tools, elevate privileges, establish persistence, and hide inside process hierarchies on endpoints.

The primary objective of Step 16 is to teach students **how SOC analysts investigate endpoints**:
- Moving beyond isolated alerts to analyze **full host context**.
- Examining **parent-child process hierarchies** (`explorer.exe` ➔ `powershell.exe` ➔ `update.exe`).
- Evaluating **authentication anomalies** (logon sessions, brute-force patterns, credential spray).
- Correlating process executions with **network socket connections**, **DNS queries**, and **file writes**.
- Identifying **persistence mechanisms** (Scheduled Tasks, Registry Run Keys, Service Installations).
- Formulating testable **hypotheses**, collecting corroborating **evidence**, documenting **findings**, and submitting an analytical **verdict** with automated rubric evaluation.

---

## 2. Investigation Lifecycle

The educational investigation workflow follows a disciplined scientific method:

```text
HOST
  ↓
TELEMETRY
  ↓
EVENT
  ↓
OBSERVATION
  ↓
CORRELATION
  ↓
DETECTION
  ↓
IOC
  ↓
INVESTIGATION
  ↓
HYPOTHESIS
  ↓
EVIDENCE
  ↓
CONCLUSION
```

1. **Host Selection**: The analyst selects a workstation or server from the synthetic fleet (`NN-WIN-001`, `NN-WIN-002`, `NN-LINUX-001`, `NN-SRV-001`).
2. **Telemetry Exploration**: Telemetry streams are analyzed across 10 specialized categories (Process, Auth, Network, DNS, Files, Persistence, Privileges).
3. **Process Hierarchy Analysis**: The parent-child process tree is traversed to identify defense evasion or ingress tool transfer.
4. **Hypothesis Formulation**: The analyst constructs working hypotheses with analytical confidence tiers (`LOW`, `MEDIUM`, `HIGH`).
5. **Evidence Collection**: Events and observables are tagged as `SUPPORTING` or `REFUTING`.
6. **Findings Narrative**: Key adversary techniques (with MITRE ATT&CK references) are recorded.
7. **Verdict & Rubric Scoring**: A final case conclusion (`CONFIRMED_COMPROMISE`, `SUSPICIOUS`, `FALSE_POSITIVE`, `BENIGN`) is evaluated against an automated grading rubric (0–100 score).

---

## 3. Architecture & Data Model

### Relational Schema

```text
+-----------------------+       1:N       +-----------------------+
|     EndpointHost      |---------------->|     EndpointEvent     |
+-----------------------+                 +-----------------------+
| id, stable_id         |                 | id, stable_id         |
| hostname, platform    |                 | host_id, timestamp    |
| risk_level, status    |                 | event_category, type  |
| ip_address, mac_addr  |                 | process_name, pid     |
+-----------------------+                 | parent_process_name   |
            |                             | command_line, hash    |
            | 1:N                         | dest_ip, domain       |
            v                             +-----------------------+
+-----------------------+                            |
| EndpointInvestigation |                            |
+-----------------------+                            |
| id, stable_id         |                            |
| user_id (IDOR scoped) |                            |
| title, description    |                            |
| priority, status      |                            |
| scenario_slug         |                            |
+-----------------------+                            |
   |         |         |                             |
   | 1:N     | 1:N     | 1:N                         |
   v         v         v                             |
+---------+ +--------+ +-----------------+           |
|Hypothesis| |Evidence| |EndpointFinding  |           |
+---------+ +--------+ +-----------------+           |
|statement| |obs_type| |title, description|          |
|status   | |obs_val | |mitre_technique  |           |
|confidenc| |relevanc| |severity         |           |
+---------+ +--------+ +-----------------+           |
                 ^                                   |
                 +-----------------------------------+
```

---

## 4. API Endpoints Reference

All endpoints are mounted under `/api/v1/endpoint-security`:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/overview` | Fleet-wide host metrics, risk counts, and active cases |
| `GET` | `/hosts` | Filterable host inventory (by platform, risk level, search) |
| `GET` | `/hosts/{host_id}` | Detailed host metadata by ID or stable ID |
| `GET` | `/hosts/{host_id}/overview` | Aggregated telemetry counts for a host |
| `GET` | `/hosts/{host_id}/events` | Filtered events for a specific host |
| `GET` | `/hosts/{host_id}/processes` | Hierarchical parent-child process tree |
| `GET` | `/hosts/{host_id}/processes/{pid}` | Detailed process context with socket & file correlations |
| `GET` | `/hosts/{host_id}/authentication` | Authentication events & pattern detection evaluation |
| `GET` | `/hosts/{host_id}/network` | Socket connection telemetry |
| `GET` | `/hosts/{host_id}/dns` | DNS query telemetry |
| `GET` | `/hosts/{host_id}/files` | File modification telemetry |
| `GET` | `/hosts/{host_id}/services` | Service installations & state changes |
| `GET` | `/hosts/{host_id}/persistence` | Scheduled tasks, run keys, persistence hooks |
| `GET` | `/hosts/{host_id}/privileges` | Privilege elevation & sudo executions |
| `GET` | `/hosts/{host_id}/timeline` | Unified chronological host timeline |
| `GET` | `/events` | Multi-host searchable events explorer |
| `GET` | `/events/{event_id}` | Single event detail |
| `POST` | `/events/{event_id}/pivot-intel` | Pivot event observables into Threat Intelligence (Step 13) |
| `POST` | `/events/{event_id}/start-threat-hunt` | Launch Threat Hunt initialized with event (Step 14) |
| `POST` | `/events/{event_id}/investigate-in-soc` | Escalate event into SOC Investigation Case (Step 12) |
| `GET` | `/events/{event_id}/correlate-siem` | Find matching SIEM security logs (Step 15) |
| `GET` | `/events/{event_id}/correlate-pcap` | Correlate network connections with PCAP packets (Step 10) |
| `GET` | `/investigations` | Student's investigation cases list |
| `POST` | `/investigations` | Create new endpoint investigation case |
| `GET` | `/investigations/{id}` | Case details with hypotheses, evidence, findings, conclusion |
| `PATCH` | `/investigations/{id}` | Update case status or priority |
| `POST` | `/investigations/{id}/hypotheses` | Add working hypothesis |
| `PATCH` | `/investigations/{id}/hypotheses/{hId}` | Update hypothesis status/confidence |
| `POST` | `/investigations/{id}/evidence` | Record corroborating evidence artifact |
| `POST` | `/investigations/{id}/findings` | Document security finding |
| `POST` | `/investigations/{id}/conclusion` | Finalize verdict and calculate rubric score |
| `GET` | `/scenarios` | List guided training scenarios |
| `GET` | `/scenarios/{slug}` | Scenario details, background, objectives, and hints |
| `POST` | `/scenarios/{slug}/validate` | Validate student findings against grading rubric |
