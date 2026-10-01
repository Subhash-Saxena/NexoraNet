# NexoraNet SIEM & Security Log Analysis Engine

**Step 15 — SIEM & Security Log Analysis Architecture**  
*Platform Tagline: "Learn. Simulate. Analyze. Defend."*

---

## 1. Overview & Pedagogical Mission

The **NexoraNet SIEM Engine** introduces learners to central Security Information and Event Management concepts within an offline, educational, and safe architecture. It bridges the gap between individual network packets (Steps 10-11), tactical SOC triage (Step 12), indicator enrichment (Step 13), and proactive threat hunting (Step 14) by simulating how modern enterprise security teams ingest, normalize, query, and correlate heterogeneous log data.

```text
HETEROGENEOUS LOG SOURCES
  (Windows Security, Linux Syslog/SSH, Cisco ASA Firewall, Core DNS, Web Server)
                         │
                         ▼
             [INGESTION & SANITIZATION]
  (5MB Payload Limits, Max 2,000 Records, CSV Formula Sanitization)
                         │
                         ▼
            [LOG NORMALIZATION ENGINE]
  (Harmonizes JSON, CSV, Syslog, Windows XML, CEF to Standard Taxonomy)
                         │
                         ▼
             [CENTRAL EVENT STORAGE]
           (PostgreSQL / SQLite Storage)
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
[VISUAL SEARCH]   [AGGREGATIONS]   [CORRELATION ENGINE]
 (AND/OR Logic,   (Top Entities,   (Sliding Windows,
  Field Filters)    Histograms)     Threshold Rules)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
              [CORRELATION ALERTS]
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
[SOC INVESTIGATION] [THREAT HUNT]   [IOC EXTRACTION]
   (Step 12 Triage)  (Step 14 Hunt)  (Step 13 Threat Intel)
```

---

## 2. Core Functional Layers

### 2.1 Ingestion & Normalization
* **Multiformat Support**: Ingests JSON, comma-separated values (CSV), Linux/Unix Syslog (RFC 3164/5424), Windows Event Log XML (Events 4624, 4625, 4688, 4740, 7045), and ArcSight Common Event Format (CEF).
* **Taxonomy Harmonization**: Maps vendor-specific action codes and severity levels into a unified schema (`LOGIN`, `LOGIN_FAILURE`, `CONNECTION`, `CONNECTION_BLOCKED`, `DNS_QUERY`, `PROCESS_START`, etc.).

### 2.2 Visual Query & Search Builder
* **Whitelisted Field Queries**: Enables precise search across indexed attributes: `action`, `event_category`, `source_type`, `host`, `username`, `source_ip`, `destination_ip`, `destination_port`, `protocol`, `severity`, `status`, `message`, `domain`, `process_name`.
* **Logical Operations**: Supports `AND` and `OR` boolean combinations.
* **Operators**: Supports `=`, `!=`, `CONTAINS`, `STARTSWITH`, `>`, `<`, `>=`, `<=`.
* **Quick Filters**: Instant pre-sets for failed logins, firewall drops, sudo elevation, DNS queries, and critical severity events.
* **Saved Searches & History**: Persists analytical search definitions for repeated execution.

### 2.3 Real-Time Aggregation & Dashboards
* **Event Counts & Severity Distributions**: High, Medium, Low, Info distributions.
* **Top Entity Frequency**: Identifies anomalous talkers, high-frequency user accounts, most targeted destination ports, and domain queries.
* **Timeline Histograms**: Binned temporal distribution showing volume spikes and authentication anomalies.

### 2.4 Correlation & Behavioral Alerting
* **Sliding Window Thresholds**: Evaluates multiple events occurring within bounded time windows (e.g. 5 failures within 300 seconds).
* **Cross-Source Correlation**: Detects multi-stage attack chains (e.g. brute force followed by firewall exfiltration attempt).
* **Dry-Run Rule Tester**: Allows students to simulate detection rules against historical datasets without polluting production alert queues.

### 2.5 Cross-Platform Pivoting & Escalation
* **To Step 12 Mini SOC**: One-click escalation to an `INV-YYYY-XXXX` SOC Investigation with attached telemetry evidence.
* **To Step 13 Threat Intelligence**: Automatic extraction of candidate observables (IPs, domains, hashes) into enriched Threat Intel feeds.
* **To Step 14 Threat Hunting**: Direct campaign launch initializing pivot queries and hypothesis tracking around the anomalous entity.

---

## 3. Pre-Configured Educational Datasets

| Dataset ID | Name | Primary Log Sources | Focus Area |
| :--- | :--- | :--- | :--- |
| `DS-AUTH-BEG-01` | Authentication Anomalies & Brute Force | Windows DC, Linux SSH | Password spraying, dictionary attacks, logon failures |
| `DS-NET-INT-01` | Network Reconnaissance & Port Scanning | Cisco ASA, iptables, Core DNS | Inbound scans, blocked ports, DNS tunneling probes |
| `DS-SOC-ADV-01` | Multi-Stage APT Simulation & Lateral Movement | Windows, Linux, Firewall, Web | Initial access, privilege escalation, lateral spread |
