"""Seed script for Step 15 SIEM & Security Log Analysis Engine.

Populates:
1. 7 Standard Educational Log Sources across Windows, Linux, Firewall, DNS, and Web
2. 3 Comprehensive Synthetic Security Log Datasets (Beginner, Intermediate, Advanced)
3. 9 Default Correlation Rules and Initial Correlated Alerts
4. 8 Structured SIEM Hands-On Lab Scenarios
5. Exemplar Saved Searches and Search History
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.enums import (
    RawLogFormat,
    SecurityEventAction,
    SecurityEventCategory,
    SecurityEventSeverity,
)
from app.models.siem import (
    CorrelationAlert,
    LogCorrelationRule,
    LogSource,
    RawLogEvent,
    SavedSearch,
    SecurityEvent,
    SecurityLogDataset,
    SIEMLabScenario,
)
from app.models.user import User
from app.services.siem.correlation_engine import SiemCorrelationEngine
from app.services.siem.dataset_service import SiemDatasetService
from sqlalchemy import select


def seed_siem():
    """Seed comprehensive SIEM simulation environment."""
    db = SessionLocal()
    try:
        print("[+] Seeding Step 15 SIEM Environment...")

        # 1. Base seeding via SiemDatasetService
        seed_result = SiemDatasetService.seed_all_siem_data(db)
        print(f"[+] Initial seeding completed: {seed_result}")

        # 2. Enrich datasets with background telemetry
        auth_ds = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.stable_id == "DS-AUTH-BEG-01")
        ).scalar_one()

        net_ds = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.stable_id == "DS-NET-INT-01")
        ).scalar_one()

        adv_ds = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.stable_id == "DS-SOC-ADV-01")
        ).scalar_one()

        win_src = db.execute(
            select(LogSource).where(LogSource.stable_id == "SRC-WIN-SEC-01")
        ).scalar_one()
        net_src = db.execute(
            select(LogSource).where(LogSource.stable_id == "SRC-NET-FW-01")
        ).scalar_one()
        dns_src = db.execute(
            select(LogSource).where(LogSource.stable_id == "SRC-NET-DNS-01")
        ).scalar_one()
        web_src = db.execute(
            select(LogSource).where(LogSource.stable_id == "SRC-WEB-NGX-01")
        ).scalar_one()

        # Add 120 benign authentication background events
        print("[+] Generating benign baseline events for DS-AUTH-BEG-01...")
        curr_seq = auth_ds.event_count or 0
        base_t = auth_ds.start_time or datetime(2026, 9, 30, 8, 0, 0, tzinfo=timezone.utc)
        users = ["john.doe", "sarah.connor", "michael.scott", "pam.beesly", "jim.halpert", "dwight.schrute", "stanley.hudson", "angela.martin"]

        for i in range(120):
            curr_seq += 1
            u = users[i % len(users)]
            t = base_t + timedelta(minutes=random.randint(5, 220), seconds=random.randint(0, 59))
            is_fail = (i % 15 == 0)

            raw = RawLogEvent(
                source_id=win_src.id,
                dataset_id=auth_ds.id,
                timestamp=t,
                raw_message=f"<Event><System><EventID>{'4625' if is_fail else '4624'}</EventID><Computer>DC01.corp.test</Computer></System><EventData><Data Name='TargetUserName'>{u}</Data></EventData></Event>",
                format=RawLogFormat.WINDOWS_EVENT_XML.value,
                sequence_number=curr_seq,
            )
            db.add(raw)
            db.flush()

            sec = SecurityEvent(
                event_id=f"EVT-SIEM-{random.randint(100000, 999999)}",
                timestamp=t,
                event_type="windows_logon_failure" if is_fail else "windows_logon_success",
                event_category=SecurityEventCategory.AUTHENTICATION.value,
                source_type=win_src.source_type,
                host="DC01.corp.test",
                username=u,
                source_ip=f"192.0.2.{100 + (i % 50)}",
                destination_ip="192.0.2.10",
                destination_port=88,
                protocol="Kerberos",
                action=SecurityEventAction.LOGIN_FAILURE.value if is_fail else SecurityEventAction.LOGIN.value,
                status="FAILURE" if is_fail else "SUCCESS",
                severity=SecurityEventSeverity.LOW.value if is_fail else SecurityEventSeverity.INFO.value,
                result="FAILURE" if is_fail else "SUCCESS",
                message=f"Account {'failed to logon' if is_fail else 'successfully logged on'}: {u}",
                raw_event_id=raw.id,
                dataset_id=auth_ds.id,
                source_id=win_src.id,
            )
            db.add(sec)

        auth_ds.event_count = curr_seq
        db.commit()

        # Add 200 background network events for DS-NET-INT-01
        print("[+] Generating network traffic for DS-NET-INT-01...")
        curr_seq = net_ds.event_count or 0
        base_t = net_ds.start_time or datetime(2026, 9, 30, 10, 0, 0, tzinfo=timezone.utc)
        domains = ["api.nexoranet.test", "update.microsoft.test", "cdn.cloudflare.test", "github.test", "internal-portal.test"]

        for i in range(200):
            curr_seq += 1
            t = base_t + timedelta(minutes=random.randint(2, 170), seconds=random.randint(0, 59))
            is_dns = (i % 2 == 0)

            if is_dns:
                d = domains[i % len(domains)]
                raw = RawLogEvent(
                    source_id=dns_src.id,
                    dataset_id=net_ds.id,
                    timestamp=t,
                    raw_message=f"Sep 30 10:30:00 dns-primary-01 named[982]: query: {d} IN A + (192.0.2.{50 + (i % 40)})",
                    format=RawLogFormat.SYSLOG.value,
                    sequence_number=curr_seq,
                )
                db.add(raw)
                db.flush()

                sec = SecurityEvent(
                    event_id=f"EVT-SIEM-{random.randint(100000, 999999)}",
                    timestamp=t,
                    event_type="dns_query_record",
                    event_category=SecurityEventCategory.DNS.value,
                    source_type=dns_src.source_type,
                    host="dns-primary-01.corp.test",
                    source_ip=f"192.0.2.{50 + (i % 40)}",
                    destination_ip="192.0.2.2",
                    destination_port=53,
                    protocol="DNS",
                    action=SecurityEventAction.DNS_QUERY.value,
                    domain=d,
                    status="NOERROR",
                    severity=SecurityEventSeverity.INFO.value,
                    message=f"Standard DNS query resolved: {d}",
                    raw_event_id=raw.id,
                    dataset_id=net_ds.id,
                    source_id=dns_src.id,
                )
                db.add(sec)
            else:
                raw = RawLogEvent(
                    source_id=net_src.id,
                    dataset_id=net_ds.id,
                    timestamp=t,
                    raw_message=f"Sep 30 10:30:00 fw-edge-01 kernel: IPTABLES ALLOW: SRC=192.0.2.{50 + (i % 40)} DST=198.51.100.{10 + (i % 10)} PROTO=TCP SPT={40000 + i} DPT=443",
                    format=RawLogFormat.SYSLOG.value,
                    sequence_number=curr_seq,
                )
                db.add(raw)
                db.flush()

                sec = SecurityEvent(
                    event_id=f"EVT-SIEM-{random.randint(100000, 999999)}",
                    timestamp=t,
                    event_type="firewall_flow_allow",
                    event_category=SecurityEventCategory.FIREWALL.value,
                    source_type=net_src.source_type,
                    host="fw-edge-01.corp.test",
                    source_ip=f"192.0.2.{50 + (i % 40)}",
                    source_port=40000 + i,
                    destination_ip=f"198.51.100.{10 + (i % 10)}",
                    destination_port=443,
                    protocol="TCP",
                    action=SecurityEventAction.CONNECTION.value,
                    status="ALLOWED",
                    severity=SecurityEventSeverity.INFO.value,
                    message="Outbound HTTPS permitted through edge firewall.",
                    raw_event_id=raw.id,
                    dataset_id=net_ds.id,
                    source_id=net_src.id,
                )
                db.add(sec)

        net_ds.event_count = curr_seq
        db.commit()

        # Add 300 background enterprise events for DS-SOC-ADV-01
        print("[+] Generating enterprise events for DS-SOC-ADV-01...")
        curr_seq = adv_ds.event_count or 0
        base_t = adv_ds.start_time or datetime(2026, 9, 30, 13, 0, 0, tzinfo=timezone.utc)

        for i in range(300):
            curr_seq += 1
            t = base_t + timedelta(minutes=random.randint(1, 280), seconds=random.randint(0, 59))
            u = users[i % len(users)]
            host_name = f"WS-{u.split('.')[0].upper()}-01.corp.test"

            raw = RawLogEvent(
                source_id=web_src.id,
                dataset_id=adv_ds.id,
                timestamp=t,
                raw_message=f'{{"timestamp": "{t.isoformat()}", "host": "{host_name}", "user": "{u}", "url": "/app/dashboard", "status": 200}}',
                format=RawLogFormat.JSON.value,
                sequence_number=curr_seq,
            )
            db.add(raw)
            db.flush()

            sec = SecurityEvent(
                event_id=f"EVT-SIEM-{random.randint(100000, 999999)}",
                timestamp=t,
                event_type="web_access_routine",
                event_category=SecurityEventCategory.WEB.value,
                source_type=web_src.source_type,
                host=host_name,
                username=u,
                source_ip=f"192.0.2.{10 + (i % 80)}",
                destination_ip="192.0.2.80",
                destination_port=443,
                protocol="HTTP",
                action=SecurityEventAction.CONNECTION.value,
                status="SUCCESS",
                severity=SecurityEventSeverity.INFO.value,
                message=f"User {u} accessed routine internal enterprise dashboard.",
                raw_event_id=raw.id,
                dataset_id=adv_ds.id,
                source_id=web_src.id,
            )
            db.add(sec)

        adv_ds.event_count = curr_seq
        db.commit()

        # 3. Seed Saved Searches
        user = db.execute(select(User).limit(1)).scalar_one_or_none()
        owner_id = user.id if user else 1

        saved_queries = [
            {
                "name": "Investigate Brute Force Attacks",
                "description": "Find repeated failed login attempts across Linux and Windows authentication logs.",
                "query": {"conditions": [{"field": "action", "operator": "=", "value": "LOGIN_FAILURE"}], "logical_op": "AND"},
            },
            {
                "name": "Firewall Blocked Port Sweeps",
                "description": "Isolate dropped external connections on perimeter firewalls.",
                "query": {"conditions": [{"field": "action", "operator": "=", "value": "CONNECTION_BLOCKED"}], "logical_op": "AND"},
            },
            {
                "name": "Covert DNS Queries (.test)",
                "description": "Detect possible DNS tunneling queries directed toward .test domains.",
                "query": {"conditions": [{"field": "domain", "operator": "CONTAINS", "value": "tunnel"}], "logical_op": "AND"},
            },
            {
                "name": "High Severity Security Events",
                "description": "Filter for critical and high severity alerts across all sources.",
                "query": {"conditions": [{"field": "severity", "operator": "IN", "value": "HIGH,CRITICAL"}], "logical_op": "AND"},
            },
        ]

        for sq in saved_queries:
            ex = db.execute(select(SavedSearch).where(SavedSearch.name == sq["name"])).first()
            if not ex:
                s = SavedSearch(
                    name=sq["name"],
                    description=sq["description"],
                    query_definition=json.dumps(sq["query"]),
                    owner_id=owner_id,
                    is_public=True,
                )
                db.add(s)
        db.commit()

        # 4. Re-run Correlation to capture all events
        print("[+] Running correlation engine across updated datasets...")
        SiemCorrelationEngine.run_correlation(db, auth_ds.id)
        SiemCorrelationEngine.run_correlation(db, net_ds.id)
        SiemCorrelationEngine.run_correlation(db, adv_ds.id)

        # Print summary
        total_sources = db.execute(select(LogSource)).scalars().all()
        total_datasets = db.execute(select(SecurityLogDataset)).scalars().all()
        total_events = db.execute(select(SecurityEvent)).scalars().all()
        total_rules = db.execute(select(LogCorrelationRule)).scalars().all()
        total_alerts = db.execute(select(CorrelationAlert)).scalars().all()
        total_labs = db.execute(select(SIEMLabScenario)).scalars().all()

        print("\n=======================================================")
        print("  STEP 15 SIEM SEEDING SUCCESSFUL")
        print("=======================================================")
        print(f"Log Sources:        {len(total_sources)}")
        print(f"Security Datasets:  {len(total_datasets)}")
        print(f"Security Events:    {len(total_events)}")
        print(f"Correlation Rules:  {len(total_rules)}")
        print(f"Correlation Alerts: {len(total_alerts)}")
        print(f"SIEM Labs:          {len(total_labs)}")
        print("=======================================================\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed_siem()
