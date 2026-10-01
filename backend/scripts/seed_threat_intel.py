"""Seed script for Step 13 Threat Intelligence & IOC Investigation.

Populates:
1. Threat Intelligence Sources (Synthetic, Internal, Public, Commercial, Community)
2. Safe Baseline Educational Indicators (RFC 5737 IPs, .test Domains, Hashes, URLs)
3. Structural Indicator Relationships
4. 5 Hands-On Threat Intelligence Investigation Challenges
"""

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.enums import IndicatorRelationshipType
from app.models.threat_intel import (
    Indicator,
    IndicatorRelationship,
    IndicatorTimeline,
    ThreatIntelChallenge,
    ThreatIntelSource,
)
from app.services.threat_intel.normalization_service import normalization_service


def seed_sources(db) -> dict[str, ThreatIntelSource]:
    """Seed synthetic and educational threat intel sources."""
    sources_data = [
        {
            "name": "NexoraNet Synthetic Threat Intelligence",
            "source_type": "SYNTHETIC",
            "description": "Curated educational threat intelligence repository built for safe defensive training.",
            "reliability": "HIGH",
            "enabled": True,
            "is_synthetic": True,
        },
        {
            "name": "NexoraNet Internal Telemetry",
            "source_type": "INTERNAL",
            "description": "Telemetry collected from NexoraNet simulated endpoints, switches, and firewalls.",
            "reliability": "HIGH",
            "enabled": True,
            "is_synthetic": True,
        },
        {
            "name": "Synthetic OSINT Open Source Feed",
            "source_type": "PUBLIC",
            "description": "Educational public intelligence feed aggregating community OSINT submissions.",
            "reliability": "MEDIUM",
            "enabled": True,
            "is_synthetic": True,
        },
        {
            "name": "Synthetic Commercial Threat Feed",
            "source_type": "COMMERCIAL",
            "description": "Commercial threat actor intelligence feed with high analytical curation.",
            "reliability": "HIGH",
            "enabled": True,
            "is_synthetic": True,
        },
        {
            "name": "Synthetic Community Abuse List",
            "source_type": "COMMUNITY",
            "description": "Unmoderated crowdsourced indicator reporting feed.",
            "reliability": "LOW",
            "enabled": True,
            "is_synthetic": True,
        },
    ]

    source_map = {}
    for src in sources_data:
        existing = db.query(ThreatIntelSource).filter(ThreatIntelSource.name == src["name"]).first()
        if not existing:
            existing = ThreatIntelSource(**src)
            db.add(existing)
            db.flush()
        source_map[src["name"]] = existing
    db.commit()
    print(f"[*] Seeded {len(source_map)} threat intelligence sources.")
    return source_map


