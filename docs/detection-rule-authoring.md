# NexoraNet Detection Rule Authoring Guide

> **Target Audience:** Curriculum Creators, Instructors, Advanced Students  
> **Module:** Step 11 — Network Detection Engine

---

## 1. Rule Structure

Every detection rule in NexoraNet is defined with declarative metadata and parametric threshold configurations stored in the `detection_rules` table:

```json
{
  "rule_id": "NET-TCP-001",
  "name": "Repeated TCP SYN Connection Attempts",
  "description": "Identifies bursts of TCP SYN packets from a source without completed three-way handshakes.",
  "category": "TCP",
  "severity": "HIGH",
  "status": "ENABLED",
  "logic_type": "SYN_BURST_DETECTION",
  "threshold_config": {
    "min_syn_count": 5,
    "window_seconds": 10.0
  },
  "mitre_attack_id": "T1046",
  "mitre_technique": "Network Service Discovery",
  "explanation_template": "Identified {syn_count} TCP SYN packets targeting destination {destination_ip}:{destination_port} within {window_seconds}s.",
  "investigation_steps": [
    "Verify whether the destination responded with SYN-ACK or RST.",
    "Examine source host identity and running processes.",
    "Assess if the behavior matches legitimate application reconnection."
  ],
  "is_builtin": true
}
```

---

## 2. Core Fields Explained

1. **`rule_id`**: Unique string identifier following the `NET-<CATEGORY>-<NUMBER>` convention (e.g. `NET-DNS-001`).
2. **`category`**: Protocol or behavioral domain (`TCP`, `UDP`, `DNS`, `ARP`, `ICMP`, `HTTP`, `RECON`, `SUSPICIOUS_PORT`, `TRAFFIC`).
3. **`severity`**: Triage urgency indicator (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`).
4. **`logic_type`**: Evaluator routine hook in `backend/app/services/detection/detection_engine.py`.
5. **`threshold_config`**: JSON object containing numeric bounds, time intervals, port lists, or entropy thresholds.
6. **`explanation_template`**: Parameterized string rendered into the final alert explanation.
7. **`investigation_steps`**: Array of ordered, actionable instructions displayed to the student during SOC triage.

---

## 3. Supported Logic Types

| Logic Type | Parameters | Description |
| :--- | :--- | :--- |
| `SYN_BURST_DETECTION` | `min_syn_count`, `window_seconds` | Flags excessive SYN packets without ACK |
| `RST_SPIKE_DETECTION` | `min_rst_count`, `window_seconds` | Flags high volume of connection resets |
| `INCOMPLETE_HANDSHAKE_RATIO` | `ratio_threshold`, `min_total_connections` | Evaluates failed connection percentage |
| `BEACONING_DETECTION` | `min_events`, `max_interval_std_dev` | Detects regular automated check-ins |
| `HORIZONTAL_SWEEP` | `min_distinct_ips`, `window_seconds` | Detects subnet host discovery |
| `DNS_NXDOMAIN_BURST` | `min_nxdomain_count`, `window_seconds` | Detects failed domain query spikes |
| `DNS_HIGH_ENTROPY` | `min_entropy`, `min_length` | Detects randomized/encoded subdomains |
| `DNS_BURST_VOLUME` | `min_queries`, `window_seconds` | Detects rapid external DNS query spikes |
| `ARP_CONFLICT_DETECTION` | `min_macs_per_ip` | Detects conflicting MAC bindings |
| `ICMP_FLOOD_BURST` | `min_echo_requests`, `window_seconds` | Detects ICMP echo request bursts |
| `SUSPICIOUS_PORT_TRAFFIC` | `risk_ports` | Flags packets on known high-risk ports |
| `ASYMMETRIC_FLOW_VOLUME` | `ratio_threshold`, `min_bytes` | Detects heavy outbound data asymmetry |
| `PACKET_BURST_RATE` | `min_packets`, `window_seconds` | Detects sudden high-frequency surges |
| `HTTP_CLEARTEXT_AUTH` | `detect_headers` | Detects unencrypted credentials in transit |
| `VERTICAL_PORT_SCAN` | `min_distinct_ports`, `window_seconds` | Detects multi-port reconnaissance |

---

## 4. Testing Rules with the Sandbox API

Before enabling or deploying a rule, authors can execute a **dry-run simulation** without creating persistent database records:

### Request:
`POST /api/v1/detection/rules/test`
```json
{
  "rule_id": "NET-TCP-001",
  "capture_id": 14,
  "threshold_config": {
    "min_syn_count": 3,
    "window_seconds": 5.0
  }
}
```

### Response:
```json
{
  "rule_id": "NET-TCP-001",
  "matches_found": 2,
  "simulated_alerts": [
    {
      "title": "Repeated TCP SYN Connection Attempts Without Completion",
      "category": "TCP",
      "severity": "HIGH",
      "confidence": "HIGH",
      "source_ip": "192.168.1.100",
      "destination_ip": "192.168.1.50",
      "packet_count": 7,
      "evidence_count": 7
    }
  ],
  "execution_time_ms": 3.8
}
```

---

## 5. Authoring Best Practices

- **Avoid Sensationalism:** Write explanations that objectively describe the network behavior, why it was flagged, and what common benign mechanisms could cause it.
- **Provide Actionable Steps:** Write investigation steps that direct students to check specific packet headers, compare baseline volumes, and inspect related DNS or ARP records.
- **Calibrate Thresholds:** Ensure default thresholds are sensitive enough to catch educational capture exercises without overwhelming students with false alarms.
