# NexoraNet Personalization Engine (Step 8)

> **Core Philosophy:** Personalization in NexoraNet is transparent, explainable, and respectful of student privacy. It avoids permanent labels, predictive pigeonholing, or competitive ranking.

---

## 1. Student Diagnostic Profiling

Personalization is derived from authentic activity across four distinct sources:

1. **Mock Test Attempts:** Chronological scores, durations, and passing statuses.
2. **Question-Level Student Answers:** Correctness, answer times, and unattempted rates.
3. **Curriculum Progress:** Lesson completions, module tracks, and bookmarks.
4. **Hands-On Lab Attempts:** Step validation correctness, hint usage, and verification retries.

### Privacy & Data Minimization:
- All telemetry is stored locally in the relational database.
- No personal identifiable information is shared with external services.
- No competitive leaderboards, student ranking percentiles, or social scoreboards exist.

---

## 2. Dynamic Performance States

Instead of binary "pass/fail" or subjective labels, topics are classified into five neutral performance states:

| Performance State | Recent Accuracy | Statistical Sample | Pedagogical Meaning |
| :--- | :---: | :---: | :--- |
| **`INSUFFICIENT_DATA`** | N/A | $< 5$ questions | Baseline is not yet established; introductory lessons or diagnostic quizzes are recommended. |
| **`NEEDS_PRACTICE`** | $< 60\%$ | $\ge 5$ questions | Core mechanics require reinforcement; targeted drills and hands-on labs are prioritized. |
| **`DEVELOPING`** | $60\% - 79.9\%$ | $\ge 5$ questions | Concept understanding is forming; continued intermediate practice recommended to solidify skills. |
| **`SOLID`** | $80\% - 89.9\%$ | $\ge 5$ questions | Strong operational proficiency; ready for scenario-based challenges and comprehensive mocks. |
| **`STRONG`** | $\ge 90\%$ | $\ge 5$ questions | Mastery demonstrated; candidate for advanced drills and peer troubleshooting scenarios. |

---

## 3. Performance Decay & Long-Term Skill Retention

Knowledge of computer networking protocols naturally decays without active reinforcement.

- If a student demonstrated `SOLID` or `STRONG` proficiency in a topic (e.g. DNS or Subnetting), but has not answered questions in that topic for $> 14$ days (`ADAPTIVE_DECAY_DAYS`):
- The topic is flagged with a **Quick Refresher Review** state rather than being marked as weak.
- The UI surfaces a non-punitive reminder:  
  *"You performed well on DNS previously, but haven't practiced it recently. Recommended: Quick DNS Review."*

---

## 4. Beginner Onboarding Experience

For new cadets with zero or few answered questions:
- The engine gracefully bypasses sparse statistical charts.
- The **Recommended Foundational Sequence** is surfaced:
  1. Step 01: What is Computer Networking?
  2. Step 02: OSI Reference Model
  3. Step 03: TCP/IP Protocol Suite
  4. Step 04: IPv4 Addressing
  5. Step 05: TCP & UDP Mechanics
- Once 5 questions across completed examinations are logged, the full adaptive diagnostic dashboard activates automatically.
