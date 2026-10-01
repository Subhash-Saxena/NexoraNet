# Process Hierarchy & Telemetry Investigation Guide

**NexoraNet** — *"Learn. Simulate. Analyze. Defend."*

---

## 1. What is Process Hierarchy?

In modern operating systems, processes do not run in isolation; they are spawned by existing processes. This relationship is recorded as:
- **PID (Process Identifier)**: The numeric handle of the running program.
- **PPID (Parent Process Identifier)**: The numeric handle of the program that spawned it.
- **Process Lineage**: The ancestor chain leading from system initialization (`systemd` on Linux, `smss.exe` / `services.exe` / `explorer.exe` on Windows) down to ephemeral worker threads.

### Why Process Trees Matter to SOC Analysts

Attackers routinely abuse legitimate administrative shells (`powershell.exe`, `cmd.exe`, `bash`) or LOLBins (Living Off the Land Binaries like `certutil.exe`, `mshta.exe`, `curl`) to execute their payloads. Looking at the process name alone is insufficient; **the context of who spawned it and what it spawned tells the true story**:

| Typical Normal Execution | Suspicious Execution (Anomaly) |
|---|---|
| User double-clicks `powershell.exe` from Start Menu (Parent: `explorer.exe`) | Web server (`w3wp.exe` or `nginx`) spawns `cmd.exe` or `powershell.exe` (Web shell / RCE) |
| Word opens normal document (Parent: `explorer.exe`) | Word (`winword.exe`) spawns `cmd.exe` or `powershell.exe` (Malicious macro / exploit) |
| Browser renders webpage (`chrome.exe` spawns `chrome.exe --type=renderer`) | Browser spawns `powershell.exe` or `bash` with encoded command (Drive-by compromise) |
| PowerShell runs admin script interactively | PowerShell runs with `-nop -w hidden -enc` and downloads binary to `%TEMP%` (Ingress Tool Transfer) |

---

## 2. Process Integrity Levels

Windows assigns security integrity levels to token contexts:

1. **Untrusted**: Sandbox contexts (e.g., AppContainer, browser renderers).
2. **Low**: Protected mode (temporary internet files, isolated tabs).
3. **Medium**: Standard logged-on user applications (e.g., `explorer.exe`, user applications).
4. **High**: Elevated administrative contexts (User Account Control / UAC elevation, Run as Administrator).
5. **System**: Core operating system services (`NT AUTHORITY\SYSTEM`).

In Linux, a similar boundary exists between standard user UID processes and `UID 0` (`root`), often crossed via `sudo` or SUID binaries.

### Anomaly Indicator
If a process spawned by a medium-integrity parent suddenly runs with `HIGH` or `SYSTEM` integrity without an interactive UAC prompt event, this indicates **Privilege Escalation** (e.g. UAC bypass or kernel exploit).

---

## 3. Investigating Step 16 Synthetic Scenarios

In `ESCEN-01` (`Suspicious PowerShell Process Spawning` on `NN-WIN-002`), the student analyzes the following synthetic hierarchy:

```text
explorer.exe (PID 1000) [bob.developer - MEDIUM]
  └── powershell.exe (PID 2040) [bob.developer - MEDIUM]
        Arguments: powershell.exe -nop -w hidden -enc JABjAGw...
        Action: Ingress tool transfer from 198.51.100.45
        └── update.exe (PID 3180) [bob.developer - MEDIUM]
              Path: C:\Users\bob\AppData\Local\Temp\update.exe
              Arguments: update.exe --beacon-interval 60
              Egress: Sockets to 198.51.100.45:443 & DNS malicious-c2.training.test
```

### Educational Takeaways:
- Obfuscated base64 flags (`-enc`) hide download commands.
- Temporary directory staging (`AppData\Local\Temp`) indicates unauthorized binary drops.
- Correlating the spawned PID (`3180`) with network telemetry reveals the C2 beacon destination (`198.51.100.45:443`).
