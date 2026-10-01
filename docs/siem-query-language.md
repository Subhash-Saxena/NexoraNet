# SIEM Query Language & Visual Filter Builder

**Step 15 — SIEM Query Syntax & Visual Condition Builder Guide**  
*Platform Tagline: "Learn. Simulate. Analyze. Defend."*

---

## 1. Visual Query Builder Concept

To teach query structuring without demanding syntax memorization from beginners, NexoraNet implements a safe, AST-driven **Visual Query Builder** backed by a deterministic REST API.

Every query consists of:
1. **Conditions Array**: List of field-level filter criteria.
2. **Logical Operator**: `AND` (all conditions must match) or `OR` (any condition may match).
3. **Full-Text Filter**: Free-form keyword search scanning across message, command summary, and metadata.
4. **Time Preset / Range**: `ALL`, `LAST_15M`, `LAST_1H`, `LAST_24H`, `LAST_7D`, or custom ISO datetimes.

---

## 2. Whitelisted Query Fields

Only secure, indexed columns in the normalized taxonomy may be queried:

* `action`: Action code (`LOGIN`, `LOGIN_FAILURE`, `CONNECTION_BLOCKED`, `DNS_QUERY`, `PROCESS_START`)
* `event_category`: Category (`AUTHENTICATION`, `FIREWALL`, `NETWORK`, `DNS`, `WEB`, `PROCESS`, `PRIVILEGE`)
* `source_type`: Collector type (`WINDOWS_SECURITY`, `LINUX_SSH`, `FIREWALL`, `DNS`, `WEB_SERVER`)
* `source_ip`: Originating IPv4/IPv6 address
* `destination_ip`: Target IPv4/IPv6 address
* `destination_port`: Target port number (`22`, `53`, `80`, `443`, `445`, `3389`)
* `username`: Subject identity
* `host`: Target host or computer name
* `protocol`: Transport/network protocol (`TCP`, `UDP`, `SSH`, `HTTP`, `DNS`)
* `severity`: Severity level (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`)
* `status`: Event outcome (`SUCCESS`, `FAILURE`, `BLOCKED`, `LOCKED`)
* `domain`: Queried DNS hostname
* `process_name`: Name of executed binary or daemon

---

## 3. Supported Relational Operators

| Operator | Meaning | Example |
| :--- | :--- | :--- |
| `=` | Exact match | `action = LOGIN_FAILURE` |
| `!=` | Inequality | `username != alice.smith` |
| `CONTAINS` | Substring match | `message CONTAINS sudo` |
| `STARTSWITH` | Prefix match | `source_ip STARTSWITH 198.51.100` |
| `>` | Greater than (integers / timestamps) | `destination_port > 1024` |
| `<` | Less than | `destination_port < 1024` |
| `>=` | Greater than or equal to | `destination_port >= 80` |
| `<=` | Less than or equal to | `destination_port <= 443` |

---

## 4. Example Queries

### 4.1 SSH Brute Force Detection
```json
{
  "conditions": [
    { "field": "action", "operator": "=", "value": "LOGIN_FAILURE" },
    { "field": "source_type", "operator": "=", "value": "LINUX_SSH" }
  ],
  "logical_op": "AND",
  "limit": 50
}
```

### 4.2 Inbound Firewall Probing
```json
{
  "conditions": [
    { "field": "action", "operator": "=", "value": "CONNECTION_BLOCKED" },
    { "field": "destination_port", "operator": "=", "value": 445 }
  ],
  "logical_op": "AND"
}
```

### 4.3 High-Risk Anomaly Investigation
```json
{
  "conditions": [
    { "field": "severity", "operator": "=", "value": "HIGH" },
    { "field": "severity", "operator": "=", "value": "CRITICAL" }
  ],
  "logical_op": "OR"
}
```