def seed_indicators(db, source_map: dict[str, ThreatIntelSource]):
    """Seed baseline safe synthetic indicators."""
    primary_source = source_map["NexoraNet Synthetic Threat Intelligence"]
    now_utc = datetime.now(timezone.utc)

    indicators_data = [
        # 1. C2 IP
        {
            "indicator_id": "IOC-2026-0001",
            "raw_value": "198.51.100.25",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "CRITICAL",
            "description": "Known Command and Control (C2) server associated with simulated Cobalt Strike beaconing.",
            "tags": ["c2", "cobalt-strike", "beaconing", "rfc5737"],
            "mitre_attack_id": "T1071.001",
            "mitre_technique": "Application Layer Protocol: Web Protocols",
        },
        # 2. C2 Domain
        {
            "indicator_id": "IOC-2026-0002",
            "raw_value": "c2-controller.training.test",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "CRITICAL",
            "description": "Domain name resolving to C2 infrastructure hosting simulated reverse shell handlers.",
            "tags": ["c2", "dns", "command-and-control"],
            "mitre_attack_id": "T1071.004",
            "mitre_technique": "Application Layer Protocol: DNS",
        },
        # 3. Beacon URL
        {
            "indicator_id": "IOC-2026-0003",
            "raw_value": "http://c2-controller.training.test:8080/api/v1/beacon",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "HIGH",
            "description": "HTTP endpoint used for periodic heartbeat check-ins by infected hosts.",
            "tags": ["http", "beacon", "heartbeat"],
            "mitre_attack_id": "T1071.001",
            "mitre_technique": "Application Layer Protocol: Web Protocols",
        },
        # 4. Reconnaissance Scanner IP
        {
            "indicator_id": "IOC-2026-0004",
            "raw_value": "203.0.113.10",
            "classification": "SUSPICIOUS",
            "confidence": "MEDIUM",
            "severity": "MEDIUM",
            "description": "External IP address performing automated TCP port scanning and service fingerprinting.",
            "tags": ["scanner", "reconnaissance", "port-scan", "rfc5737"],
            "mitre_attack_id": "T1046",
            "mitre_technique": "Network Service Discovery",
        },
        # 5. Benign CDN Edge IP
        {
            "indicator_id": "IOC-2026-0005",
            "raw_value": "192.0.2.50",
            "classification": "BENIGN",
            "confidence": "HIGH",
            "severity": "INFO",
            "description": "Legitimate global content delivery network (CDN) edge server. High traffic volume is normal.",
            "tags": ["cdn", "infrastructure", "whitelisted", "benign", "rfc5737"],
            "mitre_attack_id": None,
            "mitre_technique": None,
        },
        # 6. Benign CDN Domain
        {
            "indicator_id": "IOC-2026-0006",
            "raw_value": "cdn-edge-global.training.test",
            "classification": "BENIGN",
            "confidence": "HIGH",
            "severity": "INFO",
            "description": "Valid content delivery domain for asset distribution. Often triggers heuristic volume alerts.",
            "tags": ["cdn", "benign", "assets"],
            "mitre_attack_id": None,
            "mitre_technique": None,
        },
        # 7. Phishing Domain
        {
            "indicator_id": "IOC-2026-0007",
            "raw_value": "portal-nexora-login.training.test",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "HIGH",
            "description": "Typosquatting credential harvesting portal mimicking corporate single sign-on page.",
            "tags": ["phishing", "credential-harvesting", "typosquatting"],
            "mitre_attack_id": "T1566.002",
            "mitre_technique": "Phishing: Spearphishing Link",
        },
        # 8. Phishing Login URL
        {
            "indicator_id": "IOC-2026-0008",
            "raw_value": "https://portal-nexora-login.training.test/auth/login",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "HIGH",
            "description": "Phishing credential capture URL embedded in spearphishing emails.",
            "tags": ["phishing", "url", "harvesting"],
            "mitre_attack_id": "T1566.002",
            "mitre_technique": "Phishing: Spearphishing Link",
        },
        # 9. Malicious Dropper File Hash
        {
            "indicator_id": "IOC-2026-0009",
            "raw_value": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "CRITICAL",
            "description": "SHA-256 hash of simulated payload dropper delivering second-stage payload.",
            "tags": ["malware", "dropper", "trojan", "sha256"],
            "mitre_attack_id": "T1204.002",
            "mitre_technique": "User Execution: Malicious File",
        },
        # 10. DNS Tunneling Domain
        {
            "indicator_id": "IOC-2026-0010",
            "raw_value": "tunnel-exfil.training.test",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "HIGH",
            "description": "Authoritative nameserver receiving high-entropy TXT queries for DNS data exfiltration.",
            "tags": ["dns-tunneling", "exfiltration", "covert-channel"],
            "mitre_attack_id": "T1048.003",
            "mitre_technique": "Exfiltration Over Alternative Protocol: Exfiltration Over Symmetric Encrypted Protocol",
        },
        # 11. DNS Tunneling IP
        {
            "indicator_id": "IOC-2026-0011",
            "raw_value": "198.51.100.99",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "HIGH",
            "description": "Rogue nameserver destination for encoded DNS exfiltration requests.",
            "tags": ["dns", "exfiltration", "nameserver", "rfc5737"],
            "mitre_attack_id": "T1071.004",
            "mitre_technique": "Application Layer Protocol: DNS",
        },
        # 12. Phishing Sender Email
        {
            "indicator_id": "IOC-2026-0012",
            "raw_value": "admin-security-alert@phishing-campaign.training.test",
            "classification": "MALICIOUS",
            "confidence": "HIGH",
            "severity": "MEDIUM",
            "description": "Spoofed email sender address delivering fake urgent account verification links.",
            "tags": ["email", "phishing", "social-engineering"],
            "mitre_attack_id": "T1566.001",
            "mitre_technique": "Phishing: Spearphishing Attachment",
        },
    ]

    indicator_objs = {}
    for item in indicators_data:
        norm_res = normalization_service.normalize(item["raw_value"])
        existing = db.query(Indicator).filter(Indicator.normalized_value == norm_res["normalized_value"]).first()
        if not existing:
            existing = Indicator(
                indicator_id=item["indicator_id"],
                indicator_type=norm_res["indicator_type"],
                hash_type=norm_res["hash_type"],
                value=norm_res["value"],
                normalized_value=norm_res["normalized_value"],
                display_value=norm_res["display_value"],
                source_id=primary_source.id,
                source_name=primary_source.name,
                classification=item["classification"],
                confidence=item["confidence"],
                severity=item["severity"],
                status="ACTIVE",
                description=item["description"],
                tags=json.dumps(item["tags"]),
                mitre_attack_id=item["mitre_attack_id"],
                mitre_technique=item["mitre_technique"],
                is_synthetic=True,
                first_seen=now_utc - timedelta(days=14),
                last_seen=now_utc - timedelta(hours=2),
            )
            db.add(existing)
            db.flush()

            # Add initial timeline
            tl = IndicatorTimeline(
                indicator_id=existing.id,
                event_type="ENRICHED",
                title=f"Indicator Cataloged: {existing.display_value}",
                description=f"Cataloged as {existing.classification} ({existing.confidence} confidence).",
                actor_name="NexoraNet Synthetic Feed",
                event_timestamp=now_utc - timedelta(days=14),
            )
            db.add(tl)
        indicator_objs[item["raw_value"]] = existing

    db.commit()
    print(f"[*] Seeded {len(indicator_objs)} baseline threat indicators.")

    # Relationships
    relationships_data = [
        ("c2-controller.training.test", "198.51.100.25", IndicatorRelationshipType.RESOLVES_TO.value, "Resolves to C2 server IP."),
        ("http://c2-controller.training.test:8080/api/v1/beacon", "c2-controller.training.test", IndicatorRelationshipType.HOSTS.value, "Hosted on C2 domain."),
        ("portal-nexora-login.training.test", "203.0.113.10", IndicatorRelationshipType.RESOLVES_TO.value, "Phishing domain hosted on suspicious IP."),
        ("https://portal-nexora-login.training.test/auth/login", "portal-nexora-login.training.test", IndicatorRelationshipType.HOSTS.value, "Phishing login path hosted on domain."),
        ("cdn-edge-global.training.test", "192.0.2.50", IndicatorRelationshipType.RESOLVES_TO.value, "Legitimate CDN distribution edge IP."),
        ("tunnel-exfil.training.test", "198.51.100.99", IndicatorRelationshipType.RESOLVES_TO.value, "Tunneling nameserver resolved IP."),
        ("admin-security-alert@phishing-campaign.training.test", "portal-nexora-login.training.test", IndicatorRelationshipType.ASSOCIATED_WITH.value, "Email links to phishing domain."),
    ]

    for src_raw, tgt_raw, rel_type, desc in relationships_data:
        src_norm = normalization_service.normalize(src_raw)["normalized_value"]
        tgt_norm = normalization_service.normalize(tgt_raw)["normalized_value"]
        src_ind = db.query(Indicator).filter(Indicator.normalized_value == src_norm).first()
        tgt_ind = db.query(Indicator).filter(Indicator.normalized_value == tgt_norm).first()
        if src_ind and tgt_ind:
            existing_rel = db.query(IndicatorRelationship).filter(
                IndicatorRelationship.source_indicator_id == src_ind.id,
                IndicatorRelationship.target_indicator_id == tgt_ind.id,
                IndicatorRelationship.relationship_type == rel_type,
            ).first()
            if not existing_rel:
                rel = IndicatorRelationship(
                    source_indicator_id=src_ind.id,
                    target_indicator_id=tgt_ind.id,
                    relationship_type=rel_type,
                    description=desc,
                    confidence="HIGH",
                )
                db.add(rel)

    db.commit()
    print("[*] Seeded indicator correlation relationships.")


