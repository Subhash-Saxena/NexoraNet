# Indicator of Compromise (IOC) Analysis & Lifecycle

## 1. Supported Indicator Types

NexoraNet supports 5 standard network and cyber artifact types:

| Indicator Type | Description | Canonical Representation | Example |
| :--- | :--- | :--- | :--- |
| `IP_ADDRESS` | IPv4 and IPv6 network hosts | Canonical expanded/compressed IP | `198.51.100.25`, `2001:db8::1` |
| `DOMAIN` | Fully qualified domain names (FQDN) | Lowercase ASCII/IDNA, no trailing dot | `c2-controller.training.test` |
| `URL` | Web resource locators | Safe lowercase host, credentials stripped | `http://c2-controller.training.test:8080/beacon` |
| `FILE_HASH` | Cryptographic digests (MD5, SHA1, SHA256, SHA512) | Lowercase hexadecimal string | `a1b2c3d4e5f67890123456789abcdef...` |
| `EMAIL_ADDRESS` | Electronic mail sender or recipient | Lowercase `user@domain` | `attacker@phishing-campaign.training.test` |

---

## 2. Reputation Classifications

Analysts assign one of five classifications based on corroborated telemetry:

- **`MALICIOUS`**: Definitively confirmed threat infrastructure or malware payload. Associated with malicious command-and-control, active credential harvesting, or exploitation attempts.
- **`SUSPICIOUS`**: Abnormal behavior or telemetry that warrants active observation and escalation, but lacks definitive attribution (e.g. reconnaissance port scanning).
- **`BENIGN`**: Legitimate, verified benign infrastructure (e.g. public CDN edge servers, standard software update mirrors).
- **`FALSE_POSITIVE`**: Indicators that triggered security alerts or heuristics due to behavioral resemblance to threats, but have been analyzed and verified as non-malicious. Requires documented rationale.
- **`UNKNOWN`**: Indicators extracted from telemetry with no prior cataloged threat intelligence records. **Unknown is never assumed to be benign.**

---

## 3. Confidence & Severity Framework

### Confidence Levels
Confidence quantifies how certain analysts or intelligence feeds are regarding the assessment:
- **`HIGH`**: Multi-source corroboration, verified internal packet observations, or reproducible threat activity.
- **`MEDIUM`**: Reputable intelligence feed match without direct local forensic payload capture.
- **`LOW`**: Unverified single-source reporting, heuristic inferences, or newly observed unknown indicators.

### Severity Ratings
Severity measures potential operational impact on the enterprise:
- **`CRITICAL`**: Active C2 beaconing, ransomware droppers, or root-level compromise.
- **`HIGH`**: Targeted phishing links, credential exfiltration, or DNS tunneling channels.
- **`MEDIUM`**: Automated network reconnaissance, brute force attempts, or port scanners.
- **`LOW`**: Minor policy anomalies or informational probes.
- **`INFO`**: Verified benign infrastructure or reference records.

---

## 4. Indicator Lifecycle States

Indicators transition through defined operational states:
```text
NEW ──► ACTIVE ──► EXPIRED
  │        │
  │        ▼
  └──► FALSE_POSITIVE / REVOKED
```

1. **`NEW`**: Automatically extracted from incoming packet captures or detection alerts; awaiting initial review.
2. **`ACTIVE`**: Under active monitoring or confirmed in current intelligence feeds.
3. **`EXPIRED`**: Ephemeral infrastructure (e.g., dynamically generated domains or fast-flux IPs) that have ceased activity.
4. **`FALSE_POSITIVE`**: Formally cleared by an analyst with a documented justification.
5. **`REVOKED`**: Indicator retracted due to source error or feed poisoning.
