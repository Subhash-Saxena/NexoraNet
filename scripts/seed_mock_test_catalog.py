"""
Seed / Sync script for the Step 7 Mock Test Catalog.
Loads beginner.json, intermediate.json, advanced.json, and full_mocks.json,
validates question bank pool availability, assigns READY/PUBLISHED or DRAFT/NOT_READY,
and links questions deterministically to ready mock tests.
"""

import logging
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parents[1] / "backend"
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.db.session import SessionLocal
from app.services.mock_test_catalog_service import mock_test_catalog_service

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("nexoranet.seed_catalog")


def main() -> None:
    db = SessionLocal()
    try:
        logger.info("Starting Mock Test Catalog synchronization...")
        result = mock_test_catalog_service.sync_catalog_from_files(db)
        logger.info(
            "Catalog sync complete!\n"
            f"  Total tests processed: {result['total_processed']}\n"
            f"  Ready/Published tests: {result['ready_count']}\n"
            f"  Draft/Not-Ready tests: {result['draft_count']}\n"
            f"  Questions linked:     {result['questions_linked']}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
