# SOC Alert Triage Methodology & 12-Step Checklist

## 1. The Triage Lifecycle

Alert triage is the systematic evaluation of incoming detection triggers to determine validity, impact, and required response.

```text
ALERT FIRED → ACKNOWLEDGE → 12-STEP INVESTIGATION → CLASSIFY → ESCALATE / RESOLVE
```

---

## 2. The 12-Step Analyst Checklist

NexoraNet guides students through a structured 12-step investigative checklist:

1. **Check Alert Metadata**: Verify detection rule ID, signature logic, severity, and priority rationale.
2. **Inspect Source Endpoint**: Check source IP, ephemeral port, device role, and total packets sent.
3. **Inspect Destination Endpoint**: Verify target service, destination port, internal subnet vs external host.
4. **Review Protocol & Flags**: Inspect TCP flags (`SYN`, `RST`, `ACK`), DNS query types (`A`, `TXT`), or HTTP request URIs.
5. **Inspect Packet Timeline**: Evaluate temporal sequence — bursty scan vs. continuous connection.
6. **Check Volume & Packet Frequency**: Check packet rates against known network baseline behavior.
7. **Check MITRE ATT&CK Mapping**: Identify adversary tactic (e.g. Discovery `T1046`, Exfiltration `T1048`).
8. **Correlate with Source Alerts**: Check if the same IP triggered prior scanning or credential alerts.
9. **Correlate with Destination Alerts**: Determine if target host is receiving anomalous traffic from multiple sources.
10. **Formulate Working Hypothesis**: Write a concise hypothesis explaining the technical nature of the anomaly.
11. **Select Triage Classification**: Assign one of the standard SOC classifications.
12. **Record Justification Note**: Document evidence citations, packet numbers, and reasoning in the audit trail.

---

## 3. Triage Classifications

| Classification | Meaning | Next Action |
| :--- | :--- | :--- |
| `BENIGN` | Legitimate business/operational network activity. | Close alert with notes. |
| `SUSPICIOUS` | Confirmed true anomaly requiring deep analysis. | Escalate to an Investigation. |
| `FALSE_POSITIVE` | Rule triggered inappropriately on clean telemetry. | Document logic tuning note. |
| `REQUIRES_MORE_DATA`| Inconclusive evidence from current capture window. | Request broader PCAP capture. |
| `CLOSED` | Fully addressed, remediated, or resolved. | Archived with audit trail. |
