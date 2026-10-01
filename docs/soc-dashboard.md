# NexoraNet SOC Dashboard Architecture

## 1. Overview & Purpose

The **NexoraNet Security Operations Center (SOC) Dashboard** simulates an enterprise defensive monitoring workbench. It is designed to train aspiring Tier-1/Tier-2 SOC analysts in alert prioritization, telemetry examination, triage decisions, and forensic investigations.

> **Defensive Philosophy:**
> - **ALERT ≠ INCIDENT**: An anomaly detection trigger is an invitation to investigate, not conclusive proof of a breach.
> - **OBSERVATION ≠ PROOF**: Corroborating packet telemetry, conversation volume, and flags are required to formulate and support an analytical hypothesis.
> - **Strictly Offline**: Operates purely on offline simulated PCAP captures and synthetic network telemetry. No real network transmission, sniffing, or packet injection.

---

## 2. Core Dashboard Components

### 2.1 Operational Metrics Grid
The dashboard aggregates real-time indicators of operational queue health:
- **Total Alerts**: Overall number of detection events generated across all evaluated runs.
- **P1 Critical Alerts**: Immediate high-impact alerts needing urgent analyst attention.
- **P2 High Alerts**: Anomalies with high confidence or large evidence footprints.
- **Open / Unreviewed Alerts**: Triage queue backlog awaiting initial evaluation.
- **Investigating Alerts**: Alerts actively tied to active analyst investigations.
- **Active Investigations & Open Cases**: Containers organizing multi-alert incidents.

### 2.2 Explainable Priority Engine (P1–P4)
Rather than opaque scoring algorithms, NexoraNet calculates priority deterministically based on:
1. **Rule Severity Weight**: `CRITICAL` (40 pts), `HIGH` (30 pts), `MEDIUM` (20 pts), `LOW` (10 pts), `INFO` (5 pts).
2. **Confidence Weight**: `HIGH` (20 pts), `MEDIUM` (10 pts), `LOW` (5 pts).
3. **Evidence Footprint**: Logarithmic scaling of supporting packet evidence count.
4. **Packet Frequency**: Volumetric rate of packets observed in the trigger window.

**Priority Bands:**
- **P1 (Score ≥ 70)**: Critical severity or high confidence with extensive corroboration.
- **P2 (Score 50–69)**: Significant severity requiring priority same-day review.
- **P3 (Score 30–49)**: Standard anomalies (e.g. routine scanning, isolated ICMP spikes).
- **P4 (Score < 30)**: Low severity informational events.

### 2.3 Training Datasets & Demo Reset
To provide reproducible hands-on labs, the dashboard integrates 5 pre-built educational datasets:
1. `tcp_investigation`: Port scans, SYN bursts without handshakes, RST teardowns.
2. `dns_investigation`: High-volume NXDOMAIN resolution bursts, randomized subdomains.
3. `arp_investigation`: Conflicting MAC addresses claiming gateway IP ownership.
4. `mixed_investigation`: Multi-host mixed LAN telemetry with HTTP, DNS, and TCP.
5. `benign_activity`: Clean handshakes and web browsing to practice identifying False Positives.

---

## 3. Real-time Activity Stream & Audit Trail
Every analyst operation (acknowledgement, classification, hypothesis update, note addition) is recorded in an append-only audit trail (`SocAuditLog`), providing accountability and simulating enterprise compliance standards.
