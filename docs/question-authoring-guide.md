# NexoraNet Question Authoring Guide

> **Audience:** Networking Instructors, Assessment Engineers, Cybersecurity Contributors  
> **Platform Version:** NexoraNet 2.0 (Step 6)  
> **Auditing CLI:** `scripts/validate_question_bank.py`  
> **Ingestion CLI:** `scripts/import_questions.py`

---

## 1. Overview & Pedagogical Philosophy

NexoraNet questions assess real-world diagnostic, architectural, and analytical capabilities in networking and cybersecurity. Every question authored for the platform must adhere to the principle:

> **Assess authentic understanding, not memorization of trivial trivia.**

### Cognitive Levels (Bloom's Taxonomy)

Every question must declare a `cognitive_level`:

1. **`REMEMBER`**: Recall of protocol numbers, standard RFC port assignments, packet header fields, and standardized definitions.
2. **`UNDERSTAND`**: Explanation of protocol behavior, stateful vs. stateless packet filtering, TCP handshakes, and encapsulation mechanics.
3. **`APPLY`**: Execution of subnetting calculations, routing table lookups, firewall rule ordering, and CLI tool diagnostics (`ping`, `traceroute`, `ss`, `dig`).
4. **`ANALYZE`**: Dissection of Wireshark hex dumps, detection rule tuning, incident triage, and root cause diagnosis of anomalies.

---

## 2. Question JSON Format Specification

Questions are authored in JSON files within `backend/data/question_bank/{beginner|intermediate|advanced}/`.

```json
{
  "code": "SUBNET-005",
  "topic_slug": "subnetting",
  "question_text": "An administrator allocates the subnet 192.168.10.0/27 for internal servers. What is the broadcast address of this subnet?",
  "question_type": "SINGLE_CHOICE",
  "difficulty": "INTERMEDIATE",
  "cognitive_level": "APPLY",
  "points": 2,
  "estimated_seconds": 60,
  "status": "PUBLISHED",
  "explanation": "A /27 subnet mask is 255.255.255.224, giving block increments of 32 (2^(32-27) = 32). The network is 192.168.10.0, the usable host range is 192.168.10.1 through 192.168.10.30, and the broadcast address is 192.168.10.31.",
  "learning_objective": "Calculate IPv4 broadcast address for arbitrary CIDR prefixes.",
  "options": [
    {
      "option_text": "192.168.10.31",
      "is_correct": true,
      "order_index": 0,
      "explanation": "192.168.10.31 is the last address in the 32-address block."
    },
    {
      "option_text": "192.168.10.255",
      "is_correct": false,
      "order_index": 1,
      "explanation": "192.168.10.255 would be the broadcast address for a /24, not a /27."
    },
    {
      "option_text": "192.168.10.30",
      "is_correct": false,
      "order_index": 2,
      "explanation": "192.168.10.30 is the last usable host address, not the broadcast address."
    },
    {
      "option_text": "192.168.10.32",
      "is_correct": false,
      "order_index": 3,
      "explanation": "192.168.10.32 is the network address of the next subsequent subnet."
    }
  ],
  "tags": [
    "subnetting",
    "cidr",
    "broadcast-address",
    "ipv4",
    "slash27"
  ]
}
```

---

## 3. Field Definitions & Constraints

| Field | Type | Required | Rules & Constraints |
| :--- | :--- | :---: | :--- |
| `code` | `string` | **Yes** | Alphanumeric with hyphens/underscores (e.g. `OSI-012`, `SUBNET-004`). Must be globally unique across the entire database. |
| `topic_slug` | `string` | **Yes** | Must match a valid topic slug registered in the NexoraNet curriculum (`topics.slug`). |
| `question_text` | `string` | **Yes** | Minimum 5 characters. Must be clearly phrased without ambiguous double-negatives. |
| `question_type` | `string` | **Yes** | `SINGLE_CHOICE`, `MULTIPLE_CHOICE`, `TRUE_FALSE`, `NUMERICAL`, `SUBNETTING`, `SCENARIO`, `PACKET_ANALYSIS`. |
| `difficulty` | `string` | **Yes** | `BEGINNER`, `INTERMEDIATE`, or `ADVANCED`. |
| `cognitive_level` | `string` | **Yes** | `REMEMBER`, `UNDERSTAND`, `APPLY`, or `ANALYZE`. |
| `points` | `int` | **Yes** | Integer > 0 (Standard: 1 for simple recall, 2 for calculations/scenarios, 3 for complex packet traces). |
| `estimated_seconds` | `int` | **Yes** | Recommended pacing: 30-45s for recall, 60s for subnetting/routing, 90-120s for packet analysis. |
| `status` | `string` | **Yes** | `PUBLISHED` (live for exams), `DRAFT` (under review), `ARCHIVED` (retired). |
| `explanation` | `string` | **Yes** | Comprehensive educational rationale explaining why the correct choice is right and addressing common misconceptions. |
| `learning_objective` | `string` | No | Clear, actionable competency statement (e.g., "Analyze TCP FIN scan behavior"). |
| `options` | `list` | **Yes** | Minimum 2 options for choice questions. Each option must have `option_text` and `is_correct`. |
| `tags` | `list[str]` | No | Keywords for search and blueprint generation (e.g., `["tcp", "wireshark", "rst-flag"]`). |

---

## 4. Distractor Authoring Guidelines

Effective assessment depends on high-quality distractor options:

1. **Plausibility:** Distractors must reflect real-world networking behaviors or common student misconceptions (e.g. confusing the last usable host with the broadcast address, or confusing MAC addresses with IP addresses).
2. **Homogeneity:** All options in a question should be of similar length, grammatical structure, and tone. Do not make the correct answer conspicuously longer or more detailed than distractors.
3. **No Giveaways:** Avoid options like "All of the above" or "None of the above", as they undermine multiple-choice psychometric validity.
4. **No Trick Questions:** Do not rely on obscure typo catches or semantic traps. Assess understanding of networking and security principles.

---

## 5. Subnetting Calculations Programmatic Rule

For questions involving IPv4 subnet calculations:
* Authors should programmatically verify their mathematical claims against Python's `ipaddress.IPv4Network`.
* Ensure that:
  * Network addresses end on the correct bit boundary.
  * Usable host counts equal $2^{(32 - \text{prefix})} - 2$ (for prefixes $\le 30$).
  * Subnet masks correctly reflect CIDR prefixes (e.g., `/28` $\to$ `255.255.255.240`).

---

## 6. Contribution & Testing Workflow

### Step 1: Author or Edit Questions
Add questions to the appropriate file in `backend/data/question_bank/{tier}/`.

### Step 2: Run the Quality Auditor
Execute the validation auditor from the project root:
```bash
python scripts/validate_question_bank.py
```
The auditor checks:
* JSON syntax and required fields
* Topic slug resolution against curriculum tables
* Choice rules (single correct for `SINGLE_CHOICE`, at least one for `MULTIPLE_CHOICE`)
* Duplicate code or duplicate normalized text collisions
* Programmatic subnetting calculations

### Step 3: Test Idempotent Ingestion
Verify with dry run:
```bash
python scripts/import_questions.py --dry-run
```
Then import into the database:
```bash
python scripts/import_questions.py
```

### Step 4: Run Automated Tests
```bash
pytest backend/tests/test_question_bank_system.py
```
Ensure all tests pass before committing.
