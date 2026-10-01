# NexoraNet Mock Test Engine Architecture & Specification

## 1. Executive Overview

The **NexoraNet Mock Test Engine** (Step 5) provides an authoritative, secure, and pedagogically rich assessment platform designed for computer networking and cybersecurity students. It bridges conceptual study with realistic, timed practice mirroring professional industry certifications such as Cisco CCNA, CompTIA Network+, and CompTIA Security+.

```
LEARN (Curriculum & Lessons)
  ↓
PERFORM (Hands-on Labs)
  ↓
ASSESS (Core Mock Test Engine)
  ↓
ANALYZE (Topic & Difficulty Breakdown)
  ↓
DEFEND (Cybersecurity Challenges & Mini SOC)
```

The system strictly adheres to **zero-knowledge answer shielding**, **server-authoritative UTC timer enforcement**, **deterministic scoring**, and **diagnostic mistake analytics**.

---

## 2. Core Architectural Principles

### 2.1 Zero-Knowledge Student Answer Shielding
To guarantee examination integrity, the backend strictly never exposes answer keys, correctness flags (`is_correct`), or pedagogical explanations to the client during an active test sitting:
- `StudentQuestionPayload` and `StudentOptionBrief` strip all scoring attributes.
- Attempts to access the answer review endpoint (`/api/v1/mock-test-attempts/{attempt_id}/review`) while an attempt is `IN_PROGRESS` raise an **HTTP 403 Forbidden** error.
- Explanations and correctness keys are only unsealed post-submission (`SUBMITTED` or `EXPIRED`).

### 2.2 Server-Authoritative UTC Timer Synchronization
Exam durations and time limits cannot be spoofed by modifying local client clocks:
- When an exam sitting is created or resumed, the server calculates authoritative timestamps:
  $$\text{expires\_at} = \text{started\_at} + \text{duration\_minutes} \times 60$$
- Timestamps are persisted in timezone-aware UTC format.
- The `/status` endpoint recalculates $\text{remaining\_seconds} = \max(0, \text{expires\_at} - \text{now})$.
- If $\text{now} \ge \text{expires\_at}$, the backend automatically finalizes the sitting with status `EXPIRED`, evaluates the existing answers, and rejects any subsequent late submissions.

### 2.3 Resilient and Idempotent Answer State
- Students can navigate freely between questions.
- Every option choice is persisted asynchronously via `POST /save-answer`.
- Answers are keyed on `(attempt_id, question_id)`. Re-selecting an answer updates the existing row rather than duplicating records.
- Options can be cleared via `POST /clear-answer/{question_id}` while preserving the question's "Mark for Review" state.
- Unintentional browser refreshes or network hiccups do not cause lost progress: resuming the sitting restores all previously saved choices and the exact remaining time.

---

## 3. Database Schema & Data Models

Applied via Alembic migration `c39f182da410` (`add_step5_mock_test_engine_schema`):

### 3.1 `mock_tests`
| Field | Type | Description |
|---|---|---|
| `id` | `INTEGER` | Primary Key |
| `title` | `VARCHAR(255)` | Test title |
| `slug` | `VARCHAR(128)` | Unique URL-friendly slug |
| `description` | `TEXT` | Syllabus summary |
| `difficulty` | `ENUM` | `BEGINNER`, `INTERMEDIATE`, `ADVANCED` |
| `test_type` | `ENUM` | `TOPIC`, `DIFFICULTY`, `MIXED`, `COMPREHENSIVE`, `PRACTICE`, `FULL_MOCK` |
| `duration_minutes`| `INTEGER` | Allowed time in minutes |
| `total_questions` | `INTEGER` | Expected question count |
| `passing_percentage`| `FLOAT` | Passing requirement (e.g. 70.0%) |
| `status` | `ENUM` | `DRAFT`, `PUBLISHED`, `ARCHIVED` |
| `instructions` | `TEXT` | Dedicated pre-test candidate guidelines |

### 3.2 `student_answers`
| Field | Type | Description |
|---|---|---|
| `id` | `INTEGER` | Primary Key |
| `attempt_id` | `INTEGER` | FK -> `mock_test_attempts.id` (CASCADE) |
| `question_id` | `INTEGER` | FK -> `questions.id` (RESTRICT) |
| `answer_data` | `TEXT` | JSON-encoded array of selected option IDs `[id1, id2]` |
| `is_correct` | `BOOLEAN` | Calculated post-submission |
| `points_earned` | `INTEGER` | Points awarded |
| `is_marked_for_review` | `BOOLEAN` | Candidate review marker flag |
| `answered_at` | `DATETIME` | Timestamp of last selection |

### 3.3 `test_results`
| Field | Type | Description |
|---|---|---|
| `id` | `INTEGER` | Primary Key |
| `attempt_id` | `INTEGER` | FK -> `mock_test_attempts.id` (CASCADE) |
| `score` | `FLOAT` | Points earned |
| `total_points` | `FLOAT` | Maximum points possible |
| `earned_points` | `FLOAT` | Alias for earned score |
| `percentage` | `FLOAT` | $\frac{\text{earned}}{\text{total}} \times 100$ |
| `passing_percentage`| `FLOAT` | Snapshot of passing requirement |
| `passed` | `BOOLEAN` | $\text{percentage} \ge \text{passing\_percentage}$ |
| `correct_answers`| `INTEGER` | Correct question count |
| `incorrect_answers`| `INTEGER` | Incorrect question count |
| `unanswered` | `INTEGER` | Skipped question count |
| `total_questions`| `INTEGER` | Total exam question count |
| `time_taken_seconds`| `INTEGER` | Net time taken |

