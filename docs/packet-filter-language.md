# NexoraNet — Display Filter Language Grammar & AST Engine

## Design Rationale: Safe Deterministic Filtering

Unlike generic packet query tools that use dynamic expression evaluation (`eval()`) or raw SQL string concatenation, NexoraNet implements a dedicated **Tokenizer**, **Abstract Syntax Tree (AST)** parser, and **SQLAlchemy Expression Compiler**.

This guarantees:
1. **Zero Code Injection**: Completely eliminates `eval()` and `exec()`.
2. **Strict Field Whitelisting**: Only valid networking attributes can be queried.
3. **Database Acceleration**: Compiles into indexed relational SQL `WHERE` clauses for high-speed pagination across thousands of packets.

---

## Filter Grammar Specification (EBNF)

```ebnf
Expression   ::= OrExpr
OrExpr       ::= AndExpr ( ("||" | "or") AndExpr )*
AndExpr      ::= NotExpr ( ("&&" | "and") NotExpr )*
NotExpr      ::= ( "!" | "not" ) NotExpr | Primary
Primary      ::= "(" Expression ")"
               | ProtocolKeyword
               | FlagCheck
               | Comparison

ProtocolKeyword ::= "tcp" | "udp" | "icmp" | "arp" | "dns" | "http" | "tls" | "dhcp" | "ip" | "ipv6"
FlagCheck       ::= "tcp.flags." ( "syn" | "ack" | "fin" | "rst" | "psh" | "urg" )
Comparison      ::= Field Operator Value
Operator        ::= "==" | "!=" | "<=" | ">=" | "<" | ">" | "contains"
Field           ::= "ip.src" | "ip.dst" | "ip.addr" | "tcp.srcport" | "tcp.dstport" | "tcp.port"
                  | "udp.srcport" | "udp.dstport" | "udp.port" | "eth.src" | "eth.dst" | "eth.addr"
                  | "frame.len" | "frame.number" | "frame.time" | "info"
Value           ::= StringLiteral | NumberLiteral | IPv4Literal
```

---

## Supported Filter Fields

| Filter Field | Description | Target Column | Example |
| :--- | :--- | :--- | :--- |
| `ip.src` | Source IPv4 or IPv6 address | `source_ip` | `ip.src == 10.0.0.5` |
| `ip.dst` | Destination IPv4 or IPv6 address | `destination_ip` | `ip.dst == 10.0.0.80` |
| `ip.addr` | Either source or destination IP | `source_ip OR destination_ip` | `ip.addr == 192.168.1.1` |
| `tcp.srcport` | TCP source port | `source_port` | `tcp.srcport == 50000` |
| `tcp.dstport` | TCP destination port | `destination_port` | `tcp.dstport == 80` |
| `tcp.port` | Either TCP source or destination port | `source_port OR destination_port` | `tcp.port == 443` |
| `udp.srcport` | UDP source port | `source_port` | `udp.srcport == 53000` |
| `udp.dstport` | UDP destination port | `destination_port` | `udp.dstport == 53` |
| `udp.port` | Either UDP source or destination port | `source_port OR destination_port` | `udp.port == 67` |
| `eth.src` | Source MAC address | `source_mac` | `eth.src == 00:1a:2b:3c:4d:5e` |
| `eth.dst` | Destination MAC address | `destination_mac` | `eth.dst == ff:ff:ff:ff:ff:ff` |
| `eth.addr` | Either source or destination MAC | `source_mac OR destination_mac` | `eth.addr == 00:11:22:33:44:55` |
| `frame.len` | Captured frame byte length | `captured_length` | `frame.len > 500` |
| `frame.number`| 1-indexed packet sequence number | `packet_number` | `frame.number <= 25` |
| `frame.time` | Relative arrival offset in seconds | `relative_time` | `frame.time >= 0.5` |
| `info` | Substring match in packet summary | `info` | `info contains "GET"` |

---

## TCP Flag Keywords

| Filter Keyword | Matches Packets Where |
| :--- | :--- |
| `tcp.flags.syn` | TCP header contains the `SYN` flag |
| `tcp.flags.ack` | TCP header contains the `ACK` flag |
| `tcp.flags.fin` | TCP header contains the `FIN` flag |
| `tcp.flags.rst` | TCP header contains the `RST` flag |
| `tcp.flags.psh` | TCP header contains the `PSH` flag |
| `tcp.flags.urg` | TCP header contains the `URG` flag |

---

## Example Filter Expressions

1. **Isolate all web traffic to a specific web server**:
   ```text
   ip.addr == 10.0.0.80 && (tcp.port == 80 || tcp.port == 443)
   ```

2. **Find connection initiation (SYN) packets**:
   ```text
   tcp.flags.syn && !tcp.flags.ack
   ```

3. **Inspect DNS lookups**:
   ```text
   dns || (udp.port == 53)
   ```

4. **Isolate ICMP diagnostic ping requests and replies**:
   ```text
   icmp && ip.addr == 192.168.1.10
   ```

5. **Detect large data transfers exceeding 1000 bytes**:
   ```text
   tcp && frame.len >= 1000
   ```
