"""Script to generate synthetic educational PCAP files and seed them into the NexoraNet PCAP library.

Strictly offline: Generates packets in memory and writes them using Scapy wrpcap.
Never transmits, replays, or injects raw packets into the real host network.
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from scapy.all import Ether, IP, TCP, UDP, ICMP, ARP, DNS, DNSQR, DNSRR, Raw, wrpcap
from scapy.layers.dhcp import BOOTP, DHCP

from app.core.pcap_config import pcap_settings
from app.db.session import SessionLocal
from app.models.enums import CaptureStatus
from app.models.pcap import Capture
from app.services.pcap_parser_service import pcap_parser_service


def generate_synthetic_pcaps(dest_dir: Path) -> dict[str, dict]:
    """Generate offline synthetic PCAPs and return catalog metadata."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    catalog: dict[str, dict] = {}

    # 1. basic_ping.pcap
    p1 = dest_dir / "basic_ping.pcap"
    pkts1 = []
    base_t = 1700000000.0
    for i in range(1, 5):
        req = Ether(src="02:00:00:00:01:01", dst="02:00:00:00:00:01") / IP(src="192.168.1.10", dst="192.168.1.1") / ICMP(type=8, id=0x1234, seq=i)
        req.time = base_t + (i - 1) * 1.0
        rep = Ether(src="02:00:00:00:00:01", dst="02:00:00:00:01:01") / IP(src="192.168.1.1", dst="192.168.1.10") / ICMP(type=0, id=0x1234, seq=i)
        rep.time = req.time + 0.002
        pkts1.extend([req, rep])
    wrpcap(str(p1), pkts1)
    catalog["basic_ping.pcap"] = {
        "name": "Basic ICMP Echo (Ping)",
        "difficulty": "Beginner",
        "description": "Standard ICMP Echo Request and Reply round-trip ping exchange between a workstation and default gateway.",
    }

    # 2. tcp_handshake.pcap
    p2 = dest_dir / "tcp_handshake.pcap"
    pkts2 = []
    t = base_t + 10.0
    s_mac, d_mac = "02:00:00:00:00:02", "02:00:00:00:00:03"
    s_ip, d_ip = "10.0.0.5", "10.0.0.10"
    sp, dp = 51544, 80

    # SYN
    p = Ether(src=s_mac, dst=d_mac) / IP(src=s_ip, dst=d_ip) / TCP(sport=sp, dport=dp, flags="S", seq=1000, window=64240)
    p.time = t
    pkts2.append(p)

    # SYN-ACK
    t += 0.0015
    p = Ether(src=d_mac, dst=s_mac) / IP(src=d_ip, dst=s_ip) / TCP(sport=dp, dport=sp, flags="SA", seq=5000, ack=1001, window=65535)
    p.time = t
    pkts2.append(p)

    # ACK
    t += 0.0005
    p = Ether(src=s_mac, dst=d_mac) / IP(src=s_ip, dst=d_ip) / TCP(sport=sp, dport=dp, flags="A", seq=1001, ack=5001, window=64240)
    p.time = t
    pkts2.append(p)

    # HTTP GET
    t += 0.010
    http_payload = b"GET /index.html HTTP/1.1\r\nHost: intranet.local\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
    p = Ether(src=s_mac, dst=d_mac) / IP(src=s_ip, dst=d_ip) / TCP(sport=sp, dport=dp, flags="PA", seq=1001, ack=5001) / Raw(load=http_payload)
    p.time = t
    pkts2.append(p)

    # HTTP ACK
    t += 0.002
    p = Ether(src=d_mac, dst=s_mac) / IP(src=d_ip, dst=s_ip) / TCP(sport=dp, dport=sp, flags="A", seq=5001, ack=1001 + len(http_payload))
    p.time = t
    pkts2.append(p)

    # HTTP 200 OK Response
    t += 0.005
    resp_payload = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 45\r\n\r\n<html><body><h1>NexoraNet Server</h1></body></html>"
    p = Ether(src=d_mac, dst=s_mac) / IP(src=d_ip, dst=s_ip) / TCP(sport=dp, dport=sp, flags="PA", seq=5001, ack=1001 + len(http_payload)) / Raw(load=resp_payload)
    p.time = t
    pkts2.append(p)

    # Final ACK
    t += 0.001
    p = Ether(src=s_mac, dst=d_mac) / IP(src=s_ip, dst=d_ip) / TCP(sport=sp, dport=dp, flags="A", seq=1001 + len(http_payload), ack=5001 + len(resp_payload))
    p.time = t
    pkts2.append(p)

    wrpcap(str(p2), pkts2)
    catalog["tcp_handshake.pcap"] = {
        "name": "TCP 3-Way Handshake & HTTP Request",
        "difficulty": "Beginner",
        "description": "Complete SYN -> SYN-ACK -> ACK connection establishment followed by an HTTP GET and 200 OK response.",
    }

    # 3. dns_lookup.pcap
    p3 = dest_dir / "dns_lookup.pcap"
    pkts3 = []
    t = base_t + 20.0
    # Query 1: example.com
    q1 = Ether() / IP(src="192.168.1.50", dst="192.168.1.1") / UDP(sport=54321, dport=53) / DNS(rd=1, id=0x0001, qd=DNSQR(qname="example.com"))
    q1.time = t
    r1 = Ether() / IP(src="192.168.1.1", dst="192.168.1.50") / UDP(sport=53, dport=54321) / DNS(id=0x0001, qr=1, aa=1, qd=DNSQR(qname="example.com"), an=DNSRR(rrname="example.com", rdata="93.184.216.34"))
    r1.time = t + 0.015
    pkts3.extend([q1, r1])

    # Query 2: internal.corp
    t += 0.5
    q2 = Ether() / IP(src="192.168.1.50", dst="192.168.1.1") / UDP(sport=54322, dport=53) / DNS(rd=1, id=0x0002, qd=DNSQR(qname="internal.corp"))
    q2.time = t
    r2 = Ether() / IP(src="192.168.1.1", dst="192.168.1.50") / UDP(sport=53, dport=54322) / DNS(id=0x0002, qr=1, aa=1, qd=DNSQR(qname="internal.corp"), an=DNSRR(rrname="internal.corp", rdata="192.168.1.100"))
    r2.time = t + 0.008
    pkts3.extend([q2, r2])

    # Query 3: nxdomain
    t += 0.5
    q3 = Ether() / IP(src="192.168.1.50", dst="192.168.1.1") / UDP(sport=54323, dport=53) / DNS(rd=1, id=0x0003, qd=DNSQR(qname="unknown-hostname-xyz.local"))
    q3.time = t
    r3 = Ether() / IP(src="192.168.1.1", dst="192.168.1.50") / UDP(sport=53, dport=54323) / DNS(id=0x0003, qr=1, rcode=3, qd=DNSQR(qname="unknown-hostname-xyz.local"))
    r3.time = t + 0.020
    pkts3.extend([q3, r3])

    wrpcap(str(p3), pkts3)
    catalog["dns_lookup.pcap"] = {
        "name": "Standard DNS Resolution & NXDOMAIN",
        "difficulty": "Beginner",
        "description": "DNS queries for public and corporate domain names, culminating in an NXDOMAIN non-existent domain response.",
    }

    # 4. http_request.pcap
    p4 = dest_dir / "http_request.pcap"
    pkts4 = []
    t = base_t + 30.0
    for ep, uri in [("GET", "/login"), ("POST", "/api/auth"), ("GET", "/dashboard"), ("GET", "/notfound")]:
        status_code = b"200 OK" if uri != "/notfound" else b"404 Not Found"
        req = Ether() / IP(src="192.168.1.25", dst="192.168.1.80") / TCP(sport=48000, dport=80, flags="PA") / Raw(load=f"{ep} {uri} HTTP/1.1\r\nHost: app.local\r\n\r\n".encode())
        req.time = t
        resp = Ether() / IP(src="192.168.1.80", dst="192.168.1.25") / TCP(sport=80, dport=48000, flags="PA") / Raw(load=b"HTTP/1.1 " + status_code + b"\r\nContent-Type: text/plain\r\n\r\nData")
        resp.time = t + 0.005
        pkts4.extend([req, resp])
        t += 0.2
    wrpcap(str(p4), pkts4)
    catalog["http_request.pcap"] = {
        "name": "HTTP Web Application Session",
        "difficulty": "Intermediate",
        "description": "Interactive web session showing GET and POST methods, successful 200 OK responses, and 404 Not Found errors.",
    }

    # 5. dhcp_exchange.pcap
    p5 = dest_dir / "dhcp_exchange.pcap"
    pkts5 = []
    t = base_t + 40.0
    cli_mac = "02:00:00:aa:bb:cc"
    # Discover
    p_disc = Ether(src=cli_mac, dst="ff:ff:ff:ff:ff:ff") / IP(src="0.0.0.0", dst="255.255.255.255") / UDP(sport=68, dport=67) / BOOTP(chaddr=b"\x02\x00\x00\xaa\xbb\xcc") / DHCP(options=[("message-type", 1), "end"])
    p_disc.time = t
    # Offer
    t += 0.05
    p_off = Ether(src="02:00:00:00:00:01", dst=cli_mac) / IP(src="192.168.1.1", dst="192.168.1.150") / UDP(sport=67, dport=68) / BOOTP(yiaddr="192.168.1.150", chaddr=b"\x02\x00\x00\xaa\xbb\xcc") / DHCP(options=[("message-type", 2), ("server_id", "192.168.1.1"), "end"])
    p_off.time = t
    # Request
    t += 0.02
    p_req = Ether(src=cli_mac, dst="ff:ff:ff:ff:ff:ff") / IP(src="0.0.0.0", dst="255.255.255.255") / UDP(sport=68, dport=67) / BOOTP(chaddr=b"\x02\x00\x00\xaa\xbb\xcc") / DHCP(options=[("message-type", 3), ("requested_addr", "192.168.1.150"), ("server_id", "192.168.1.1"), "end"])
    p_req.time = t
    # ACK
    t += 0.04
    p_ack = Ether(src="02:00:00:00:00:01", dst=cli_mac) / IP(src="192.168.1.1", dst="192.168.1.150") / UDP(sport=67, dport=68) / BOOTP(yiaddr="192.168.1.150", chaddr=b"\x02\x00\x00\xaa\xbb\xcc") / DHCP(options=[("message-type", 5), ("server_id", "192.168.1.1"), "end"])
    p_ack.time = t
    pkts5.extend([p_disc, p_off, p_req, p_ack])
    wrpcap(str(p5), pkts5)
    catalog["dhcp_exchange.pcap"] = {
        "name": "DHCP 4-Way DORA Lease Negotiation",
        "difficulty": "Beginner",
        "description": "Complete Dynamic Host Configuration Protocol exchange: Discover, Offer, Request, and Acknowledgment.",
    }

    # 6. arp_resolution.pcap
    p6 = dest_dir / "arp_resolution.pcap"
    pkts6 = []
    t = base_t + 50.0
    a1 = Ether(src="02:00:00:01:00:01", dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, hwsrc="02:00:00:01:00:01", psrc="192.168.1.50", hwdst="00:00:00:00:00:00", pdst="192.168.1.1")
    a1.time = t
    a2 = Ether(src="02:00:00:00:00:01", dst="02:00:00:01:00:01") / ARP(op=2, hwsrc="02:00:00:00:00:01", psrc="192.168.1.1", hwdst="02:00:00:01:00:01", pdst="192.168.1.50")
    a2.time = t + 0.001
    pkts6.extend([a1, a2])
    wrpcap(str(p6), pkts6)
    catalog["arp_resolution.pcap"] = {
        "name": "ARP Request and Resolution",
        "difficulty": "Beginner",
        "description": "Layer 2 Address Resolution Protocol query broadcast and unicast reply resolving default gateway hardware address.",
    }

    # 7. tcp_reset.pcap
    p7 = dest_dir / "tcp_reset.pcap"
    pkts7 = []
    t = base_t + 60.0
    for port in [23, 22, 21]:
        syn = Ether(src="02:00:00:01:00:01", dst="02:00:00:00:00:01") / IP(src="192.168.1.15", dst="192.168.1.1") / TCP(sport=51000 + port, dport=port, flags="S", seq=100)
        syn.time = t
        rst = Ether(src="02:00:00:00:00:01", dst="02:00:00:01:00:01") / IP(src="192.168.1.1", dst="192.168.1.15") / TCP(sport=port, dport=51000 + port, flags="RA", seq=0, ack=101)
        rst.time = t + 0.002
        pkts7.extend([syn, rst])
        t += 0.1
    wrpcap(str(p7), pkts7)
    catalog["tcp_reset.pcap"] = {
        "name": "TCP Connection Reset (RST) Events",
        "difficulty": "Intermediate",
        "description": "Connection attempts to closed ports (Telnet, SSH, FTP) being rejected with TCP RST flags.",
    }

    # 8. multi_host_traffic.pcap
    p8 = dest_dir / "multi_host_traffic.pcap"
    pkts8 = []
    t = base_t + 70.0
    for host_idx in range(1, 6):
        src_ip = f"192.168.1.{10 + host_idx}"
        p = Ether() / IP(src=src_ip, dst="192.168.1.200") / TCP(sport=40000 + host_idx, dport=80, flags="S", seq=host_idx * 100)
        p.time = t + host_idx * 0.05
        pkts8.append(p)
    wrpcap(str(p8), pkts8)
    catalog["multi_host_traffic.pcap"] = {
        "name": "Enterprise Multi-Host Campus Traffic",
        "difficulty": "Intermediate",
        "description": "Simultaneous traffic streams from multiple department workstations communicating with central application servers.",
    }

    # 9. noteworthy_syn_pattern.pcap
    p9 = dest_dir / "noteworthy_syn_pattern.pcap"
    pkts9 = []
    t = base_t + 80.0
    scanner_ip = "10.0.0.99"
    targets = [("10.0.0.5", 80), ("10.0.0.5", 443), ("10.0.0.5", 22), ("10.0.0.6", 80), ("10.0.0.6", 443), ("10.0.0.7", 445), ("10.0.0.7", 3389)]
    for target_ip, target_port in targets:
        syn = Ether() / IP(src=scanner_ip, dst=target_ip) / TCP(sport=60000 + target_port, dport=target_port, flags="S", seq=100)
        syn.time = t
        rst = Ether() / IP(src=target_ip, dst=scanner_ip) / TCP(sport=target_port, dport=60000 + target_port, flags="RA", seq=0, ack=101)
        rst.time = t + 0.003
        pkts9.extend([syn, rst])
        t += 0.05
    wrpcap(str(p9), pkts9)
    catalog["noteworthy_syn_pattern.pcap"] = {
        "name": "Noteworthy SYN Traffic Pattern Investigation",
        "difficulty": "Advanced",
        "description": "High volume of unidirectional SYN requests across various destination ports, triggering investigation evidence collection.",
    }

    return catalog


def seed_pcap_library():
    """Seed synthetic PCAPs into database and parse them into parsed_packets."""
    sample_dir = pcap_settings.SAMPLE_CAPTURES_DIR
    catalog = generate_synthetic_pcaps(sample_dir)

    db = SessionLocal()
    try:
        for filename, meta in catalog.items():
            file_path = sample_dir / filename
            existing = db.query(Capture).filter(Capture.filename == filename, Capture.is_sample == True).first()

            if not existing:
                print(f"Creating sample capture entry: {filename}")
                capture = Capture(
                    user_id=None,
                    name=meta["name"],
                    filename=filename,
                    storage_path=str(file_path),
                    file_size=file_path.stat().st_size,
                    format="pcap",
                    status=CaptureStatus.UPLOADED,
                    is_sample=True,
                    sample_category=meta["difficulty"],
                    description=meta["description"],
                )
                db.add(capture)
                db.commit()
                db.refresh(capture)
            else:
                capture = existing
                capture.storage_path = str(file_path)
                capture.file_size = file_path.stat().st_size
                db.commit()

            print(f"Parsing sample capture: {capture.name} (id={capture.id})...")
            pcap_parser_service.parse_and_index_capture(db, capture)

        print("PCAP sample library seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_pcap_library()
