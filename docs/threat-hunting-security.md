# NexoraNet Threat Hunting Security Architecture

## 1. Defensive Safety Principles

The **NexoraNet Threat Hunting Workspace** adheres to the platform's core safety mandate:

> **NexoraNet is an offline, defensive learning and simulation platform. It analyzes synthetic and imported telemetry offline and NEVER interacts with live external network targets.**

### Strict Behavioral Boundaries
1. **Zero Raw Socket Transmission**: The engine does not transmit raw packets, SYN packets, ICMP probes, or TCP connections to any network interface.
2. **Zero Active Scanning**: No port scanners (Nmap-style), vulnerability scanners, or active service probes exist within the hunting engine.
3. **Zero External Requests (SSRF Immunity)**: Investigated domains, IP addresses, and URLs are never fetched, DNS-resolved over live sockets, or pinged.
4. **Data vs. Code Distinction**: Telemetry events, packet payloads, HTTP headers, and script artifacts are treated strictly as read-only data strings, never executed in a shell or runtime.

---

## 2. Query Safety & Injection Prevention

Because the query engine evaluates complex condition trees and keyword searches, multiple layers of defense protect against injection attacks:

### Whitelisted Abstract Syntax Tree (AST) Evaluator
- **Field Whitelist**: Queries can only reference explicit columns mapped in `QUERY_FIELD_MAPPING` (`src_ip`, `dst_ip`, `src_port`, `dst_port`, `protocol`, `domain`, `summary`, etc.). Any unrecognized field name triggers an immediate `ValueError` and HTTP 400 rejection before database execution.
- **Operator Whitelist**: Only 11 safe operators are parsed (`=`, `!=`, `CONTAINS`, `STARTS_WITH`, `ENDS_WITH`, `IN`, `NOT_IN`, `>`, `<`, `>=`, `<=`).
- **ORM Parameterization**: All values are bound as parameterized variables in SQLAlchemy expressions (`column.ilike(:value)`, `column == :value`, `column.in_(:list)`). Zero string interpolation or SQL concatenation is permitted.
- **Wildcard Sanitization**: Search patterns automatically sanitize `%` and `_` characters to avoid intentional wildcard exhaustion or catastrophic DB performance degradation.

---

## 3. Resource & DoS Protection

Large datasets and complex entity graphs introduce potential denial-of-service vectors if unconstrained. The following limits are enforced:

| Defense Boundary | Constraint | Implementation |
| :--- | :--- | :--- |
| **Max Query Limit** | $\le 100$ records per page | Query parameter validation in FastAPI schema |
| **Max Graph Traversal Depth** | $\le 2$ hops | Hardcoded BFS/DFS iteration limit in `HuntService` |
| **Max Graph Node Count** | $\le 50$ nodes | Early termination guard in graph builder |
| **Max Pivot Co-occurrences** | $\le 50$ events | Clamped SQL limit in pivot correlator |
| **String Payload Size** | $\le 1000$ characters preview | Truncation in normalization service |

---

## 4. Input Sanitization & Content Security

- **Analyst Notes & Markdown**: Analyst journal entries, hypothesis text, and finding descriptions are sanitized against cross-site scripting (XSS) before rendering in the UI.
- **Payload Inspection**: Raw hexadecimal packet bytes are rendered in monospace visual containers with safe ASCII decoding (replacing unprintable characters with `.`).
- **Reserved IP & Domain Names**: All seed scenarios and mock telemetry strictly utilize IANA/IETF reserved documentation ranges:
  - IPv4: `192.0.2.0/24` (TEST-NET-1), `198.51.100.0/24` (TEST-NET-2), `203.0.113.0/24` (TEST-NET-3)
  - Private Networks: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`
  - Domains: `.test`, `.example`, `.invalid`, `.localhost`
