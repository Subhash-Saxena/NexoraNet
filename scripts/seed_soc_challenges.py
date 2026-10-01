"""Seed standard educational SOC challenge scenarios into the database."""

import json
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parents[1] / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.db.session import SessionLocal
from app.models.pcap import Capture
from app.models.soc import SocChallenge

CHALLENGES = [
    {
        "slug": "investigate-tcp-activity",
        "title": "Scenario 1: Investigate Suspicious TCP Activity",
        "scenario_type": "TCP",
        "difficulty": "BEGINNER",
        "target_capture_filename": "noteworthy_syn_pattern.pcap",
        "description": "Analyze a sequence of rapid TCP SYN and RST events. Determine whether the traffic represents automated port reconnaissance or benign connection retries.",
        "instructions": (
            "1. Review the alert metadata and identify the source and destination endpoints.\n"
            "2. Inspect the linked packet evidence to check TCP flag sequences and handshake completion.\n"
            "3. Formulate a hypothesis regarding the connection intent.\n"
            "4. Select an appropriate classification (SUSPICIOUS, BENIGN, or FALSE_POSITIVE).\n"
            "5. Document your conclusion with supporting evidence."
        ),
        "expected_observations": ["SYN", "RST", "port scan", "handshake", "connection"],
        "rubric_json": {
            "valid_classifications": ["SUSPICIOUS", "BENIGN", "FALSE_POSITIVE"],
            "key_focus": "Evaluation of incomplete handshakes vs application retry behavior.",
        },
    },
    {
        "slug": "investigate-dns-activity",
        "title": "Scenario 2: Investigate DNS Resolution Anomalies",
        "scenario_type": "DNS",
        "difficulty": "INTERMEDIATE",
        "target_capture_filename": "dns_lookup.pcap",
        "description": "Examine a burst of NXDOMAIN query failures and randomized subdomain lookups to differentiate domain generation algorithms from corporate DNS typos.",
        "instructions": (
            "1. Review DNS query names and record types in the evidence table.\n"
            "2. Inspect the Shannon entropy and character distribution of query labels.\n"
            "3. Formulate a hypothesis on whether queries reflect automated beaconing or search-list suffixes.\n"
            "4. Classify the alert and justify your reasoning in the notes."
        ),
        "expected_observations": ["NXDOMAIN", "entropy", "resolver", "subdomain", "query"],
        "rubric_json": {
            "valid_classifications": ["SUSPICIOUS", "BENIGN", "FALSE_POSITIVE", "REQUIRES_MORE_DATA"],
            "key_focus": "Distinguishing algorithmic DGA patterns from legitimate DNS search suffixes.",
        },
    },
    {
        "slug": "investigate-arp-conflict",
        "title": "Scenario 3: Investigate Conflicting ARP Mapping",
        "scenario_type": "ARP",
        "difficulty": "INTERMEDIATE",
        "target_capture_filename": "arp_resolution.pcap",
        "description": "Evaluate multiple MAC addresses claiming ownership of a single IP gateway address. Discern ARP spoofing from high-availability router failover (VRRP).",
        "instructions": (
            "1. Examine the source MAC addresses claiming the disputed IPv4 address.\n"
            "2. Check if MAC addresses share vendor OUI prefixes or VRRP virtual router MAC formats.\n"
            "3. Evaluate the time delta between conflicting ARP replies.\n"
            "4. Determine whether the event is malicious poisoning or legitimate router failover."
        ),
        "expected_observations": ["MAC", "ARP", "conflict", "poisoning", "VRRP", "gateway"],
        "rubric_json": {
            "valid_classifications": ["SUSPICIOUS", "BENIGN", "FALSE_POSITIVE"],
            "key_focus": "Layer 2 MAC verification and high-availability protocol awareness.",
        },
    },
    {
        "slug": "investigate-http-error-pattern",
        "title": "Scenario 4: Investigate HTTP Error Pattern & Cleartext Auth",
        "scenario_type": "HTTP",
        "difficulty": "BEGINNER",
        "target_capture_filename": "http_request.pcap",
        "description": "Inspect unencrypted HTTP traffic transmitting cleartext authentication headers. Assess exposure and recommend encryption remediation.",
        "instructions": (
            "1. Identify the HTTP method, URI, and request headers in the packet payload.\n"
            "2. Confirm presence of Authorization: Basic headers in cleartext.\n"
            "3. Formulate a hypothesis on risk exposure over local subnets.\n"
            "4. Document recommendations to enforce TLS encryption."
        ),
        "expected_observations": ["Authorization", "Basic", "HTTP", "cleartext", "credentials"],
        "rubric_json": {
            "valid_classifications": ["SUSPICIOUS", "BENIGN"],
            "key_focus": "Identifying cleartext credential leakage and recommending TLS migration.",
        },
    },
    {
        "slug": "investigate-multi-destination-traffic",
        "title": "Scenario 5: Investigate Multi-Destination Network Sweep",
        "scenario_type": "Mixed",
        "difficulty": "ADVANCED",
        "target_capture_filename": "multi_host_traffic.pcap",
        "description": "Analyze horizontal subnet sweeps and asymmetric flow volumes to identify automated discovery tools across LAN endpoints.",
        "instructions": (
            "1. Review the destination IP distribution queried by the source host.\n"
            "2. Check port uniformity across scanned hosts.\n"
            "3. Verify whether endpoints replied or dropped requests.\n"
            "4. Formulate an investigation conclusion explaining the scope of the sweep."
        ),
        "expected_observations": ["sweep", "subnet", "horizontal", "burst", "reconnaissance"],
        "rubric_json": {
            "valid_classifications": ["SUSPICIOUS", "BENIGN"],
            "key_focus": "Correlating multi-host telemetry and assessing horizontal discovery scope.",
        },
    },
]


def seed_challenges() -> None:
    """Seed the 5 challenges into SQLite database."""
    db = SessionLocal()
    try:
        created_count = 0
        updated_count = 0

        for item in CHALLENGES:
            # Find capture ID if present
            cap = db.query(Capture).filter(Capture.filename == item["target_capture_filename"]).first()
            cap_id = cap.id if cap else None

            existing = db.query(SocChallenge).filter(SocChallenge.slug == item["slug"]).first()
            if not existing:
                ch = SocChallenge(
                    slug=item["slug"],
                    title=item["title"],
                    description=item["description"],
                    scenario_type=item["scenario_type"],
                    difficulty=item["difficulty"],
                    capture_id=cap_id,
                    instructions=item["instructions"],
                    expected_observations=json.dumps(item["expected_observations"]),
                    rubric_json=json.dumps(item["rubric_json"]),
                )
                db.add(ch)
                created_count += 1
            else:
                existing.title = item["title"]
                existing.description = item["description"]
                existing.scenario_type = item["scenario_type"]
                existing.difficulty = item["difficulty"]
                existing.capture_id = cap_id
                existing.instructions = item["instructions"]
                existing.expected_observations = json.dumps(item["expected_observations"])
                existing.rubric_json = json.dumps(item["rubric_json"])
                updated_count += 1

        db.commit()
        print(f"Seeding completed: {created_count} challenges created, {updated_count} updated.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_challenges()
