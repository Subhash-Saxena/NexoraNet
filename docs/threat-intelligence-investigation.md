# Threat Intelligence Investigation Workflow & Challenges

## 1. Step-by-Step Investigation Workflow

When a Tier-1 SOC analyst encounters a suspicious network artifact, they follow a standardized 6-phase triage methodology:

```text
1. DISCOVERY & EXTRACTION
   │ Extracted from PCAP packets, detection alerts, or user reports.
   ▼
2. NORMALIZATION & DEFANGING
   │ Convert defanged URLs/IPs into canonical format; redact credentials.
   ▼
3. THREAT INTEL ENRICHMENT
   │ Query repository for reputation, confidence, and MITRE mapping.
   ▼
4. TELEMETRY CORROBORATION
   │ Cross-examine internal PCAP streams, packet counts, ports, and alerts.
   ▼
5. ENTITY CORRELATION & GRAPHING
   │ Trace related domains, IP resolutions, and associated incident cases.
   ▼
6. ACTIONABLE SOC DISPOSITION
   │ Formulate conclusion, add to watchlist, tune rules, or escalate to Tier-2.
```

---

## 2. Hands-On Investigation Challenges

NexoraNet includes 5 hands-on educational scenarios:

### Challenge 1: Command & Control IP Attribution (`c2-ip-attribution`)
- **Difficulty:** Beginner
- **Scenario:** Outbound HTTP POST traffic on port 8080 from internal host `10.0.0.45` to `198.51.100.25` at fixed 60-second intervals.
- **Expected Classification:** `MALICIOUS`
- **Learning Goal:** Identify C2 heartbeat patterns, correlate with domain `c2-controller.training.test`, and recommend perimeter containment.

### Challenge 2: Typosquatting Phishing Domain Analysis (`typosquatting-phishing-domain`)
- **Difficulty:** Beginner
- **Scenario:** An employee forwards an urgent email redirecting to `https://portal-nexora-login.training.test/auth/login`.
- **Expected Classification:** `MALICIOUS`
- **Learning Goal:** Inspect domain registration nuances, correlate with sender email, and prevent credential harvesting.

### Challenge 3: Malicious Dropper File Hash Triage (`malicious-file-hash-triage`)
- **Difficulty:** Intermediate
- **Scenario:** SHA-256 digest `a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0` extracted during an HTTP file download.
- **Expected Classification:** `MALICIOUS`
- **Learning Goal:** Map hash to MITRE ATT&CK technique T1204.002 and initiate endpoint isolation.

### Challenge 4: High-Volume CDN False Positive Investigation (`benign-cdn-false-positive`)
- **Difficulty:** Intermediate
- **Scenario:** IP `192.0.2.50` triggers a heuristic rule for high outbound data volume. Junior analyst proposes perimeter blocking.
- **Expected Classification:** `BENIGN` / `FALSE_POSITIVE`
- **Learning Goal:** Distinguish legitimate CDN asset distribution from exfiltration; avoid disruptive false-positive firewall blocks.

### Challenge 5: DNS Exfiltration Tunneling Domain (`dns-tunneling-exfiltration-domain`)
- **Difficulty:** Advanced
- **Scenario:** High-entropy base64 TXT and NULL queries directed to subdomains of `tunnel-exfil.training.test`.
- **Expected Classification:** `MALICIOUS`
- **Learning Goal:** Recognize DNS tunneling covert channels, correlate with rogue nameserver `198.51.100.99`, and implement DNS detection tuning.

---

## 3. Five-Dimension Pedagogical Rubric

Student submissions are evaluated by `ChallengeService` against a 100-point rubric with a 70% passing threshold:

| Dimension | Points | Pedagogical Criteria |
| :--- | :--- | :--- |
| **1. IOC Identification & Classification** | 20 pts | Correctly assigns reputation (`MALICIOUS`, `SUSPICIOUS`, `BENIGN`, `FALSE_POSITIVE`). |
| **2. Evidence Review & Observation Rigor** | 20 pts | Cites specific telemetry details (packet numbers, intervals, ports, queries). |
| **3. Threat Intelligence Interpretation** | 20 pts | Evaluates source reliability and distinguishes feed confidence from local telemetry. |
| **4. Correlation & Relationship Context** | 20 pts | Traces connected infrastructure (resolutions, C2 hosts, related alerts). |
| **5. Defensible SOC Conclusion** | 20 pts | Formulates actionable next steps (watchlist monitoring, rule tuning, containment). |
