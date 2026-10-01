"""Seed script for Step 20: 28 Cybersecurity Skills, 10 Achievements, and Admin/Instructor accounts."""

import logging

from app.models.analytics import Achievement, Skill
from app.models.enums import UserRole
from app.models.user import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

SKILLS_SEED = [
    {
        "skill_code": "NETWORKING",
        "name": "Computer Networking Foundations",
        "category": "FOUNDATIONS",
        "description": "Understanding of fundamental networking models, topologies, media, and hardware elements.",
        "related_topics": ["network-fundamentals", "osi-model", "tcp-ip-model", "physical-layer"],
    },
    {
        "skill_code": "NETWORK_SECURITY",
        "name": "Network Security & Defense",
        "category": "DEFENSE",
        "description": "Principles of defense-in-depth, perimeter security, access controls, and defense strategies.",
        "related_topics": ["network-security-basics", "firewalls-basics", "defense-in-depth"],
    },
    {
        "skill_code": "TCP_IP",
        "name": "TCP/IP Protocol Suite",
        "category": "PROTOCOLS",
        "description": "Core protocols of the Internet suite including IP, ICMP, ARP, TCP, and UDP communication flows.",
        "related_topics": ["tcp-ip-overview", "ip-protocol", "tcp-mechanisms", "udp-protocol"],
    },
    {
        "skill_code": "SUBNETTING",
        "name": "IPv4 Subnetting & Addressing",
        "category": "FOUNDATIONS",
        "description": "Binary math, VLSM, CIDR prefix calculations, broadcast addresses, and host ranges.",
        "related_topics": ["ipv4-addressing", "subnet-masks", "cidr-notation", "vlsm-design"],
    },
    {
        "skill_code": "DNS",
        "name": "DNS Protocol & Security",
        "category": "PROTOCOLS",
        "description": "Domain name resolution, zone transfers, DNS tunneling detection, and cache poisoning protection.",
        "related_topics": ["dns-fundamentals", "dns-queries-records", "dns-security-threats"],
    },
    {
        "skill_code": "DHCP",
        "name": "DHCP Protocol & Snooping",
        "category": "PROTOCOLS",
        "description": "Dynamic Host Configuration DORA transaction, DHCP starvation, and rogue DHCP mitigation.",
        "related_topics": ["dhcp-fundamentals", "dhcp-dora-process", "dhcp-snooping"],
    },
    {
        "skill_code": "HTTP_HTTPS",
        "name": "HTTP/HTTPS & Web Security",
        "category": "PROTOCOLS",
        "description": "Web protocols, TLS handshakes, certificate validation, and malicious HTTP telemetry inspection.",
        "related_topics": ["http-protocol", "https-tls-basics", "web-traffic-analysis"],
    },
    {
        "skill_code": "TCP_UDP",
        "name": "Transport Layer Flow & Mechanics",
        "category": "PROTOCOLS",
        "description": "Three-way handshakes, sequence/acknowledgment numbers, sliding windows, and port multiplexing.",
        "related_topics": ["tcp-handshake", "tcp-flags-control", "udp-transport", "port-numbers"],
    },
    {
        "skill_code": "ROUTING",
        "name": "IP Routing & Gateways",
        "category": "OPERATIONS",
        "description": "Next-hop routing tables, default gateways, static routes, and interior gateway protocols.",
        "related_topics": ["routing-fundamentals", "routing-tables", "static-vs-dynamic-routing"],
    },
    {
        "skill_code": "SWITCHING",
        "name": "Ethernet Switching & MAC Operations",
        "category": "OPERATIONS",
        "description": "MAC address tables, frame forwarding, collision/broadcast domains, and STP concepts.",
        "related_topics": ["ethernet-switching", "mac-address-learning", "broadcast-domains"],
    },
    {
        "skill_code": "VLAN",
        "name": "VLAN Segmentation & Trunking",
        "category": "OPERATIONS",
        "description": "Virtual LAN isolation, 802.1Q encapsulation, access vs trunk ports, and inter-VLAN routing.",
        "related_topics": ["vlan-fundamentals", "trunking-8021q", "vlan-hopping-defense"],
    },
    {
        "skill_code": "FIREWALLS",
        "name": "Firewalls & Packet Filtering",
        "category": "DEFENSE",
        "description": "Stateful vs stateless inspection, access control lists, network address translation, and perimeter rules.",
        "related_topics": ["firewall-architecture", "acl-rules", "stateful-inspection"],
    },
    {
        "skill_code": "IDS_IPS",
        "name": "Intrusion Detection & Prevention",
        "category": "DEFENSE",
        "description": "Signature-based vs anomaly-based detection, Snort/Suricata rules, and inline prevention behavior.",
        "related_topics": ["ids-ips-fundamentals", "snort-suricata-basics", "detection-signatures"],
    },
    {
        "skill_code": "PACKET_ANALYSIS",
        "name": "Deep Packet Inspection & Forensics",
        "category": "FORENSICS",
        "description": "Dissecting raw PCAP captures, frame headers, protocol field anomalies, and stream reconstruction.",
        "related_topics": ["pcap-dissection", "wireshark-filters", "packet-forensics"],
    },
    {
        "skill_code": "TRAFFIC_ANALYSIS",
        "name": "Network Traffic & Flow Analysis",
        "category": "FORENSICS",
        "description": "NetFlow/IPFIX telemetry, beaconing pattern identification, bandwidth anomalies, and exfiltration flows.",
        "related_topics": ["traffic-profiling", "c2-beaconing-analysis", "data-exfiltration-telemetry"],
    },
    {
        "skill_code": "SIEM",
        "name": "SIEM Architecture & Data Ingestion",
        "category": "OPERATIONS",
        "description": "Centralized log normalization, parsing, indexing pipelines, and security analytics platforms.",
        "related_topics": ["siem-architecture", "log-ingestion-pipelines", "event-normalization"],
    },
    {
        "skill_code": "LOG_ANALYSIS",
        "name": "Security Log Forensics",
        "category": "FORENSICS",
        "description": "Querying and interpreting Windows Event Logs, Syslog, authentication failures, and audit trails.",
        "related_topics": ["windows-event-logs", "syslog-analysis", "authentication-telemetry"],
    },
    {
        "skill_code": "SOC_TRIAGE",
        "name": "SOC Alert Triage & Prioritization",
        "category": "OPERATIONS",
        "description": "Alert queue monitoring, false positive filtering, severity classification, and escalation playbooks.",
        "related_topics": ["alert-triage-workflows", "false-positive-analysis", "analyst-prioritization"],
    },
    {
        "skill_code": "DETECTION_ENGINEERING",
        "name": "Detection Engineering & Rule Writing",
        "category": "DEFENSE",
        "description": "Authoring Sigma rules, Snort/Suricata syntax, alert tuning, and detection test validation.",
        "related_topics": ["sigma-rule-authoring", "suricata-rule-crafting", "detection-tuning"],
    },
    {
        "skill_code": "THREAT_INTELLIGENCE",
        "name": "Cyber Threat Intelligence (CTI)",
        "category": "OPERATIONS",
        "description": "Threat actor tracking, Diamond model, campaign profiling, and contextual intelligence enrichment.",
        "related_topics": ["threat-intelligence-lifecycle", "diamond-model", "threat-actor-profiling"],
    },
    {
        "skill_code": "IOC_ANALYSIS",
        "name": "Indicator of Compromise (IOC) Analysis",
        "category": "OPERATIONS",
        "description": "Extracting, validating, and searching hashes, suspicious domains, IP addresses, and CIDR blocks.",
        "related_topics": ["ioc-types-handling", "indicator-enrichment", "pyramid-of-pain"],
    },
    {
        "skill_code": "THREAT_HUNTING",
        "name": "Proactive Threat Hunting",
        "category": "OPERATIONS",
        "description": "Hypothesis-driven investigation, anomaly baselining, and searching for un-alerted adversary activity.",
        "related_topics": ["threat-hunting-methodology", "hypothesis-generation", "hunting-telemetry"],
    },
    {
        "skill_code": "ENDPOINT_SECURITY",
        "name": "Endpoint Security & Host Investigation",
        "category": "FORENSICS",
        "description": "Process hierarchy inspection, parent-child anomalies, scheduled tasks, persistence, and memory artifacts.",
        "related_topics": ["process-tree-analysis", "persistence-mechanisms", "host-artifact-inspection"],
    },
    {
        "skill_code": "INCIDENT_RESPONSE",
        "name": "Incident Response & NIST Lifecycle",
        "category": "OPERATIONS",
        "description": "NIST SP 800-61 lifecycle, containment planning, eradication simulation, timeline reconstruction, and lessons learned.",
        "related_topics": ["nist-ir-framework", "containment-strategies", "post-incident-review"],
    },
    {
        "skill_code": "DIGITAL_FORENSICS",
        "name": "Digital Forensics & Evidence Handling",
        "category": "FORENSICS",
        "description": "Chain of custody preservation, cryptographic hash verification, artifact timeline reconstruction, and integrity logging.",
        "related_topics": ["chain-of-custody", "evidence-integrity-hashes", "forensic-timelines"],
    },
    {
        "skill_code": "MITRE_ATTACK",
        "name": "MITRE ATT&CK Framework Mapping",
        "category": "DEFENSE",
        "description": "Mapping observed attacker telemetry to enterprise tactics, techniques, and procedures (TTPs).",
        "related_topics": ["mitre-matrix-tactics", "technique-attribution", "heat-map-analysis"],
    },
    {
        "skill_code": "SOAR",
        "name": "Security Orchestration & Automation (SOAR)",
        "category": "DEFENSE",
        "description": "Automated playbook execution, condition-based containment, analyst approval gates, and orchestration.",
        "related_topics": ["soar-playbook-design", "approval-gates", "automated-triage"],
    },
    {
        "skill_code": "SECURITY_REASONING",
        "name": "Defensive Security Reasoning & Analysis",
        "category": "FOUNDATIONS",
        "description": "Critical analytical evaluation of attack paths, root cause deduction, trade-off analysis, and risk mitigation.",
        "related_topics": ["root-cause-analysis", "attack-path-evaluation", "defensive-tradeoffs"],
    },
]

