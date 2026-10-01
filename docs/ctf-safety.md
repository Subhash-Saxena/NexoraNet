# Step 19: CTF Safety & Offline Simulation Invariants

## 1. Safety Mandate

NexoraNet is an **offline educational cybersecurity platform**. The CTF challenge engine is strictly constrained to prevent any offensive misuse or security risks on student workstations or networks:

> **CRITICAL INVARIANT:** NexoraNet CTF challenges never scan real networks, never query external domains, never execute live binaries, and never alter host system configurations.

All challenges operate exclusively with `simulation_only = True`.

---

## 2. Prohibited Capabilities & Guardrails

The following operations are strictly forbidden and eliminated by design:

| Prohibited Capability | Enforcement Mechanism |
|---|---|
| **Real network scanning** | Zero network sockets; packet traces are pre-generated JSON or offline fixtures. |
| **Outbound C2 requests** | Zero outbound HTTP/DNS lookups; domain analysis uses synthetic sandbox logs. |
| **Malware execution** | Zero binary execution; samples are represented solely by SHA-256 strings and disassemblies. |
| **Arbitrary code execution** | No `eval()`, no `exec()`, no `subprocess.Popen()` or shell invocations. |
| **Host system alteration** | No registry modifications, no process terminations, no file system changes outside the application database. |
| **Credential brute forcing** | Rate limits (2 seconds minimum between attempts) and hard attempt caps (25 attempts). |

---

## 3. Cryptographic Invariants for Flag Storage

1. **Zero Raw Flags in Database:**
   - Raw flags are never stored in plaintext within the persistent database schema.
   - All flags are stored as `flag_hash` using salted SHA-256 with unique 16-byte random salts.
2. **Zero-Knowledge API:**
   - The REST endpoints never return `flag_hash`, `flag_salt`, or plaintext stage answers.
   - Solution walkthroughs remain redacted until the student either solves the challenge or confirms an explicit surrender ("give up").
3. **Constant-Time Verification:**
   - Hash comparisons utilize Python's `secrets.compare_digest` to eliminate timing discrepancies that could leak byte matches.

---

## 4. Input Sanitization & Anti-Abuse

- **Submission String Truncation:** Submissions are bounded to a maximum length of 256 characters to avoid memory bloating and denial of service.
- **Notes Field Boundary:** Student scratchpad investigation notes are limited to 20,000 characters and sanitized before persistence.
- **Student Sandbox Isolation:** Each student's attempts and submissions are isolated by `user_id` and unique `attempt_id` UUID tokens.
