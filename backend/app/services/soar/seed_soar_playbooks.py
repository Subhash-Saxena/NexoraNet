"""Seed 8 Comprehensive Educational SOAR Playbooks for Step 18.

Deterministic, safe, educational playbooks covering Phishing, Endpoint Malware,
Credential Stuffing, Ransomware, DNS Tunneling, Privilege Escalation,
Threat Intel Sweep, and Web Shell Eradication.
Strictly non-destructive simulation.
"""

import json
from typing import Any

from app.models.enums import (
    AutomationActionType,
    PlaybookRiskLevel,
    PlaybookStatus,
    PlaybookTriggerType,
)
from app.models.soar import AutomationPlaybook, AutomationStep
from sqlalchemy.orm import Session


def seed_soar_playbooks(db: Session) -> list[AutomationPlaybook]:
    """Seed or update the 8 official educational SOAR playbooks."""

    playbook_definitions: list[dict[str, Any]] = [
        # 1. Phishing Triage & URL Sandboxing
        {
            "playbook_id": "SOAR-PB-001",
            "name": "Phishing Triage & URL Sandboxing",
            "description": "Automatically extracts suspicious URLs from user reports, performs threat intelligence reputation queries, simulates headless URL sandboxing, and creates an incident case if classified malicious.",
            "category": "PHISHING",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.ALERT_CREATED,
            "trigger_filter": {"category": "PHISHING", "severity": "HIGH"},
            "risk_level": PlaybookRiskLevel.LOW,
            "requires_approval": False,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Enrich Suspicious Indicators",
                    "description": "Extract domain and IP IOCs from alert metadata and query synthetic threat feeds.",
                    "action_type": AutomationActionType.ENRICH_IOC,
                    "parameters": {"indicator_value": "{{ioc_value}}", "indicator_type": "URL"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 2,
                    "name": "Threat Intel Reputation Query",
                    "description": "Collect correlating high-fidelity indicators and reputation scores.",
                    "action_type": AutomationActionType.COLLECT_RELATED_IOCS,
                    "parameters": {"query": "{{ioc_value}}", "min_confidence": 60},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 3,
                    "name": "Simulated Gateway Domain Block",
                    "description": "Execute simulated perimeter sinkhole and URL isolation in training environment.",
                    "action_type": AutomationActionType.SIMULATE_IOC_BLOCK,
                    "parameters": {"indicator": "{{ioc_value}}", "depth": 2},
                    "condition": {"operator": "greater_than_or_equal", "field": "threat_score", "value": 40},
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 4,
                    "name": "Escalate to Incident Case",
                    "description": "Automatically open a high-priority phishing investigation case in NexoraNet SOC.",
                    "action_type": AutomationActionType.CREATE_CASE,
                    "parameters": {
                        "title": "Phishing Attack: Malicious Credential Harvester",
                        "severity": "HIGH",
                        "summary": "Automated triage confirmed weaponized credential harvesting infrastructure.",
                    },
                    "condition": {"operator": "greater_than_or_equal", "field": "threat_score", "value": 60},
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 5,
                    "name": "Dispatch Analyst Notification",
                    "description": "Send simulated SOC notification to analysts on duty.",
                    "action_type": AutomationActionType.SIMULATE_ANALYST_NOTIFICATION,
                    "parameters": {
                        "recipient": "soc-tier1-queue",
                        "channel": "SLACK",
                        "message": "Playbook SOAR-PB-001 completed triage. Case generated for malicious phishing campaign.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 2. Malicious Host Isolation & Forensic Capture
        {
            "playbook_id": "SOAR-PB-002",
            "name": "Malicious Host Isolation & Forensic Capture",
            "description": "Collects endpoint telemetry upon confirmed malware detection, mandates human analyst authorization, isolates the host from the network, and gathers forensic evidence.",
            "category": "ENDPOINT_MALWARE",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.ALERT_CREATED,
            "trigger_filter": {"category": "MALWARE", "severity": "HIGH"},
            "risk_level": PlaybookRiskLevel.HIGH,
            "requires_approval": True,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Enrich Endpoint Host Information",
                    "description": "Retrieve host details, OS version, logged-in users, and active IP interfaces.",
                    "action_type": AutomationActionType.ENRICH_HOST,
                    "parameters": {"hostname": "{{hostname}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Collect Endpoint Telemetry & Events",
                    "description": "Inspect active process tree and outbound connections to identify persistence.",
                    "action_type": AutomationActionType.COLLECT_RELATED_ENDPOINT_EVENTS,
                    "parameters": {"hostname": "{{hostname}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 3,
                    "name": "Simulated Network Host Isolation",
                    "description": "Cut endpoint network connectivity via simulated EDR firewall rule (analyst approval gate).",
                    "action_type": AutomationActionType.SIMULATE_HOST_ISOLATION,
                    "parameters": {"target_identifier": "{{hostname}}", "reason": "Confirmed Trojan infection"},
                    "condition": None,
                    "requires_approval": True,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 4,
                    "name": "Capture Forensic Evidence Package",
                    "description": "Package simulated memory capture and event log package for incident analysis.",
                    "action_type": AutomationActionType.ADD_EVIDENCE,
                    "parameters": {"title": "Host Memory & Process Snapshot", "evidence_type": "ENDPOINT"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 5,
                    "name": "Document Forensic Action Note",
                    "description": "Record containment state and attach forensic artifact notes to active case.",
                    "action_type": AutomationActionType.ADD_ANALYST_NOTE,
                    "parameters": {"note": "Host isolated and volatile triage artifacts preserved."},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 3. Credential Stuffing & Impossible Travel Response
        {
            "playbook_id": "SOAR-PB-003",
            "name": "Credential Stuffing & Impossible Travel Response",
            "description": "Detects anomalous authentication from distant geographic regions within short timeframes, blocks attacking proxy IP, invalidates active user sessions, and forces password reset.",
            "category": "IDENTITY_SECURITY",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.CORRELATION_MATCH,
            "trigger_filter": {"rule_name": "Impossible Travel Detected"},
            "risk_level": PlaybookRiskLevel.MEDIUM,
            "requires_approval": False,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Correlate Authentication SIEM Logs",
                    "description": "Search SIEM authentication logs for rapid geo-location shifts and failed passwords.",
                    "action_type": AutomationActionType.COLLECT_RELATED_SIEM_EVENTS,
                    "parameters": {"query": "event_type:authentication AND user:{{username}}", "time_window_minutes": 60},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Enrich Attacking IP via Threat Intel",
                    "description": "Check if source IP is an anonymizing VPN, Tor exit node, or commercial proxy.",
                    "action_type": AutomationActionType.ENRICH_IOC,
                    "parameters": {"ioc_value": "{{src_ip}}", "indicator_type": "IP"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 3,
                    "name": "Block Source IP on Perimeter Firewall",
                    "description": "Simulate adding IP to edge perimeter blocklist.",
                    "action_type": AutomationActionType.SIMULATE_NETWORK_BLOCK,
                    "parameters": {"ip_address": "{{src_ip}}", "duration_hours": 24},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 4,
                    "name": "Revoke Compromised Active User Sessions",
                    "description": "Invalidate OAuth tokens and active browser sessions for the targeted identity.",
                    "action_type": AutomationActionType.SIMULATE_SESSION_REVOCATION,
                    "parameters": {"username": "{{username}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 5,
                    "name": "Force Self-Service Password Reset",
                    "description": "Flag account for mandatory password update upon next MFA authentication.",
                    "action_type": AutomationActionType.SIMULATE_CREDENTIAL_RESET,
                    "parameters": {"username": "{{username}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 6,
                    "name": "Notify User and Security Team",
                    "description": "Dispatch out-of-band security advisory notice to the impacted employee.",
                    "action_type": AutomationActionType.SIMULATE_ANALYST_NOTIFICATION,
                    "parameters": {
                        "recipient": "{{username}}",
                        "channel": "EMAIL",
                        "message": "Suspicious login detected from foreign IP. Sessions revoked; password reset required.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 4. Ransomware Outbreak Auto-Containment
        {
            "playbook_id": "SOAR-PB-004",
            "name": "Ransomware Outbreak Auto-Containment",
            "description": "Emergency rapid-response workflow triggered upon detection of file entropy anomalies, mass file renames, or shadow copy deletion. Kills malicious process, isolates subnet hosts, and halts lateral spread.",
            "category": "RANSOMWARE",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.INCIDENT_ESCALATED,
            "trigger_filter": {"incident_type": "RANSOMWARE"},
            "risk_level": PlaybookRiskLevel.CRITICAL,
            "requires_approval": True,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Inspect Endpoint Threat State",
                    "description": "Identify parent process tree and file encryption rate on target host.",
                    "action_type": AutomationActionType.COLLECT_RELATED_ENDPOINT_EVENTS,
                    "parameters": {"hostname": "{{hostname}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Purge Malicious Persistence Artifacts",
                    "description": "Remove simulated persistence mechanisms and dropper scripts.",
                    "action_type": AutomationActionType.SIMULATE_REMOVE_PERSISTENCE,
                    "parameters": {"hostname": "{{hostname}}", "process_id": "{{pid}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 3,
                    "name": "Emergency Host Network Isolation",
                    "description": "Sever network interfaces to prevent SMB / PsExec lateral movement.",
                    "action_type": AutomationActionType.SIMULATE_HOST_ISOLATION,
                    "parameters": {"target_identifier": "{{hostname}}"},
                    "condition": None,
                    "requires_approval": True,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 4,
                    "name": "Fleetwide Hash Blacklist Deployment",
                    "description": "Push cryptographic SHA256 of ransomware binary to simulated global blocklist.",
                    "action_type": AutomationActionType.SIMULATE_IOC_BLOCK,
                    "parameters": {"indicator": "{{file_hash}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 5,
                    "name": "Escalate to Tier 3 CIRT Unit",
                    "description": "Trigger highest-priority P1 alert to Incident Commander and CIRT team.",
                    "action_type": AutomationActionType.SIMULATE_ESCALATION,
                    "parameters": {
                        "recipient": "incident-command-pager",
                        "channel": "PAGERDUTY",
                        "message": "P1 Ransomware Outbreak contained on endpoint. CIRT activation initiated.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 5. DNS Tunneling & C2 Traffic Disruption
        {
            "playbook_id": "SOAR-PB-005",
            "name": "DNS Tunneling & C2 Traffic Disruption",
            "description": "Investigates high-volume anomalous DNS requests exhibiting tunneling characteristics (Base64 subdomains, high entropy). Redirects queries to educational sinkhole and blocks remote resolver.",
            "category": "NETWORK_ATTACK",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.ALERT_CREATED,
            "trigger_filter": {"rule_name": "DNS Tunneling Detected"},
            "risk_level": PlaybookRiskLevel.MEDIUM,
            "requires_approval": False,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Analyze DNS Indicators & Entropy",
                    "description": "Enrich domain name IOCs and calculate Shannon entropy of domain label chunks.",
                    "action_type": AutomationActionType.ENRICH_IOC,
                    "parameters": {"ioc_value": "{{domain_name}}", "indicator_type": "DOMAIN"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Simulated DNS Sinkhole Redirection",
                    "description": "Modify simulated recursive resolver response to point attacker domain to sinkhole.",
                    "action_type": AutomationActionType.SIMULATE_IOC_BLOCK,
                    "parameters": {"indicator": "{{domain_name}}", "sinkhole_ip": "10.254.254.254"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 3,
                    "name": "Block Rogue Nameserver IP",
                    "description": "Drop outbound UDP port 53 packets to rogue authoritative nameserver.",
                    "action_type": AutomationActionType.SIMULATE_NETWORK_BLOCK,
                    "parameters": {"ip_address": "{{dst_ip}}", "duration_hours": 72},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 4,
                    "name": "Preserve Tunneling Evidence Logs",
                    "description": "Attach correlated PCAP stream and DNS query logs to active case evidence.",
                    "action_type": AutomationActionType.ADD_EVIDENCE,
                    "parameters": {"title": "Correlated DNS Tunneling Logs", "evidence_type": "DNS_EVENT"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 5,
                    "name": "Notify Network Operations",
                    "description": "Inform NOC and SOC analysts regarding sinkholed C2 domain.",
                    "action_type": AutomationActionType.SIMULATE_ANALYST_NOTIFICATION,
                    "parameters": {
                        "recipient": "netops-channel",
                        "channel": "SLACK",
                        "message": "DNS Tunneling C2 successfully neutralized and sinkholed.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 6. Privileged Account Escalation Investigation
        {
            "playbook_id": "SOAR-PB-006",
            "name": "Privileged Account Escalation Investigation",
            "description": "Correlates unexpected privilege escalation events (Windows Event 4672, Linux sudoers modifications) with user directory role, temporarily suspends account, and documents investigation.",
            "category": "IDENTITY_SECURITY",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.CORRELATION_MATCH,
            "trigger_filter": {"rule_name": "Unauthorized Privilege Escalation"},
            "risk_level": PlaybookRiskLevel.MEDIUM,
            "requires_approval": False,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Correlate SIEM Security Event Logs",
                    "description": "Retrieve audit logs for user account and system security group alterations.",
                    "action_type": AutomationActionType.COLLECT_RELATED_SIEM_EVENTS,
                    "parameters": {"query": "event_id:4672 OR event_id:4728", "time_window_minutes": 30},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Audit User Account Context",
                    "description": "Query endpoint telemetry to inspect command-line arguments used during escalation.",
                    "action_type": AutomationActionType.ENRICH_USER,
                    "parameters": {"username": "{{username}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 3,
                    "name": "Simulated Account Access Restriction",
                    "description": "Lock account credentials in directory service to prevent unauthorized administration.",
                    "action_type": AutomationActionType.SIMULATE_ACCOUNT_RESTRICTION,
                    "parameters": {"username": "{{username}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 4,
                    "name": "Document Findings in Incident Log",
                    "description": "Append investigation notes and audit trace to case journal.",
                    "action_type": AutomationActionType.ADD_ANALYST_NOTE,
                    "parameters": {
                        "note": "Automated containment: Account suspended following unapproved sudo/Domain Admin escalation.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 7. Automated IOC Threat Intel Sweep
        {
            "playbook_id": "SOAR-PB-007",
            "name": "Automated IOC Threat Intel Sweep",
            "description": "Periodically ingests fresh high-confidence threat feed indicators and executes an automated historical sweep across SIEM logs and endpoint telemetry for proactive threat hunting.",
            "category": "THREAT_INTEL",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.SCHEDULED_TIMER,
            "trigger_filter": {"schedule": "0 2 * * *"},
            "risk_level": PlaybookRiskLevel.LOW,
            "requires_approval": False,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Fetch Latest Threat Intelligence Feed",
                    "description": "Query threat intelligence database for indicators published recently.",
                    "action_type": AutomationActionType.COLLECT_RELATED_IOCS,
                    "parameters": {"min_confidence": 75, "days_active": 1},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Historical SIEM Log Sweep",
                    "description": "Search historical proxy, firewall, and DNS logs for indicator matches.",
                    "action_type": AutomationActionType.COLLECT_RELATED_SIEM_EVENTS,
                    "parameters": {"query": "indicator_sweep", "time_window_minutes": 43200},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 3,
                    "name": "Endpoint Telemetry Sweep",
                    "description": "Compare ingested file hashes against endpoint execution history.",
                    "action_type": AutomationActionType.COLLECT_RELATED_ENDPOINT_EVENTS,
                    "parameters": {"hostname": "all-endpoints"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 4,
                    "name": "Build Multi-Source Timeline",
                    "description": "Flag correlated events for senior threat hunter review.",
                    "action_type": AutomationActionType.BUILD_TIMELINE,
                    "parameters": {"timeline_name": "Nightly Threat Intel Sweep Matches"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 5,
                    "name": "Publish Sweep Summary Report",
                    "description": "Distribute automated intelligence digest to threat hunting team.",
                    "action_type": AutomationActionType.SIMULATE_ANALYST_NOTIFICATION,
                    "parameters": {
                        "recipient": "threat-hunting-team",
                        "channel": "EMAIL",
                        "message": "Nightly IOC threat intel sweep completed. 0 active compromises detected.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },

        # 8. Vulnerability Exploit & Web Shell Eradication
        {
            "playbook_id": "SOAR-PB-008",
            "name": "Vulnerability Exploit & Web Shell Eradication",
            "description": "Responds to web application file upload exploits and suspected web shell installations. Quarantines dropper script, blocks attacker source IP via virtual patch, and initializes containment case.",
            "category": "WEB_APPLICATION",
            "version": "1.0",
            "trigger_type": PlaybookTriggerType.ALERT_CREATED,
            "trigger_filter": {"category": "WEB_EXPLOIT", "severity": "HIGH"},
            "risk_level": PlaybookRiskLevel.HIGH,
            "requires_approval": False,
            "steps": [
                {
                    "step_order": 1,
                    "name": "Correlate Web Server Access Logs",
                    "description": "Identify suspicious HTTP POST requests returning status 200 with shell commands.",
                    "action_type": AutomationActionType.COLLECT_RELATED_SIEM_EVENTS,
                    "parameters": {"query": "method:POST AND uri:*.php", "time_window_minutes": 60},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 2,
                    "name": "Enrich Web Application Alert Context",
                    "description": "Extract server virtual host, document root path, and caller identity.",
                    "action_type": AutomationActionType.ENRICH_ALERT,
                    "parameters": {"alert_id": "{{alert_id}}"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 3,
                    "name": "Quarantine Dropped Web Shell File",
                    "description": "Move suspicious .php/.jsp file to simulated secure quarantine vault.",
                    "action_type": AutomationActionType.SIMULATE_REMOVE_INDICATOR,
                    "parameters": {"hostname": "{{hostname}}", "file_path": "/var/www/html/uploads/c99.php"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 4,
                    "name": "Block Attacker IP on Simulated WAF",
                    "description": "Deploy instantaneous Layer 7 rate-limit and deny rule for remote IP address.",
                    "action_type": AutomationActionType.SIMULATE_NETWORK_BLOCK,
                    "parameters": {"ip_address": "{{src_ip}}", "duration_hours": 48},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
                {
                    "step_order": 5,
                    "name": "Open Web Compromise IR Case",
                    "description": "Open case for root-cause application vulnerability analysis and patching.",
                    "action_type": AutomationActionType.CREATE_CASE,
                    "parameters": {
                        "title": "Web Shell Compromise - Insecure File Upload",
                        "severity": "HIGH",
                        "summary": "Dropper quarantined and attacker IP blocked. Web code review pending.",
                    },
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "STOP",
                },
                {
                    "step_order": 6,
                    "name": "Record Chronological Remediation Milestone",
                    "description": "Document successful immediate eradication of web shell artifact.",
                    "action_type": AutomationActionType.ADD_TIMELINE_EVENT,
                    "parameters": {"title": "Web shell eradicated & IP blocked", "category": "ERADICATION"},
                    "condition": None,
                    "requires_approval": False,
                    "on_failure": "CONTINUE",
                },
            ],
        },
    ]

    seeded: list[AutomationPlaybook] = []

    for pb_data in playbook_definitions:
        existing = (
            db.query(AutomationPlaybook)
            .filter(AutomationPlaybook.playbook_id == pb_data["playbook_id"])
            .first()
        )
        if existing:
            # Update basic attributes
            existing.name = pb_data["name"]
            existing.description = pb_data["description"]
            existing.category = pb_data["category"]
            existing.version = pb_data["version"]
            existing.trigger_type = pb_data["trigger_type"]
            existing.trigger_filter_json = json.dumps(pb_data.get("trigger_filter"))
            existing.risk_level = pb_data["risk_level"]
            existing.requires_approval = pb_data["requires_approval"]
            existing.is_system = True
            existing.simulation_only = True
            playbook_obj = existing
        else:
            playbook_obj = AutomationPlaybook(
                playbook_id=pb_data["playbook_id"],
                name=pb_data["name"],
                description=pb_data["description"],
                category=pb_data["category"],
                version=pb_data["version"],
                status=PlaybookStatus.ENABLED,
                trigger_type=pb_data["trigger_type"],
                trigger_filter_json=json.dumps(pb_data.get("trigger_filter")),
                risk_level=pb_data["risk_level"],
                requires_approval=pb_data["requires_approval"],
                is_system=True,
                simulation_only=True,
                created_by="system",
            )
            db.add(playbook_obj)
            db.flush()

        # Sync steps: clear existing steps to avoid duplicates if re-seeding
        db.query(AutomationStep).filter(AutomationStep.playbook_id == playbook_obj.id).delete()
        for step_data in pb_data["steps"]:
            step = AutomationStep(
                playbook_id=playbook_obj.id,
                step_order=step_data["step_order"],
                name=step_data["name"],
                description=step_data["description"],
                action_type=str(step_data["action_type"]),
                parameters_json=json.dumps(step_data.get("parameters", {})),
                condition_json=json.dumps(step_data["condition"]) if step_data.get("condition") else None,
                requires_approval=step_data.get("requires_approval", False),
                timeout_seconds=30,
                enabled=True,
                on_failure=step_data.get("on_failure", "STOP"),
                retry_count=1,
            )
            db.add(step)

        seeded.append(playbook_obj)

    db.commit()
    return seeded