ACHIEVEMENTS_SEED = [
    {
        "code": "NETWORKING_FOUNDATIONS",
        "title": "Networking Foundations",
        "description": "Complete at least 5 foundational networking lessons.",
        "category": "CURRICULUM",
        "badge_icon": "BookOpen",
        "criteria_description": "Study and complete 5 or more curriculum lessons in networking topics.",
        "required_count": 5,
        "target_type": "LESSON",
    },
    {
        "code": "SUBNETTING_PRACTITIONER",
        "title": "Subnetting Practitioner",
        "description": "Successfully complete 3 subnetting or addressing exercises.",
        "category": "HANDS_ON",
        "badge_icon": "Binary",
        "criteria_description": "Complete 3 hands-on subnetting labs or addressing calculation challenges.",
        "required_count": 3,
        "target_type": "LAB",
    },
    {
        "code": "PACKET_ANALYST",
        "title": "Packet Analyst",
        "description": "Analyze 5 packet captures or PCAP challenge datasets.",
        "category": "FORENSICS",
        "badge_icon": "Search",
        "criteria_description": "Inspect and complete forensic analysis on 5 synthetic packet capture streams.",
        "required_count": 5,
        "target_type": "PCAP_ANALYSIS",
    },
    {
        "code": "SOC_TRIAGE_BEGINNER",
        "title": "SOC Triage Practitioner",
        "description": "Triage and classify 5 SOC security alerts.",
        "category": "OPERATIONS",
        "badge_icon": "Radio",
        "criteria_description": "Review and assign triage verdicts to 5 alerts in the SOC Alert Queue.",
        "required_count": 5,
        "target_type": "SOC_TRIAGE",
    },
    {
        "code": "SIEM_ANALYST",
        "title": "SIEM Log Analyst",
        "description": "Complete 3 SIEM queries and log investigation workflows.",
        "category": "OPERATIONS",
        "badge_icon": "Database",
        "criteria_description": "Perform 3 structured queries and log analysis sessions in the SIEM workbench.",
        "required_count": 3,
        "target_type": "SIEM_ANALYSIS",
    },
    {
        "code": "DETECTION_EXPLORER",
        "title": "Detection Engineering Explorer",
        "description": "Analyze and test 3 intrusion detection rules.",
        "category": "DEFENSE",
        "badge_icon": "ShieldAlert",
        "criteria_description": "Execute detection testing runs and verify matches against 3 detection rules.",
        "required_count": 3,
        "target_type": "DETECTION_ENGINEERING",
    },
    {
        "code": "THREAT_INTELLIGENCE_EXPLORER",
        "title": "Threat Intelligence Explorer",
        "description": "Investigate and annotate 5 threat intelligence IOCs.",
        "category": "OPERATIONS",
        "badge_icon": "Target",
        "criteria_description": "Examine, pivot, and enrich 5 IOC indicators in the Threat Intelligence workspace.",
        "required_count": 5,
        "target_type": "THREAT_INTEL",
    },
    {
        "code": "INCIDENT_INVESTIGATOR",
        "title": "Incident Response Investigator",
        "description": "Investigate 2 security incident cases through NIST phases.",
        "category": "OPERATIONS",
        "badge_icon": "Flame",
        "criteria_description": "Progress 2 incident response cases through triage, evidence, and response simulations.",
        "required_count": 2,
        "target_type": "INCIDENT_RESPONSE",
    },
    {
        "code": "MITRE_ANALYST",
        "title": "MITRE ATT&CK Analyst",
        "description": "Map 5 adversary techniques to verified incident evidence.",
        "category": "DEFENSE",
        "badge_icon": "Grid3X3",
        "criteria_description": "Link 5 MITRE ATT&CK techniques with observed telemetry evidence.",
        "required_count": 5,
        "target_type": "MITRE_MAPPING",
    },
    {
        "code": "CTF_PRACTITIONER",
        "title": "Defensive CTF Practitioner",
        "description": "Capture and submit flags for 5 synthetic challenges.",
        "category": "CHALLENGES",
        "badge_icon": "Trophy",
        "criteria_description": "Successfully solve and verify flags for 5 defensive cybersecurity challenges.",
        "required_count": 5,
        "target_type": "CHALLENGE",
    },
]


