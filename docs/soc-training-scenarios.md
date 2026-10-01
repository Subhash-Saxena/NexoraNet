# Educational SOC Training Scenarios & Rubric Evaluation

## 1. Built-in Practice Scenarios

NexoraNet seeds 5 pre-configured educational challenge scenarios:

1. **`investigate-tcp-activity` (Beginner)**:
   - Scenario: Multiple internal web servers receive bursty SYN packets on unusual ports.
   - Objective: Distinguish between standard client connections and automated port reconnaissance.
   - MITRE ATT&CK: `T1046` (Network Service Discovery).

2. **`investigate-dns-activity` (Intermediate)**:
   - Scenario: Workstation generating excessive NXDOMAIN responses with randomized subdomains.
   - Objective: Analyze DNS query rates and evaluate hypotheses regarding DNS tunneling vs misconfiguration.
   - MITRE ATT&CK: `T1071.004` (Application Layer Protocol: DNS).

3. **`investigate-arp-conflict` (Beginner)**:
   - Scenario: Conflicting Layer 2 MAC addresses claiming the subnet default gateway IP.
   - Objective: Inspect ARP requests and replies to detect spoofing or IP duplicate conflicts.
   - MITRE ATT&CK: `T1557.002` (Man-in-the-Middle: ARP Poisoning).

4. **`investigate-http-error-pattern` (Intermediate)**:
   - Scenario: Web server telemetry exhibiting bursts of HTTP 404/500 status codes.
   - Objective: Identify directory fuzzing or vulnerability scanning attempts.
   - MITRE ATT&CK: `T1595.002` (Active Scanning: Vulnerability Scanning).

5. **`investigate-multi-destination-traffic` (Advanced)**:
   - Scenario: Single internal host transmitting high-frequency outbound packets to diverse subnets.
   - Objective: Differentiate internal network discovery from broadcast noise.
   - MITRE ATT&CK: `T1018` (Remote System Discovery).

---

## 2. Objective Rubric Evaluation (5 Criteria, 20% Each)

When a student submits an investigation attempt, the system deterministically evaluates their work across 5 weighted criteria:

1. **Alert Triaged & Reviewed (20 pts)**:
   - Verification that alerts associated with the capture were examined.
2. **Classification Accuracy (20 pts)**:
   - Correctness of the classification decision (e.g. `SUSPICIOUS` vs `FALSE_POSITIVE`).
3. **Hypothesis Validity (20 pts)**:
   - Technical quality, clarity, and relevance of the formulated working hypothesis.
4. **Evidence Linking (20 pts)**:
   - Identification of corroborating packet numbers from the capture telemetry.
5. **Conclusion & Synthesis Depth (20 pts)**:
   - Thoroughness of the final analytical determination and defensive remediation plan.

**Passing Threshold:** ≥ 70% total score earns passing certification status with qualitative feedback tips.
