# NexoraNet Hunt Query Language (HQL) & Query Engine

## 1. Overview

The **NexoraNet Hunt Query Engine** empowers students to interrogate extensive network telemetry, detection alerts, and threat intelligence records without exposing the database to SQL injection, catastrophic backtracking, or arbitrary code execution vulnerabilities.

HQL uses a strictly governed, whitelist-backed Abstract Syntax Tree (AST) evaluator. Queries are parsed and transformed into parameterized SQLAlchemy expressions executed within safe resource limits (bounded page size, execution timers, and sanitized wildcards).

---

## 2. Field Whitelist & Types

Only approved fields from the `HuntEvent` model are accessible in hunt queries. Unknown or unapproved field names trigger immediate validation errors.

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `event_type` | String | Event classification (`NETWORK_FLOW`, `DNS_QUERY`, `HTTP_REQUEST`, `TLS_HANDSHAKE`, etc.) |
| `protocol` | String | Transport / application protocol (`TCP`, `UDP`, `DNS`, `HTTP`, `TLS`, `ICMP`, `SMB`, etc.) |
| `src_ip` | IP String | Source IPv4 or IPv6 address |
| `src_port` | Integer | Source port number (1 - 65535) |
| `dst_ip` | IP String | Destination IPv4 or IPv6 address |
| `dst_port` | Integer | Destination port number (1 - 65535) |
| `domain` | String | FQDN or hostname observed in DNS queries, HTTP headers, or TLS SNI |
| `summary` | String | Brief human-readable description of the network event |
| `is_suspicious` | Boolean | Pre-flagged indicator of interest (`true` or `false`) |
| `severity` | String | Event severity rating (`INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) |
| `packet_id` | Integer | Optional reference to raw PCAP packet index |
| `detection_alert_id` | Integer | Optional reference to originating detection alert |
| `timestamp` | DateTime | Timestamp when event was observed |

---

## 3. Allowed Comparison Operators

HQL supports 11 deterministic operators:

| Operator | Syntax | Description | Example |
| :--- | :--- | :--- | :--- |
| `EQUALS` | `=` | Exact match (case-insensitive for strings) | `dst_port = 53` |
| `NOT_EQUALS` | `!=` | Value does not equal target | `protocol != "ARP"` |
| `CONTAINS` | `CONTAINS` | Substring match (SQL `LIKE %val%`) | `domain CONTAINS "evil"` |
| `STARTS_WITH` | `STARTS_WITH` | Prefix match (SQL `LIKE val%`) | `src_ip STARTS_WITH "192.168.1."` |
| `ENDS_WITH` | `ENDS_WITH` | Suffix match (SQL `LIKE %val`) | `domain ENDS_WITH ".test"` |
| `GREATER_THAN` | `>` | Numeric / date strictly greater than | `dst_port > 1024` |
| `GREATER_EQUAL`| `>=` | Numeric / date greater than or equal | `dst_port >= 80` |
| `LESS_THAN` | `<` | Numeric / date strictly less than | `dst_port < 1024` |
| `LESS_EQUAL` | `<=` | Numeric / date less than or equal | `dst_port <= 443` |
| `IN` | `IN` | Value is present in comma-separated list | `protocol IN ("DNS", "HTTP")` |
| `NOT_IN` | `NOT_IN` | Value is absent from comma-separated list | `dst_port NOT_IN (80, 443)` |

---

## 4. Query Structure & Parameters

Queries are submitted via POST to `/api/v1/threat-hunting/query` or filtered via GET `/api/v1/threat-hunting/events`.

### JSON Request Payload Schema
```json
{
  "dataset_id": 1,
  "conditions": [
    {
      "field": "protocol",
      "operator": "=",
      "value": "DNS"
    },
    {
      "field": "domain",
      "operator": "CONTAINS",
      "value": "tunnel"
    }
  ],
  "logical_op": "AND",
  "search_text": "exfil",
  "limit": 50,
  "offset": 0,
  "sort_by": "timestamp",
  "sort_asc": false
}
```

### Logical Operations
- `AND`: Every condition in the `conditions` array must evaluate to true.
- `OR`: Any condition in the `conditions` array must evaluate to true.
- When `search_text` is supplied, it is combined with `AND` against the logical block, performing an automated substring search across `summary`, `src_ip`, `dst_ip`, and `domain`.

---

## 5. Execution Metrics & Explanation

Each query returns diagnostic execution telemetry:
- `query_time_ms`: Wall-clock execution time in milliseconds.
- `human_readable`: Plain English explanation of the AST filter tree (e.g. *"protocol EQUALS 'DNS' AND domain CONTAINS 'tunnel' (dataset: 1)"*).
- `total`: Total matching records count.
- `events`: Array of sanitized `HuntEvent` objects.

```json
{
  "total": 34,
  "query_time_ms": 1.45,
  "human_readable": "protocol = 'DNS' AND domain CONTAINS 'tunnel' AND text CONTAINS 'exfil'",
  "events": [ ... ]
}
```
