# Response Action Simulation Sandbox (Step 17)

## Overview

The **Response Action Simulation Sandbox** provides students with hands-on practice formulating and executing defensive incident response actions without the risk of affecting production systems or running dangerous scripts.

All response actions in NexoraNet operate under a strict, non-destructive **Simulation-Only Invariant**.

---

## 1. Safety Guarantees & Pedagogical Philosophy

### Invariant: Non-Destructive Simulated Execution
- **Zero Real Execution**: The platform NEVER runs real isolation commands, does not terminate live operating system processes, does not modify real host firewalls, and does not alter production Active Directory accounts.
- **Mandatory Flag**: Every response record in the database enforces `simulation_only = True` with a table-level check constraint.
- **Visual Safety Banners**: The user interface displays prominent warning banners on all simulation views:
  > *"NexoraNet Incident Response Lab — Synthetic Training Environment: All defensive actions executed within this workbench are non-destructive and simulated."*

### Purpose of Simulation
Real incident responders must understand the trade-offs between rapid containment and operational disruption:
- "If I isolate this domain controller, what business services will break?"
- "If I block this IP at the perimeter, will the attacker pivot to another proxy?"
- "If I kill the parent process before dumping its memory, do we lose forensic evidence?"

NexoraNet teaches these trade-offs by showing the **simulated outcome**, **side effects preview**, and **educational rationale** for every countermeasure.

---

## 2. Supported Simulated Defensive Action Types

### Containment Actions
- `SIMULATE_HOST_ISOLATION`: Severing network connectivity of an endpoint to prevent lateral movement while maintaining agent communication for forensics.
- `SIMULATE_ACCOUNT_RESTRICTION`: Disabling or locking an employee account compromised by brute force or phishing.
- `SIMULATE_NETWORK_BLOCK`: Injecting temporary firewall rules to drop traffic to a malicious C2 IP or external subnet.
- `SIMULATE_IOC_BLOCK`: Adding malicious domains or file hashes to perimeter gateway deny lists.
- `SIMULATE_SESSION_REVOCATION`: Invalidating active OAuth/SAML tokens or Kerberos tickets to eject an unauthorized session.

### Eradication Actions
- `SIMULATE_REMOVE_INDICATOR`: Quarantining malicious binaries or dropper scripts.
- `SIMULATE_REMOVE_PERSISTENCE`: Deleting rogue scheduled tasks, startup registry run keys, or cron jobs.
- `SIMULATE_RESET_CREDENTIAL`: Enforcing password rotation and Kerberos krbtgt account renewal.
- `SIMULATE_CLEAN_HOST`: Re-imaging or restoring an endpoint from a trusted golden image.

### Recovery Actions
- `SIMULATE_RESTORE_HOST`: Re-connecting a remediated workstation to the production network.
- `SIMULATE_RESTORE_SERVICE`: Bringing an authenticated web service back online after patching.
- `SIMULATE_REENABLE_ACCOUNT`: Restoring normal account access following password verification and security briefing.
- `SIMULATE_RESTORE_NETWORK`: Lifting temporary egress filter restrictions.

---

## 3. Action Lifecycle

```text
PROPOSED ──▶ EXECUTED (Simulated Outcome Recorded) ──▶ REVERTED
    │
    └──▶ CANCELLED
```

1. **Propose**: The analyst selects the category, action type, target (e.g. host `NN-DEV-001`), and writes the justification, risk assessment, and expected impact.
2. **Execute**: The simulator validates parameters, updates status to `EXECUTED`, generates a realistic educational outcome explanation, and logs the execution timestamp.
3. **Revert**: If an action caused unintended simulated business impact or if remediation has concluded, the analyst can revert the action to restore baseline simulated operational state.
