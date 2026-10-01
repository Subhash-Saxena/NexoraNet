"""
Mock Test Catalog and Test Library Validator CLI for NexoraNet.
Validates structural integrity, uniqueness of codes and slugs, blueprint rules,
and question availability across all mock tests.
"""

import json
import logging
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parents[1] / "backend"
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.db.session import SessionLocal
from app.models.curriculum import Topic
from app.models.enums import DifficultyLevel, QuestionStatus
from app.models.mock_test import MockTest
from app.models.question import Question

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("nexoranet.validate_catalog")


def validate_catalog() -> int:
    db = SessionLocal()
    catalog_dir = backend_root / "data" / "mock_tests"
    files = [
        catalog_dir / "beginner.json",
        catalog_dir / "intermediate.json",
        catalog_dir / "advanced.json",
        catalog_dir / "full_mocks.json",
    ]

    all_tests: list[dict] = []
    seen_codes: dict[str, str] = {}
    seen_slugs: dict[str, str] = {}
    errors: list[str] = []

    print("\n" + "=" * 80)
    print(" NEXORANET — MOCK TEST CATALOG & TEST LIBRARY VALIDATOR")
    print("=" * 80)

    # 1. Structural and File Validation
    for fpath in files:
        if not fpath.exists():
            errors.append(f"Missing catalog file: {fpath}")
            continue
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                specs = json.load(f)
            print(f"Loaded {len(specs):2d} test definitions from {fpath.name}")
            all_tests.extend(specs)
        except Exception as e:
            errors.append(f"Failed to read/parse {fpath.name}: {e}")

    # 2. Schema and Uniqueness Checks
    for spec in all_tests:
        code = spec.get("code")
        slug = spec.get("slug")
        title = spec.get("title")

        if not code:
            errors.append(f"Test '{title}' missing 'code'")
        elif code in seen_codes:
            errors.append(f"Duplicate test code '{code}' in '{title}' and '{seen_codes[code]}'")
        else:
            seen_codes[code] = title

        if not slug:
            errors.append(f"Test '{title}' missing 'slug'")
        elif slug in seen_slugs:
            errors.append(f"Duplicate test slug '{slug}' in '{title}' and '{seen_slugs[slug]}'")
        else:
            seen_slugs[slug] = title

        if spec.get("duration_minutes", 0) <= 0:
            errors.append(f"Test '{code}' has invalid duration: {spec.get('duration_minutes')}")
        if spec.get("total_questions", 0) <= 0:
            errors.append(f"Test '{code}' has invalid total_questions: {spec.get('total_questions')}")
        if not (0 < spec.get("passing_percentage", 0) <= 100):
            errors.append(f"Test '{code}' has invalid passing_percentage: {spec.get('passing_percentage')}")

        bp = spec.get("blueprint")
        if not bp or not bp.get("topics"):
            errors.append(f"Test '{code}' is missing blueprint topic rules")
        else:
            sum_q = sum(r.get("question_count", 0) for r in bp.get("topics", []))
            if sum_q != spec.get("total_questions"):
                errors.append(
                    f"Test '{code}' blueprint sum of questions ({sum_q}) does not match total_questions ({spec.get('total_questions')})"
                )

    # 3. Database Availability Report
    topics_by_slug = {t.slug: t for t in db.query(Topic).all()}
    ready_tests: list[dict] = []
    not_ready_tests: list[dict] = []

    for spec in all_tests:
        code = spec["code"]
        bp = spec.get("blueprint", {})
        is_ready = True
        shortfalls: list[str] = []

        for rule in bp.get("topics", []):
            t_slug = rule["topic_slug"]
            req_count = rule["question_count"]
            diff_str = rule.get("difficulty")
            diff = DifficultyLevel(diff_str) if diff_str else None

            topic_entity = topics_by_slug.get(t_slug)
            if not topic_entity:
                is_ready = False
                shortfalls.append(f"Missing topic '{t_slug}'")
                continue

            q_query = db.query(Question).filter(
                Question.topic_id == topic_entity.id,
                Question.status == QuestionStatus.PUBLISHED,
            )
            if diff:
                q_query = q_query.filter(Question.difficulty == diff)

            avail = q_query.count()
            if avail < req_count:
                is_ready = False
                diff_label = diff.value if diff else "ANY"
                shortfalls.append(
                    f"'{topic_entity.title}' ({diff_label}): need {req_count}, avail {avail} (shortfall {req_count - avail})"
                )

        if is_ready:
            ready_tests.append({"code": code, "title": spec["title"], "total_q": spec["total_questions"]})
        else:
            not_ready_tests.append(
                {"code": code, "title": spec["title"], "total_q": spec["total_questions"], "shortfalls": shortfalls}
            )

    db_test_count = db.query(MockTest).count()
    db.close()

    print("\n" + "-" * 80)
    print(" CATALOG AVAILABILITY & READINESS REPORT")
    print("-" * 80)
    print(f"Total Tests Defined:     {len(all_tests)}")
    print(f"Total Tests in Database: {db_test_count}")
    print(f"Ready / Published Tests: {len(ready_tests)} [READY]")
    print(f"Draft / Shortfall Tests: {len(not_ready_tests)} [DRAFT / NOT READY]")
    print("-" * 80)

    if sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if ready_tests:
        print("\n [READY TO ATTEMPT] (Pool Sufficient):")
        for t in ready_tests:
            print(f"  [READY] [{t['code']:<30}] {t['title']} ({t['total_q']} Qs)")

    if not_ready_tests:
        print("\n [DRAFT / SHORTFALL] (Question pool deficient for specific narrow subtopic):")
        for t in not_ready_tests:
            print(f"  [DRAFT] [{t['code']:<30}] {t['title']} ({t['total_q']} Qs)")
            for sf in t["shortfalls"]:
                print(f"      -> {sf}")

    print("\n" + "=" * 80)
    if errors:
        print(f" VALIDATION FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"  [ERROR] {err}")
        print("=" * 80 + "\n")
        return 1
    else:
        print(" ALL STRUCTURAL, BLUEPRINT, AND SCHEMA CHECKS PASSED SUCCESSFULLY!")
        print("=" * 80 + "\n")
        return 0


if __name__ == "__main__":
    sys.exit(validate_catalog())
