# NexoraNet — Packet Parser & Protocol Dissector Reference

## Architecture Overview

The `PcapParserService` decodes raw packet buffers into normalized relational records stored in SQLite / PostgreSQL. It leverages Scapy's streaming `PcapReader` in a pure-Python read context to guarantee clean resource handling across Windows and Linux environments.

---

## Supported Protocols & Extracted Header Fields

### Layer 2: Data Link

#### 1. Ethernet II
- **Fields Extracted**:
  - `src`: Source hardware MAC address (e.g. `00:1a:2b:3c:4d:5e`)
  - `dst`: Destination hardware MAC address or broadcast (`ff:ff:ff:ff:ff:ff`)
  - `type`: EtherType (e.g. `0x0800` for IPv4, `0x0806` for ARP, `0x86dd` for IPv6)

#### 2. Address Resolution Protocol (ARP)
- **Fields Extracted**:
  - `hwtype`: Hardware address format (typically `1` for Ethernet)
  - `ptype`: Protocol address format (typically `0x0800` for IPv4)
  - `op`: Operation code (`1` = who-has request, `2` = is-at response)
  - `hwsrc`: Sender hardware MAC
  - `psrc`: Sender protocol IPv4 address
  - `hwdst`: Target hardware MAC
  - `pdst`: Target protocol IPv4 address

---

### Layer 3: Network

#### 3. Internet Protocol Version 4 (IPv4)
- **Fields Extracted**:
  - `version`: IP version (`4`)
  - `ihl`: Internet Header Length (in 32-bit words)
  - `tos`: Type of Service / Differentiated Services Code Point (DSCP)
  - `len`: Total datagram length in bytes
  - `id`: Identification sequence number (for reassembly)
  - `flags`: Fragmentation flags (`DF` = Don't Fragment, `MF` = More Fragments)
  - `ttl`: Time to Live (hop counter)
  - `proto`: Transport protocol number (`6` = TCP, `17` = UDP, `1` = ICMP)
  - `chksum`: Header checksum
  - `src`: Source IPv4 address
  - `dst`: Destination IPv4 address

#### 4. Internet Protocol Version 6 (IPv6)
- **Fields Extracted**:
  - `version`: IP version (`6`)
  - `tc`: Traffic Class
  - `fl`: Flow Label
  - `plen`: Payload length
  - `nh`: Next Header (identifies L4 protocol or extension header)
  - `hlim`: Hop Limit
  - `src`: 128-bit source IPv6 address
  - `dst`: 128-bit destination IPv6 address

#### 5. Internet Control Message Protocol (ICMP)
- **Fields Extracted**:
  - `type`: Message category (`0` = Echo Reply, `3` = Destination Unreachable, `8` = Echo Request, `11` = Time Exceeded)
  - `code`: Sub-code providing context for unreachable/time exceeded messages
  - `chksum`: Checksum
  - `id`: Echo identifier
  - `seq`: Echo sequence number

---

### Layer 4: Transport

#### 6. Transmission Control Protocol (TCP)
- **Fields Extracted**:
  - `sport`: Source port
  - `dport`: Destination port
  - `seq`: Sequence number
  - `ack`: Acknowledgment number
  - `flags`: List of active control flags:
    - `SYN` (Synchronize connection)
    - `ACK` (Acknowledge reception)
    - `FIN` (Graceful connection teardown)
    - `RST` (Abrupt connection reset)
    - `PSH` (Push buffered data to application)
    - `URG` (Urgent pointer field significant)
  - `window`: Receiver window advertisement
  - `chksum`: TCP checksum

#### 7. User Datagram Protocol (UDP)
- **Fields Extracted**:
  - `sport`: Source port
  - `dport`: Destination port
  - `len`: UDP datagram length (header + payload)
  - `chksum`: Datagram checksum

---

### Layer 7: Application

#### 8. Domain Name System (DNS)
- **Fields Extracted**:
  - `id`: 16-bit transaction identifier
  - `qr`: Query (`0`) or Response (`1`) indicator
  - `opcode`: Standard query (`0`), inverse (`1`), server status (`2`)
  - `rcode`: Response return code (`0` = NoError, `3` = NXDomain, `2` = ServerFailure)
  - `qname`: Queried domain name (e.g. `example.com.`)
  - `qtype`: Resource record type (`A`, `AAAA`, `MX`, `CNAME`, `TXT`, `PTR`)
  - `answers`: Formatted list of returned record data (e.g. `93.184.216.34`)

#### 9. Hypertext Transfer Protocol (HTTP)
- **Fields Extracted**:
  - `first_line`: Request method + URI (e.g. `GET /api/v1/health HTTP/1.1`) or response status (e.g. `HTTP/1.1 200 OK`)
  - `raw_header_preview`: Sanitized ASCII representation of request/response headers (Host, User-Agent, Content-Type, Server) truncated to 512 bytes.

#### 10. Dynamic Host Configuration Protocol (DHCP)
- **Fields Extracted**:
  - `op`: Boot request (`1`) or boot reply (`2`)
  - `xid`: 32-bit transaction ID
  - `ciaddr`: Client IP address
  - `yiaddr`: "Your" assigned IP address
  - `siaddr`: Next server IP
  - `chaddr`: Client hardware MAC address
  - `message_type`: DHCP phase (`DISCOVER`, `OFFER`, `REQUEST`, `ACK`, `NAK`, `RELEASE`)

#### 11. Transport Layer Security (TLS Handshake Metadata)
- **Fields Extracted**:
  - `content_type`: Record layer type (`22` = Handshake)
  - `handshake_type`: Message type (`1` = ClientHello, `2` = ServerHello)
  - `version`: Negotiated TLS protocol version (`TLS 1.2`, `TLS 1.3`)
  - `server_name`: Server Name Indication (SNI) host header extracted passively from ClientHello extensions without decrypting session payload.
