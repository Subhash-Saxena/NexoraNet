# NexoraNet Advanced SOC Scenario Engine

> **Tagline:** Learn. Simulate. Analyze. Defend.  
> **Subsystem:** Advanced Guided SOC Scenarios  
> **Step:** 18

---

## 1. Executive Overview

The **Advanced SOC Scenario Engine** is a comprehensive, multi-stage investigation simulator designed to bridge the gap between classroom theory and enterprise SOC triage.

The engine provides **28 synthetic incident response scenarios** across 4 difficulty tiers and 5 incident categories. Each scenario guides students through a structured 9-stage investigation lifecycle, testing their ability to distinguish true attack signals from telemetry noise, correlate disparate data sources, map adversary tactics to the MITRE ATT&CK matrix, and deploy measured containment measures.

---

## 2. The 9-Stage Investigation Lifecycle

Every scenario follows a disciplined investigation sequence:

```text
STAGE 1: INITIAL SIGNAL
  └─ Ingest SOC detection alert, examine reported severity, asset, and timestamp.
STAGE 2: EVIDENCE SELECTION
  └─ Sift through available artifacts (processes, network logs, hashes, registry keys).
  └─ Discriminate relevant indicators from benign background noise.
STAGE 3: MULTI-SOURCE CORRELATION
  └─ Link host telemetry with user identity, DNS lookups, and network egress.
STAGE 4: THREAT HYPOTHESIS
  └─ Select and justify root-cause attacker vectors (e.g., spearphishing vs drive-by).
STAGE 5: HYPOTHESIS VALIDATION
  └─ Validate assumptions against secondary telemetry and verification queries.
STAGE 6: MITRE ATT&CK MAPPING
  └─ Align observed indicators to MITRE Enterprise tactics and techniques.
STAGE 7: RESPONSE DECISION
  └─ Formulate a containment, eradication, and recovery plan.
STAGE 8: SIMULATED OUTCOME
  └─ Review simulated execution results and collateral impact on business operations.
STAGE 9: LESSONS LEARNED & AUDIT
  └─ Propose preventative hardening recommendations and submit for evaluation.
```

---

## 3. Scenario Difficulty Distribution & Catalog

The 28 seeded scenarios are distributed across four experience tiers:

### 1. Beginner Tier (5 Scenarios)
- `SCEN-001`: Phishing to Suspicious PowerShell Execution
- `SCEN-002`: Brute Force Password Guessing on SSH
- `SCEN-003`: Web Application SQL Injection Attack
- `SCEN-004`: Suspicious Scheduled Task Creation
- `SCEN-005`: Unauthorized USB Device Connected

### 2. Intermediate Tier (8 Scenarios)
- `SCEN-006`: DLL Side-Loading in Third-Party Utility
- `SCEN-007`: Kerberoasting Ticket Request Spike
- `SCEN-008`: DNS Tunneling Data Exfiltration
- `SCEN-009`: Ransomware Pre-Encryption Staging
- `SCEN-010`: Pass-the-Hash Lateral Movement via SMB
- `SCEN-011`: Malicious Browser Extension Token Theft
- `SCEN-012`: Cloud Storage Bucket Public Exposure
- `SCEN-013`: Living-off-the-Land (LOLBAS) Certutil Egress

### 3. Advanced Tier (10 Scenarios)
- `SCEN-014`: Supply Chain Dependency Poisoning
- `SCEN-015`: Active Directory DCSync Attack
- `SCEN-016`: Multi-Stage Ransomware Outbreak
- `SCEN-017`: Compromised Service Account Privilege Escalation
- `SCEN-018`: EDR Bypass via API Unhooking
- `SCEN-019`: Cloud IAM Role Chaining & Secret Theft
- `SCEN-020`: Staged Cloud Data Exfiltration via rclone
- `SCEN-021`: Insider Threat Database Dump
- `SCEN-022`: Weaponized PDF Exploitation
- `SCEN-023`: Exchange Web Services (EWS) Mailbox Snooping

### 4. Expert Tier (5 Scenarios)
- `SCEN-024`: Nation-State APT Long-Dwell Espionage
- `SCEN-025`: Hypervisor-Level Ransomware Encryption
- `SCEN-026`: Hardware Implant / Out-of-Band Exfiltration
- `SCEN-027`: Golden Ticket Domain Compromise
- `SCEN-028`: Zero-Day Web Framework Remote Code Execution

---

## 4. Transparent 7-Factor Rubric Scoring

Investigations are scored against an objective, multi-dimensional rubric (0–100%):

1. **Signal Analysis & Triage (15%):** Quality and accuracy of initial assessment notes.
2. **Evidence Relevance & Noise Rejection (20%):** Ratio of correctly identified attack artifacts vs noise artifacts selected. Noise penalties prevent blind guessing.
3. **Correlation Accuracy (15%):** Correct identification of parent-child relationships, network endpoints, and user credentials.
4. **Threat Hypothesis Correctness (20%):** Selection of the true threat vector and root-cause statement.
5. **MITRE ATT&CK Mapping (15%):** Precision and recall of mapped ATT&CK technique IDs.
6. **Incident Response Planning (15%):** Proportionality and effectiveness of chosen containment actions.
7. **Progressive Hint Deductions (-5% to -10% per hint):** Points deducted for each unlocked progressive hint.

---

## 5. Progressive Hint System

When students encounter challenging scenarios, they can unlock contextual hints:
- Progressive disclosure: hints are sequenced from high-level orientation to specific telemetry pointers.
- Transparent confirmation modal alerts students to the -5.0 point deduction prior to revealing the clue.
- Hint usage is recorded in the attempt history for longitudinal mastery tracking.
