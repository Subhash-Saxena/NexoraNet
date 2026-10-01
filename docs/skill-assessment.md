# NexoraNet — Skill Assessment Matrix & Confidence Framework

**“Learn. Simulate. Analyze. Defend.”**

## 1. 28 Core Competency Domains
NexoraNet continuously assesses 28 granular cybersecurity proficiencies spanning 8 core defensive domains:

1. **Networking:**
   - `NETWORKING_BASICS`: Layered models, addressing foundations.
   - `TCP_IP`: TCP 3-way handshake, state transitions, windowing, flags.
   - `SUBNETTING`: IPv4/IPv6 CIDR prefixes, host capacity, VLSM.
   - `ROUTING_SWITCHING`: ARP, VLAN tagging, static and dynamic routing.
   - `DNS_DHCP`: Name resolution chains, DORA process, lease scopes.
   - `NETWORK_PROTOCOLS`: HTTP/HTTPS, TLS, SSH, FTP, ICMP operational mechanics.
2. **Packet & Traffic Analysis:**
   - `PACKET_ANALYSIS`: Wireshark frame dissection, stream reassembly.
   - `NETWORK_TRAFFIC_ANALYSIS`: Flow statistics, protocol distribution, throughput.
   - `NETWORK_FORENSICS`: PCAP evidence extraction, beacon detection.
3. **Detection Engineering & Network Defense:**
   - `NETWORK_DEFENSE`: Firewall policies, NAT topologies, perimeter control.
   - `DETECTION_ENGINEERING`: Snort/Suricata syntax, payload inspection rules.
   - `SECURITY_AUTOMATION`: Deterministic dry-run workflows, SOAR playbooks.
4. **SOC Analysis & Alert Triage:**
   - `SOC_ANALYSIS`: Level 1 alert triage, false positive elimination.
   - `ALERT_TRIAGE`: Severity prioritization, context enrichment.
   - `SOC_SCENARIOS`: 9-stage end-to-end incident investigation workflows.
5. **Threat Intelligence & Threat Hunting:**
   - `THREAT_INTEL`: IOC extraction, hash defanging, indicator pivoting.
   - `THREAT_HUNTING`: Hypothesis formulation, entity relationship queries.
6. **SIEM & Security Log Analysis:**
   - `SIEM_ANALYSIS`: Multi-source event ingestion, timestamp normalization.
   - `LOG_ANALYSIS`: Auth failure spikelines, process invocation telemetry.
7. **Endpoint Security & Host Investigation:**
   - `ENDPOINT_SECURITY`: Process tree ancestry, parent-child anomaly detection.
   - `HOST_INVESTIGATION`: Persistence keys, privilege escalation vectors.
   - `DIGITAL_FORENSICS`: Disk, memory, and artifact reconstruction concepts.
8. **Incident Response & Defense Execution:**
   - `INCIDENT_RESPONSE`: NIST 800-61 / SANS 6-phase response lifecycle.
   - `CASE_MANAGEMENT`: Tamper-evident evidence custody, chain of custody.
   - `MITRE_ATTACK`: TTP mapping to enterprise matrix techniques.
   - `INCIDENT_PLAYBOOKS`: Standardized response procedures.
   - `RESPONSE_SIMULATION`: Non-destructive host isolation and account lockdown.
   - `SECURITY_REASONING`: Root cause identification and defensive mitigations.

## 2. Recency Weighting Formula
Skills are calculated deterministically using a recency-weighted formula:
$$\text{Proficiency} = 0.50 \times \text{Recent Performance} + 0.30 \times \text{Historical Performance} + 0.20 \times \text{Practical Performance}$$

## 3. Explainable Confidence Levels
Confidence is strictly decoupled from score to ensure students understand the evidence volume backing an assessment:
- **`HIGH`** ($\ge 5$ evidence entries with $\ge 2$ recent): Solid statistical basis.
- **`MEDIUM`** ($2 - 4$ evidence entries): Developing evidence record.
- **`LOW`** ($< 2$ evidence entries): Sparse preliminary assessment; flagged for targeted practice.
