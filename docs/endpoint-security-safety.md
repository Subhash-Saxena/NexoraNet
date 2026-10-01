# Endpoint Security Simulator — Safety & Isolation Model

**NexoraNet** — *"Learn. Simulate. Analyze. Defend."*

---

## 1. Safety Mandate

NexoraNet is strictly an **educational platform** designed to provide realistic, hands-on defensive training without endangering student machines, institutional networks, or production systems.

Under no circumstances does Step 16 interact with the host operating system running the server or browser.

---

## 2. Technical Boundaries & Safeguards

| Safety Requirement | Implementation Standard in NexoraNet Step 16 |
|---|---|
| **No Live Endpoint Agents** | No Sysmon, Osquery, Falcon, Wazuh, or background monitoring daemons are deployed or required. All telemetry is synthetic data stored in the relational database. |
| **No Command Execution** | Zero execution of PowerShell, Bash, CMD, Python `eval()`, `exec()`, `os.system()`, or `subprocess.Popen()` triggered by telemetry analysis or user actions. |
| **No Process Enumeration** | The system does not query running processes on the host machine (`psutil`, `tasklist`, `ps` are forbidden). |
| **No Process Termination** | Students cannot terminate, pause, or kill any OS process. All "containment" or "mitigation" actions are analytical case notes or simulated responses. |
| **No Registry Editing** | No Windows Registry modifications (`winreg`, `reg.exe`) are executed. Registry events are simulated strings. |
| **No Real Malware** | No live malicious payloads, shellcode, or malicious scripts are stored or downloaded. Dropped files are synthetic filenames (`update.exe`, `exfil.sh`). |
| **RFC 5737 IP Ranges** | All external IP addresses strictly use documentation-reserved blocks: `192.0.2.0/24` (TEST-NET-1), `198.51.100.0/24` (TEST-NET-2), and `203.0.113.0/24` (TEST-NET-3). |
| **RFC 2606 Domain Names** | All external simulated domains use reserved TLDs: `.test`, `.example`, `.invalid`. No real internet domains are queried. |
| **IDOR Protection** | Investigation cases are strictly isolated per student. Students cannot access or tamper with cases belonging to other users. |

---

## 3. Threat Modeling & Defense Verification

1. **Synthetic Telemetry Seeding**:
   The database is initialized via static deterministic seed scripts (`scripts/seed_endpoint_security.py`).
2. **Safe Analytical Pivots**:
   Pivoting from an endpoint event into Threat Intel (Step 13) or Threat Hunting (Step 14) performs in-database lookups against normalized hashes and IP strings. No active DNS resolution or network scanning is conducted.
3. **Simulated Isolation**:
   When an analyst flags a host as `ISOLATED_SIMULATED`, it simply updates the synthetic database record (`EndpointHost.status = 'ISOLATED_SIMULATED'`). No firewall rules or network interface changes are executed.
