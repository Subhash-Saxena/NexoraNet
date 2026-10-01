#!/usr/bin/env python3
"""
NexoraNet Question Bank Quality & Validation Auditor.
Strictly verifies that all questions meet quality standards:
- Valid topic mapping
- Valid options and single/multi-choice counts
- Pedagogical explanations present
- Programmatically verified IPv4 subnetting calculations
- Zero duplicate codes or normalized question texts
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
from app.models.curriculum import Topic
from app.services.question_importer import QuestionImporter
from app.services.question_validator import QuestionValidator


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate NexoraNet Question Bank Quality")
    parser.add_argument(
        "--dir",
        type=str,
        default=str(backend_dir / "data" / "question_bank"),
        help="Directory containing question bank files",
    )
    args = parser.parse_args()

    base_path = Path(args.dir)
    print("==================================================")
    print("NexoraNet Question Bank Quality Auditor")
    print("==================================================")
    print(f"Scanning Directory: {base_path}")

    file_entries = QuestionImporter.load_questions_from_directory(base_path)
    if not file_entries:
        print(f"⚠️  No question files (.json or .jsonl) found in {base_path}")
        return 1

    all_questions = []
    file_map = []
    for fp, q_list in file_entries:
        for q in q_list:
            all_questions.append(q)
            file_map.append((fp, q))

    print(f"Total Files Scanned: {len(file_entries)}")
    print(f"Total Questions Found: {len(all_questions)}")
    print("--------------------------------------------------")

    # Connect to DB to fetch valid topic slugs
    db = SessionLocal()
    try:
        topics = db.query(Topic).all()
        topic_slugs = {t.slug for t in topics}
        topic_ids = {t.id for t in topics}
    finally:
        db.close()

    validation_errors = []
    calculation_errors = []

    for fp, q in file_map:
        code = q.get("code", "UNKNOWN")
        errs = QuestionValidator.validate_question_dict(
            q,
            valid_topic_slugs=topic_slugs,
            valid_topic_ids=topic_ids,
        )
        if errs:
            validation_errors.append((fp.name, code, errs))

        # Check subnetting verification if calculation metadata is provided
        calc_meta = q.get("calculation_metadata")
        if calc_meta and isinstance(calc_meta, dict):
            cidr = calc_meta.get("cidr")
            prop = calc_meta.get("property")
            expected = calc_meta.get("expected")
            if cidr and prop and expected is not None:
                is_valid, msg = QuestionValidator.verify_subnet_calculation(cidr, prop, expected)
                if not is_valid:
                    calculation_errors.append((fp.name, code, msg))

    # Duplicate check
    duplicates = QuestionValidator.check_duplicate_questions(all_questions)

    has_errors = False

    if validation_errors:
        has_errors = True
        print(f"\n[FAIL] VALIDATION ERRORS DETECTED ({len(validation_errors)} questions):")
        for fname, code, errs in validation_errors[:20]:
            print(f"  * [{fname}] {code}:")
            for e in errs:
                print(f"      - {e}")
        if len(validation_errors) > 20:
            print(f"  ... and {len(validation_errors) - 20} more questions with errors.")

    if calculation_errors:
        has_errors = True
        print(f"\n[FAIL] CALCULATION/SUBNETTING ERRORS DETECTED ({len(calculation_errors)}):")
        for fname, code, msg in calculation_errors:
            print(f"  * [{fname}] {code}: {msg}")

    if duplicates:
        has_errors = True
        print(f"\n[FAIL] DUPLICATES DETECTED ({len(duplicates)}):")
        for d in duplicates[:15]:
            print(f"  * [{d['type']}] Code: {d.get('code')} -> Conflict: {d.get('conflict_with', d.get('conflict_with_code'))}")
            print(f"    Text: {d.get('question_text')[:70]}...")

    if not has_errors:
        print("\n[PASS] ALL QUALITY CHECKS PASSED:")
        print("  - Schema validation: OK")
        print("  - Topic mapping: OK")
        print("  - Single/Multiple choice correctness rules: OK")
        print("  - Subnetting calculations: OK")
        print("  - Zero duplicate codes or normalized text: OK")
        print("==================================================")
        return 0
    else:
        print("\n==================================================")
        print("[FAIL] QUALITY AUDIT FAILED. Please review and fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
