# NexoraNet — PCAP Engine Safety & Security Architecture

## The Defensive Principle: Offline Analysis Only

The NexoraNet PCAP & Packet Analysis Engine operates strictly as an **offline defensive forensics tool**. It is built on the core security premise that:

$$\textbf{PCAP files are data to analyze, never instructions to execute.}$$

---

## Strict Safety Boundaries

The PCAP engine enforces the following technical boundaries:

1. **Zero Raw Socket Transmission**:
   - The engine does not send packets over the local network interface.
   - It will never replay or retransmit captured traffic toward any internal or external host.

2. **Zero Network Sniffing / Interception**:
   - The engine does not capture live packets from the user's host network card or local loopback.
   - It does not install kernel packet capture drivers (e.g. WinPcap, Npcap) and requires no elevated root/Administrator privileges.

3. **Zero Payload Execution**:
   - Application layer payloads (e.g. JavaScript, HTML, shellcode, binary blobs) are never parsed by a browser scripting engine or executed by local sub-processes.
   - HTTP previews are strictly encoded as sanitized ASCII text strings without evaluating `<script>` tags or inline DOM elements.

4. **Zero Remote Target Probing**:
   - The engine never initiates HTTP requests, DNS queries, or TCP handshakes toward IP addresses or domains identified inside a packet capture.
   - All addresses are treated as static analytical symbols.

5. **Safe Display Filter Architecture**:
   - The filter parser operates entirely through a deterministic lexer and recursive-descent AST compiler.
   - No Python `eval()`, `exec()`, or raw shell commands are ever invoked to evaluate user filter criteria.

---

## File Upload Hardening

To protect the server environment against file upload exploits and resource exhaustion, the backend applies the following security controls:

- **File Size Ceiling**: Strictly capped at 50 MB (`MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024`). Files exceeding this size are rejected immediately prior to reading into memory.
- **Extension Whitelist**: Only `.pcap`, `.pcapng`, and `.cap` files are accepted.
- **Extension Blacklist**: Explicit blocklist rejects dangerous binary formats (`.exe`, `.dll`, `.bat`, `.cmd`, `.sh`, `.py`, `.js`, `.vbs`, `.ps1`, `.msi`, `.jar`, `.scr`, `.com`, `.bin`).
- **Path Traversal Protection**: Uploaded files are stripped of client path metadata via `pathlib.Path(sanitized_name).name`. Internally, files are persisted with UUID4 identifiers (`capture_{uuid}.pcap`) in a sandboxed directory (`backend/data/captures/`), completely preventing directory traversal attacks.
- **Resource Limits**: Parser enforces a cap of 5,000 parsed packets per capture (`MAX_PACKETS_TO_STORE`) to ensure memory safety and deterministic query speeds.

---

## Prominent Disclaimers

The user interface renders prominent security notices across all analysis views:

> [!NOTE]
> **NexoraNet analyzes packet captures offline.** It does not transmit, replay, or execute captured network traffic. Packet captures may contain sensitive network information. Only analyze captures you are authorized to use.
