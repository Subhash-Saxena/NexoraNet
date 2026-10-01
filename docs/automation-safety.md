# NexoraNet Automation & Simulation Safety Guarantees

> **Core Invariant:** `simulation_only = True` across 100% of actions and entities.  
> **Target Audience:** Instructors, Auditors, Security Engineers, and Students.

---

## 1. Safety First Principle

NexoraNet is an offline educational simulator designed to teach defensive and analytical security concepts. Under no circumstances should NexoraNet function as, integrate with, or emulate a live remote access tool (RAT), active offensive exploit platform, or live endpoint management utility.

---

## 2. Strict Prohibition Inventory

The SOAR engine and scenario investigation workspaces strictly prohibit:

| Action Category | Prohibited Behavior | NexoraNet Enforcement Mechanism |
| :--- | :--- | :--- |
| **Code Execution** | `eval()`, `exec()`, arbitrary Python or JavaScript evaluation | Whitelist-based AST/regex condition evaluator with 13 approved operators. Zero dynamic code execution. |
| **Shell & OS Commands**| Invoking PowerShell, Bash, `cmd.exe`, `subprocess.Popen`, `os.system` | No subprocess, shell, or OS execution modules are imported or callable by playbook action handlers. |
| **Live Host Mutation** | Real process termination, registry modification, real filesystem deletion | All host actions mutate synthetic in-memory or SQLite records; host OS remains entirely untouched. |
| **Network Control** | Real firewall configuration (`iptables`, Windows Firewall), router ACL changes | Actions append records to synthetic rule tables (`SyntheticFirewallRule`), zero socket-level reconfigurations. |
| **Outbound Requests** | Real webhooks, public cloud API updates, live email sending | Notifications are written to the local `SocNotification` database table for simulated display. |
| **Credential Abuse** | Password dumping, LSASS memory inspection, token extraction | Only simulated synthetic username and role strings exist in the test datasets. |

---

## 3. Sandboxed Action Handlers

Every playbook action handler in `backend/app/services/soar/action_handlers.py` is pre-defined with a strict allowlist. When an action executes:
1. It validates parameters against static Pydantic schemas.
2. It interacts solely with local synthetic database models (`Case`, `SocNotification`, `IncidentEvidence`).
3. It emits an output dictionary containing `{ "status": "SIMULATED_SUCCESS", "simulation_only": True }`.

```python
# Guaranteed Invariant Pattern in action_handlers.py
return {
    "status": "SIMULATED_SUCCESS",
    "simulation_only": True,
    "action": "SIMULATED_ISOLATE_HOST",
    "details": f"Simulated network isolation applied to host {target_host} in educational lab.",
    "effective_time": datetime.now(timezone.utc).isoformat(),
}
```

---

## 4. Human-in-the-Loop Analyst Approvals

Automated playbooks carrying `risk_level in ["HIGH", "CRITICAL"]` or containing steps flagged with `requires_approval=True` cannot proceed automatically to containment:
- The execution state machine halts immediately before the gated step.
- Execution status transitions to `WAITING_APPROVAL`.
- A human analyst must review the telemetry and explicitly send an approval decision (`POST /api/v1/automation/executions/{id}/approve`).
- Rejection halts the workflow cleanly without executing the sensitive action.
- Every decision creates an immutable entry in the `AutomationAuditLog` database table.

---

## 5. Idempotency & Failure Tolerance

- Each playbook execution creates a SHA-256 idempotency key ensuring that redundant trigger signals (such as duplicate alerts) do not trigger runaway cascading actions.
- Step failures are contained: if a step fails, the playbook respects `on_failure="STOP"` or `on_failure="CONTINUE"`, with a strict cap of **maximum 2 retries** on simulated transient conditions.
