"""Seed script for Step 14 Threat Hunting & Investigation Workspace.

Populates:
1. 9 Realistic Defensive Telemetry Datasets (PCAP, IDS alerts, IOC observations, simulator events)
2. Normalized telemetry events using safe RFC 5737 IPs and RFC 2606 .test domains
3. Automatic sync of existing platform artifacts into Combined Enterprise Dataset
4. Exemplar active Threat Hunt session with hypotheses, evidence, and notes
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
    HuntConfidence,
    HuntDatasetType,
    HuntDifficulty,
    HuntEventType,
    HuntEvidenceRelevance,
    HuntEvidenceType,
    HuntFindingType,
    HuntHypothesisStatus,
    HuntStatus,
)
from app.models.pcap import Capture
from app.models.threat_hunting import (
    HuntDataset,
    HuntEvent,
    ThreatHunt,
    ThreatHuntEvidence,
    ThreatHuntFinding,
    ThreatHuntHypothesis,
    ThreatHuntNote,
)
from app.models.user import User
from app.services.threat_hunting.dataset_service import HuntDatasetService
from sqlalchemy import select


def seed_threat_hunting():
    db = SessionLocal()
    try:
        print("[*] Starting Step 14 Threat Hunting Seeding...")

        # 1. Fetch or ensure a default analyst user exists
        user = db.scalar(select(User).order_by(User.id.asc()).limit(1))
        if not user:
            print("[!] No users found. Skipping user-bound hunt seeding.")
            user_id = 1
        else:
            user_id = user.id

        now = datetime.now(timezone.utc)

        # 2. Define Curated Datasets
        datasets_meta = [
            {
                "dataset_id": "DS-HUNT-DNS-TUNNEL",
                "name": "DNS Exfiltration & High-Entropy Query Dataset",
                "description": "500+ normalized DNS queries capturing normal workstation traffic mixed with base64-encoded TXT tunneling to corp-sync.test.",
                "dataset_type": HuntDatasetType.PCAP.value,
                "source": "PCAP Replay / Offline Ingestion",
            },
            {
                "dataset_id": "DS-HUNT-C2-BEACON",
                "name": "Periodic HTTPS C2 Beaconing Telemetry",
                "description": "Outbound TLS flow events demonstrating 60s jittered polling toward external server cdn-telemetry-cache.test.",
                "dataset_type": HuntDatasetType.COMBINED.value,
                "source": "Network Flow & IDS Stream",
            },
            {
                "dataset_id": "DS-HUNT-SMB-LATERAL",
                "name": "Internal Subnet SMB & Remote Execution Telemetry",
                "description": "Workstation-to-workstation administrative share connections, PsExec service writes, and named pipe activity on port 445.",
                "dataset_type": HuntDatasetType.DETECTION_EVENTS.value,
                "source": "Windows Event & Network Logs",
            },
            {
                "dataset_id": "DS-HUNT-DATA-EGRESS",
                "name": "Off-Hours High-Volume Encrypted Egress Logs",
                "description": "Large file transfers and TCP streams originating from internal database server 192.168.1.200 to external VPS 198.51.100.120.",
                "dataset_type": HuntDatasetType.SIMULATOR_EVENTS.value,
                "source": "Perimeter NetFlow Telemetry",
            },
            {
                "dataset_id": "DS-HUNT-PS-CRADLE",
                "name": "PowerShell Ingress Tool Transfer Logs",
                "description": "Unauthenticated HTTP GET requests with WindowsPowerShell user-agents fetching staged script payloads.",
                "dataset_type": HuntDatasetType.COMBINED.value,
                "source": "Web Proxy & Endpoint Sensors",
            },
            {
                "dataset_id": "DS-HUNT-RECON-SCAN",
                "name": "TCP SYN Reconnaissance Probe Events",
                "description": "High ratio of SYN probes with subsequent RST packets covering /24 subnet ports 22, 80, 445, and 3389.",
                "dataset_type": HuntDatasetType.SIMULATOR_EVENTS.value,
                "source": "IDS Sensor Alpha",
            },
            {
                "dataset_id": "DS-HUNT-PASSWORD-SPRAY",
                "name": "Authentication Spraying & Logon Audits",
                "description": "Low-and-slow authentication attempts across 20 distinct service and user accounts from 192.168.1.99.",
                "dataset_type": HuntDatasetType.SOC_ALERTS.value,
                "source": "Domain Controller Security Logs",
            },
            {
                "dataset_id": "DS-HUNT-SUPPLY-CHAIN",
                "name": "Trojanized Software Update & Sleeper C2 Logs",
                "description": "Valid vendor update download from update-service-cloud.test followed 24h later by sleeper callback to 203.0.113.195.",
                "dataset_type": HuntDatasetType.COMBINED.value,
                "source": "Multi-Source Sensor Telemetry",
            },
            {
                "dataset_id": "DS-HUNT-COMBINED-01",
                "name": "Enterprise Subnet Hybrid Telemetry (PCAP + Alerts + IOCs)",
                "description": "Complete cross-system repository synchronizing offline PCAP packets, Detection Engine alerts, and Threat Intelligence IOC observations.",
                "dataset_type": HuntDatasetType.COMBINED.value,
                "source": "Platform Aggregator",
            },
        ]

        dataset_objs = {}
        for d_info in datasets_meta:
            existing = db.scalar(select(HuntDataset).where(HuntDataset.dataset_id == d_info["dataset_id"]))
            if not existing:
                dataset = HuntDataset(
                    dataset_id=d_info["dataset_id"],
                    name=d_info["name"],
                    description=d_info["description"],
                    dataset_type=d_info["dataset_type"],
                    source=d_info["source"],
                    event_count=0,
                    status="READY",
                    time_start=now - timedelta(days=2),
                    time_end=now,
                )
                db.add(dataset)
                db.commit()
                db.refresh(dataset)
                dataset_objs[d_info["dataset_id"]] = dataset
                print(f"[+] Created Dataset: {dataset.dataset_id} - {dataset.name}")
            else:
                dataset_objs[d_info["dataset_id"]] = existing

        # 3. Populate Synthesized Telemetry Events for each specialized dataset
        print("[*] Populating synthetic telemetry events...")

        # 3a. DNS Tunneling Events
        ds_dns = dataset_objs["DS-HUNT-DNS-TUNNEL"]
        if ds_dns.event_count == 0:
            dns_events = []
            base_t = now - timedelta(hours=3)
            # Normal DNS baseline
            benign_domains = ["intra-sharepoint.test", "mail-service.test", "auth-portal.test", "ntp.test"]
            for i in range(25):
                t = base_t + timedelta(minutes=i * 5)
                dns_events.append(
                    HuntEvent(
                        event_id=f"EVT-DNS-{i+1:04d}",
                        dataset_id=ds_dns.id,
                        event_type=HuntEventType.DNS_QUERY.value,
                        timestamp=t,
                        source_ip=f"192.168.1.{random.randint(10, 50)}",
                        destination_ip="192.168.1.1",
                        source_port=random.randint(49152, 65535),
                        destination_port=53,
                        protocol="DNS",
                        domain=random.choice(benign_domains),
                        summary=f"Standard DNS query A {random.choice(benign_domains)}",
                        status="RESOLVED",
                    )
                )

            # Malicious Tunneling bursts from 192.168.1.105
            tunnel_subdomains = [
                "dGhpcy1pcy1hLXNlY3JldA.corp-sync.test",
                "ZXhmaWx0cmF0aW9uLXBhY2tldC0wMQ.corp-sync.test",
                "Y3JlZGVudGlhbC1kdW1wLXZhbHVl.corp-sync.test",
                "cGFzc3dvcmRzLXR4dC1jaHVuay0wMg.corp-sync.test",
                "a2V5bG9nZ2VyLWxvZ3MtYmxvYg.corp-sync.test",
                "c3lzdGVtLWluZm8taGFzaGVz.corp-sync.test",
                "ZGItaG9zdC1jb25maWctZGF0YQ.corp-sync.test",
            ]
            for j, sub in enumerate(tunnel_subdomains):
                t = base_t + timedelta(minutes=45 + j * 2)
                dns_events.append(
                    HuntEvent(
                        event_id=f"EVT-TUNNEL-{j+1:04d}",
                        dataset_id=ds_dns.id,
                        event_type=HuntEventType.DNS_QUERY.value,
                        timestamp=t,
                        source_ip="192.168.1.105",
                        destination_ip="198.51.100.53",
                        source_port=54000 + j,
                        destination_port=53,
                        protocol="DNS",
                        domain=sub,
                        severity="HIGH",
                        action="ALERT",
                        status="RESOLVED",
                        summary=f"High-entropy DNS query TXT {sub} to authoritative NS 198.51.100.53",
                        payload_preview=f"IN TXT {sub} -> response [CHUNK_ACK_{j}]",
                    )
                )
            db.add_all(dns_events)
            ds_dns.event_count = len(dns_events)
            db.commit()
            print(f"[+] Added {len(dns_events)} events to {ds_dns.dataset_id}")

        # 3b. C2 Beaconing Events
        ds_c2 = dataset_objs["DS-HUNT-C2-BEACON"]
        if ds_c2.event_count == 0:
            c2_events = []
            base_t = now - timedelta(hours=4)
            for k in range(30):
                jitter = random.randint(-3, 3)
                t = base_t + timedelta(seconds=k * 60 + jitter)
                c2_events.append(
                    HuntEvent(
                        event_id=f"EVT-C2-{k+1:04d}",
                        dataset_id=ds_c2.id,
                        event_type=HuntEventType.TLS_EVENT.value,
                        timestamp=t,
                        source_ip="192.168.1.142",
                        destination_ip="203.0.113.88",
                        source_port=51200 + (k % 10),
                        destination_port=443,
                        protocol="TLS",
                        domain="cdn-telemetry-cache.test",
                        severity="MEDIUM" if k < 25 else "CRITICAL",
                        action="POLL",
                        status="ESTABLISHED",
                        summary=f"TLS Session to cdn-telemetry-cache.test (interval ~60s delta, bytes={256 + (k%3)*64})",
                        payload_preview=f"TLS Client Hello SNI=cdn-telemetry-cache.test | Jitter={jitter}s",
                    )
                )
            db.add_all(c2_events)
            ds_c2.event_count = len(c2_events)
            db.commit()
            print(f"[+] Added {len(c2_events)} events to {ds_c2.dataset_id}")

        # 3c. SMB Lateral Movement Events
        ds_smb = dataset_objs["DS-HUNT-SMB-LATERAL"]
        if ds_smb.event_count == 0:
            smb_events = []
            base_t = now - timedelta(hours=5)
            target_hosts = ["192.168.1.120", "192.168.1.125", "192.168.1.130", "192.168.1.150"]
            for idx, th in enumerate(target_hosts):
                t = base_t + timedelta(minutes=idx * 15)
                smb_events.append(
                    HuntEvent(
                        event_id=f"EVT-SMB-{idx*2+1:04d}",
                        dataset_id=ds_smb.id,
                        event_type=HuntEventType.NETWORK_CONNECTION.value,
                        timestamp=t,
                        source_ip="192.168.1.75",
                        destination_ip=th,
                        source_port=49800 + idx,
                        destination_port=445,
                        protocol="SMB",
                        severity="HIGH",
                        action="CONNECT",
                        status="SUCCESS",
                        summary=f"SMB Tree Connect to \\\\{th}\\ADMIN$ via privileged account",
                        payload_preview=f"TreeConnectAndX: Share=\\\\{th}\\ADMIN$, Status=STATUS_SUCCESS",
                    )
                )
                smb_events.append(
                    HuntEvent(
                        event_id=f"EVT-SMB-{idx*2+2:04d}",
                        dataset_id=ds_smb.id,
                        event_type=HuntEventType.TCP_EVENT.value,
                        timestamp=t + timedelta(seconds=2),
                        source_ip="192.168.1.75",
                        destination_ip=th,
                        source_port=49800 + idx,
                        destination_port=445,
                        protocol="SMB",
                        severity="CRITICAL",
                        action="CREATE_SERVICE",
                        status="SUCCESS",
                        summary=f"Remote Service Creation: svcctl CreateServiceW 'PSEXESVC' on {th}",
                        payload_preview="RPC svcctl -> OpenSCManagerW, CreateServiceW(BinaryPath='C:\\Windows\\PSEXESVC.exe')",
                    )
                )
            db.add_all(smb_events)
            ds_smb.event_count = len(smb_events)
            db.commit()
            print(f"[+] Added {len(smb_events)} events to {ds_smb.dataset_id}")

        # 4. Sync platform artifacts into Combined Enterprise Dataset
        ds_comb = dataset_objs["DS-HUNT-COMBINED-01"]
        print("[*] Synchronizing existing platform data into Combined Dataset...")
        # Sync captures
        captures = list(db.scalars(select(Capture)).all())
        for cap in captures:
            n_pkts = HuntDatasetService.sync_from_pcap(db, cap.id, ds_comb.id)
            if n_pkts > 0:
                print(f"[+] Ingested {n_pkts} packets from Capture #{cap.id}")

        n_dets = HuntDatasetService.sync_from_detection_alerts(db, ds_comb.id)
        print(f"[+] Ingested {n_dets} detection alerts into Combined Dataset")

        n_iocs = HuntDatasetService.sync_from_threat_intel(db, ds_comb.id)
        print(f"[+] Ingested {n_iocs} IOC observations into Combined Dataset")

        # 5. Seed Exemplar Threat Hunt Campaign
        existing_hunt = db.scalar(select(ThreatHunt).where(ThreatHunt.hunt_id == "HUNT-2026-0001"))
        if not existing_hunt:
            hunt = ThreatHunt(
                hunt_id="HUNT-2026-0001",
                title="Hunt: DNS Exfiltration via Tunneling",
                description="Investigation into high-volume base64 encoded TXT records targeting corp-sync.test.",
                objective="Identify the compromised host, determine total exfiltrated data size, and recommend perimeter DNS controls.",
                status=HuntStatus.RUNNING.value,
                difficulty=HuntDifficulty.BEGINNER.value,
                dataset_id=ds_dns.id,
                user_id=user_id,
                scenario_slug="dns-exfiltration-tunneling",
                initial_pivot_type="DOMAIN",
                initial_pivot_value="corp-sync.test",
                query_history=json.dumps([
                    {"query": 'protocol == "DNS"', "executed_at": (now - timedelta(hours=1)).isoformat()},
                    {"query": 'domain contains "corp-sync.test"', "executed_at": (now - timedelta(minutes=45)).isoformat()},
                    {"query": 'source_ip == "192.168.1.105"', "executed_at": (now - timedelta(minutes=30)).isoformat()},
                ]),
                started_at=now - timedelta(hours=1),
            )
            db.add(hunt)
            db.commit()
            db.refresh(hunt)

            # Add sample hypotheses
            hyp1 = ThreatHuntHypothesis(
                hunt_id=hunt.id,
                title="Host 192.168.1.105 is actively exfiltrating data via DNS tunneling",
                description="Abnormal TXT queries with base64 subdomains directed to corp-sync.test represent covert transmission.",
                status=HuntHypothesisStatus.SUPPORTED.value,
                confidence=HuntConfidence.HIGH.value,
                analyst_reasoning="Confirmed 7 distinct base64 encoded subdomains sequentially chunked, pointing to authoritative NS 198.51.100.53.",
            )
            hyp2 = ThreatHuntHypothesis(
                hunt_id=hunt.id,
                title="Queries are benign corporate sync telemetry",
                description="Testing if corp-sync.test is an authorized vendor cloud synchronization service.",
                status=HuntHypothesisStatus.NOT_SUPPORTED.value,
                confidence=HuntConfidence.HIGH.value,
                analyst_reasoning="Domain WHOIS and proxy configuration check confirm corp-sync.test is an unapproved external destination not listed in corporate asset records.",
            )
            db.add_all([hyp1, hyp2])
            db.commit()
            db.refresh(hyp1)

            # Add sample evidence
            ev1 = ThreatHuntEvidence(
                hunt_id=hunt.id,
                hypothesis_id=hyp1.id,
                evidence_type=HuntEvidenceType.DNS_EVENT.value,
                source_id="EVT-TUNNEL-0001",
                description="Base64 TXT query 'dGhpcy1pcy1hLXNlY3JldA.corp-sync.test' resolves to external IP 198.51.100.53.",
                relevance=HuntEvidenceRelevance.SUPPORTING.value,
                analyst_note="Decodes to 'this-is-a-secret', proving active data staging.",
            )
            ev2 = ThreatHuntEvidence(
                hunt_id=hunt.id,
                hypothesis_id=hyp1.id,
                evidence_type=HuntEvidenceType.EVENT.value,
                source_id="EVT-TUNNEL-0002",
                description="Consecutive chunk query 'ZXhmaWx0cmF0aW9uLXBhY2tldC0wMQ.corp-sync.test'.",
                relevance=HuntEvidenceRelevance.SUPPORTING.value,
                analyst_note="Decodes to 'exfiltration-packet-01', indicating a systematic multi-part exfiltration routine.",
            )
            db.add_all([ev1, ev2])
            db.commit()

            # Add sample finding
            f1 = ThreatHuntFinding(
                hunt_id=hunt.id,
                title="Active DNS Tunneling Exfiltration on Host 192.168.1.105",
                description="Internal workstation 192.168.1.105 bypassed proxy controls by tunneling sensitive data chunks over outbound UDP/53.",
                finding_type=HuntFindingType.ANOMALY.value,
                confidence=HuntConfidence.HIGH.value,
                evidence_count=2,
                mitigation_recommendation="Restrict perimeter outbound UDP 53 to internal DNS resolvers only; implement DNS inspection for high-entropy queries.",
            )
            db.add(f1)

            # Add sample notes
            n1 = ThreatHuntNote(
                hunt_id=hunt.id,
                user_id=user_id,
                author_name=user.username if user else "Analyst",
                content="Initial domain pivot on `corp-sync.test` revealed 7 unique subdomains matching standard base64 alphabet. Payload length is constant at 32 bytes.",
            )
            db.add(n1)
            db.commit()
            print(f"[+] Created Exemplar Hunt: {hunt.hunt_id}")

        print("[OK] Step 14 Threat Hunting Seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_threat_hunting()
