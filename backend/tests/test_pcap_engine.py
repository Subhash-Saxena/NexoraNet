"""Comprehensive unit and integration tests for Step 10 PCAP and Packet Analysis Engine."""

import io
import tempfile
from pathlib import Path

import pytest
from app.db.session import SessionLocal
from app.main import app
from app.models.enums import CaptureStatus, ObservationSeverity, TcpHandshakeState
from app.models.pcap import Capture, ParsedPacket
from app.schemas.pcap import (
    BookmarkCreateRequest,
    FindingCreateRequest,
    NoteCreateRequest,
)
from app.services.conversation_service import conversation_service
from app.services.packet_analysis_service import packet_analysis_service
from app.services.packet_filter_service import (
    FilterValidationError,
    packet_filter_service,
)
from app.services.packet_observation_service import packet_observation_service
from app.services.pcap_parser_service import pcap_parser_service
from app.services.pcap_statistics_service import pcap_statistics_service
from fastapi import status
from fastapi.testclient import TestClient
from scapy.all import ARP, DNS, DNSQR, DNSRR, ICMP, IP, TCP, UDP, Ether, Raw, wrpcap


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_synthetic_pcap():
    """Create a temporary synthetic PCAP file containing ICMP, TCP, DNS, and ARP frames."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    pkts = []
    base_t = 1700000000.0

    # 1. ARP exchange
    a1 = Ether(src="02:00:00:00:00:01", dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, hwsrc="02:00:00:00:00:01", psrc="192.168.1.10", pdst="192.168.1.1")
    a1.time = base_t
    a2 = Ether(src="02:00:00:00:00:02", dst="02:00:00:00:00:01") / ARP(op=2, hwsrc="02:00:00:00:00:02", psrc="192.168.1.1", pdst="192.168.1.10")
    a2.time = base_t + 0.001
    pkts.extend([a1, a2])

    # 2. ICMP Echo Ping
    ping_req = Ether() / IP(src="192.168.1.10", dst="192.168.1.1") / ICMP(type=8, id=0x1111, seq=1)
    ping_req.time = base_t + 0.1
    ping_rep = Ether() / IP(src="192.168.1.1", dst="192.168.1.10") / ICMP(type=0, id=0x1111, seq=1)
    ping_rep.time = base_t + 0.102
    pkts.extend([ping_req, ping_rep])

    # 3. TCP Handshake + HTTP
    # SYN
    p_syn = Ether() / IP(src="10.0.0.5", dst="10.0.0.80") / TCP(sport=50000, dport=80, flags="S", seq=100)
    p_syn.time = base_t + 0.2
    # SYN-ACK
    p_synack = Ether() / IP(src="10.0.0.80", dst="10.0.0.5") / TCP(sport=80, dport=50000, flags="SA", seq=200, ack=101)
    p_synack.time = base_t + 0.202
    # ACK
    p_ack = Ether() / IP(src="10.0.0.5", dst="10.0.0.80") / TCP(sport=50000, dport=80, flags="A", seq=101, ack=201)
    p_ack.time = base_t + 0.203
    # HTTP GET
    http_payload = b"GET /index.html HTTP/1.1\r\nHost: example.local\r\n\r\n"
    p_http = Ether() / IP(src="10.0.0.5", dst="10.0.0.80") / TCP(sport=50000, dport=80, flags="PA", seq=101, ack=201) / Raw(load=http_payload)
    p_http.time = base_t + 0.205
    pkts.extend([p_syn, p_synack, p_ack, p_http])

    # 4. DNS query & response
    d_q = Ether() / IP(src="192.168.1.10", dst="192.168.1.1") / UDP(sport=53000, dport=53) / DNS(id=0xAAAA, rd=1, qd=DNSQR(qname="test.local"))
    d_q.time = base_t + 0.3
    d_r = Ether() / IP(src="192.168.1.1", dst="192.168.1.10") / UDP(sport=53, dport=53000) / DNS(id=0xAAAA, qr=1, qd=DNSQR(qname="test.local"), an=DNSRR(rrname="test.local", rdata="10.0.0.80"))
    d_r.time = base_t + 0.308
    pkts.extend([d_q, d_r])

    wrpcap(str(tmp_path), pkts)
    yield tmp_path
    tmp_path.unlink(missing_ok=True)


# ===========================================================================
# 1. PARSER TESTS
# ===========================================================================


def test_parser_extracts_all_protocols(db_session, sample_synthetic_pcap):
    """Verify offline parser decodes Frame, Ethernet, ARP, IPv4, ICMP, TCP, HTTP, and DNS."""
    capture = Capture(
        name="Synthetic Test",
        filename="test.pcap",
        storage_path=str(sample_synthetic_pcap),
        file_size=sample_synthetic_pcap.stat().st_size,
        format="pcap",
        status=CaptureStatus.UPLOADED,
    )
    db_session.add(capture)
    db_session.commit()

    updated = pcap_parser_service.parse_and_index_capture(db_session, capture)
    assert updated.status == CaptureStatus.READY
    assert updated.packet_count == 10
    assert updated.duration > 0.0

    # Verify packets in DB
    packets = db_session.query(ParsedPacket).filter(ParsedPacket.capture_id == capture.id).all()
    assert len(packets) == 10

    protocols = {p.protocol for p in packets}
    assert "ARP" in protocols
    assert "ICMP" in protocols
    assert "TCP" in protocols
    assert "HTTP" in protocols
    assert "DNS" in protocols

    # Check ICMP packet fields
    icmp_pkt = next(p for p in packets if p.protocol == "ICMP" and "Echo Request" in p.info)
    assert icmp_pkt.source_ip == "192.168.1.10"
    assert icmp_pkt.destination_ip == "192.168.1.1"


def test_parser_handles_malformed_file(db_session):
    """Verify parser fails gracefully with friendly error when given corrupt file."""
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp.write(b"NOT_A_VALID_PCAP_FILE_DATA_HERE_12345")
        corrupt_path = Path(tmp.name)

    capture = Capture(
        name="Corrupt Test",
        filename="corrupt.pcap",
        storage_path=str(corrupt_path),
        file_size=corrupt_path.stat().st_size,
        format="pcap",
        status=CaptureStatus.UPLOADED,
    )
    db_session.add(capture)
    db_session.commit()

    try:
        updated = pcap_parser_service.parse_and_index_capture(db_session, capture)
        assert updated.status == CaptureStatus.FAILED
        assert "Invalid or corrupted packet capture" in updated.error_message
    finally:
        corrupt_path.unlink(missing_ok=True)


# ===========================================================================
# 2. FILTER LANGUAGE TESTS
# ===========================================================================


def test_filter_tokenizer_and_parser():
    """Verify AST construction for supported filter grammar."""
    ast = packet_filter_service.parse("tcp.port == 80 && ip.addr == 10.0.0.5")
    assert ast is not None

    ast_or = packet_filter_service.parse("dns || icmp")
    assert ast_or is not None

    ast_not = packet_filter_service.parse("!arp")
    assert ast_not is not None


def test_filter_rejects_unsupported_fields():
    """Verify parser safely rejects unapproved fields without eval or shell execution."""
    with pytest.raises(FilterValidationError, match="Unsupported filter field"):
        packet_filter_service.parse("ip.malicious_field == 123")

    with pytest.raises(FilterValidationError, match="Unsupported filter field"):
        packet_filter_service.parse("system.exec == 'whoami'")


def test_filter_evaluation_on_database(db_session, sample_synthetic_pcap):
    """Verify SQL criterion generator filters actual packet rows accurately."""
    capture = Capture(
        name="Filter Test",
        filename="filter.pcap",
        storage_path=str(sample_synthetic_pcap),
        file_size=sample_synthetic_pcap.stat().st_size,
        format="pcap",
        status=CaptureStatus.UPLOADED,
    )
    db_session.add(capture)
    db_session.commit()
    pcap_parser_service.parse_and_index_capture(db_session, capture)

    # 1. Filter TCP
    res_tcp = packet_analysis_service.get_packets(db_session, capture.id, filter_str="tcp")
    assert res_tcp.total_matched >= 3

    # 2. Filter IP address
    res_ip = packet_analysis_service.get_packets(db_session, capture.id, filter_str="ip.addr == 10.0.0.5")
    assert res_ip.total_matched == 4

    # 3. Filter specific flag
    res_syn = packet_analysis_service.get_packets(db_session, capture.id, filter_str="tcp.flags.syn")
    assert res_syn.total_matched >= 1

    # 4. Filter port
    res_port = packet_analysis_service.get_packets(db_session, capture.id, filter_str="tcp.port == 80")
    assert res_port.total_matched == 4


# ===========================================================================
# 3. CONVERSATION & FLOW TESTS
# ===========================================================================


def test_conversation_service_and_handshake_state(db_session, sample_synthetic_pcap):
    """Verify 5-tuple conversation grouping and TCP handshake detection."""
    capture = Capture(
        name="Conv Test",
        filename="conv.pcap",
        storage_path=str(sample_synthetic_pcap),
        file_size=sample_synthetic_pcap.stat().st_size,
        format="pcap",
        status=CaptureStatus.UPLOADED,
    )
    db_session.add(capture)
    db_session.commit()
    pcap_parser_service.parse_and_index_capture(db_session, capture)

    convs = conversation_service.get_conversations(db_session, capture.id)
    assert len(convs) >= 2

    # Find the HTTP TCP conversation
    http_conv = next((c for c in convs if "80" in c.server_endpoint or "80" in c.client_endpoint), None)
    assert http_conv is not None
    assert http_conv.protocol == "TCP"
    assert http_conv.handshake_state == TcpHandshakeState.COMPLETE
    assert len(http_conv.ladder) == 4


# ===========================================================================
# 4. STATISTICS, ENDPOINTS, PORTS, TIMELINE TESTS
# ===========================================================================


def test_statistics_service(db_session, sample_synthetic_pcap):
    """Verify traffic metrics, endpoints, and port statistics."""
    capture = Capture(
        name="Stats Test",
        filename="stats.pcap",
        storage_path=str(sample_synthetic_pcap),
        file_size=sample_synthetic_pcap.stat().st_size,
        format="pcap",
        status=CaptureStatus.UPLOADED,
    )
    db_session.add(capture)
    db_session.commit()
    pcap_parser_service.parse_and_index_capture(db_session, capture)

    stats = pcap_statistics_service.get_statistics(db_session, capture)
    assert stats.total_packets == 10
    assert stats.total_bytes > 0
    assert "TCP" in stats.protocol_distribution

    endpoints = pcap_statistics_service.get_endpoints(db_session, capture.id)
    assert len(endpoints) >= 3
    ip_list = [e.ip for e in endpoints]
    assert "10.0.0.5" in ip_list
    assert "192.168.1.10" in ip_list

    ports = pcap_statistics_service.get_ports(db_session, capture.id)
    port_nums = [p.port for p in ports]
    assert 80 in port_nums or 53 in port_nums

    timeline = pcap_statistics_service.get_timeline(db_session, capture, bucket_count=10)
    assert len(timeline) == 10
    total_timeline_pkts = sum(b.packet_count for b in timeline)
    assert total_timeline_pkts == 10


# ===========================================================================
# 5. OBSERVATION ENGINE TESTS
# ===========================================================================


def test_observation_engine_detects_patterns(db_session):
    """Verify rule-based neutral pattern observation detector."""
    # Synthetic capture with 6 SYN packets (SYN pattern trigger)
    with tempfile.NamedTemporaryFile(suffix=".pcap", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    pkts = []
    base_t = 1700000000.0
    for p in range(1, 8):
        syn = Ether() / IP(src="10.0.0.99", dst=f"10.0.0.{p}") / TCP(sport=50000 + p, dport=80, flags="S", seq=p * 10)
        syn.time = base_t + p * 0.05
        pkts.append(syn)
    wrpcap(str(tmp_path), pkts)

    try:
        capture = Capture(
            name="Obs Test",
            filename="obs.pcap",
            storage_path=str(tmp_path),
            file_size=tmp_path.stat().st_size,
            format="pcap",
            status=CaptureStatus.UPLOADED,
        )
        db_session.add(capture)
        db_session.commit()
        pcap_parser_service.parse_and_index_capture(db_session, capture)

        observations = packet_observation_service.analyze_observations(db_session, capture.id)
        assert len(observations) >= 1
        syn_obs = next(o for o in observations if o.type == "HIGH_SYN_RATE")
        assert "10.0.0.99" in syn_obs.description
        assert syn_obs.severity == ObservationSeverity.LOW
        assert len(syn_obs.evidence_packets) >= 5
    finally:
        tmp_path.unlink(missing_ok=True)


# ===========================================================================
# 6. INVESTIGATION WORKSPACE TESTS (BOOKMARKS, NOTES, FINDINGS, REPORT)
# ===========================================================================


def test_investigation_workspace(db_session, sample_synthetic_pcap):
    """Verify bookmarks, notes, findings, and JSON report generation."""
    capture = Capture(
        name="Investigate Test",
        filename="investigate.pcap",
        storage_path=str(sample_synthetic_pcap),
        file_size=sample_synthetic_pcap.stat().st_size,
        format="pcap",
        status=CaptureStatus.UPLOADED,
    )
    db_session.add(capture)
    db_session.commit()
    pcap_parser_service.parse_and_index_capture(db_session, capture)

    # 1. Bookmark
    b_req = BookmarkCreateRequest(packet_number=5, note="HTTP SYN packet", tags=["syn", "web"])
    bookmark = packet_analysis_service.create_bookmark(db_session, capture.id, b_req)
    assert bookmark.packet_number == 5

    # 2. Note
    n_req = NoteCreateRequest(target_type="packet", target_id="5", title="Analysis Note", content="Inspected TCP port 80 handshake.")
    note = packet_analysis_service.create_note(db_session, capture.id, n_req)
    assert note.content == "Inspected TCP port 80 handshake."

    # 3. Finding
    f_req = FindingCreateRequest(
        title="Web Connection Established",
        description="Observed clean 3-way handshake to port 80.",
        severity="INFO",
        evidence_packets=[5, 6, 7],
        source_endpoint="10.0.0.5:50000",
        destination_endpoint="10.0.0.80:80",
        hypothesis="Client initiated standard HTTP session.",
        conclusion="Traffic is consistent with normal HTTP browsing.",
    )
    finding = packet_analysis_service.create_finding(db_session, capture.id, f_req)
    assert finding.title == "Web Connection Established"

    # 4. Report
    report = packet_analysis_service.generate_investigation_report(db_session, capture.id)
    assert report.capture.id == capture.id
    assert len(report.bookmarks) == 1
    assert len(report.notes) == 1
    assert len(report.findings) == 1
    assert "Educational Report" in report.disclaimer


# ===========================================================================
# 7. FASTAPI API INTEGRATION TESTS
# ===========================================================================


def test_api_status_endpoint(client):
    """Test GET /api/v1/packet-analysis/status."""
    resp = client.get("/api/v1/packet-analysis/status")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["module"] == "packet-analysis"
    assert data["status"] in ["planned", "operational"]


def test_api_upload_rejects_disallowed_extension(client):
    """Test POST /api/v1/packet-analysis/captures rejects executable extensions."""
    fake_exe = io.BytesIO(b"MZ\x90\x00executable content")
    resp = client.post(
        "/api/v1/packet-analysis/captures",
        files={"file": ("malware.exe", fake_exe, "application/octet-stream")},
    )
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Prohibited file type" in resp.json()["detail"]


def test_api_upload_and_inspect_flow(client, sample_synthetic_pcap):
    """Test full API lifecycle: upload, list, packets, details, statistics, and report."""
    with open(sample_synthetic_pcap, "rb") as f:
        file_bytes = f.read()

    # Upload
    upload_resp = client.post(
        "/api/v1/packet-analysis/captures",
        files={"file": ("api_test.pcap", io.BytesIO(file_bytes), "application/vnd.tcpdump.pcap")},
        params={"name": "API Test Capture"},
    )
    assert upload_resp.status_code == status.HTTP_201_CREATED
    cap_data = upload_resp.json()
    cap_id = cap_data["id"]
    assert cap_data["name"] == "API Test Capture"
    assert cap_data["status"] == "READY"
    assert "NexoraNet analyzes packet captures offline" in cap_data["safety_disclaimer"]

    # List
    list_resp = client.get("/api/v1/packet-analysis/captures")
    assert list_resp.status_code == status.HTTP_200_OK
    assert any(c["id"] == cap_id for c in list_resp.json())

    # Get Packets with filter
    pkts_resp = client.get(f"/api/v1/packet-analysis/captures/{cap_id}/packets?filter=tcp")
    assert pkts_resp.status_code == status.HTTP_200_OK
    assert pkts_resp.json()["total_matched"] >= 3

    # Invalid Filter produces 400
    bad_filter_resp = client.get(f"/api/v1/packet-analysis/captures/{cap_id}/packets?filter=ip.invalid_field == 1")
    assert bad_filter_resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "Unsupported filter field" in bad_filter_resp.json()["detail"]

    # Get Packet Detail
    pkt_detail_resp = client.get(f"/api/v1/packet-analysis/captures/{cap_id}/packets/1")
    assert pkt_detail_resp.status_code == status.HTTP_200_OK
    assert "Frame" in pkt_detail_resp.json()["layers"]

    # Get Statistics
    stats_resp = client.get(f"/api/v1/packet-analysis/captures/{cap_id}/statistics")
    assert stats_resp.status_code == status.HTTP_200_OK
    assert stats_resp.json()["total_packets"] == 10

    # Get Conversations
    conv_resp = client.get(f"/api/v1/packet-analysis/captures/{cap_id}/conversations")
    assert conv_resp.status_code == status.HTTP_200_OK
    assert len(conv_resp.json()) >= 1

    # Get Investigation Report
    report_resp = client.get(f"/api/v1/packet-analysis/captures/{cap_id}/report")
    assert report_resp.status_code == status.HTTP_200_OK
    assert report_resp.json()["capture"]["id"] == cap_id
