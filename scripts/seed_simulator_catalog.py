"""Seed script for Network Simulator prebuilt topologies and scenarios."""

import logging
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parents[1] / "backend"
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.db.session import SessionLocal
from app.services.simulator_catalog_service import simulator_catalog_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("nexoranet.seed_simulator")


def main() -> None:
    db = SessionLocal()
    try:
        logger.info("Synchronizing prebuilt simulator topologies and scenarios...")
        res = simulator_catalog_service.sync_catalog(db)
        logger.info(
            f"Simulator catalog synchronized successfully!\n"
            f"  Topologies synced: {res['topologies_synced']}\n"
            f"  Scenarios synced:  {res['scenarios_synced']}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