def seed_step20_data(db: Session) -> dict[str, int]:
    """Seed skills, achievements, admin, and instructor accounts if not present."""
    stats = {"skills": 0, "achievements": 0, "users": 0}

    # 1. Seed Admin User
    admin_user = db.query(User).filter(User.username == "admin_dev").first()
    if not admin_user:
        admin_user = User(
            username="admin_dev",
            email="admin@nexoranet.internal",
            password_hash="argon2id$v=19$m=65536,t=3,p=4$admin_dev_hash",
            display_name="Admin Security Lead",
            current_level="Staff Engineer",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin_user)
        stats["users"] += 1

    # 2. Seed Instructor User
    instructor_user = db.query(User).filter(User.username == "instructor_dev").first()
    if not instructor_user:
        instructor_user = User(
            username="instructor_dev",
            email="instructor@nexoranet.internal",
            password_hash="argon2id$v=19$m=65536,t=3,p=4$instructor_dev_hash",
            display_name="Chief Instructor",
            current_level="Senior Faculty",
            role=UserRole.INSTRUCTOR,
            is_active=True,
        )
        db.add(instructor_user)
        stats["users"] += 1

    db.flush()

    # 3. Seed Skills
    for skill_data in SKILLS_SEED:
        existing = db.query(Skill).filter(Skill.skill_code == skill_data["skill_code"]).first()
        if not existing:
            new_skill = Skill(
                skill_code=skill_data["skill_code"],
                name=skill_data["name"],
                category=skill_data["category"],
                description=skill_data["description"],
                related_topics=skill_data["related_topics"],
            )
            db.add(new_skill)
            stats["skills"] += 1

    # 4. Seed Achievements
    for ach_data in ACHIEVEMENTS_SEED:
        existing = db.query(Achievement).filter(Achievement.code == ach_data["code"]).first()
        if not existing:
            new_ach = Achievement(
                code=ach_data["code"],
                title=ach_data["title"],
                description=ach_data["description"],
                category=ach_data["category"],
                badge_icon=ach_data["badge_icon"],
                criteria_description=ach_data["criteria_description"],
                required_count=ach_data["required_count"],
                target_type=ach_data["target_type"],
            )
            db.add(new_ach)
            stats["achievements"] += 1

    db.commit()
    return stats
