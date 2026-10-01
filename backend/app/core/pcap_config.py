"""Configuration and security thresholds for PCAP file uploads, storage, and offline parsing."""

from pathlib import Path

from pydantic_settings import BaseSettings


class PcapSettings(BaseSettings):
    """PCAP module settings and safety policies."""

    # Storage paths
    STORAGE_ROOT: Path = Path(__file__).resolve().parent.parent.parent / "data"
    CAPTURES_DIR: Path = STORAGE_ROOT / "captures"
    SAMPLE_CAPTURES_DIR: Path = STORAGE_ROOT / "sample_captures"

    # Upload thresholds
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    MAX_PACKETS_TO_STORE: int = 10000              # Cap on parsed packet relational rows

    # Parser execution controls
    PARSER_TIMEOUT_SECONDS: int = 30
    MAX_FILTER_QUERY_LENGTH: int = 500

    # Whitelist & Blacklist extensions
    ALLOWED_EXTENSIONS: set[str] = {".pcap", ".pcapng", ".cap"}
    DISALLOWED_EXTENSIONS: set[str] = {
        ".exe", ".dll", ".so", ".dylib", ".bin",
        ".js", ".py", ".sh", ".bat", ".ps1", ".cmd", ".vbs",
        ".zip", ".rar", ".tar", ".gz", ".7z", ".iso",
        ".php", ".asp", ".aspx", ".jsp", ".html", ".htm"
    }

    # Educational and defensive notices
    SAFETY_DISCLAIMER: str = (
        "NexoraNet analyzes packet captures offline. It does not transmit, replay, or execute captured network traffic."
    )
    PRIVACY_DISCLAIMER: str = (
        "Packet captures may contain sensitive network information. Only analyze captures you are authorized to use."
    )


pcap_settings = PcapSettings()
