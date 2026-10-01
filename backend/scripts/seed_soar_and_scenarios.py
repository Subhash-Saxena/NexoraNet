"""Master Seed Script for Step 18: SOAR Automation & Advanced SOC Scenario Engine.

Seeds:
1. 8 Comprehensive Educational SOAR Playbooks with sequential steps
2. 28 Advanced Multi-Stage SOC Scenarios across 4 difficulties and 5 categories
3. 15 Interactive Lessons on SOAR, Orchestration, Approvals, and 9-Stage Investigations
4. 10 Question Bank entries for SOAR and SOC Scenario question types
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal
from app.services.soar.seed_learning_and_questions import (
    seed_soar_lessons_and_questions,
)
from app.services.soar.seed_soar_playbooks import seed_soar_playbooks
from app.services.soc_scenarios.seed_soc_scenarios import seed_soc_scenarios


def main() -> None:
    print("=" * 70)
    print("NexoraNet Step 18: Seeding SOAR Automation & Advanced SOC Scenarios...")
    print("=" * 70)

    db = SessionLocal()
    try:
        # 1. SOAR Playbooks
        print("[*] Seeding 8 Educational SOAR Playbooks...")
        playbooks = seed_soar_playbooks(db)
        print(f"[+] Successfully seeded {len(playbooks)} SOAR Playbooks with allowlisted actions.")

        # 2. SOC Scenarios
        print("[*] Seeding 28 Multi-Stage Educational SOC Scenarios...")
        scenarios = seed_soc_scenarios(db)
        print(f"[+] Successfully seeded {len(scenarios)} SOC Scenarios across 4 difficulties.")

        # 3. Lessons & Questions
        print("[*] Seeding 15 Lessons and Question Bank entries...")
        curriculum_res = seed_soar_lessons_and_questions(db)
        print(f"[+] Successfully seeded {curriculum_res['lessons_seeded']} Lessons.")
        print(f"[+] Successfully seeded {curriculum_res['questions_seeded']} Question Bank Questions.")

        print("=" * 70)
        print("[+] Step 18 Dataset Seed Completed Successfully!")
        print("=" * 70)
    except Exception as e:
        print(f"[!] Error seeding Step 18 data: {e}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
