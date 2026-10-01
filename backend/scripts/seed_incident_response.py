"""Seed script for Step 17: Incident Response, Case Management & MITRE ATT&CK Framework."""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.services.incident_response.seed_service import IncidentResponseSeedService


def main() -> None:
    print("Seeding Step 17 Incident Response & MITRE ATT&CK dataset...")
    db = SessionLocal()
    try:
        results = IncidentResponseSeedService.seed_all(db)
        print(f"[+] MITRE ATT&CK Tactics & Techniques Seeded: {results['tactics_count']}")
        print(f"[+] Incident Response Playbooks Seeded: {results['playbooks_count']}")
        print(f"[+] Synthetic Educational Incidents Seeded: {results['incidents_count']}")
        print("[+] Step 17 Incident Response seed complete!")
    except Exception as e:
        print(f"Error seeding incident response data: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
