# NexoraNet Threat Hunting & Investigation Workspace

## 1. Overview & Objectives

The **NexoraNet Threat Hunting & Investigation Workspace** (Step 14) elevates students from passive alert responders into proactive threat hunters. In modern security operations, signature-based detections and IOC match engines cannot catch novel, low-and-slow, or zero-day adversary activity. Threat hunters formulate proactive hypotheses, interrogate normalized multi-source telemetry, correlate entities, test assumptions, and bind validated evidence to construct actionable cases.

```text
LEARN
  ↓
OBSERVE
  ↓
ALERT
  ↓
IOC
  ↓
HUNT
  ↓
CORRELATE
  ↓
FORM HYPOTHESIS
  ↓
COLLECT EVIDENCE
  ↓
VALIDATE
  ↓
CONCLUDE
  ↓
DOCUMENT
```

### The Analytical Question
Unlike standard alert triage which begins with *"Why did this fire?"*, threat hunting begins with:
> **"What happened, how did it happen, and where else is this adversary hiding?"**

---

## 2. System Architecture

The Threat Hunting Workspace connects the entire NexoraNet stack into an investigative loop:

```text
PCAP (Step 10)
  ↓
Packet Metadata
  ↓
Detection Alerts (Step 11)
  ↓
SOC Alerts (Step 12)
  ↓
IOCs & Threat Intelligence (Step 13)
  ↓
Threat Hunting Datasets & Query Engine (Step 14)
  ↓
Investigation Workbench & Entity Graphs (Step 14)
  ↓
Findings, Conclusions & Scoring (Step 14)
```

### Architecture Diagram
```text
┌─────────────────────────────────────────────────────────────┐
│                 Analyst Workspace (Frontend)                │
│   (Dashboard, Scenario Catalog, 7-Tab Investigation Room)  │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP REST
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI Engine Router                    │
│                 /api/v1/threat-hunting/*                    │
├──────────────────────────────┬──────────────────────────────┤
│ Core Services:                                              │
│  - DatasetService     (Normalizes PCAPs, Alerts, IOCs)      │
│  - QueryEngine        (Safe AST-Parsed Multi-Field Search)  │
│  - HuntService        (Campaign Lifecycle, Graphs, Pivoting)│
│  - InvestigationService (Hypotheses, Evidence, Notes)       │
│  - ScoringService     (100-pt Multi-Criteria Rubric)        │
│  - ScenarioService    (8 Curated MITRE ATT&CK Scenarios)    │
├──────────────────────────────┴──────────────────────────────┤
│ Storage Layer (SQLite / Alembic Migrations)                  │
│  - hunt_datasets        - hunt_events                       │
│  - threat_hunts         - threat_hunt_hypotheses            │
│  - threat_hunt_evidence - threat_hunt_findings              │
│  - threat_hunt_notes                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Seven-Tab Investigation Room

Each hunt launched in the workspace provides an integrated 7-tab workbench:

1. **Telemetry & Query Engine**:
   - Filter and query thousands of normalized events using safe field conditions, logic (`AND`/`OR`), and full-text keyword searches.
   - Inspect JSON context, payload previews, protocols, and ports.
   - One-click *Pin as Evidence* directly from any telemetry record.

2. **Investigation Timeline**:
   - Interactive chronological timeline aggregating all hunt telemetry, alert generation, and hypothesis milestones.
   - Highlights critical attack sequences, C2 beacon intervals, and lateral movement hops.

3. **Entity Correlation Graph**:
   - Bounded topological graph (depth $\le 2$, nodes $\le 50$) visualizing IP-to-Domain, IP-to-Port, Host-to-Host, and Alert-to-Indicator relationships.
   - Color-coded nodes (Red: Malicious/Suspicious, Sky: Pivot focus, Gray: Standard network assets).

4. **Pivot Correlator**:
   - Rapid pivoting engine supporting `IP`, `DOMAIN`, `PORT`, and `ALERT` pivots.
   - Reveals related entities, connection frequency, and co-occurring telemetry events.

5. **Hypotheses Workbench**:
   - Formulate structured attack assumptions (e.g. *"Host 192.168.1.105 is exfiltrating sensitive data via encrypted DNS tunnels"*).
   - Track hypothesis status: `PROPOSED`, `INVESTIGATING`, `CONFIRMED`, `REFUTED`, or `INCONCLUSIVE`.
   - Record test methodology, validation rationale, and confidence ratings.

6. **Evidence & Findings Binding**:
   - Bind raw events as `SUPPORTING`, `CONTRADICTING`, or `CONTEXTUAL` evidence.
   - Attach analyst notes to justify evidence relevance.
   - Promote validated evidence clusters into formal `HuntFindings` tagged with MITRE ATT&CK techniques.

7. **Analyst Journal & Conclusion Scoring**:
   - Chronological investigator logbook recording timestamped field notes.
   - Final disposition selection (`MALICIOUS_CONFIRMED`, `SUSPICIOUS_UNRESOLVED`, `BENIGN_FALSE_POSITIVE`, `INCONCLUSIVE`).
   - Executive summary and remediation guidance generation.
   - Evaluated by an automated 100-point educational grading rubric.

---

## 4. Curated MITRE ATT&CK Scenarios

NexoraNet Step 14 includes 8 realistic educational scenarios covering common adversary Tactics, Techniques, and Procedures (TTPs):

| Scenario Slug | Title | Difficulty | Primary MITRE ATT&CK |
| :--- | :--- | :--- | :--- |
| `lateral-movement-smb` | Lateral Movement via SMB & PsExec | Beginner | T1021.002 |
| `dns-tunneling-exfil` | Covert DNS Tunneling & Exfiltration | Intermediate | T1071.004 |
| `powershell-beaconing` | PowerShell C2 Beaconing to External IP | Intermediate | T1071.001 |
| `kerberoasting-ad` | Kerberoasting & Service Ticket Harvesting | Advanced | T1558.003 |
| `internal-recon-scan` | Internal Network Reconnaissance & Port Sweeps | Beginner | T1046 |
| `tls-encrypted-c2` | Encrypted TLS C2 with Self-Signed Certificates | Intermediate | T1573.002 |
| `phishing-malware-stage` | Phishing Execution & Multi-Stage Stager Fetch | Advanced | T1204.002 |
| `scheduled-task-persist` | Remote Scheduled Task Creation for Persistence | Beginner | T1053.005 |

---

## 5. Educational Philosophy & Guardrails

- **Zero Arbitrary Code Execution**: No `eval()`, raw SQL string concatenation, or regex DDoS risks.
- **Safety First**: All simulated indicators use reserved documentation ranges (RFC 5737 `198.51.100.0/24`, RFC 2606 `.test` domains).
- **Explainable Scoring**: Objective evaluation breaks down performance into 5 distinct analyst competency dimensions.
