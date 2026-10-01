"""Seed script for Step 16 Endpoint Security & Host Investigation Engine."""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.services.endpoint_security.dataset_service import DatasetService


def main() -> None:
    print("Seeding Step 16 Endpoint Security synthetic datasets and scenarios...")
    db = SessionLocal()
    try:
        results = DatasetService.seed_data(db)
        print(f"[+] Synthetic Hosts Created: {results['hosts_created']}")
        print(f"[+] Synthetic Events Created: {results['events_created']}")
        print(f"[+] Investigation Scenarios Created: {results['scenarios_created']}")
        print("[+] Step 16 Endpoint Security seed complete!")
    except Exception as e:
        print(f"Error seeding endpoint security data: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
