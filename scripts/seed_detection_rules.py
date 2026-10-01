"""Seed script for Step 11 Detection Engine built-in detection rules.

Populates the database with the 15 standard network detection rules.
"""

import json
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.models.detection import DetectionRule
from app.services.detection.rule_registry import BUILTIN_RULES


def seed_detection_rules() -> None:
    """Insert or update all built-in detection rules."""
    db = SessionLocal()
    try:
        created_count = 0
        updated_count = 0

        for r_data in BUILTIN_RULES:
            rule_id = r_data["rule_id"]
            existing = db.query(DetectionRule).filter(DetectionRule.rule_id == rule_id).first()

            conditions_json = (
                json.dumps(r_data["conditions"])
                if isinstance(r_data["conditions"], dict)
                else str(r_data["conditions"])
            )

            if existing:
                existing.name = r_data["name"]
                existing.description = r_data["description"]
                existing.category = r_data["category"]
                existing.severity = r_data["severity"]
                existing.confidence_default = r_data["confidence_default"]
                existing.status = r_data["status"]
                existing.logic_type = r_data.get("logic_type", "THRESHOLD")
                existing.conditions = conditions_json
                existing.threshold = r_data.get("threshold")
                existing.time_window_seconds = r_data.get("time_window_seconds")
                existing.mitre_attack_id = r_data.get("mitre_attack_id")
                existing.mitre_technique = r_data.get("mitre_technique")
                existing.explanation_template = r_data["explanation_template"]
                existing.investigation_guide = r_data["investigation_guide"]
                existing.is_builtin = True
                updated_count += 1
            else:
                new_rule = DetectionRule(
                    rule_id=rule_id,
                    name=r_data["name"],
                    description=r_data["description"],
                    category=r_data["category"],
                    severity=r_data["severity"],
                    confidence_default=r_data["confidence_default"],
                    status=r_data["status"],
                    logic_type=r_data.get("logic_type", "THRESHOLD"),
                    conditions=conditions_json,
                    threshold=r_data.get("threshold"),
                    time_window_seconds=r_data.get("time_window_seconds"),
                    mitre_attack_id=r_data.get("mitre_attack_id"),
                    mitre_technique=r_data.get("mitre_technique"),
                    explanation_template=r_data["explanation_template"],
                    investigation_guide=r_data["investigation_guide"],
                    is_builtin=True,
                )
                db.add(new_rule)
                created_count += 1

        db.commit()
        print(f"[+] Successfully seeded detection rules: {created_count} created, {updated_count} updated.")
    except Exception as e:
        db.rollback()
        print(f"[-] Error seeding detection rules: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_detection_rules()