def seed_challenges(db):
    """Seed the 5 hands-on educational threat intelligence challenges."""
    challenges_data = [
        {
            "slug": "c2-ip-attribution",
            "title": "Command & Control IP Attribution & Correlation",
            "difficulty": "BEGINNER",
            "category": "C2_INVESTIGATION",
            "objective": "Investigate external IP 198.51.100.25 communicating on abnormal ports, correlate with known C2 infrastructure, and formulate a defensible SOC response.",
            "scenario_description": (
                "A perimeter detection alert flagged repeated outbound HTTP POST connections from an internal workstation "
                "(10.0.0.45) to external address 198.51.100.25 at fixed 60-second intervals. Your task as a Tier-1 SOC analyst "
                "is to inspect the indicator, query the threat intelligence repository, review related domains, and decide "
                "on classification and containment steps."
            ),
            "target_indicator_value": "198.51.100.25",
            "expected_classification": "MALICIOUS",
            "expected_observations": json.dumps(["Repeated 60s beaconing interval", "Resolves from c2-controller.training.test", "POST /api/v1/beacon"]),
            "rubric_description": "20% IOC Match, 20% Evidence Review, 20% Intel Interpretation, 20% Entity Correlation, 20% SOC Conclusion.",
        },
        {
            "slug": "typosquatting-phishing-domain",
            "title": "Typosquatting Phishing Domain Analysis",
            "difficulty": "BEGINNER",
            "category": "PHISHING_TRIAGE",
            "objective": "Analyze the suspicious domain portal-nexora-login.training.test reported by an employee, verify its hosting context and reputation, and establish whether it is part of an active campaign.",
            "scenario_description": (
                "An employee forwarded a suspicious email claiming 'Urgent Security Password Reset Required' that directed "
                "to https://portal-nexora-login.training.test/auth/login. The employee noticed the slight spelling difference "
                "from the corporate domain. Examine the domain indicator, check its threat intelligence history, and assess "
                "the appropriate classification."
            ),
            "target_indicator_value": "portal-nexora-login.training.test",
            "expected_classification": "MALICIOUS",
            "expected_observations": json.dumps(["Credential harvesting login form", "Links to phishing sender email", "Resolves to 203.0.113.10"]),
            "rubric_description": "20% IOC Match, 20% Evidence Review, 20% Intel Interpretation, 20% Entity Correlation, 20% SOC Conclusion.",
        },
        {
            "slug": "malicious-file-hash-triage",
            "title": "Malicious Dropper File Hash Triage",
            "difficulty": "INTERMEDIATE",
            "category": "MALWARE_TRIAGE",
            "objective": "Investigate SHA-256 hash a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0 detected during an HTTP file transfer, assess its threat score, and determine host impact.",
            "scenario_description": (
                "Network inspection extracted a downloaded executable payload and computed its SHA-256 hash as "
                "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0. Query the threat intelligence database, "
                "determine malware family attribution, and decide if endpoint containment is warranted."
            ),
            "target_indicator_value": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
            "expected_classification": "MALICIOUS",
            "expected_observations": json.dumps(["Matched Trojan Dropper signature", "MITRE T1204.002", "Correlated with initial phishing ingress"]),
            "rubric_description": "20% IOC Match, 20% Evidence Review, 20% Intel Interpretation, 20% Entity Correlation, 20% SOC Conclusion.",
        },
        {
            "slug": "benign-cdn-false-positive",
            "title": "High-Volume CDN False Positive Investigation",
            "difficulty": "INTERMEDIATE",
            "category": "FALSE_POSITIVE_TUNING",
            "objective": "Investigate IP 192.0.2.50 flagged by a high-volume anomaly alert, evaluate whether it represents genuine exfiltration or benign web asset loading, and avoid business disruption.",
            "scenario_description": (
                "An automated heuristic rule triggered an alert for 'High Outbound Data Volume to External Host' for "
                "IP 192.0.2.50 from 25 internal workstations. A junior analyst suggested immediately blocking the IP on the perimeter firewall. "
                "Investigate the indicator reputation, analyze the domain cdn-edge-global.training.test, and evaluate whether "
                "this is a false positive."
            ),
            "target_indicator_value": "192.0.2.50",
            "expected_classification": "BENIGN",
            "expected_observations": json.dumps(["Global CDN provider", "High volume is expected asset caching", "Avoid perimeter disruption"]),
            "rubric_description": "20% IOC Match, 20% Evidence Review, 20% Intel Interpretation, 20% Entity Correlation, 20% SOC Conclusion.",
        },
        {
            "slug": "dns-tunneling-exfiltration-domain",
            "title": "DNS Exfiltration Tunneling Domain Investigation",
            "difficulty": "ADVANCED",
            "category": "DNS_EXFILTRATION",
            "objective": "Analyze the authoritative domain tunnel-exfil.training.test receiving anomalous base64-encoded subdomains, verify its threat intelligence profile, and recommend detection tuning.",
            "scenario_description": (
                "The detection engine identified suspicious DNS TXT and NULL queries with high Shannon entropy directed toward "
                "subdomains of tunnel-exfil.training.test. Examine the domain and its associated nameserver 198.51.100.99, "
                "confirm whether it functions as a covert exfiltration channel, and construct an incident response plan."
            ),
            "target_indicator_value": "tunnel-exfil.training.test",
            "expected_classification": "MALICIOUS",
            "expected_observations": json.dumps(["High entropy subdomains", "Base64 payload encoded in queries", "Nameserver 198.51.100.99"]),
            "rubric_description": "20% IOC Match, 20% Evidence Review, 20% Intel Interpretation, 20% Entity Correlation, 20% SOC Conclusion.",
        },
    ]

    for ch in challenges_data:
        existing = db.query(ThreatIntelChallenge).filter(ThreatIntelChallenge.slug == ch["slug"]).first()
        if not existing:
            existing = ThreatIntelChallenge(**ch)
            db.add(existing)
        else:
            for k, v in ch.items():
                setattr(existing, k, v)
    db.commit()
    print(f"[*] Seeded {len(challenges_data)} threat intelligence challenges.")


def main():
    db = SessionLocal()
    try:
        print("[+] Starting Step 13 Threat Intelligence seeding...")
        source_map = seed_sources(db)
        seed_indicators(db, source_map)
        seed_challenges(db)
        print("[+] Seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
