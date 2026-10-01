# Step 19: CTF Challenges & Advanced Cybersecurity Training Engine

## 1. Overview & Learning Philosophy

The **NexoraNet Challenge Engine** provides an offline, gamified cybersecurity solving workspace. Following NexoraNet's core tagline:

> **"Learn. Simulate. Analyze. Defend."**

the Challenge Engine embodies the defensive problem-solving progression:

```text
LEARN → PRACTICE → INVESTIGATE → SOLVE → EXPLAIN → DEFEND
```

Unlike offensive CTFs that teach exploitation against live infrastructure, NexoraNet challenges focus exclusively on **defensive security reasoning**, **forensic artifact correlation**, **traffic decoding**, and **incident investigation**.

---

## 2. Core Architecture

The challenge system consists of four interconnected layers:

```text
┌────────────────────────────────────────────────────────┐
│                   Frontend Client                      │
│   ChallengesPage | ChallengeWorkspace | ResultPage     │
└──────────────────────────┬─────────────────────────────┘
                           │ JSON REST API
┌──────────────────────────▼─────────────────────────────┐
│                 FastAPI REST Endpoints                 │
│   /api/v1/challenges/* | Rate Limiting | Zero-Leak     │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│             Challenge & Attempt Services               │
│   FlagService (Salted SHA-256 & Constant Time)         │
│   AttemptService (Penalties, Velocity, Autosave)       │
│   AdaptiveChallengeService (Personalized Next Steps)   │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│                  Relational Storage                    │
│   challenges | challenge_stages | challenge_hints      │
│   challenge_evidence | challenge_attempts              │
└────────────────────────────────────────────────────────┘
```

---

## 3. Zero-Knowledge Flag Validation & Storage

To prevent client-side flag disclosure via browser developer tools or API inspection, raw flags are never returned by the backend:

1. **Salted SHA-256 Hashing:** Every challenge flag is hashed with a cryptographically secure 16-byte random salt generated via `secrets.token_hex(16)`.
2. **Constant-Time Verification:** Flag verification uses `secrets.compare_digest` to prevent timing side-channel attacks.
3. **Data Sanitization:** The public `/api/v1/challenges/{id}` endpoint completely strips `flag_hash` and `flag_salt` from responses.
4. **Answer Normalization:** The `FlagService` supports five validation modes:
   - `EXACT`: Case-sensitive exact match.
   - `CASE_INSENSITIVE`: Trims whitespace and normalizes case.
   - `NORMALIZED`: Removes extra internal whitespace and punctuation.
   - `NUMERIC`: Parses and compares numerical integer/float answers.
   - `IP_CIDR`: Normalizes IPv4 and CIDR block representations (e.g., `10.0.0.1/24`).

---

## 4. Progressive Hint System & Scoring Model

Every challenge includes progressive hints designed to coach students through obstacles without giving away the full answer immediately:

- **Hint Progression:** Hints must be unlocked sequentially (Hint 1 $\rightarrow$ Hint 2 $\rightarrow$ Hint 3).
- **Penalty Deductions:** Unlocking a hint applies a deterministic deduction (e.g., -10%, -25% of maximum points) to the attempt's score.
- **Minimum Score Guarantee:** Correctly solving a challenge always awards a minimum of 10 points regardless of hints used, ensuring effort is recognized.
- **Solution Reveal ("Give Up"):** Students may forfeit their attempt at any time to unlock the full technical walkthrough and common mistakes review. Revealed attempts award 0 points.

---

## 5. Anti-Enumeration & Velocity Limits

To prevent brute-force automated dictionary guessing:

- **Rate Limiting:** Enforces a minimum 2-second cooldown between consecutive submissions on an attempt.
- **Velocity Threshold:** Caps attempts at 25 guesses per challenge attempt before requiring hint review or remediation.
- **Submission History:** Logs all submitted flags, timestamps, and correctness in `challenge_submissions`.

---

## 6. Curated Content Summary

- **40 Synthetic Challenges:** Seeded across 4 difficulty tiers:
  - `BEGINNER`: 10 challenges (50–75 pts)
  - `INTERMEDIATE`: 12 challenges (100–125 pts)
  - `ADVANCED`: 12 challenges (150–200 pts)
  - `EXPERT`: 6 challenges (250–350 pts)
- **5 Training Tracks:**
  1. *Network Defender* (8 challenges)
  2. *SOC Analyst* (8 challenges)
  3. *Network Detection* (8 challenges)
  4. *Incident Investigator* (8 challenges)
  5. *Endpoint Investigator* (8 challenges)