---

## 4. Multi-Dimensional Question Evaluation

The `ScoringService` implements strict validation across the core question types:

1. **`SINGLE_CHOICE`**: Exactly one correct answer required.
   - Evaluated as: `set(selected_ids) == set([correct_option_id])`.
2. **`MULTIPLE_CHOICE`**: Two or more correct answers required.
   - Evaluated as exact set equality:
     $$\text{selected\_ids} = \text{correct\_option\_ids}$$
   - Partial selections or over-selection of incorrect choices receive 0 points.
3. **`TRUE_FALSE`**: Two options (`True` and `False`), exactly one correct.
   - Evaluated as single choice matching.

### Performance Analytics Breakdown
Post-submission, the backend calculates:
- **Topic Breakdown**: Aggregates questions by syllabus topic, computing correct questions, points earned, total points, and percentage mastery.
- **Difficulty Breakdown**: Evaluates Beginner, Intermediate, and Advanced question performance.

---

## 5. API Reference

### Mock Examination Catalog (`/api/v1/mock-tests`)
- `GET /api/v1/mock-tests`: List published exams. Supports filters: `?difficulty=...`, `?test_type=...`, `?q=...`.
- `GET /api/v1/mock-tests/{id_or_slug}`: Detailed test overview, instructions, and syllabus topic distribution.
- `POST /api/v1/mock-tests/{id_or_slug}/start?retake=false`: Launch new sitting or resume active sitting.
- `GET /api/v1/mock-tests/blueprints/list`: List exam generation blueprints.
- `GET /api/v1/mock-tests/blueprints/{id}/validate`: Check question bank sufficiency against blueprint rules.
- `POST /api/v1/mock-tests/blueprints/{id}/generate`: Dynamically generate mock test from blueprint.

### Sitting & Session Management (`/api/v1/mock-test-attempts`)
- `GET /api/v1/mock-test-attempts/history`: List chronological student attempt history.
- `GET /api/v1/mock-test-attempts/{attempt_id}/status`: Authoritative server-side timer synchronization.
- `POST /api/v1/mock-test-attempts/{attempt_id}/save-answer`: Save/update option selections idempotently.
- `POST /api/v1/mock-test-attempts/{attempt_id}/clear-answer/{question_id}`: Clear choice for a question.
- `POST /api/v1/mock-test-attempts/{attempt_id}/mark-question/{question_id}`: Toggle review marker.
- `POST /api/v1/mock-test-attempts/{attempt_id}/submit`: Authoritatively grade sitting and generate scorecard.
- `GET /api/v1/mock-test-attempts/{attempt_id}/result`: Retrieve scorecard and performance metrics.
- `GET /api/v1/mock-test-attempts/{attempt_id}/review`: Question-by-question review with revealed answers and explanations (403 if in progress).
- `POST /api/v1/mock-test-attempts/{attempt_id}/practice?mode=incorrect_or_unanswered`: Generate targeted practice session from missed questions.

---

## 6. Seeded Sample Examinations

NexoraNet includes 4 production-grade seed mock examinations:

| Test Title | Slug | Questions | Duration | Pass Req | Test Type |
|---|---|---|---|---|---|
| **Beginner Networking Fundamentals Test** | `beginner-networking-fundamentals-test` | 30 | 30 mins | 70% | `COMPREHENSIVE` |
| **Beginner Networking Basics** | `beginner-networking-basics` | 10 | 30 mins | 70% | `TOPIC` |
| **Beginner OSI and TCP/IP Test** | `beginner-osi-and-tcpip-test` | 10 | 15 mins | 70% | `TOPIC` |
| **Intermediate Networking & Subnetting** | `intermediate-networking-subnetting` | 12 | 25 mins | 75% | `DIFFICULTY` |

---

## 7. Frontend User Experience Architecture

```
/mock-tests (Catalog & Filters)
  ↓
/mock-tests/:slug (Pre-test Guidelines & Syllabus Breakdown)
  ↓
/mock-tests/attempt/:attemptId (Two-Column Workspace with Timer & Question Navigator)
  ↓
/mock-tests/attempt/:attemptId/result (Scorecard, Pass/Fail Banner, & Topic Meters)
  ↓
/mock-tests/attempt/:attemptId/review (Post-Exam Explanations & Mistake Review)
  ↓
/mock-tests/history (Chronological Attempt Records)
```

- **Sticky Top Bar**: Displays test title, question counter, countdown timer (amber warning at < 5m, pulsing red at < 1m), and Submit button.
- **Left Column**: Clean question presentation with responsive radio/checkbox inputs, Clear Choice button, Mark for Review flag toggle, and Previous/Next buttons.
- **Right Column Navigator**: Interactive grid palette showing Current (blue), Answered (green), Marked (amber flag), and Unanswered (gray) states.
- **Submit Modal**: Confirms total answered, unanswered, and marked counts before committing.
- **Review Mode**: Filter by All, Incorrect, Unanswered, Correct, or Marked questions, revealing exact answers and in-depth networking explanations.
