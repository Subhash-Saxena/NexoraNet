# Step 19: Challenge Authoring Guide

## 1. Authoring Workflow

To contribute or author a new educational challenge for NexoraNet:

```text
CONCEPT & LEARNING GOAL
           ↓
SYNTHETIC SCENARIO DESIGN
           ↓
EVIDENCE & ARTIFACT PREPARATION
           ↓
FLAG & NORMALIZATION DEFINITION
           ↓
PROGRESSIVE HINT CRAFTING
           ↓
SOLUTION WALKTHROUGH & COMMON PITFALLS
           ↓
SEED & VERIFICATION
```

---

## 2. Challenge Specification Schema

Every challenge entry in `RAW_CHALLENGES` must satisfy the following specification:

```python
{
    "challenge_id": "CHAL-INT-013",                 # Unique identifier (e.g. CHAL-BEG-*, CHAL-INT-*, CHAL-ADV-*, CHAL-EXP-*)
    "title": "Investigate Web Shell Ingress",        # Clear, actionable title
    "category": ChallengeCategory.INCIDENT_RESPONSE, # Valid ChallengeCategory enum
    "difficulty": ChallengeDifficulty.INTERMEDIATE,  # Valid ChallengeDifficulty enum
    "challenge_type": ChallengeType.LOG_DECODER,     # Interaction format
    "points": 125,                                   # Standard point tier
    "estimated_minutes": 20,                         # Realistic completion duration
    "description": "Short summary for the catalog card.",
    "scenario": "Detailed incident context and situation report.",
    "learning_objectives": [                         # 1-3 Bloom's taxonomy objectives
        "Identify web shell access patterns in Apache access logs."
    ],
    "prerequisites": ["HTTP status codes", "Web application security"],
    "environment_description": "Synthetic Apache access log from compromised DMZ web server.",
    "tasks": [                                       # Step-by-step investigation checklist
        "Inspect the access log in evidence.",
        "Locate the POST request with status 200 to an unusual PHP script.",
        "Submit the filename in format: FLAG{shell.php}."
    ],
    "skills_tested": ["Log analysis", "Web shell identification"],
    "related_lesson_slug": "web-application-security-basics",
    "related_lab_slug": "web-log-investigation",
    "related_mitre_technique": "T1505.003",          # MITRE technique ID
    "flag": "FLAG{c99_bypass.php}",                  # Expected answer (hashed upon seeding)
    "validation_type": "CASE_INSENSITIVE",           # EXACT, CASE_INSENSITIVE, NORMALIZED, NUMERIC, IP_CIDR
    "solution_explanation": "Detailed pedagogical walkthrough...",
    "common_mistakes": [                             # 1-3 pitfalls to guide students
        "Confusing legitimate CMS updates with obfuscated file uploads."
    ],
    "hints": [                                       # 1-3 progressive hints
        {"hint_number": 1, "hint_text": "Look for POST requests with size over 10KB.", "penalty_percent": 10.0, "penalty_points": 12},
        {"hint_number": 2, "hint_text": "Examine the /uploads/ directory specifically.", "penalty_percent": 25.0, "penalty_points": 30}
    ],
    "evidence": [                                    # 1-4 synthetic evidence artifacts
        {
            "evidence_type": "LOGS",
            "title": "access.log",
            "description": "DMZ Web Server Access Logs",
            "content": "..."
        }
    ]
}
```

---

## 3. Evidence Types

Evidence attachments must use synthetic datasets:

- `PCAP`: Formatted JSON packet captures containing frame numbers, protocol flags, and payloads.
- `LOGS`: Syslog, Windows Event Logs (Event ID 4624, 4688, 7045), or web server logs.
- `CONFIG`: Network interface listings (`ip addr`), firewall tables, or DNS configuration files.
- `PROCESS_TREE`: Parent-child execution lineage dictionaries.
- `TELEMETRY`: Aggregated flow records with NetFlow or Zeek-style summaries.

---

## 4. Multi-Stage Challenges

For complex, multi-step incident investigations:

1. Set `is_multi_stage = True`.
2. Define sequential `ChallengeStage` records with distinct `stage_order` numbers.
3. Each stage specifies its own `flag_hash` and tasks.
4. Terminal stages mark `is_terminal = True` to complete the attempt.
