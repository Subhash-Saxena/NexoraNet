"""Curated educational threat hunting scenarios mapped to MITRE ATT&CK techniques."""

from __future__ import annotations

from typing import Any, ClassVar

from sqlalchemy.orm import Session

from app.models.threat_hunting import ThreatHunt
from app.services.threat_hunting.hunt_service import ThreatHuntService


class HuntScenarioService:
    """Provides structured training scenarios and hands-on investigation workflows."""

    SCENARIOS: ClassVar[dict[str, dict[str, Any]]] = {
        "dns-exfiltration-tunneling": {
            "slug": "dns-exfiltration-tunneling",
            "title": "DNS Exfiltration via Tunneling",
            "difficulty": "BEGINNER",
            "category": "Exfiltration",
            "estimated_minutes": 25,
            "mitre_tactics": ["Exfiltration (TA0010)", "Command and Control (TA0011)"],
            "mitre_techniques": ["T1071.004 (DNS)", "T1048.003 (Exfiltration Over Alternative Protocol)"],
            "brief": "Detect sensitive data encoding and covert exfiltration within anomalous DNS TXT and high-entropy subdomain queries.",
            "objective": "Identify the compromised internal endpoint transmitting high-entropy subdomains to an unauthorized external nameserver.",
            "background": "Network monitoring flagged anomalous outbound UDP/53 traffic. The internal client 192.168.1.105 appears to be issuing hundreds of uniquely structured queries under `corp-sync.test`.",
            "dataset_code": "DS-HUNT-DNS-TUNNEL",
            "initial_pivot_type": "DOMAIN",
            "initial_pivot_value": "corp-sync.test",
            "guided_questions": [
                "Which internal IP address is issuing the abnormal volume of DNS requests?",
                "What unusual record types (TXT, NULL, CNAME) are being requested?",
                "What is the average subdomain length or entropy observed in the queries?",
                "What external IP address answered or hosted the authoritative DNS resolution?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Host 192.168.1.105 is using DNS tunneling for covert exfiltration",
                    "description": "High frequency of base64-encoded subdomains to corp-sync.test represents active staging or data transmission.",
                }
            ],
            "expected_findings": [
                {
                    "title": "Base64 Encoded Subdomain Payload in DNS Queries",
                    "description": "Observed 120+ sequential DNS queries encoding chunked confidential payloads targeting external nameserver 198.51.100.53.",
                    "finding_type": "ANOMALY",
                    "mitigation_recommendation": "Enforce internal DNS recursive resolver policies; restrict direct external outbound port 53 traffic at the perimeter firewall.",
                }
            ],
        },
        "c2-beaconing-investigation": {
            "slug": "c2-beaconing-investigation",
            "title": "Suspicious C2 Beaconing Activity",
            "difficulty": "INTERMEDIATE",
            "category": "Command and Control",
            "estimated_minutes": 35,
            "mitre_tactics": ["Command and Control (TA0011)"],
            "mitre_techniques": ["T1071.001 (Web Protocols)", "T1573.002 (Asymmetric Cryptography)"],
            "brief": "Hunt for periodic HTTP/TLS beaconing patterns to suspicious external infrastructure hidden in standard web browsing.",
            "objective": "Isolate the beacon interval, jitter, and identify infected internal hosts communicating with known C2 infrastructure.",
            "background": "Threat intelligence feeds reported that an APT group is actively using domain `cdn-telemetry-cache.test` for intermittent C2 callbacks.",
            "dataset_code": "DS-HUNT-C2-BEACON",
            "initial_pivot_type": "DOMAIN",
            "initial_pivot_value": "cdn-telemetry-cache.test",
            "guided_questions": [
                "What is the connection periodicity (interval in seconds)? Is there evidence of jitter?",
                "What HTTP URI paths and user-agents are utilized during the connections?",
                "Are payloads symmetric in size or do request/response lengths vary when tasks are executed?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Endpoint 192.168.1.142 has established an active C2 channel",
                    "description": "Periodic outbound HTTPS requests every ~60 seconds to cdn-telemetry-cache.test indicate compromised agent polling.",
                }
            ],
            "expected_findings": [
                {
                    "title": "Periodic Jittered HTTPS Beaconing",
                    "description": "Identified periodic outbound connections on port 443 with a 60-second delta (±5% jitter) directed to 203.0.113.88.",
                    "finding_type": "NETWORK_BEHAVIOR",
                    "mitigation_recommendation": "Block malicious domain on proxy and DNS sinks; perform memory analysis on endpoint 192.168.1.142.",
                }
            ],
        },
        "lateral-movement-smb": {
            "slug": "lateral-movement-smb",
            "title": "SMB Lateral Movement & Remote Execution",
            "difficulty": "ADVANCED",
            "category": "Lateral Movement",
            "estimated_minutes": 45,
            "mitre_tactics": ["Lateral Movement (TA0008)", "Execution (TA0002)"],
            "mitre_techniques": ["T1021.002 (SMB/Windows Admin Shares)", "T1569.002 (Service Execution)"],
            "brief": "Trace an adversary pivoting between workstations using ADMIN$ share writes and PsExec-style remote service registration.",
            "objective": "Reconstruct the timeline of lateral movement from initial beachhead to domain controller or database server.",
            "background": "SOC detected suspicious administrative share access originating from workstation 192.168.1.75 across internal subnet 192.168.1.0/24.",
            "dataset_code": "DS-HUNT-SMB-LATERAL",
            "initial_pivot_type": "IP",
            "initial_pivot_value": "192.168.1.75",
            "guided_questions": [
                "Which destination IPs received SMB (port 445) connections from 192.168.1.75?",
                "What named pipes or administrative shares (C$, IPC$, ADMIN$) were accessed?",
                "Was there any service binary dropped into Windows System32?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Workstation 192.168.1.75 is propagating malicious payloads via SMB",
                    "description": "Rapid succession of SMB connections with ADMIN$ access signals automated lateral movement.",
                }
            ],
            "expected_findings": [
                {
                    "title": "PsExec Style Remote Execution Across Multiple Hosts",
                    "description": "Observed ADMIN$ connection followed by svcctl service creation on 192.168.1.120 and 192.168.1.125.",
                    "finding_type": "PATTERN",
                    "mitigation_recommendation": "Disable SMBv1; enforce workstation-to-workstation firewall blocking; restrict Domain Admin account usage on standard endpoints.",
                }
            ],
        },
        "data-staging-encrypted-egress": {
            "slug": "data-staging-encrypted-egress",
            "title": "Data Staging & Encrypted Egress",
            "difficulty": "INTERMEDIATE",
            "category": "Exfiltration",
            "estimated_minutes": 30,
            "mitre_tactics": ["Collection (TA0009)", "Exfiltration (TA0010)"],
            "mitre_techniques": ["T1074.001 (Local Data Staging)", "T1048.002 (Exfiltration Over Asymmetric Encrypted Non-C2 Protocol)"],
            "brief": "Detect large volume outbound data transfers to cloud file-sharing services or unauthorized VPS IP addresses.",
            "objective": "Determine the total bytes transferred, egress protocol, and identify sensitive file archives staged for transfer.",
            "background": "Bandwidth monitoring triggered a spike alert during off-hours originating from internal file repository 192.168.1.200.",
            "dataset_code": "DS-HUNT-DATA-EGRESS",
            "initial_pivot_type": "IP",
            "initial_pivot_value": "192.168.1.200",
            "guided_questions": [
                "What was the total volume of data transmitted to external destination 198.51.100.120?",
                "What destination port was used, and does it match the expected service banner?",
                "Did this transfer occur during normal business operations or after-hours?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Large scale unauthorized file exfiltration over HTTPS",
                    "description": "Continuous megabyte streams to an untrusted external cloud IP represent data theft.",
                }
            ],
            "expected_findings": [
                {
                    "title": "Off-Hours Exfiltration of 850MB Archive",
                    "description": "Server 192.168.1.200 egressed 850MB to unclassified IP 198.51.100.120 between 02:00 and 03:15 UTC.",
                    "finding_type": "ANOMALY",
                    "mitigation_recommendation": "Configure Data Loss Prevention (DLP) egress thresholds; revoke compromised backup service credentials.",
                }
            ],
        },
        "powershell-download-cradle": {
            "slug": "powershell-download-cradle",
            "title": "Malicious PowerShell Download Cradle",
            "difficulty": "BEGINNER",
            "category": "Execution",
            "estimated_minutes": 20,
            "mitre_tactics": ["Execution (TA0002)", "Defense Evasion (TA0005)"],
            "mitre_techniques": ["T1059.001 (PowerShell)", "T1105 (Ingress Tool Transfer)"],
            "brief": "Analyze HTTP GET requests fetching encoded payloads with suspicious User-Agent headers like WindowsPowerShell.",
            "objective": "Extract the remote payload URL, identify the downloading workstation, and inspect the downloaded script structure.",
            "background": "Proxy logs show an unusual HTTP request to `paste-code-host.test/raw/v849.ps1` with User-Agent `WindowsPowerShell/5.1`.",
            "dataset_code": "DS-HUNT-PS-CRADLE",
            "initial_pivot_type": "DOMAIN",
            "initial_pivot_value": "paste-code-host.test",
            "guided_questions": [
                "Which internal endpoint requested the .ps1 script?",
                "What was the HTTP response status code and payload size?",
                "What malicious actions does the downloaded script initiate upon execution?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Client 192.168.1.80 executed an unauthenticated web cradle",
                    "description": "Outbound HTTP request by PowerShell binary retrieved remote second-stage script.",
                }
            ],
            "expected_findings": [
                {
                    "title": "PowerShell Download of Obfuscated Dropper",
                    "description": "Endpoint 192.168.1.80 fetched 45KB obfuscated script from paste-code-host.test.",
                    "finding_type": "IOC_CORRELATION",
                    "mitigation_recommendation": "Enable PowerShell Constrained Language Mode and Script Block Logging; block direct PowerShell outbound proxy egress.",
                }
            ],
        },
        "internal-recon-portscan": {
            "slug": "internal-recon-portscan",
            "title": "Internal Reconnaissance & Port Scanning",
            "difficulty": "BEGINNER",
            "category": "Discovery",
            "estimated_minutes": 20,
            "mitre_tactics": ["Discovery (TA0007)"],
            "mitre_techniques": ["T1046 (Network Service Discovery)"],
            "brief": "Uncover horizontal and vertical port scanning behavior across sensitive internal subnets.",
            "objective": "Identify the scanner host, target IP list, scanned ports, and assess whether any open ports responded with SYN-ACK.",
            "background": "Intrusion detection flagged high TCP RST packet ratios originating from workstation 192.168.1.66.",
            "dataset_code": "DS-HUNT-RECON-SCAN",
            "initial_pivot_type": "IP",
            "initial_pivot_value": "192.168.1.66",
            "guided_questions": [
                "What ports were targeted by the scan (e.g., 22, 80, 445, 3389, 8080)?",
                "Was the scanning pattern sequential or randomized?",
                "Which internal targets returned SYN-ACK indicating active services?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Host 192.168.1.66 is conducting unauthorized internal reconnaissance",
                    "description": "High velocity TCP SYN probes to ports 22, 80, 445 across /24 range indicates discovery phase.",
                }
            ],
            "expected_findings": [
                {
                    "title": "SYN Stealth Scan Against Internal Subnet",
                    "description": "Host 192.168.1.66 scanned 254 internal addresses across 10 common management ports.",
                    "finding_type": "NETWORK_BEHAVIOR",
                    "mitigation_recommendation": "Isolate host 192.168.1.66 for malware investigation; review switch port security policies.",
                }
            ],
        },
        "password-spraying-brute-force": {
            "slug": "password-spraying-brute-force",
            "title": "Internal Password Spraying & Brute Force",
            "difficulty": "INTERMEDIATE",
            "category": "Credential Access",
            "estimated_minutes": 35,
            "mitre_tactics": ["Credential Access (TA0006)"],
            "mitre_techniques": ["T1110.003 (Password Spraying)", "T1110.001 (Password Guessing)"],
            "brief": "Detect slow and distributed password spraying attacks targeting authentication protocols like Kerberos or RDP.",
            "objective": "Differentiate between benign user lockout bursts and malicious low-and-slow authentication attempts against multiple accounts.",
            "background": "Authentication service logged failed logon spikes across 20 distinct corporate user accounts from single IP 192.168.1.99.",
            "dataset_code": "DS-HUNT-PASSWORD-SPRAY",
            "initial_pivot_type": "IP",
            "initial_pivot_value": "192.168.1.99",
            "guided_questions": [
                "What authentication protocol was targeted (Kerberos, NTLM, RDP, LDAP)?",
                "What was the time interval between logon attempts across distinct usernames?",
                "Did any authentication attempts succeed?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Distributed password spray originating from compromised host 192.168.1.99",
                    "description": "Single-password multi-account authentication attempts designed to evade lockout thresholds.",
                }
            ],
            "expected_findings": [
                {
                    "title": "Horizontal Password Spray Across 20 User Accounts",
                    "description": "Host 192.168.1.99 submitted single common password across 20 accounts, achieving success on account 'svc_backup'.",
                    "finding_type": "PATTERN",
                    "mitigation_recommendation": "Enforce multi-factor authentication (MFA); implement dynamic IP throttling on authentication endpoints.",
                }
            ],
        },
        "supply-chain-compromise": {
            "slug": "supply-chain-compromise",
            "title": "Multi-Stage Supply Chain Compromise",
            "difficulty": "ADVANCED",
            "category": "Initial Access",
            "estimated_minutes": 50,
            "mitre_tactics": ["Initial Access (TA0001)", "Command and Control (TA0011)", "Exfiltration (TA0010)"],
            "mitre_techniques": ["T1195.002 (Compromise Software Supply Chain)", "T1071.001 (Web Protocols)"],
            "brief": "Investigate a legitimate software update binary that contained trojanized payload communicating with sleeper C2 infrastructure.",
            "objective": "Map the entire multi-stage chain: legitimate updater fetch, trojanized execution, sleeper beaconing, and credential harvesting.",
            "background": "Vendor security advisory warns that build v4.2.1 of internal inventory agent contained unauthorized backdoors.",
            "dataset_code": "DS-HUNT-SUPPLY-CHAIN",
            "initial_pivot_type": "DOMAIN",
            "initial_pivot_value": "update-service-cloud.test",
            "guided_questions": [
                "Which systems downloaded the compromised software update version?",
                "What secondary domains were contacted 24 hours after the update installation?",
                "What evidence indicates lateral movement or credential access following the compromise?",
            ],
            "suggested_hypotheses": [
                {
                    "title": "Legitimate software update server delivered trojanized payload",
                    "description": "Downloaded binary executed disguised beaconing routine to sleeper domain telemetry-analytics.test.",
                }
            ],
            "expected_findings": [
                {
                    "title": "Trojanized Agent Binary Triggering Secondary C2 Callback",
                    "description": "Update package downloaded from update-service-cloud.test executed unauthorized thread contacting 203.0.113.195.",
                    "finding_type": "IOC_CORRELATION",
                    "mitigation_recommendation": "Rollback agent to verified checksum v4.2.0; revoke software signing certificates; block auxiliary C2 IPs.",
                }
            ],
        },
    }

    @classmethod
    def list_scenarios(cls, difficulty: str | None = None) -> list[dict[str, Any]]:
        """List all available guided hunting scenarios."""
        scenarios = list(cls.SCENARIOS.values())
        if difficulty:
            scenarios = [s for s in scenarios if s["difficulty"].upper() == difficulty.upper()]
        return scenarios

    @classmethod
    def get_scenario(cls, slug: str) -> dict[str, Any] | None:
        """Fetch scenario detail by slug."""
        return cls.SCENARIOS.get(slug)

    @classmethod
    def launch_scenario(
        cls,
        db: Session,
        user_id: int,
        slug: str,
        target_dataset_id: int | None = None,
    ) -> ThreatHunt | None:
        """Instantiate a structured ThreatHunt session initialized from a training scenario."""
        scenario = cls.get_scenario(slug)
        if not scenario:
            return None

        # Create hunt session
        hunt = ThreatHuntService.create_hunt(
            db=db,
            user_id=user_id,
            title=f"Hunt: {scenario['title']}",
            description=scenario["brief"],
            objective=scenario["objective"],
            dataset_id=target_dataset_id,
            difficulty=scenario["difficulty"],
            scenario_slug=slug,
            initial_pivot_type=scenario.get("initial_pivot_type"),
            initial_pivot_value=scenario.get("initial_pivot_value"),
        )

        return hunt
