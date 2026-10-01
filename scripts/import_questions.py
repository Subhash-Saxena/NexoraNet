#!/usr/bin/env python3
"""
NexoraNet Question Bank Import Script.
Loads structured JSON/JSONL question files, validates schema, detects duplicates,
and safely upserts questions into the database.
"""

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Configure UTF-8 output on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from app.db.session import SessionLocal
from app.services.question_importer import QuestionImporter


def main() -> int:
    parser = argparse.ArgumentParser(description="Import NexoraNet Question Bank")
    parser.add_argument(
        "--dir",
        type=str,
        default=str(backend_dir / "data" / "question_bank"),
        help="Directory containing question bank files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and check duplicates without modifying database",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed information for each question",
    )
    args = parser.parse_args()

    base_path = Path(args.dir)
    print("==================================================")
    print("NexoraNet Question Bank Importer")
    print("==================================================")
    print(f"Target Directory: {base_path}")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'DATABASE COMMIT'}")
    print("--------------------------------------------------")

    db = SessionLocal()
    try:
        result = QuestionImporter.import_all(db, base_path, dry_run=args.dry_run)

        if not result["success"]:
            print("\n[FAIL] IMPORT FAILED DUE TO VALIDATION ERRORS:\n")
            for err in result["validation_errors"]:
                print(f"  * File: {err['file']} | Code: {err['code']}")
                for msg in err["errors"]:
                    print(f"      - {msg}")
            return 1

        print("\n[OK] IMPORT SUMMARY:")
        print(f"  * Total Files Processed: {result['total_files']}")
        print(f"  * Total Questions:       {result['total_questions']}")
        print(f"  * Created Records:       {result['created_count']}")
        print(f"  * Updated Records:       {result['updated_count']}")

        print("\nDIFFICULTY BREAKDOWN:")
        for diff, count in result.get("by_difficulty", {}).items():
            print(f"  * {diff:<15}: {count}")

        print("\nCOGNITIVE LEVEL BREAKDOWN:")
        for cog, count in result.get("by_cognitive_level", {}).items():
            print(f"  * {cog:<15}: {count}")

        print("\nSTATUS BREAKDOWN:")
        for st, count in result.get("by_status", {}).items():
            print(f"  * {st:<15}: {count}")

        dups = result.get("duplicates_detected", [])
        if dups:
            print(f"\n[WARN] DUPLICATES DETECTED: {len(dups)}")
            for d in dups[:10]:
                print(f"  * [{d['type']}] {d.get('code')} -> {d.get('conflict_with', d.get('conflict_with_code'))}")
        else:
            print("\nZero duplicate codes or normalized question texts detected.")

        print("==================================================")
        return 0

    except Exception as e:
        print(f"\n[ERROR] Unhandled exception during import: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
