"""Educational Seed Service for Step 17: Incident Response, Case Management & MITRE ATT&CK.

Populates the versioned MITRE ATT&CK Enterprise matrix, 10 IR Playbooks,
and 6 realistic synthetic educational incidents across diverse threat categories.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    EvidenceAuditAction,
    EvidenceRelevance,
    EvidenceType,
    IncidentClassification,
    IncidentPhase,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    MitreMappingConfidence,
    ResponseActionCategory,
    ResponseActionStatus,
    ResponseActionType,
)
from app.models.incident import (
    EvidenceAuditLog,
    Incident,
    IncidentEvidence,
    IncidentFinding,
    IncidentHypothesis,
    IncidentNote,
    IncidentTimelineEvent,
    ResponseAction,
)
from app.models.mitre import AttackTactic, AttackTechnique, IncidentTechniqueMapping
from app.models.playbook import IncidentPlaybook

logger = logging.getLogger(__name__)


class IncidentResponseSeedService:
    """Manages idempotent seeding of MITRE catalog, playbooks, and incidents."""

    @classmethod
    def seed_all(cls, db: Session) -> dict[str, int]:
        tactics_count = cls.seed_mitre_catalog(db)
        playbooks_count = cls.seed_playbooks(db)
        incidents_count = cls.seed_synthetic_incidents(db)
        return {
            "tactics_count": tactics_count,
            "playbooks_count": playbooks_count,
            "incidents_count": incidents_count,
        }

    @classmethod
    def seed_mitre_catalog(cls, db: Session) -> int:
        """Seeds the 14 MITRE ATT&CK Enterprise Tactics and 35+ core techniques."""
        existing_tactic = db.execute(select(AttackTactic)).first()
        if existing_tactic:
            return db.execute(select(AttackTactic)).scalars().all().__len__()

        tactics_data = [
            {"tactic_id": "TA0043", "name": "Reconnaissance", "display_order": 1, "description": "The adversary is trying to gather information they can use to plan future operations.", "external_url": "https://attack.mitre.org/tactics/TA0043/"},
            {"tactic_id": "TA0042", "name": "Resource Development", "display_order": 2, "description": "The adversary is trying to establish resources they can use to support operations.", "external_url": "https://attack.mitre.org/tactics/TA0042/"},
            {"tactic_id": "TA0001", "name": "Initial Access", "display_order": 3, "description": "The adversary is trying to get into your network.", "external_url": "https://attack.mitre.org/tactics/TA0001/"},
            {"tactic_id": "TA0002", "name": "Execution", "display_order": 4, "description": "The adversary is trying to run malicious code.", "external_url": "https://attack.mitre.org/tactics/TA0002/"},
            {"tactic_id": "TA0003", "name": "Persistence", "display_order": 5, "description": "The adversary is trying to maintain their foothold.", "external_url": "https://attack.mitre.org/tactics/TA0003/"},
            {"tactic_id": "TA0004", "name": "Privilege Escalation", "display_order": 6, "description": "The adversary is trying to gain higher-level permissions.", "external_url": "https://attack.mitre.org/tactics/TA0004/"},
            {"tactic_id": "TA0005", "name": "Defense Evasion", "display_order": 7, "description": "The adversary is trying to avoid being detected.", "external_url": "https://attack.mitre.org/tactics/TA0005/"},
            {"tactic_id": "TA0006", "name": "Credential Access", "display_order": 8, "description": "The adversary is trying to steal account names and passwords.", "external_url": "https://attack.mitre.org/tactics/TA0006/"},
            {"tactic_id": "TA0007", "name": "Discovery", "display_order": 9, "description": "The adversary is trying to figure out your environment.", "external_url": "https://attack.mitre.org/tactics/TA0007/"},
            {"tactic_id": "TA0008", "name": "Lateral Movement", "display_order": 10, "description": "The adversary is trying to move through your environment.", "external_url": "https://attack.mitre.org/tactics/TA0008/"},
            {"tactic_id": "TA0009", "name": "Collection", "display_order": 11, "description": "The adversary is trying to gather data of interest to their goal.", "external_url": "https://attack.mitre.org/tactics/TA0009/"},
            {"tactic_id": "TA0011", "name": "Command and Control", "display_order": 12, "description": "The adversary is trying to communicate with compromised systems to control them.", "external_url": "https://attack.mitre.org/tactics/TA0011/"},
            {"tactic_id": "TA0010", "name": "Exfiltration", "display_order": 13, "description": "The adversary is trying to steal data.", "external_url": "https://attack.mitre.org/tactics/TA0010/"},
            {"tactic_id": "TA0040", "name": "Impact", "display_order": 14, "description": "The adversary is trying to manipulate, interrupt, or destroy your systems and data.", "external_url": "https://attack.mitre.org/tactics/TA0040/"},
        ]

        tactic_objects: dict[str, AttackTactic] = {}
        for td in tactics_data:
            t = AttackTactic(**td)
            db.add(t)
            tactic_objects[td["tactic_id"]] = t
        db.flush()

        techniques_data = [
            # Reconnaissance
            ("TA0043", "T1595", "Active Scanning", "Adversaries may execute active reconnaissance scans to gather information on IP blocks and open ports.", "Monitor network perimeter logs for port scanning patterns and SYN bursts.", "Block aggressive scanning IPs at border firewall.", False, None, "Linux, Windows, Network", "Network Traffic"),
            ("TA0043", "T1592", "Gather Victim Host Information", "Adversaries gather host details such as OS version and software versions before exploitation.", "Log external HTTP requests with unusual reconnaissance probes.", "Obfuscate software version headers.", False, None, "Linux, Windows", "Web Server Logs"),
            # Resource Development
            ("TA0042", "T1583", "Acquire Infrastructure", "Adversaries acquire domains, VPS, or cloud servers for hosting C2 and phishing sites.", "Perform domain age queries and WHOIS reputation checks.", "Restrict connections to freshly registered domains.", False, None, "Cloud, DNS", "Threat Intel Feeds"),
            # Initial Access
            ("TA0001", "T1566", "Phishing", "Adversaries send malicious emails containing links or attachments to gain unauthorized access.", "Inspect email gateway logs for suspicious SPF/DKIM failures and quarantine flags.", "Enable email sandboxing and SPF/DMARC enforcement.", False, None, "Linux, Windows, macOS", "Email Gateway"),
            ("TA0001", "T1566.001", "Spearphishing Attachment", "Adversaries attach weaponized documents or archives to targeted emails.", "Scan email attachments with antivirus and sandboxing.", "Block macro-enabled documents from untrusted senders.", True, "T1566", "Windows, macOS", "Email Gateway, Antivirus"),
            ("TA0001", "T1190", "Exploit Public-Facing Application", "Adversaries exploit web application vulnerabilities such as SQLi, RCE, or SSRF.", "Correlate WAF alerts with backend application error responses.", "Apply security patches and deploy WAF rules.", False, None, "Linux, Windows", "WAF, Web Application Logs"),
            ("TA0001", "T1078", "Valid Accounts", "Adversaries compromise legitimate credentials to access enterprise systems.", "Detect anomalous geo-velocity and impossible travel logins.", "Enforce multi-factor authentication (MFA) and conditional access.", False, None, "Linux, Windows, Cloud", "Authentication Logs, SIEM"),
            # Execution
            ("TA0002", "T1059", "Command and Scripting Interpreter", "Adversaries abuse command interpreters to execute arbitrary commands.", "Monitor process command lines for encoded or obfuscated flags.", "Restrict script interpreters via AppLocker / WDAC.", False, None, "Linux, Windows, macOS", "Process Creation, Sysmon"),
            ("TA0002", "T1059.001", "PowerShell", "Adversaries execute malicious commands using PowerShell with bypass flags.", "Enable PowerShell Script Block Logging (Event ID 4104) and transcription.", "Enforce Constrained Language Mode and signed scripts.", True, "T1059", "Windows", "Windows Event Log, Sysmon"),
            ("TA0002", "T1059.003", "Windows Command Shell", "Adversaries execute cmd.exe commands to perform reconnaissance and execution.", "Audit cmd.exe executions spawned by non-standard parent processes.", "Restrict command prompt execution for unprivileged accounts.", True, "T1059", "Windows", "Process Creation"),
            ("TA0002", "T1053", "Scheduled Task/Job", "Adversaries configure scheduled tasks to achieve repeated or delayed execution.", "Monitor TaskScheduler Operational log (Event ID 106) and crontab modifications.", "Audit scheduled task registrations.", False, None, "Linux, Windows", "Scheduled Task Logs"),
            # Persistence
            ("TA0003", "T1547", "Boot or Logon Autostart Execution", "Adversaries configure run keys or startup folders to maintain persistence across reboots.", "Monitor registry modifications under Run/RunOnce keys.", "Lock down startup folders and registry permissions.", False, None, "Windows", "Registry Monitoring, Sysmon"),
            ("TA0003", "T1543", "Create or Modify System Process", "Adversaries create system services or daemons to execute on system boot.", "Monitor new service installations (Event ID 7045) and systemd service additions.", "Audit service installation privileges.", False, None, "Linux, Windows", "System Service Logs"),
            # Privilege Escalation
            ("TA0004", "T1068", "Exploitation for Privilege Escalation", "Adversaries exploit software flaws to escalate from unprivileged user to SYSTEM/root.", "Look for sudden user context changes and unquoted service path exploitation.", "Keep operating systems and drivers updated.", False, None, "Linux, Windows", "Kernel Logs, Sysmon"),
            ("TA0004", "T1548", "Abuse Elevation Control Mechanism", "Adversaries bypass UAC or sudo rules to execute commands with elevated tokens.", "Audit UAC consent prompts and sudo privilege elevations in /var/log/auth.log.", "Enforce strict sudoers configuration.", False, None, "Linux, Windows", "Authentication, Process Token"),
            # Defense Evasion
            ("TA0005", "T1070", "Indicator Removal", "Adversaries delete event logs, bash history, or files to cover their tracks.", "Alert on Security Log clearing events (Event ID 1102) and rm -rf commands.", "Forward security logs immediately to a centralized SIEM.", False, None, "Linux, Windows", "Centralized SIEM, Sysmon"),
            ("TA0005", "T1027", "Obfuscated Files or Information", "Adversaries encode scripts with Base64, XOR, or encryption to evade string detection.", "Inspect command-line parameters for -EncodedCommand and excessive entropy.", "De-obfuscate payloads during sandbox inspection.", False, None, "Linux, Windows", "Process CommandLine"),
            ("TA0005", "T1055", "Process Injection", "Adversaries inject malicious code into benign running processes like explorer.exe.", "Monitor CreateRemoteThread, WriteProcessMemory, and VirtualAllocEx Sysmon calls.", "Deploy EDR with process memory protection.", False, None, "Windows, Linux", "Sysmon Event ID 8, EDR"),
            # Credential Access
            ("TA0006", "T1110", "Brute Force", "Adversaries execute automated password guessing or spraying across multiple accounts.", "Analyze SIEM authentication failures grouped by source IP or target account.", "Implement account lockout thresholds and CAPTCHA.", False, None, "Linux, Windows, Cloud", "Authentication Logs"),
            ("TA0006", "T1110.003", "Password Spraying", "Adversaries test a single common password against many enterprise user accounts.", "Detect high counts of Event ID 4625 across multiple distinct usernames within minutes.", "Enforce strong password policies and detect breached passwords.", True, "T1110", "Windows, Linux", "Active Directory, SIEM"),
            ("TA0006", "T1003", "OS Credential Dumping", "Adversaries extract credentials from LSASS process memory or SAM database.", "Alert on open handle requests to lsass.exe (Sysmon Event ID 10) by non-system tools.", "Enable LSA Protection (RunAsPPL) and Credential Guard.", False, None, "Windows", "Sysmon, EDR"),
            # Discovery
            ("TA0007", "T1046", "Network Service Discovery", "Adversaries scan remote IP addresses and ports to find listening network services.", "Detect internal ICMP sweeps or port scanning from workstation subnets.", "Segment internal subnets and restrict inter-VLAN routing.", False, None, "Network, Linux, Windows", "NetFlow, Firewall Logs"),
            ("TA0007", "T1087", "Account Discovery", "Adversaries query user accounts using commands like net user or get-aduser.", "Audit command execution of net.exe, whoami, and LDAP queries.", "Monitor LDAP queries originating from unexpected workstations.", False, None, "Windows, Linux", "Process Creation, LDAP Logs"),
            ("TA0007", "T1082", "System Information Discovery", "Adversaries query system hardware, OS version, and patch levels.", "Monitor systeminfo, uname -a, and hostname executions.", "Establish baseline telemetry for workstation commands.", False, None, "Linux, Windows", "Process CommandLine"),
            # Lateral Movement
            ("TA0008", "T1021", "Remote Services", "Adversaries use valid credentials to access remote systems via RDP, SSH, or SMB.", "Monitor unexpected RDP connections (Event ID 4624 Type 10) between workstations.", "Disable workstation-to-workstation RDP via Host Firewalls.", False, None, "Linux, Windows", "Remote Desktop Logs"),
            ("TA0008", "T1021.001", "Remote Desktop Protocol", "Adversaries connect to internal systems via RDP to interact with graphical desktops.", "Track RDP logon events and alert on simultaneous multi-system sessions.", "Enforce RDP Network Level Authentication (NLA) and MFA.", True, "T1021", "Windows", "TerminalServices Logs"),
            ("TA0008", "T1021.002", "SMB/Windows Admin Shares", "Adversaries use SMB administrative shares (C$, ADMIN$) to move files across the network.", "Monitor Event ID 5140 and 5145 for sensitive share access.", "Restrict SMB traffic across boundary firewalls.", True, "T1021", "Windows", "File Share Auditing"),
            # Collection
            ("TA0009", "T1005", "Data from Local System", "Adversaries search local disk drives to find documents, databases, and configuration files.", "Monitor unusual file read volumes on sensitive directory shares.", "Implement Least Privilege access control on file shares.", False, None, "Linux, Windows", "File Integrity Monitoring"),
            ("TA0009", "T1560", "Archive Collected Data", "Adversaries compress and encrypt files into zip/7z/tar archives prior to exfiltration.", "Look for 7z.exe, rar.exe, or tar executions targeting user document folders.", "Block unauthorized archiving binaries on endpoints.", False, None, "Linux, Windows", "Process Creation, File Creation"),
            # Command and Control
            ("TA0011", "T1071", "Application Layer Protocol", "Adversaries communicate with external C2 infrastructure over HTTP, HTTPS, or DNS.", "Correlate outbound network traffic with known malicious C2 IP and domain feeds.", "Use SSL inspection and DNS filtering proxies.", False, None, "Network, Web", "Proxy Logs, DNS Logs"),
            ("TA0011", "T1071.001", "Web Protocols", "Adversaries use HTTP/HTTPS requests to disguise C2 beaconing in normal web traffic.", "Detect regular beacon interval patterns (jitter) and abnormal user agents.", "Employ web proxy content filtering and anomaly detection.", True, "T1071", "Network", "Web Proxy, NetFlow"),
            ("TA0011", "T1071.004", "DNS", "Adversaries encode commands in DNS query subdomains and responses.", "Detect high request frequencies, abnormal domain entropy, and large TXT answers.", "Direct all DNS through internal resolving resolvers and enforce DNS RPZ.", True, "T1071", "Network", "DNS Logs, PCAP"),
            ("TA0011", "T1105", "Ingress Tool Transfer", "Adversaries transfer hacking tools or malware from external servers to the target host.", "Monitor curl, wget, certutil -urlcache, and bitsadmin download commands.", "Restrict outbound egress connections to authorized destinations.", False, None, "Linux, Windows", "Process Creation, Network Connections"),
            # Exfiltration
            ("TA0010", "T1041", "Exfiltration Over C2 Channel", "Adversaries transfer stolen data through the existing command and control channel.", "Detect high outbound traffic volumes to external IP addresses.", "Deploy Data Loss Prevention (DLP) controls and egress filtering.", False, None, "Network", "NetFlow, Firewall Logs"),
            ("TA0010", "T1048", "Exfiltration Over Alternative Protocol", "Adversaries exfiltrate sensitive data over protocols like SFTP, FTP, or cloud storage.", "Monitor large file uploads to cloud file sharing sites like Mega or Google Drive.", "Enforce Cloud Access Security Broker (CASB) upload restrictions.", False, None, "Network, Cloud", "CASB, Web Proxy"),
            # Impact
            ("TA0040", "T1486", "Data Encrypted for Impact", "Adversaries encrypt enterprise files and demand ransom for the decryption key.", "Detect rapid mass file modifications, file rename bursts, and ransom note creation.", "Maintain immutable offline backups and deploy anti-ransomware EDR rules.", False, None, "Linux, Windows", "File System Events, EDR"),
            ("TA0040", "T1489", "Service Stop", "Adversaries stop security services, database engines, or backup software.", "Monitor net stop, sc stop, and systemctl stop commands on critical services.", "Protect service control managers with tamper protection.", False, None, "Linux, Windows", "Service Logs, Process CommandLine"),
        ]

        for tactic_id, tech_id, name, desc, det, mit, is_sub, parent_id, plats, data_src in techniques_data:
            tactic = tactic_objects.get(tactic_id)
            if not tactic:
                continue
            tech = AttackTechnique(
                technique_id=tech_id,
                tactic_id=tactic.id,
                name=name,
                description=desc,
                detection_guidance=det,
                mitigation_guidance=mit,
                is_subtechnique=is_sub,
                parent_technique_id=parent_id,
                platforms=plats,
                data_sources=data_src,
                external_url=f"https://attack.mitre.org/techniques/{tech_id.replace('.', '/')}/",
            )
            db.add(tech)
        db.commit()
        return len(tactics_data)

    @classmethod
    def seed_playbooks(cls, db: Session) -> int:
        """Seeds 10 standardized educational incident response playbooks."""
        existing = db.execute(select(IncidentPlaybook)).first()
        if existing:
            return db.execute(select(IncidentPlaybook)).scalars().all().__len__()

        playbooks = [
            {
                "playbook_id": "PB-RANSOMWARE",
                "title": "Ransomware Intrusion & Extortion Response",
                "category": "MALWARE",
                "severity_guidance": "CRITICAL",
                "primary_tactic_id": "TA0040",
                "description": "Standard operating procedure for responding to active ransomware staging, execution, and extortion events across server and endpoint environments.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Verify immutable offline backup status", "Ensure out-of-band communication channels are established", "Pre-position forensic collection tools on secure USB or isolated share"],
                    "IDENTIFICATION": ["Identify affected hostnames, IP addresses, and encrypted volume shares", "Extract ransom note text, contact addresses, and file extension signatures", "Determine initial infection vector via auth logs, web server logs, or phishing reports"],
                    "CONTAINMENT": ["Execute simulated network isolation on affected hosts to prevent lateral spread", "Revoke compromised user and service account credentials", "Block external C2 command IP addresses at firewall perimeter"],
                    "ERADICATION": ["Terminate malicious processes and remove scheduled tasks / registry Run keys", "Delete staging directories and dropper binaries", "Scan network shares for unexecuted payload droppers"],
                    "RECOVERY": ["Restore affected systems from verified clean, immutable backups", "Validate operating system integrity and patch exploited vulnerabilities", "Re-enable network access under heightened telemetry monitoring"],
                    "LESSONS_LEARNED": ["Document root cause timeline from initial access to ransomware execution", "Review gap in endpoint detection or MFA bypass", "Update detection rules and host hardening baselines"]
                }),
                "checklist_json": json.dumps([
                    "Are backups separated logically and physically from Active Directory?",
                    "Has the ransomware binary been preserved in safe memory dump / sandbox?",
                    "Have network shares been checked for unauthorized write locks?",
                    "Are domain admin credentials suspected of compromise?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_HOST_ISOLATION",
                    "SIMULATE_ACCOUNT_RESTRICTION",
                    "SIMULATE_IOC_BLOCK",
                    "SIMULATE_SESSION_REVOCATION"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-CRED-STUFFING",
                "title": "Credential Stuffing & Password Spraying Response",
                "category": "CREDENTIALS",
                "severity_guidance": "HIGH",
                "primary_tactic_id": "TA0006",
                "description": "Systematic response to distributed authentication attacks, VPN spraying, and credential validation probes.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Configure centralized authentication logging (RADIUS, SSO, AD)", "Establish baseline login failure rate per hour"],
                    "IDENTIFICATION": ["Analyze SIEM authentication failures grouped by source IP subnet", "Identify targeted accounts and successful logins following bursts", "Inspect User-Agent strings and proxy headers"],
                    "CONTAINMENT": ["Implement temporary IP rate limiting or geo-blocking on gateway", "Force password reset and terminate sessions for targeted accounts with successful logins", "Enforce step-up MFA challenge"],
                    "ERADICATION": ["Revoke active tokens for compromised accounts", "Audit recent activities performed by compromised accounts during the window", "Update breached password filter lists"],
                    "RECOVERY": ["Restore normal login access following user identity re-verification", "Monitor targeted accounts for repeat login attempts"],
                    "LESSONS_LEARNED": ["Evaluate feasibility of FIDO2 WebAuthn mandatory rollout", "Tune SIEM threshold correlation rules for distributed spraying"]
                }),
                "checklist_json": json.dumps([
                    "Were any logins successful from the spraying IP addresses?",
                    "Did attackers bypass MFA or exploit legacy authentication protocols (e.g., IMAP, POP3)?",
                    "Are affected accounts shared or privileged service accounts?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_NETWORK_BLOCK",
                    "SIMULATE_RESET_CREDENTIAL",
                    "SIMULATE_SESSION_REVOCATION"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-PHISHING",
                "title": "Spear Phishing & Credential Harvester Response",
                "category": "PHISHING",
                "severity_guidance": "MEDIUM",
                "primary_tactic_id": "TA0001",
                "description": "Guidance for analyzing reported phishing emails, credential harvest landing pages, and weaponized document attachments.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Provide user phishing report button in email client", "Maintain safe URL detonation environment"],
                    "IDENTIFICATION": ["Extract headers: Return-Path, Authentication-Results (SPF, DKIM, DMARC)", "Identify recipient list and determine who clicked or submitted credentials", "Analyze landing page domain age, TLS cert, and hosted payload"],
                    "CONTAINMENT": ["Purge phishing message from all recipient mailboxes across tenant", "Block sender address and domain at email gateway", "Block harvest URL and domain at web proxy and DNS filter"],
                    "ERADICATION": ["Reset credentials for any user who interacted with the landing page", "Revoke OAuth consent grants for suspicious third-party apps"],
                    "RECOVERY": ["Re-enable mail delivery after sender block verification", "Notify affected users with guidance on recognizing lure techniques"],
                    "LESSONS_LEARNED": ["Add lure theme to upcoming educational awareness simulation", "Adjust inbound spam and DMARC quarantine enforcement"]
                }),
                "checklist_json": json.dumps([
                    "Did any recipients enter credentials or MFA codes on the site?",
                    "Did the email contain a malicious attachment that executed macros or scripts?",
                    "Has the malicious domain been reported to domain registrar / hosting provider?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_IOC_BLOCK",
                    "SIMULATE_RESET_CREDENTIAL",
                    "SIMULATE_SESSION_REVOCATION"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-DATA-EXFIL",
                "title": "Unauthorized Data Exfiltration via DNS/HTTPS Response",
                "category": "EXFILTRATION",
                "severity_guidance": "HIGH",
                "primary_tactic_id": "TA0010",
                "description": "Investigating high-volume or stealthy exfiltration channels including DNS tunneling, cloud uploads, and C2 beacons.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Deploy NetFlow collection on border switches", "Enable DNS query logging and entropy scoring"],
                    "IDENTIFICATION": ["Identify source internal host generating high outbound bytes or DNS queries", "Analyze payload entropy, query frequency, and record types (TXT, NULL)", "Determine what files were read on the host prior to the transfer"],
                    "CONTAINMENT": ["Simulate host isolation to cut off the active exfiltration stream", "Block target destination IP/domain at border proxy and DNS firewall", "Kill suspicious processes holding network sockets"],
                    "ERADICATION": ["Locate staging zip/7z archives and delete them from disk", "Identify and remove exfiltration utility or staging scripts"],
                    "RECOVERY": ["Assess exact classification of exfiltrated data (PII, IP, financial)", "Perform compliance notification assessment if sensitive data was breached"],
                    "LESSONS_LEARNED": ["Implement DLP endpoint controls restricting cloud storage uploads", "Enforce strict DNS recursion policy blocking direct external queries"]
                }),
                "checklist_json": json.dumps([
                    "What is the estimated volume of exfiltrated bytes?",
                    "Was the exfiltrated data encrypted before leaving the network?",
                    "Are regulatory disclosure deadlines triggered (e.g. GDPR, HIPAA)?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_HOST_ISOLATION",
                    "SIMULATE_NETWORK_BLOCK",
                    "SIMULATE_IOC_BLOCK"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-WEB-EXPLOIT",
                "title": "Public-Facing Web Application Exploit (SQLi/RCE)",
                "category": "NETWORK",
                "severity_guidance": "CRITICAL",
                "primary_tactic_id": "TA0001",
                "description": "Handling compromise of public-facing web applications, web shell drops, and database injection attacks.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Maintain up-to-date software bill of materials (SBOM)", "Deploy Web Application Firewall (WAF) in blocking mode"],
                    "IDENTIFICATION": ["Correlate WAF alerts with web server access logs and HTTP 500/200 responses", "Inspect file system for newly modified files in web roots (.php, .jsp, .aspx)", "Check database query audit logs for UNION SELECT or xp_cmdshell execution"],
                    "CONTAINMENT": ["Block attacking IP addresses at WAF and border ACLs", "Isolate compromised web server from backend database subnet", "Disable vulnerable endpoint or apply virtual patch on WAF"],
                    "ERADICATION": ["Remove web shells, backdoors, and unauthorized cron jobs", "Review database tables for injected malicious scripts or altered records"],
                    "RECOVERY": ["Deploy tested source code patch fixing the underlying vulnerability", "Restore web server from verified immutable container image", "Resume public traffic with strict WAF inspection"],
                    "LESSONS_LEARNED": ["Perform static code analysis (SAST) on application repository", "Conduct third-party web application penetration test"]
                }),
                "checklist_json": json.dumps([
                    "Did the attacker successfully drop a persistent web shell?",
                    "Was the web application running as root / SYSTEM or a low-privileged service account?",
                    "Was the database breached or data exfiltrated?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_NETWORK_BLOCK",
                    "SIMULATE_HOST_ISOLATION",
                    "SIMULATE_CLEAN_HOST"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-LATERAL-MOV",
                "title": "Pass-the-Hash & SMB/RDP Lateral Movement Response",
                "category": "ENDPOINT",
                "severity_guidance": "HIGH",
                "primary_tactic_id": "TA0008",
                "description": "Responding to attacker movement across workstations and member servers using compromised hashes or tickets.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Enforce Local Administrator Password Solution (LAPS)", "Disable NTLMv1 and restrict SMBv1"],
                    "IDENTIFICATION": ["Analyze Event ID 4624 (Logon Type 3 and 10) originating from non-admin machines", "Detect PsExec, WMI, or WinRM execution across internal IPs", "Identify Kerberos ticket requests with anomalous encryption types"],
                    "CONTAINMENT": ["Isolate origin host initiating lateral connections", "Reset compromised service and domain user accounts", "Enforce host firewall rule blocking SMB (TCP 445) between workstations"],
                    "ERADICATION": ["Kill remote processes spawned via WMI or WinRM", "Clear cached credentials using simulated system reboot", "Remove unauthorized scheduled tasks installed remotely"],
                    "RECOVERY": ["Re-issue Kerberos Krbtgt account password twice", "Re-enable host networking under strict behavioral monitoring"],
                    "LESSONS_LEARNED": ["Implement tiered administration model (Tier 0, Tier 1, Tier 2)", "Enforce Credential Guard on all Windows endpoints"]
                }),
                "checklist_json": json.dumps([
                    "Did lateral movement reach Domain Controllers or Tier 0 assets?",
                    "Were credentials dumped from LSASS on intermediate workstations?",
                    "Was Kerberoasting or AS-REP roasting observed?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_HOST_ISOLATION",
                    "SIMULATE_RESET_CREDENTIAL",
                    "SIMULATE_SESSION_REVOCATION"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-MALICIOUS-PROC",
                "title": "Living-off-the-Land (LotL) / PowerShell Abuse Response",
                "category": "ENDPOINT",
                "severity_guidance": "MEDIUM",
                "primary_tactic_id": "TA0002",
                "description": "Detecting and containing legitimate built-in tools (certutil, bitsadmin, mshta, powershell) abused for malicious purposes.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Enable Sysmon Event ID 1 (Process Creation) with command-line auditing", "Enable PowerShell script block logging (Event ID 4104)"],
                    "IDENTIFICATION": ["Analyze anomalous parent-child relationships (e.g., word.exe spawning powershell.exe)", "Decode Base64 encoded flags (-enc, -encodedcommand)", "Inspect downloaded payloads in temp and user AppData folders"],
                    "CONTAINMENT": ["Isolate endpoint to prevent command execution completion", "Terminate suspicious process tree via EDR", "Block download staging URL at perimeter proxy"],
                    "ERADICATION": ["Delete dropped scripts and temporary payload files", "Inspect autoruns and scheduled tasks created by the process"],
                    "RECOVERY": ["Verify system state integrity against baseline", "Reconnect endpoint with strict application control rules active"],
                    "LESSONS_LEARNED": ["Implement AppLocker / WDAC rules blocking powershell for non-technical staff", "Tune detection rules for certutil and bitsadmin misuse"]
                }),
                "checklist_json": json.dumps([
                    "What was the parent process that spawned the shell?",
                    "Was the payload fully decoded and analyzed?",
                    "Did the script attempt credential dumping or internal discovery?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_HOST_ISOLATION",
                    "SIMULATE_IOC_BLOCK",
                    "SIMULATE_CLEAN_HOST"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-INSIDER-THREAT",
                "title": "Privilege Escalation & Rogue Admin Activity Response",
                "category": "CREDENTIALS",
                "severity_guidance": "HIGH",
                "primary_tactic_id": "TA0004",
                "description": "Responding to unauthorized privilege abuse, rogue admin accounts, or after-hours bulk data access by internal personnel.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Maintain privileged access management (PAM) audit logs", "Define approved change management windows"],
                    "IDENTIFICATION": ["Review SIEM alerts for new admin account creation outside change windows", "Check Event ID 4720 (User Created) and 4728 (Member Added to Security Group)", "Correlate physical badge access with workstation login times"],
                    "CONTAINMENT": ["Disable suspected rogue account immediately", "Revoke active VPN and SSO sessions", "Preserve audit logs in read-only forensic repository"],
                    "ERADICATION": ["Remove unauthorized accounts from privileged groups (Domain Admins, sudoers)", "Revert unapproved system configurations or permissions"],
                    "RECOVERY": ["Review change logs with department leadership", "Re-establish normal administrative workflow with Dual-Control approvals"],
                    "LESSONS_LEARNED": ["Deploy Just-In-Time (JIT) privileged access management", "Establish peer review requirements for security group changes"]
                }),
                "checklist_json": json.dumps([
                    "Was there an authorized change request corresponding to the activity?",
                    "Were sensitive files copied to personal cloud storage or USB media?",
                    "Is HR / Legal counsel notified per company incident policy?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_ACCOUNT_RESTRICTION",
                    "SIMULATE_SESSION_REVOCATION"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-SUPPLY-CHAIN",
                "title": "Malicious Dependency / Compromised Package Response",
                "category": "MALWARE",
                "severity_guidance": "HIGH",
                "primary_tactic_id": "TA0001",
                "description": "Investigating compromised third-party dependencies, malicious PyPI/NPM packages, or modified vendor software updates.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Enforce package lockfiles and cryptographic hash verification", "Maintain private artifact repository proxy (e.g. Nexus, Artifactory)"],
                    "IDENTIFICATION": ["Identify affected build pipelines and production deployments containing the package", "Extract malicious install scripts (setup.py, preinstall hook)", "Inspect outbound connections initiated during package build/test"],
                    "CONTAINMENT": ["Quarantine package in private artifact repository", "Stop running containers or services executing the compromised build", "Block package author C2 infrastructure at firewall"],
                    "ERADICATION": ["Remove tainted package from all project dependency files", "Rotate API keys and secrets stored in the build environment"],
                    "RECOVERY": ["Rebuild and redeploy applications using verified clean packages", "Perform integrity scans across all deployed artifacts"],
                    "LESSONS_LEARNED": ["Implement Software Composition Analysis (SCA) tooling in CI/CD pipeline", "Enforce automated vulnerability scanning prior to package promotion"]
                }),
                "checklist_json": json.dumps([
                    "Did the malicious package harvest CI/CD environment secrets or tokens?",
                    "Was the build artifact distributed to end-customers?",
                    "Has an advisory been submitted to public package registries?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_IOC_BLOCK",
                    "SIMULATE_RESET_CREDENTIAL",
                    "SIMULATE_CLEAN_HOST"
                ]),
                "version": "1.0",
            },
            {
                "playbook_id": "PB-DOS-EXHAUSTION",
                "title": "Application Layer Denial of Service & Resource Exhaustion",
                "category": "NETWORK",
                "severity_guidance": "MEDIUM",
                "primary_tactic_id": "TA0040",
                "description": "Handling HTTP flood attacks, slowloris socket exhaustion, and volumetric network disruptions.",
                "phases_definition": json.dumps({
                    "PREPARATION": ["Deploy upstream CDN / DDoS mitigation service", "Establish baseline request rate and connection limits"],
                    "IDENTIFICATION": ["Analyze web server connection states and CPU/memory utilization", "Inspect access logs for repetitive URI paths and abnormal request headers", "Distinguish legitimate traffic spikes (flash crowds) from distributed botnet floods"],
                    "CONTAINMENT": ["Enable CDN 'Under Attack' mode with JS challenges", "Apply rate limiting rules on specific URI endpoints", "Drop malicious botnet ASNs or geographic origins at upstream edge"],
                    "ERADICATION": ["Identify and block persistent offending IP ranges", "Tune web server worker limits and keepalive timeouts"],
                    "RECOVERY": ["Gradually restore standard CDN caching and rate limiting policies", "Monitor backend database queue and application response times"],
                    "LESSONS_LEARNED": ["Scale horizontal autoscaling trigger thresholds", "Review API rate-limiting architecture with engineering team"]
                }),
                "checklist_json": json.dumps([
                    "Is the attack targeting network bandwidth (Layer 3/4) or application resources (Layer 7)?",
                    "Are upstream transit providers aware of the volumetric flood?",
                    "Were internal systems breached during the distraction attack?"
                ]),
                "recommended_actions_json": json.dumps([
                    "SIMULATE_NETWORK_BLOCK"
                ]),
                "version": "1.0",
            },
        ]

        for pb_data in playbooks:
            p = IncidentPlaybook(**pb_data)
            db.add(p)
        db.commit()
        return len(playbooks)

    @classmethod
    def seed_synthetic_incidents(cls, db: Session) -> int:
        """Seeds 6 comprehensive synthetic educational incidents with rich investigation artifacts."""
        existing = db.execute(select(Incident)).first()
        if existing:
            return db.execute(select(Incident)).scalars().all().__len__()

        now = datetime.now(timezone.utc)
        playbooks_map = {p.playbook_id: p for p in db.execute(select(IncidentPlaybook)).scalars().all()}
        techniques_map = {t.technique_id: t for t in db.execute(select(AttackTechnique)).scalars().all()}

        # ----------------------------------------------------------------------
        # INCIDENT 1: Ransomware Staging on Finance Server
        # ----------------------------------------------------------------------
        inc1 = Incident(
            incident_id="INC-2026-0001",
            title="Critical Ransomware Staging on Finance Server (FIN-SRV-01)",
            description="SOC telemetry detected rapid file encryption indicators, volume shadow copy deletion commands, and C2 beacons originating from the core finance database server.",
            incident_type=IncidentType.MALWARE_INDICATOR,
            severity=IncidentSeverity.CRITICAL,
            priority="P1",
            status=IncidentStatus.CONTAINMENT,
            phase=IncidentPhase.CONTAINMENT_ERADICATION_RECOVERY,
            classification=IncidentClassification.CONFIRMED_INCIDENT,
            lead_analyst="Senior SOC Analyst Chen",
            playbook_id=playbooks_map.get("PB-RANSOMWARE").id if playbooks_map.get("PB-RANSOMWARE") else None,
            detected_at=now - timedelta(hours=4),
            contained_at=now - timedelta(hours=2),
            summary="Attacker leveraged compromised credentials on FIN-SRV-01, dropped BlackCat-variant ransomware payload, and attempted volume shadow copy deletion before host isolation was executed.",
            impact_assessment="Confined to FIN-SRV-01. Host isolated before network shares were encrypted. No data exfiltration detected in egress NetFlow.",
            root_cause="Phishing email compromised finance contractor workstation, which held cached RDP credentials to FIN-SRV-01.",
            lessons_learned="Enforce tiered administration and restrict RDP connections between workstation subnets and critical server subnets.",
            recommendations="Deploy immutable backup repositories and enforce Credential Guard on all finance servers.",
            simulation_mode=True,
        )
        db.add(inc1)
        db.flush()

        # Add Evidence for INC-1
        ev1_1 = IncidentEvidence(
            evidence_id="EVD-2026-0001",
            incident_id=inc1.id,
            title="PowerShell Volume Shadow Copy Deletion Command",
            description="Sysmon Event ID 1 captured vssadmin.exe Delete Shadows /All /Quiet executed by parent powershell.exe",
            evidence_type=EvidenceType.PROCESS_EVENT,
            source_engine="ENDPOINT_SECURITY",
            source_id="HOST-FIN-SRV-01-EVT-4091",
            hash_sha256=hashlib.sha256(b"vssadmin delete shadows /all /quiet").hexdigest(),
            relevance=EvidenceRelevance.SUPPORTING,
            is_contained=True,
            collected_at=now - timedelta(hours=3, minutes=45),
            data_payload=json.dumps({"command": "vssadmin.exe Delete Shadows /All /Quiet", "parent": "powershell.exe", "pid": 4820, "user": "NT AUTHORITY\\SYSTEM"}),
        )
        db.add(ev1_1)
        db.flush()

        db.add(EvidenceAuditLog(
            evidence_id=ev1_1.id,
            action=EvidenceAuditAction.ATTACHED,
            details="Collected from host FIN-SRV-01 during triage investigation",
            timestamp=now - timedelta(hours=3, minutes=40),
        ))
        db.add(EvidenceAuditLog(
            evidence_id=ev1_1.id,
            action=EvidenceAuditAction.HASH_VERIFIED,
            details="Cryptographic SHA-256 hash verified against endpoint event log payload",
            timestamp=now - timedelta(hours=3, minutes=38),
        ))

        ev1_2 = IncidentEvidence(
            evidence_id="EVD-2026-0002",
            incident_id=inc1.id,
            title="Outbound C2 Beacon to Known Malicious IP 198.51.100.23",
            description="SIEM network log recorded repeated periodic HTTP beacons every 60 seconds with jitter",
            evidence_type=EvidenceType.SIEM_EVENT,
            source_engine="SIEM",
            source_id="SIEM-LOG-882194",
            hash_sha256=hashlib.sha256(b"198.51.100.23:443 beacon").hexdigest(),
            relevance=EvidenceRelevance.SUPPORTING,
            is_contained=True,
            collected_at=now - timedelta(hours=3, minutes=30),
            data_payload=json.dumps({"destination_ip": "198.51.100.23", "destination_port": 443, "frequency": "60s", "protocol": "TLS"}),
        )
        db.add(ev1_2)

        # Timeline for INC-1
        db.add(IncidentTimelineEvent(
            incident_id=inc1.id,
            timestamp=now - timedelta(hours=4),
            title="Initial RDP Logon from Workstation WS-FIN-04",
            description="Account 'svc_backup' authenticated via RDP from internal workstation WS-FIN-04 (192.168.10.42)",
            event_category="INITIAL_ACCESS",
            source="ENDPOINT",
            source_id="EVT-4624-991",
            mitre_technique_id="T1078",
            is_milestone=True,
        ))
        db.add(IncidentTimelineEvent(
            incident_id=inc1.id,
            timestamp=now - timedelta(hours=3, minutes=50),
            title="Encoded PowerShell Execution Detected",
            description="PowerShell process launched with Base64 payload downloading second-stage binary",
            event_category="EXECUTION",
            source="ENDPOINT",
            source_id="EVT-4104-102",
            mitre_technique_id="T1059.001",
            is_milestone=False,
        ))
        db.add(IncidentTimelineEvent(
            incident_id=inc1.id,
            timestamp=now - timedelta(hours=3, minutes=45),
            title="Shadow Copy Deletion Attempted",
            description="Attacker ran vssadmin.exe delete shadows to inhibit system recovery",
            event_category="DEFENSE_EVASION",
            source="ENDPOINT",
            source_id="EVT-1-4820",
            mitre_technique_id="T1489",
            is_milestone=False,
        ))
        db.add(IncidentTimelineEvent(
            incident_id=inc1.id,
            timestamp=now - timedelta(hours=2),
            title="Simulated Host Isolation Executed",
            description="SOC analyst Chen executed simulated host containment isolating FIN-SRV-01 from all internal networks",
            event_category="CONTAINMENT",
            source="ACTION",
            source_id="ACT-2026-0001",
            is_milestone=True,
        ))

        # Hypotheses for INC-1
        db.add(IncidentHypothesis(
            hypothesis_id="HYP-2026-0001",
            incident_id=inc1.id,
            statement="Attacker moved laterally from WS-FIN-04 to FIN-SRV-01 using compromised backup service credentials.",
            status="SUPPORTED",
            confidence="HIGH",
            rationale="Auth logs confirm svc_backup authenticated via RDP immediately prior to execution.",
            tested_at=now - timedelta(hours=2, minutes=30),
            concluded_at=now - timedelta(hours=2),
        ))
        db.add(IncidentHypothesis(
            hypothesis_id="HYP-2026-0002",
            incident_id=inc1.id,
            statement="Attacker attempted to exfiltrate financial databases before initiating encryption.",
            status="NOT_SUPPORTED",
            confidence="HIGH",
            rationale="NetFlow egress analysis confirms total outbound bytes was under 2.4 MB (C2 beaconing only, no bulk transfer).",
            tested_at=now - timedelta(hours=2, minutes=15),
            concluded_at=now - timedelta(hours=1, minutes=45),
        ))

        # Findings for INC-1
        db.add(IncidentFinding(
            finding_id="FND-2026-0001",
            incident_id=inc1.id,
            title="Ransomware Binary Staged in C:\\Windows\\Temp",
            description="Payload dropper 'win_update_x64.exe' was written to C:\\Windows\\Temp\\ and executed via scheduled task.",
            severity="CRITICAL",
            confidence="HIGH",
            affected_systems="FIN-SRV-01 (10.0.4.15)",
            affected_accounts="svc_backup",
            indicators_observed="198.51.100.23, win_update_x64.exe, SHA256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            mitre_technique="T1486",
            mitre_tactic="TA0040",
        ))

        # Simulated Response Actions for INC-1
        db.add(ResponseAction(
            action_id="ACT-2026-0001",
            incident_id=inc1.id,
            category=ResponseActionCategory.CONTAINMENT,
            action_type=ResponseActionType.SIMULATE_HOST_ISOLATION,
            target_type="HOST",
            target_identifier="FIN-SRV-01 (10.0.4.15)",
            status=ResponseActionStatus.EXECUTED,
            simulation_only=True,
            reason="Prevent ransomware lateral movement to database cluster and file servers.",
            risk_assessment="Finance department cannot process batch invoicing during server isolation window.",
            expected_impact="All non-management network traffic dropped. Management telemetry preserved.",
            simulated_outcome="FIN-SRV-01 successfully isolated from VLAN 40. Lateral spread halted.",
            executed_at=now - timedelta(hours=2),
        ))
        db.add(ResponseAction(
            action_id="ACT-2026-0002",
            incident_id=inc1.id,
            category=ResponseActionCategory.CONTAINMENT,
            action_type=ResponseActionType.SIMULATE_IOC_BLOCK,
            target_type="IP",
            target_identifier="198.51.100.23",
            status=ResponseActionStatus.EXECUTED,
            simulation_only=True,
            reason="Terminate active C2 communication channel.",
            risk_assessment="Zero business impact; IP is an unclassified foreign VPS with high threat score.",
            expected_impact="Border firewall drops all TCP 443 outbound sessions to 198.51.100.23.",
            simulated_outcome="Firewall rule DENY_198.51.100.23 applied to perimeter ACL.",
            executed_at=now - timedelta(hours=1, minutes=50),
        ))

        # MITRE Mapping for INC-1
        if techniques_map.get("T1486"):
            db.add(IncidentTechniqueMapping(
                incident_id=inc1.id,
                technique_id=techniques_map["T1486"].id,
                mapping_confidence=MitreMappingConfidence.OBSERVED_EVIDENCE,
                evidence_summary="Ransom note observed and test file encrypted on FIN-SRV-01.",
                phase="IMPACT",
            ))
        if techniques_map.get("T1059.001"):
            db.add(IncidentTechniqueMapping(
                incident_id=inc1.id,
                technique_id=techniques_map["T1059.001"].id,
                mapping_confidence=MitreMappingConfidence.OBSERVED_EVIDENCE,
                evidence_summary="Obfuscated PowerShell script block executed vssadmin deletion.",
                phase="EXECUTION",
            ))

        # ----------------------------------------------------------------------
        # INCIDENT 2: Distributed Password Spraying on VPN Gateway
        # ----------------------------------------------------------------------
        inc2 = Incident(
            incident_id="INC-2026-0002",
            title="Distributed Password Spraying Targeting Enterprise VPN Gateway",
            description="VPN authentication logs recorded over 12,000 failed logins originating from 340 distinct residential proxy IP addresses testing seasonal passwords.",
            incident_type=IncidentType.CREDENTIAL_ATTACK,
            severity=IncidentSeverity.HIGH,
            priority="P2",
            status=IncidentStatus.ERADICATION,
            phase=IncidentPhase.CONTAINMENT_ERADICATION_RECOVERY,
            classification=IncidentClassification.CONFIRMED_INCIDENT,
            lead_analyst="SOC Analyst Patel",
            playbook_id=playbooks_map.get("PB-CRED-STUFFING").id if playbooks_map.get("PB-CRED-STUFFING") else None,
            detected_at=now - timedelta(hours=8),
            contained_at=now - timedelta(hours=6),
            eradicated_at=now - timedelta(hours=3),
            summary="Attacker automated password spraying across 450 corporate accounts. Two accounts successfully authenticated but were challenged by MFA and quarantined.",
            impact_assessment="Two accounts experienced credential compromise, but MFA stopped session initiation. No internal network penetration occurred.",
            root_cause="Lack of adaptive rate-limiting on external VPN portal allowed distributed requests below single-IP lockout thresholds.",
            lessons_learned="Implement IP reputation scoring and CAPTCHA challenge at VPN login portal.",
            recommendations="Mandate FIDO2 hardware tokens and disable SMS/push fallback for remote access.",
            simulation_mode=True,
        )
        db.add(inc2)
        db.flush()

        db.add(ResponseAction(
            action_id="ACT-2026-0003",
            incident_id=inc2.id,
            category=ResponseActionCategory.CONTAINMENT,
            action_type=ResponseActionType.SIMULATE_ACCOUNT_RESTRICTION,
            target_type="USER",
            target_identifier="jdoe@company.local, asmith@company.local",
            status=ResponseActionStatus.EXECUTED,
            simulation_only=True,
            reason="Compromised credentials verified during password spray.",
            risk_assessment="Users temporarily unable to connect to VPN until identity re-verification.",
            expected_impact="Accounts disabled in Active Directory.",
            simulated_outcome="Accounts locked out; active tokens revoked.",
            executed_at=now - timedelta(hours=5),
        ))

        # ----------------------------------------------------------------------
        # INCIDENT 3: Suspected DNS Tunneling Exfiltration
        # ----------------------------------------------------------------------
        inc3 = Incident(
            incident_id="INC-2026-0003",
            title="Suspected DNS Tunneling Exfiltration from Engineering Workstation",
            description="Network monitoring detected high-volume DNS TXT queries directed toward subdomains of data-sync-cdn.xyz from workstation WS-ENG-12.",
            incident_type=IncidentType.DATA_EXFILTRATION_PATTERN,
            severity=IncidentSeverity.HIGH,
            priority="P2",
            status=IncidentStatus.INVESTIGATING,
            phase=IncidentPhase.DETECTION_ANALYSIS,
            classification=IncidentClassification.SUSPICIOUS,
            lead_analyst="SOC Analyst Martinez",
            playbook_id=playbooks_map.get("PB-DATA-EXFIL").id if playbooks_map.get("PB-DATA-EXFIL") else None,
            detected_at=now - timedelta(hours=5),
            summary="Unusual volume of high-entropy DNS queries observed. Analyst investigating whether proprietary firmware source code was encoded.",
            impact_assessment="Under active investigation. Tunneling rate estimated at 45 KB/s over 30 minutes.",
            simulation_mode=True,
        )
        db.add(inc3)
        db.flush()

        # ----------------------------------------------------------------------
        # INCIDENT 4: Living-off-the-Land via Obfuscated PowerShell
        # ----------------------------------------------------------------------
        inc4 = Incident(
            incident_id="INC-2026-0004",
            title="Living-off-the-Land Execution via Obfuscated PowerShell",
            description="EDR alert flagged Microsoft Word launching powershell.exe with Base64 encoded payload and WebClient download cradles.",
            incident_type=IncidentType.SUSPICIOUS_PROCESS,
            severity=IncidentSeverity.MEDIUM,
            priority="P3",
            status=IncidentStatus.TRIAGED,
            phase=IncidentPhase.DETECTION_ANALYSIS,
            classification=IncidentClassification.SUSPICIOUS,
            lead_analyst="Junior SOC Analyst Lee",
            playbook_id=playbooks_map.get("PB-MALICIOUS-PROC").id if playbooks_map.get("PB-MALICIOUS-PROC") else None,
            detected_at=now - timedelta(hours=2),
            summary="Malicious Word document opened from external email attachment spawned PowerShell dropper attempting to reach staging URL.",
            simulation_mode=True,
        )
        db.add(inc4)
        db.flush()

        # ----------------------------------------------------------------------
        # INCIDENT 5: Internal Lateral Movement via Service Account
        # ----------------------------------------------------------------------
        inc5 = Incident(
            incident_id="INC-2026-0005",
            title="Internal Lateral Movement via Compromised Service Account",
            description="Kerberoasting attack detected followed by SMB session spikes across engineering file shares from an unmanaged laptop.",
            incident_type=IncidentType.ENDPOINT_COMPROMISE,
            severity=IncidentSeverity.HIGH,
            priority="P2",
            status=IncidentStatus.RECOVERY,
            phase=IncidentPhase.CONTAINMENT_ERADICATION_RECOVERY,
            classification=IncidentClassification.CONFIRMED_INCIDENT,
            lead_analyst="Senior SOC Analyst Chen",
            playbook_id=playbooks_map.get("PB-LATERAL-MOV").id if playbooks_map.get("PB-LATERAL-MOV") else None,
            detected_at=now - timedelta(days=1),
            contained_at=now - timedelta(hours=18),
            eradicated_at=now - timedelta(hours=10),
            recovered_at=now - timedelta(hours=2),
            summary="Attacker cracked weak RC4 Kerberos ticket for svc_sql, accessed engineering file shares via SMB. Shares audited, credentials changed, service restored.",
            simulation_mode=True,
        )
        db.add(inc5)
        db.flush()

        # ----------------------------------------------------------------------
        # INCIDENT 6: Authorized Vulnerability Scanner False Positive Alert
        # ----------------------------------------------------------------------
        inc6 = Incident(
            incident_id="INC-2026-0006",
            title="Routine Vulnerability Scanner Port Sweep Alert",
            description="IDS triggered critical port sweep and web vulnerability scan alerts from internal IP 10.0.1.50 against the DMZ servers.",
            incident_type=IncidentType.POLICY_VIOLATION,
            severity=IncidentSeverity.LOW,
            priority="P4",
            status=IncidentStatus.FALSE_POSITIVE,
            phase=IncidentPhase.POST_INCIDENT_ACTIVITY,
            classification=IncidentClassification.FALSE_POSITIVE,
            lead_analyst="SOC Analyst Patel",
            detected_at=now - timedelta(days=2),
            closed_at=now - timedelta(days=2, minutes=-45),
            summary="Triage confirmed 10.0.1.50 is the authorized internal Nessus vulnerability scanner running its scheduled weekly vulnerability assessment.",
            impact_assessment="No security impact. Legitimate scanner traffic matching vulnerability scan signature.",
            lessons_learned="Ensure scanner IP is whitelisted in IDS rules or correlated with scheduled change calendar.",
            simulation_mode=True,
        )
        db.add(inc6)
        db.flush()

        # Add notes to INC-6 demonstrating analyst triage thinking
        db.add(IncidentNote(
            incident_id=inc6.id,
            note="Verified scanning origin IP 10.0.1.50 against IT Asset Management database: asset 'SEC-SCANNER-01'.",
            created_at=now - timedelta(days=2, minutes=-20),
        ))
        db.add(IncidentNote(
            incident_id=inc6.id,
            note="Cross-referenced with change request CR-2026-0812 (Weekly DMZ Assessment). Classified as FALSE_POSITIVE and closed.",
            created_at=now - timedelta(days=2, minutes=-45),
        ))

        db.commit()
        return 6
