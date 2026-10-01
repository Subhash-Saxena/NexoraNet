# SOC Module Security Architecture & Boundary Guarantees

## 1. Safety Boundary & Defensive Sandbox

The NexoraNet SOC Dashboard is strictly an **offline educational simulator**.

### Explicitly Prohibited Capabilities:
- **No Live Packet Sniffing**: The system does not interface with raw network sockets (e.g. `AF_PACKET`, `libpcap` live capture).
- **No Active Packet Transmission**: No packets are transmitted, replayed, or injected into real physical networks.
- **No Active Network Remediation**: The dashboard does not alter host iptables, push firewall block rules, or isolate network adapters.
- **No Exploitation or Malware Execution**: Payloads inside capture files are never evaluated, uncompressed into executable memory, or executed.
- **No External Network Probing**: All endpoint context and flow metrics are derived from stored SQLite packet telemetry.

---

## 2. Platform Security Safeguards

1. **Authentication & Authorization**:
   - All SOC API routes require a valid user session.
   - Operations that assign or reclassify alerts enforce actor validation.
2. **Input Validation**:
   - Pydantic models validate all inputs, string lengths, and enum values.
   - Malformed JSON payloads in notes or evidence are safely caught without throwing 500 server crashes.
3. **IDOR & Multi-tenancy Protection**:
   - Inquiries into user-owned investigations and cases verify ownership or training lab tenancy.
4. **Append-Only Audit Trails**:
   - The `SocAuditLog` table maintains an immutable log of analyst actions to enforce accountability and prevent retroactive log tampering.
