# Threat Intelligence Origin Sources & Reliability

## 1. Intelligence Source Taxonomy

NexoraNet categorizes intelligence sources into 5 distinct operational tiers:

```text
┌─────────────────────────────────────────────────────────────┐
│              NexoraNet Intelligence Origin Feeds            │
├─────────────────┬─────────────────┬─────────────────────────┤
│ Tier            │ Source Type     │ Reliability             │
├─────────────────┼─────────────────┼─────────────────────────┤
│ Internal Core   │ INTERNAL        │ HIGH                    │
│ Educational     │ SYNTHETIC       │ HIGH                    │
│ Commercial Feed │ COMMERCIAL      │ HIGH                    │
│ OSINT / Public  │ PUBLIC          │ MEDIUM                  │
│ Crowdsourced    │ COMMUNITY       │ LOW                     │
└─────────────────┴─────────────────┴─────────────────────────┘
```

### Source Descriptions
1. **`NexoraNet Synthetic Threat Intelligence` (`SYNTHETIC`)**:
   - Primary educational repository utilizing RFC 5737 (`198.51.100.0/24`, `203.0.113.0/24`, `192.0.2.0/24`) and RFC 2606 (`.test`) reserved test ranges.
   - Purpose-built to teach analysts without exposing networks to real-world hostile infrastructure.
2. **`NexoraNet Internal Telemetry` (`INTERNAL`)**:
   - First-party sensor logs, firewall drops, switch netflows, and host events generated during lab exercises.
   - High analytical reliability because the observation context is known and verifiable.
3. **`Synthetic Commercial Threat Feed` (`COMMERCIAL`)**:
   - Simulates premium vendor intelligence feeds offering attributed campaign actor profiles, MITRE ATT&CK techniques, and threat signatures.
4. **`Synthetic OSINT Open Source Feed` (`PUBLIC`)**:
   - Simulates community threat sharing blogs, GitHub repositories, and security advisory lists.
   - Variable quality; requires analyst corroboration.
5. **`Synthetic Community Abuse List` (`COMMUNITY`)**:
   - Simulates unmoderated crowdsourced blocklists. Prone to false positives and stale data.

---

## 2. Source Reliability Scale

Source reliability follows intelligence community standards (Admiralty System):
- **`HIGH`**: Established track record of verified, highly curated findings; rigorous validation mechanisms.
- **`MEDIUM`**: Generally reliable, but occasionally includes unverified secondary citations or heuristic hits.
- **`LOW`**: Unverified crowd-sourced feeds or self-reported community submissions.
- **`UNKNOWN`**: New or unvetted external feeds.

---

## 3. Pedagogical Core: Reliability vs. Confidence

A fundamental SOC training concept is the distinction between **Source Reliability** and **Indicator Confidence**:

$$\text{Source Reliability} \neq \text{Indicator Confidence}$$

- **Example 1:** A `HIGH` reliability commercial feed reports a newly registered domain with `LOW` confidence because it has only observed one DNS query and no active command traffic yet.
- **Example 2:** A `LOW` reliability community list reports an IP that has been repeatedly corroborated by `HIGH` confidence internal packet captures showing active outbound beaconing.

Analysts must balance feed reputation with observed telemetry to formulate sound conclusions.
