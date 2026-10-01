# MITRE ATT&CK Investigation Framework (Step 17)

## Overview

NexoraNet integrates the **MITRE ATT&CK® Enterprise Framework** as a core analytical foundation for mapping adversary behaviors, understanding attack progression, and evaluating detection coverage.

---

## 1. Enterprise Matrix Architecture

The catalog contains the 14 core Enterprise Tactics:

| Tactic ID | Tactic Name | Description |
|:---|:---|:---|
| **TA0043** | Reconnaissance | Gathering information to plan future adversary operations |
| **TA0042** | Resource Development | Establishing resources to support operations (infrastructure, accounts) |
| **TA0001** | Initial Access | Vectors used to gain an initial foothold within the network |
| **TA0002** | Execution | Techniques that result in adversary-controlled code running |
| **TA0003** | Persistence | Mechanisms used to keep access across restarts and credential changes |
| **TA0004** | Privilege Escalation | Techniques to gain higher-level permissions (SYSTEM, root, Admin) |
| **TA0005** | Defense Evasion | Methods used to avoid detection by security controls |
| **TA0006** | Credential Access | Techniques for stealing credentials like passwords and hashes |
| **TA0007** | Discovery | Techniques to observe the environment and orient the adversary |
| **TA0008** | Lateral Movement | Techniques to move through the network to other hosts |
| **TA0009** | Collection | Gathering data of interest (documents, emails, databases) |
| **TA0011** | Command and Control | Communicating with compromised systems across network boundaries |
| **TA0010** | Exfiltration | Stealing data out of the target network |
| **TA0040** | Impact | Disrupting availability or integrity of systems and data |

Each tactic contains curated core Enterprise Techniques and Sub-techniques (e.g. `T1059.001 PowerShell`, `T1055 Process Injection`, `T1078 Valid Accounts`, `T1486 Data Encrypted for Impact`).

---

## 2. Interactive Matrix Visualizer

The frontend `MitreMatrix` component renders a dynamic 14-column interactive matrix:
- **Coverage Heatmap**: Technique tiles display color-coded indicators reflecting observed evidence.
- **Sub-technique Indentation**: Visually distinguishes parent techniques from specialized procedures.
- **Filter Controls**: Search by keyword or ATT&CK ID (e.g. `T1059`), or toggle *"Show Observed Techniques Only"*.
- **Guidance Drawer**: Clicking any technique surfaces its official description, detection guidance, mitigation strategies, and direct external MITRE references.

---

## 3. Incident Technique Mapping

Analysts can attach observed attacker techniques directly to an active incident ticket:
- **Mapping Confidence**:
  - `OBSERVED_EVIDENCE`: Direct log/packet/process telemetry verifies the technique was executed.
  - `HYPOTHESIS_SUGGESTED`: Plausible method based on current investigative theory.
  - `ANALYST_INFERRED`: Logical inference based on pre-conditions and post-conditions.
- **Evidence Linking**: Allows quoting specific evidence IDs or log entries supporting the mapping.
- **Phase Association**: Tags the technique to the incident phase where it occurred.

---

## 4. Coverage Metrics & API

- `GET /api/v1/mitre/tactics`: Retrieves all 14 tactics ordered by standard ATT&CK kill-chain flow.
- `GET /api/v1/mitre/techniques`: Retrieves techniques with optional tactic, sub-technique, and keyword filtering.
- `GET /api/v1/mitre/matrix-coverage`: Computes system-wide or per-incident heat map coverage percentages and mapped technique tallies.
- `POST /api/v1/incidents/{incident_id}/mitre/map`: Links a technique to an incident with confidence level and evidence summary.
- `DELETE /api/v1/incidents/{incident_id}/mitre/map/{technique_id}`: Removes a technique mapping.
