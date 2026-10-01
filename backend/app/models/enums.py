from enum import StrEnum


class DifficultyLevel(StrEnum):
    """Standard multi-track difficulty levels across NexoraNet."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    MIXED = "MIXED"


class QuestionType(StrEnum):
    """Supported question and assessment formats."""

    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TRUE_FALSE = "TRUE_FALSE"
    FILL_BLANK = "FILL_BLANK"
    NUMERICAL = "NUMERICAL"
    SUBNETTING = "SUBNETTING"
    SCENARIO = "SCENARIO"
    PACKET_ANALYSIS = "PACKET_ANALYSIS"
    MATCHING = "MATCHING"
    TEXT = "TEXT"
    IP_ADDRESS = "IP_ADDRESS"
    CIDR = "CIDR"
    SUBNET = "SUBNET"
    PORT = "PORT"
    SHORT_ANSWER = "SHORT_ANSWER"
    SIEM_LOG_ANALYSIS = "SIEM_LOG_ANALYSIS"
    ENDPOINT_INVESTIGATION = "ENDPOINT_INVESTIGATION"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    SOAR = "SOAR"
    SOC_SCENARIO = "SOC_SCENARIO"
    CTF_CHALLENGE = "CTF_CHALLENGE"


class LabEnvironmentType(StrEnum):
    """Execution and interaction environment for hands-on labs."""

    CONCEPTUAL = "CONCEPTUAL"
    LOCAL_SYSTEM = "LOCAL_SYSTEM"
    CONTAINER = "CONTAINER"
    PCAP = "PCAP"
    SIMULATOR = "SIMULATOR"
    LOG_ANALYSIS = "LOG_ANALYSIS"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    SOAR_AUTOMATION = "SOAR_AUTOMATION"
    SOC_SCENARIO = "SOC_SCENARIO"


class LabValidationType(StrEnum):
    """Verification mechanics for hands-on step validation."""

    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TEXT = "TEXT"
    NUMERICAL = "NUMERICAL"
    IP_ADDRESS = "IP_ADDRESS"
    CIDR = "CIDR"
    SUBNET = "SUBNET"
    PORT = "PORT"
    SHORT_ANSWER = "SHORT_ANSWER"


class CognitiveLevel(StrEnum):
    """Bloom's revised taxonomy levels for assessment questions."""

    REMEMBER = "REMEMBER"
    UNDERSTAND = "UNDERSTAND"
    APPLY = "APPLY"
    ANALYZE = "ANALYZE"


class ContentType(StrEnum):
    """Educational content presentation formats."""

    LESSON = "LESSON"
    ARTICLE = "ARTICLE"
    DIAGRAM = "DIAGRAM"
    EXAMPLE = "EXAMPLE"
    REFERENCE = "REFERENCE"


class LabStatus(StrEnum):
    """Publishing lifecycle for hands-on labs."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class QuestionStatus(StrEnum):
    """Lifecycle review states for question bank items."""

    DRAFT = "DRAFT"
    REVIEW = "REVIEW"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class MockTestType(StrEnum):
    """Assessment structural types."""

    TOPIC = "TOPIC"
    DIFFICULTY = "DIFFICULTY"
    MIXED = "MIXED"
    COMPREHENSIVE = "COMPREHENSIVE"
    PRACTICE = "PRACTICE"
    FULL_MOCK = "FULL_MOCK"
    ADAPTIVE = "ADAPTIVE"


class MockTestStatus(StrEnum):
    """Publishing status for mock exams."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AttemptStatus(StrEnum):
    """State tracking for exam and lab student attempts."""

    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"
    ABANDONED = "ABANDONED"


class UserRole(StrEnum):
    """Role-based authorization tiers."""

    STUDENT = "STUDENT"
    INSTRUCTOR = "INSTRUCTOR"
    ADMIN = "ADMIN"


class ProgressStatus(StrEnum):
    """Course and topic completion statuses."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TopicPerformanceStatus(StrEnum):
    """Explainable student performance states for networking topics."""

    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    NEEDS_PRACTICE = "NEEDS_PRACTICE"
    DEVELOPING = "DEVELOPING"
    SOLID = "SOLID"
    STRONG = "STRONG"


class RecommendationType(StrEnum):
    """Actionable recommendation categories."""

    LESSON = "LESSON"
    LAB = "LAB"
    MOCK_TEST = "MOCK_TEST"
    ADAPTIVE_TEST = "ADAPTIVE_TEST"
    TOPIC_PRACTICE = "TOPIC_PRACTICE"
    DIFFICULTY_REINFORCEMENT = "DIFFICULTY_REINFORCEMENT"
    REVIEW = "REVIEW"


class RecommendationPriority(StrEnum):
    """Internal recommendation urgency tiers."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConfidenceLevel(StrEnum):
    """Statistical sample size confidence levels."""

    INSUFFICIENT = "INSUFFICIENT"
    PRELIMINARY = "PRELIMINARY"
    DEVELOPING = "DEVELOPING"
    STRONG = "STRONG"


class SimDeviceType(StrEnum):
    """Network simulator supported node types."""

    PC = "PC"
    LAPTOP = "LAPTOP"
    SERVER = "SERVER"
    SWITCH = "SWITCH"
    ROUTER = "ROUTER"
    FIREWALL = "FIREWALL"
    INTERNET = "INTERNET"
    DNS_SERVER = "DNS_SERVER"
    DHCP_SERVER = "DHCP_SERVER"


class SimProtocol(StrEnum):
    """Educational simulation protocols."""

    ICMP = "ICMP"
    TCP = "TCP"
    UDP = "UDP"
    DNS = "DNS"
    DHCP = "DHCP"
    ARP = "ARP"
    HTTP = "HTTP"


class SimEventType(StrEnum):
    """Simulator timeline events."""

    PACKET_CREATED = "PACKET_CREATED"
    FRAME_RECEIVED = "FRAME_RECEIVED"
    FRAME_FORWARDED = "FRAME_FORWARDED"
    ARP_REQUEST = "ARP_REQUEST"
    ARP_REPLY = "ARP_REPLY"
    ROUTE_LOOKUP = "ROUTE_LOOKUP"
    ROUTE_MATCH = "ROUTE_MATCH"
    ROUTE_FAILURE = "ROUTE_FAILURE"
    PACKET_DROPPED = "PACKET_DROPPED"
    ICMP_REQUEST = "ICMP_REQUEST"
    ICMP_REPLY = "ICMP_REPLY"
    TCP_SYN = "TCP_SYN"
    TCP_SYN_ACK = "TCP_SYN_ACK"
    TCP_ACK = "TCP_ACK"
    DNS_QUERY = "DNS_QUERY"
    DNS_RESPONSE = "DNS_RESPONSE"
    DHCP_DISCOVER = "DHCP_DISCOVER"
    DHCP_OFFER = "DHCP_OFFER"
    DHCP_REQUEST = "DHCP_REQUEST"
    DHCP_ACK = "DHCP_ACK"
    FIREWALL_ALLOW = "FIREWALL_ALLOW"
    FIREWALL_DENY = "FIREWALL_DENY"
    NAT_TRANSLATION = "NAT_TRANSLATION"


class SimulatorValidationType(StrEnum):
    """Deterministic validation check rules for simulator scenarios."""

    DEVICE_EXISTS = "DEVICE_EXISTS"
    DEVICE_CONNECTED = "DEVICE_CONNECTED"
    IP_MATCH = "IP_MATCH"
    SUBNET_MATCH = "SUBNET_MATCH"
    GATEWAY_MATCH = "GATEWAY_MATCH"
    ROUTE_EXISTS = "ROUTE_EXISTS"
    PING_SUCCESS = "PING_SUCCESS"
    PORT_OPEN = "PORT_OPEN"
    VLAN_MATCH = "VLAN_MATCH"
    FIREWALL_RULE = "FIREWALL_RULE"
    PACKET_REACHES_DESTINATION = "PACKET_REACHES_DESTINATION"


class CaptureStatus(StrEnum):
    """Lifecycle status of a PCAP upload and parsing job."""

    UPLOADED = "UPLOADED"
    PARSING = "PARSING"
    READY = "READY"
    FAILED = "FAILED"
    DELETED = "DELETED"


class ObservationSeverity(StrEnum):
    """Educational severity levels for packet pattern observations."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ObservationType(StrEnum):
    """Rule-based pattern observations detected across captured traffic."""

    HIGH_SYN_RATE = "HIGH_SYN_RATE"
    MANY_TCP_RESETS = "MANY_TCP_RESETS"
    DNS_NXDOMAIN_SPIKE = "DNS_NXDOMAIN_SPIKE"
    UNUSUAL_PORT_USAGE = "UNUSUAL_PORT_USAGE"
    LARGE_PACKET_BURST = "LARGE_PACKET_BURST"
    REPEATED_CONNECTION_ATTEMPTS = "REPEATED_CONNECTION_ATTEMPTS"
    ARP_MAPPING_CHANGE = "ARP_MAPPING_CHANGE"
    SUSPICIOUS_TRAFFIC = "SUSPICIOUS_TRAFFIC"


class TcpHandshakeState(StrEnum):
    """TCP 3-way connection lifecycle status."""

    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    RESET = "RESET"
    UNKNOWN = "UNKNOWN"


class RuleStatus(StrEnum):
    """Lifecycle and operational status for detection rules."""

    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class RuleCategory(StrEnum):
    """Domain category for network detection rules."""

    TCP = "TCP"
    UDP = "UDP"
    DNS = "DNS"
    ARP = "ARP"
    ICMP = "ICMP"
    HTTP = "HTTP"
    TLS = "TLS"
    TRAFFIC_ANALYSIS = "TRAFFIC_ANALYSIS"
    RECON_DETECTION = "RECON_DETECTION"
    NETWORK_ANOMALY = "NETWORK_ANOMALY"
    CONNECTION_BEHAVIOR = "CONNECTION_BEHAVIOR"
    ENDPOINT_BEHAVIOR = "ENDPOINT_BEHAVIOR"
    PROTOCOL_ANOMALY = "PROTOCOL_ANOMALY"


class AlertSeverity(StrEnum):
    """Severity ratings for detection alerts."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertConfidence(StrEnum):
    """Analytical confidence rating for a rule match."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class AlertStatus(StrEnum):
    """Investigation workflow triage states for detection alerts."""

    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    CLOSED = "CLOSED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class DetectionRunStatus(StrEnum):
    """Execution state of a detection analysis run."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class EvidenceType(StrEnum):
    """Types of granular telemetry attached as evidence to an alert or incident."""

    PACKET = "PACKET"
    FLOW = "FLOW"
    ENDPOINT = "ENDPOINT"
    DNS_EVENT = "DNS_EVENT"
    TCP_EVENT = "TCP_EVENT"
    ARP_EVENT = "ARP_EVENT"
    ICMP_EVENT = "ICMP_EVENT"
    HTTP_EVENT = "HTTP_EVENT"
    TLS_METADATA = "TLS_METADATA"
    SIMULATOR_EVENT = "SIMULATOR_EVENT"
    STATISTICAL_OBSERVATION = "STATISTICAL_OBSERVATION"
    ALERT = "ALERT"
    PCAP = "PCAP"
    TLS_EVENT = "TLS_EVENT"
    SIEM_EVENT = "SIEM_EVENT"
    ENDPOINT_EVENT = "ENDPOINT_EVENT"
    PROCESS_EVENT = "PROCESS_EVENT"
    FILE_EVENT = "FILE_EVENT"
    AUTH_EVENT = "AUTH_EVENT"
    IOC = "IOC"
    DETECTION = "DETECTION"
    NOTE = "NOTE"
    SCREENSHOT_REFERENCE = "SCREENSHOT_REFERENCE"


class TrainingPriority(StrEnum):
    """Deterministic training priority for educational triage."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class TriageClassification(StrEnum):
    """Analyst classification after reviewing alert evidence."""

    UNREVIEWED = "UNREVIEWED"
    BENIGN = "BENIGN"
    SUSPICIOUS = "SUSPICIOUS"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    REQUIRES_MORE_DATA = "REQUIRES_MORE_DATA"
    CLOSED = "CLOSED"


class InvestigationStatus(StrEnum):
    """Workflow state for an ongoing SOC investigation."""

    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class InvestigationAlertRelationship(StrEnum):
    """Relationship role of an alert within an investigation."""

    PRIMARY = "PRIMARY"
    RELATED = "RELATED"
    CONTEXT = "CONTEXT"


class HypothesisStatus(StrEnum):
    """Status of an investigative hypothesis."""

    OPEN = "OPEN"
    UNTESTED = "UNTESTED"
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class FindingConfidence(StrEnum):
    """Confidence rating reflecting the strength of evidence supporting a finding."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class CaseStatus(StrEnum):
    """Case management lifecycle states."""

    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    PENDING = "PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class NotificationType(StrEnum):
    """Types of in-app SOC notifications."""

    NEW_ALERT = "NEW_ALERT"
    INVESTIGATION_ASSIGNED = "INVESTIGATION_ASSIGNED"
    INVESTIGATION_UPDATED = "INVESTIGATION_UPDATED"
    CASE_UPDATED = "CASE_UPDATED"
    DETECTION_RUN_COMPLETED = "DETECTION_RUN_COMPLETED"


# ==============================================================================
# Step 13 Threat Intelligence & IOC Investigation Enums
# ==============================================================================


class IndicatorType(StrEnum):
    """Supported Indicators of Compromise (IOC) and Interest types."""

    IP_ADDRESS = "IP_ADDRESS"
    DOMAIN = "DOMAIN"
    URL = "URL"
    FILE_HASH = "FILE_HASH"
    EMAIL_ADDRESS = "EMAIL_ADDRESS"


class HashType(StrEnum):
    """Cryptographic hash algorithm types for FILE_HASH indicators."""

    MD5 = "MD5"
    SHA1 = "SHA1"
    SHA256 = "SHA256"
    SHA512 = "SHA512"


class IndicatorStatus(StrEnum):
    """Lifecycle status of a threat indicator."""

    NEW = "NEW"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    UNKNOWN = "UNKNOWN"


class IndicatorClassification(StrEnum):
    """Analytical reputation classification for an indicator."""

    BENIGN = "BENIGN"
    SUSPICIOUS = "SUSPICIOUS"
    MALICIOUS = "MALICIOUS"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    UNKNOWN = "UNKNOWN"


class ThreatIntelConfidence(StrEnum):
    """Confidence level in the threat intelligence assessment."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ThreatIntelSourceType(StrEnum):
    """Origin and collection category of threat intelligence."""

    SYNTHETIC = "SYNTHETIC"
    INTERNAL = "INTERNAL"
    PUBLIC = "PUBLIC"
    COMMERCIAL = "COMMERCIAL"
    COMMUNITY = "COMMUNITY"


class SourceReliability(StrEnum):
    """Evaluated reliability of an intelligence source."""

    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IndicatorRelationshipType(StrEnum):
    """Structural relationship types between indicators and operational artifacts."""

    RESOLVES_TO = "RESOLVES_TO"
    CONTACTS = "CONTACTS"
    HOSTS = "HOSTS"
    REDIRECTS_TO = "REDIRECTS_TO"
    RELATED_TO = "RELATED_TO"
    OBSERVED_WITH = "OBSERVED_WITH"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    SAME_CONTEXT = "SAME_CONTEXT"


class IntelligenceFreshness(StrEnum):
    """Temporal freshness evaluation for intelligence observations."""

    FRESH = "FRESH"
    RECENT = "RECENT"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


# ===========================================================================
# STEP 14: Threat Hunting & Investigation Workspace Enums
# ===========================================================================


class HuntStatus(StrEnum):
    """Lifecycle statuses for a threat hunt investigation."""

    DRAFT = "DRAFT"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class HuntDifficulty(StrEnum):
    """Skill difficulty tier for threat hunting scenarios."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


class HuntDatasetType(StrEnum):
    """Source domain categorization for hunt datasets."""

    PCAP = "PCAP"
    DETECTION_EVENTS = "DETECTION_EVENTS"
    SOC_ALERTS = "SOC_ALERTS"
    IOC_DATA = "IOC_DATA"
    SIMULATOR_EVENTS = "SIMULATOR_EVENTS"
    COMBINED = "COMBINED"


class HuntEventType(StrEnum):
    """Normalized telemetry event types for hunting queries and timeline."""

    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    DNS_QUERY = "DNS_QUERY"
    DNS_RESPONSE = "DNS_RESPONSE"
    HTTP_REQUEST = "HTTP_REQUEST"
    TLS_EVENT = "TLS_EVENT"
    TCP_EVENT = "TCP_EVENT"
    UDP_EVENT = "UDP_EVENT"
    ICMP_EVENT = "ICMP_EVENT"
    ARP_EVENT = "ARP_EVENT"
    DETECTION_ALERT = "DETECTION_ALERT"
    SOC_ALERT = "SOC_ALERT"
    IOC_OBSERVATION = "IOC_OBSERVATION"
    SIMULATOR_EVENT = "SIMULATOR_EVENT"


class HuntHypothesisStatus(StrEnum):
    """Testing status of an analyst hunt hypothesis."""

    OPEN = "OPEN"
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


class HuntConfidence(StrEnum):
    """Analytical confidence in hypothesis or finding."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class HuntEvidenceType(StrEnum):
    """Classification of artifacts collected as hunt evidence."""

    EVENT = "EVENT"
    ALERT = "ALERT"
    IOC = "IOC"
    TIMELINE = "TIMELINE"
    PCAP_PACKET = "PCAP_PACKET"
    DNS_EVENT = "DNS_EVENT"
    HTTP_EVENT = "HTTP_EVENT"
    TLS_EVENT = "TLS_EVENT"
    SIMULATOR_EVENT = "SIMULATOR_EVENT"


class HuntEvidenceRelevance(StrEnum):
    """Relevance orientation of evidence relative to a hypothesis."""

    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    CONTEXT = "CONTEXT"


class HuntFindingType(StrEnum):
    """Categorization of documented threat hunt discoveries."""

    OBSERVATION = "OBSERVATION"
    PATTERN = "PATTERN"
    ANOMALY = "ANOMALY"
    IOC_CORRELATION = "IOC_CORRELATION"
    NETWORK_BEHAVIOR = "NETWORK_BEHAVIOR"
    DETECTION_GAP = "DETECTION_GAP"
    INCONCLUSIVE = "INCONCLUSIVE"


class HuntConclusionDisposition(StrEnum):
    """Final analytical disposition upon concluding a threat hunt."""

    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class LogSourceType(StrEnum):
    """Educational security log source classifications."""

    # Windows
    WINDOWS_SECURITY = "WINDOWS_SECURITY"
    WINDOWS_SYSTEM = "WINDOWS_SYSTEM"
    WINDOWS_APPLICATION = "WINDOWS_APPLICATION"
    WINDOWS_POWERSHELL = "WINDOWS_POWERSHELL"
    WINDOWS_DEFENDER = "WINDOWS_DEFENDER"
    # Linux
    LINUX_AUTH = "LINUX_AUTH"
    LINUX_SYSLOG = "LINUX_SYSLOG"
    LINUX_KERNEL = "LINUX_KERNEL"
    LINUX_SSH = "LINUX_SSH"
    # Network
    FIREWALL = "FIREWALL"
    ROUTER = "ROUTER"
    DNS = "DNS"
    DHCP = "DHCP"
    PROXY = "PROXY"
    VPN = "VPN"
    IDS = "IDS"
    # Web
    WEB_SERVER = "WEB_SERVER"
    REVERSE_PROXY = "REVERSE_PROXY"
    APPLICATION = "APPLICATION"
    API = "API"
    # Authentication & Directory
    AUTHENTICATION = "AUTHENTICATION"
    DIRECTORY_SERVICE = "DIRECTORY_SERVICE"


class LogSourceStatus(StrEnum):
    """Operational status of an educational log source."""

    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class RawLogFormat(StrEnum):
    """Supported educational raw log ingestion formats."""

    JSON = "JSON"
    CSV = "CSV"
    SYSLOG = "SYSLOG"
    WINDOWS_EVENT_XML = "WINDOWS_EVENT_XML"
    CEF_LIKE = "CEF_LIKE"


class SecurityEventCategory(StrEnum):
    """Normalized taxonomy categories for SIEM security events."""

    AUTHENTICATION = "AUTHENTICATION"
    PROCESS = "PROCESS"
    NETWORK = "NETWORK"
    DNS = "DNS"
    FILE = "FILE"
    SYSTEM = "SYSTEM"
    APPLICATION = "APPLICATION"
    WEB = "WEB"
    FIREWALL = "FIREWALL"
    SECURITY = "SECURITY"
    PRIVILEGE = "PRIVILEGE"
    ACCOUNT = "ACCOUNT"
    REMOTE_ACCESS = "REMOTE_ACCESS"
    MALWARE_ALERT = "MALWARE_ALERT"
    POLICY = "POLICY"


class SecurityEventAction(StrEnum):
    """Taxonomy actions for normalized security events."""

    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    PROCESS_START = "PROCESS_START"
    PROCESS_STOP = "PROCESS_STOP"
    CONNECTION = "CONNECTION"
    CONNECTION_BLOCKED = "CONNECTION_BLOCKED"
    DNS_QUERY = "DNS_QUERY"
    FILE_CREATE = "FILE_CREATE"
    FILE_MODIFY = "FILE_MODIFY"
    FILE_DELETE = "FILE_DELETE"
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    PRIVILEGE_CHANGE = "PRIVILEGE_CHANGE"
    SERVICE_START = "SERVICE_START"
    SERVICE_STOP = "SERVICE_STOP"
    POLICY_CHANGE = "POLICY_CHANGE"


class SecurityEventSeverity(StrEnum):
    """Event severity levels."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityLogDatasetType(StrEnum):
    """Dataset tier for SIEM training data."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    SCENARIO = "SCENARIO"


class LogCorrelationRuleStatus(StrEnum):
    """Operational status of a correlation rule."""

    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class CorrelationAlertStatus(StrEnum):
    """Triage lifecycle status for a correlation alert."""

    NEW = "NEW"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    CLOSED = "CLOSED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class EndpointPlatform(StrEnum):
    """Supported operating system platforms for synthetic endpoints."""

    WINDOWS = "WINDOWS"
    LINUX = "LINUX"


class EndpointArchitecture(StrEnum):
    """Endpoint CPU architecture."""

    X64 = "X64"
    ARM64 = "ARM64"


class EndpointEnvironment(StrEnum):
    """Deployment role / environment for synthetic endpoint."""

    WORKSTATION = "WORKSTATION"
    SERVER = "SERVER"
    TRAINING_VM = "TRAINING_VM"


class EndpointStatus(StrEnum):
    """Operational status of a synthetic host."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    UNKNOWN = "UNKNOWN"


class EndpointRiskLevel(StrEnum):
    """Assessed risk score / threat tier for synthetic training host."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class EndpointEventCategory(StrEnum):
    """Categorization of synthetic endpoint activity."""

    AUTHENTICATION = "AUTHENTICATION"
    PROCESS = "PROCESS"
    FILE = "FILE"
    NETWORK = "NETWORK"
    DNS = "DNS"
    SERVICE = "SERVICE"
    ACCOUNT = "ACCOUNT"
    PRIVILEGE = "PRIVILEGE"
    PERSISTENCE = "PERSISTENCE"
    SYSTEM = "SYSTEM"
    SECURITY = "SECURITY"
    APPLICATION = "APPLICATION"


class EndpointEventType(StrEnum):
    """Fine-grained synthetic event actions observed on endpoint."""

    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILURE = "LOGIN_FAILURE"
    LOGOUT = "LOGOUT"
    PROCESS_START = "PROCESS_START"
    PROCESS_END = "PROCESS_END"
    FILE_CREATE = "FILE_CREATE"
    FILE_MODIFY = "FILE_MODIFY"
    FILE_DELETE = "FILE_DELETE"
    FILE_READ = "FILE_READ"
    NETWORK_CONNECTION = "NETWORK_CONNECTION"
    NETWORK_LISTENER = "NETWORK_LISTENER"
    DNS_QUERY = "DNS_QUERY"
    SERVICE_START = "SERVICE_START"
    SERVICE_STOP = "SERVICE_STOP"
    ACCOUNT_CREATED = "ACCOUNT_CREATED"
    ACCOUNT_DISABLED = "ACCOUNT_DISABLED"
    ACCOUNT_MODIFIED = "ACCOUNT_MODIFIED"
    PRIVILEGE_CHANGE = "PRIVILEGE_CHANGE"
    SCHEDULED_TASK_CREATED = "SCHEDULED_TASK_CREATED"
    SCHEDULED_TASK_MODIFIED = "SCHEDULED_TASK_MODIFIED"
    SECURITY_POLICY_CHANGE = "SECURITY_POLICY_CHANGE"


class ProcessIntegrityLevel(StrEnum):
    """Execution privilege / integrity level for processes."""

    STANDARD = "STANDARD"
    ELEVATED = "ELEVATED"
    SYSTEM = "SYSTEM"
    UNKNOWN = "UNKNOWN"


class FileAction(StrEnum):
    """File operation actions."""

    CREATE = "CREATE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    READ = "READ"


class EvidenceRelevance(StrEnum):
    """Relevance relationship between evidence and hypothesis."""

    SUPPORTING = "SUPPORTING"
    CONTRADICTING = "CONTRADICTING"
    CONTEXT = "CONTEXT"
    INCONCLUSIVE = "INCONCLUSIVE"


class ThreatConfidence(StrEnum):
    """Confidence levels for threat hypotheses and conclusions."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class EndpointInvestigationStatus(StrEnum):
    """Lifecycle status of a host investigation."""

    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CLOSED = "CLOSED"


class EndpointInvestigationPriority(StrEnum):
    """Priority level for educational endpoint investigations."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class EndpointVerdict(StrEnum):
    """Conclusion verdict for an endpoint investigation."""

    BENIGN_ANOMALY = "BENIGN_ANOMALY"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    CONFIRMED_COMPROMISE = "CONFIRMED_COMPROMISE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INCONCLUSIVE = "INCONCLUSIVE"


# ==============================================================================
# STEP 17: Incident Response, Case Management & MITRE ATT&CK Framework
# ==============================================================================


class IncidentStatus(StrEnum):
    """NIST SP 800-61 / educational incident lifecycle statuses."""

    NEW = "NEW"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    CONTAINMENT = "CONTAINMENT"
    ERADICATION = "ERADICATION"
    RECOVERY = "RECOVERY"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class IncidentSeverity(StrEnum):
    """Incident severity classification."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class IncidentClassification(StrEnum):
    """Incident disposition classification."""

    BENIGN = "BENIGN"
    SUSPICIOUS = "SUSPICIOUS"
    CONFIRMED_INCIDENT = "CONFIRMED_INCIDENT"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    UNDETERMINED = "UNDETERMINED"


class IncidentType(StrEnum):
    """Incident categorization types."""

    NETWORK_INTRUSION = "NETWORK_INTRUSION"
    SUSPICIOUS_LOGIN = "SUSPICIOUS_LOGIN"
    MALWARE_INDICATOR = "MALWARE_INDICATOR"
    CREDENTIAL_ATTACK = "CREDENTIAL_ATTACK"
    PHISHING = "PHISHING"
    DATA_EXFILTRATION_PATTERN = "DATA_EXFILTRATION_PATTERN"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    ENDPOINT_COMPROMISE = "ENDPOINT_COMPROMISE"
    DNS_ANOMALY = "DNS_ANOMALY"
    SUSPICIOUS_PROCESS = "SUSPICIOUS_PROCESS"
    MULTI_STAGE_ACTIVITY = "MULTI_STAGE_ACTIVITY"
    OTHER = "OTHER"


class IncidentPhase(StrEnum):
    """NIST SP 800-61 Rev 2 incident handling phases."""

    PREPARATION = "PREPARATION"
    DETECTION_ANALYSIS = "DETECTION_ANALYSIS"
    CONTAINMENT_ERADICATION_RECOVERY = "CONTAINMENT_ERADICATION_RECOVERY"
    POST_INCIDENT_ACTIVITY = "POST_INCIDENT_ACTIVITY"


class ResponseActionCategory(StrEnum):
    """Category of simulated response action."""

    CONTAINMENT = "CONTAINMENT"
    ERADICATION = "ERADICATION"
    RECOVERY = "RECOVERY"


class ResponseActionType(StrEnum):
    """Simulated response action types - strictly educational simulation."""

    SIMULATE_HOST_ISOLATION = "SIMULATE_HOST_ISOLATION"
    SIMULATE_ACCOUNT_RESTRICTION = "SIMULATE_ACCOUNT_RESTRICTION"
    SIMULATE_NETWORK_BLOCK = "SIMULATE_NETWORK_BLOCK"
    SIMULATE_IOC_BLOCK = "SIMULATE_IOC_BLOCK"
    SIMULATE_SESSION_REVOCATION = "SIMULATE_SESSION_REVOCATION"
    SIMULATE_REMOVE_INDICATOR = "SIMULATE_REMOVE_INDICATOR"
    SIMULATE_REMOVE_PERSISTENCE = "SIMULATE_REMOVE_PERSISTENCE"
    SIMULATE_RESET_CREDENTIAL = "SIMULATE_RESET_CREDENTIAL"
    SIMULATE_CLEAN_HOST = "SIMULATE_CLEAN_HOST"
    SIMULATE_RESTORE_HOST = "SIMULATE_RESTORE_HOST"
    SIMULATE_RESTORE_SERVICE = "SIMULATE_RESTORE_SERVICE"
    SIMULATE_REENABLE_ACCOUNT = "SIMULATE_REENABLE_ACCOUNT"
    SIMULATE_RESTORE_NETWORK = "SIMULATE_RESTORE_NETWORK"


class ResponseActionStatus(StrEnum):
    """Lifecycle state of a response action."""

    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    REVERTED = "REVERTED"
    CANCELLED = "CANCELLED"


class EvidenceAuditAction(StrEnum):
    """Chain of custody audit actions."""

    ATTACHED = "ATTACHED"
    VIEWED = "VIEWED"
    ANNOTATED = "ANNOTATED"
    LINKED = "LINKED"
    UNLINKED = "UNLINKED"
    HASH_VERIFIED = "HASH_VERIFIED"


class MitreMappingConfidence(StrEnum):
    """Analytical confidence of MITRE ATT&CK mapping."""

    OBSERVED_EVIDENCE = "OBSERVED_EVIDENCE"
    HYPOTHESIS_SUGGESTED = "HYPOTHESIS_SUGGESTED"
    ANALYST_INFERRED = "ANALYST_INFERRED"


# ==============================================================================
# STEP 18: SOAR Security Automation & Advanced SOC Scenario Engine
# ==============================================================================


class PlaybookStatus(StrEnum):
    """Lifecycle status of an automation playbook."""

    DRAFT = "DRAFT"
    TESTING = "TESTING"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class PlaybookRiskLevel(StrEnum):
    """Risk tier of automated defensive workflows."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class PlaybookTriggerType(StrEnum):
    """Event triggers that invoke SOAR playbooks."""

    ALERT_CREATED = "ALERT_CREATED"
    ALERT_THRESHOLD = "ALERT_THRESHOLD"
    IOC_OBSERVED = "IOC_OBSERVED"
    INCIDENT_CREATED = "INCIDENT_CREATED"
    INCIDENT_ESCALATED = "INCIDENT_ESCALATED"
    CASE_UPDATED = "CASE_UPDATED"
    DETECTION_MATCH = "DETECTION_MATCH"
    CORRELATION_MATCH = "CORRELATION_MATCH"
    SCHEDULED_TIMER = "SCHEDULED_TIMER"
    MANUAL = "MANUAL"



class PlaybookExecutionStatus(StrEnum):
    """State machine lifecycle for playbook executions."""

    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    APPROVED = "APPROVED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"



class StepExecutionStatus(StrEnum):
    """Execution status for individual playbook steps."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class ApprovalStatus(StrEnum):
    """Analyst approval state for high-risk automated actions."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class AutomationActionType(StrEnum):
    """Strict allowlist of educational SOAR automation actions."""

    # Enrichment
    ENRICH_ALERT = "ENRICH_ALERT"
    ENRICH_IOC = "ENRICH_IOC"
    ENRICH_HOST = "ENRICH_HOST"
    ENRICH_USER = "ENRICH_USER"
    ENRICH_DETECTION = "ENRICH_DETECTION"

    # Investigation
    COLLECT_ALERT_EVIDENCE = "COLLECT_ALERT_EVIDENCE"
    COLLECT_RELATED_ALERTS = "COLLECT_RELATED_ALERTS"
    COLLECT_RELATED_IOCS = "COLLECT_RELATED_IOCS"
    COLLECT_RELATED_ENDPOINT_EVENTS = "COLLECT_RELATED_ENDPOINT_EVENTS"
    COLLECT_RELATED_SIEM_EVENTS = "COLLECT_RELATED_SIEM_EVENTS"
    BUILD_TIMELINE = "BUILD_TIMELINE"
    CALCULATE_ALERT_CONTEXT = "CALCULATE_ALERT_CONTEXT"

    # Case Management
    CREATE_INCIDENT = "CREATE_INCIDENT"
    CREATE_CASE = "CREATE_CASE"
    ADD_EVIDENCE = "ADD_EVIDENCE"
    ADD_TIMELINE_EVENT = "ADD_TIMELINE_EVENT"
    ADD_ANALYST_NOTE = "ADD_ANALYST_NOTE"
    ATTACH_PLAYBOOK = "ATTACH_PLAYBOOK"

    # Simulation (Containment)
    SIMULATE_HOST_ISOLATION = "SIMULATE_HOST_ISOLATION"
    SIMULATE_ACCOUNT_RESTRICTION = "SIMULATE_ACCOUNT_RESTRICTION"
    SIMULATE_NETWORK_BLOCK = "SIMULATE_NETWORK_BLOCK"
    SIMULATE_IOC_BLOCK = "SIMULATE_IOC_BLOCK"
    SIMULATE_SESSION_REVOCATION = "SIMULATE_SESSION_REVOCATION"
    SIMULATE_CREDENTIAL_RESET = "SIMULATE_CREDENTIAL_RESET"

    # Response (Eradication & Recovery)
    SIMULATE_REMOVE_INDICATOR = "SIMULATE_REMOVE_INDICATOR"
    SIMULATE_REMOVE_PERSISTENCE = "SIMULATE_REMOVE_PERSISTENCE"
    SIMULATE_CLEAN_HOST = "SIMULATE_CLEAN_HOST"
    SIMULATE_RESTORE_HOST = "SIMULATE_RESTORE_HOST"

    # Notification Simulation
    SIMULATE_ANALYST_NOTIFICATION = "SIMULATE_ANALYST_NOTIFICATION"
    SIMULATE_ESCALATION = "SIMULATE_ESCALATION"


class ScenarioDifficulty(StrEnum):
    """Advanced SOC investigation scenario difficulties."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class ScenarioCategory(StrEnum):
    """Categorization for multi-stage educational SOC scenarios."""

    NETWORK_INVESTIGATION = "NETWORK_INVESTIGATION"
    ENDPOINT_INVESTIGATION = "ENDPOINT_INVESTIGATION"
    SOC_INVESTIGATION = "SOC_INVESTIGATION"
    THREAT_INTELLIGENCE = "THREAT_INTELLIGENCE"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"


class ScenarioStage(StrEnum):
    """Sequential 9-stage investigation methodology."""

    STAGE_1_INITIAL_SIGNAL = "STAGE_1_INITIAL_SIGNAL"
    STAGE_2_EVIDENCE_SELECTION = "STAGE_2_EVIDENCE_SELECTION"
    STAGE_3_CORRELATION = "STAGE_3_CORRELATION"
    STAGE_4_HYPOTHESIS = "STAGE_4_HYPOTHESIS"
    STAGE_5_VALIDATION = "STAGE_5_VALIDATION"
    STAGE_6_MITRE_MAPPING = "STAGE_6_MITRE_MAPPING"
    STAGE_7_RESPONSE_DECISION = "STAGE_7_RESPONSE_DECISION"
    STAGE_8_OUTCOME = "STAGE_8_OUTCOME"
    STAGE_9_LESSONS_LEARNED = "STAGE_9_LESSONS_LEARNED"


class ScenarioAttemptStatus(StrEnum):
    """Lifecycle state of a learner's scenario attempt."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


# -----------------------------------------------------------------------------
# STEP 19: CTF / Challenges & Advanced Cybersecurity Training Engine Enums
# -----------------------------------------------------------------------------


class ChallengeCategory(StrEnum):
    """Categories for synthetic educational cybersecurity challenges."""

    NETWORKING = "NETWORKING"
    PACKET_ANALYSIS = "PACKET_ANALYSIS"
    SOC_ANALYSIS = "SOC_ANALYSIS"
    SIEM = "SIEM"
    DETECTION_ENGINEERING = "DETECTION_ENGINEERING"
    THREAT_INTELLIGENCE = "THREAT_INTELLIGENCE"
    THREAT_HUNTING = "THREAT_HUNTING"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    MITRE_ATTACK = "MITRE_ATTACK"
    ENDPOINT_SECURITY = "ENDPOINT_SECURITY"
    FORENSICS = "FORENSICS"
    CYBERSECURITY_REASONING = "CYBERSECURITY_REASONING"


class ChallengeDifficulty(StrEnum):
    """Experience tiers for CTF challenge problem solving."""

    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class ChallengeType(StrEnum):
    """Interaction format and answer structure for cybersecurity challenges."""

    FLAG_CHALLENGE = "FLAG_CHALLENGE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    MULTI_SELECT = "MULTI_SELECT"
    SHORT_ANSWER = "SHORT_ANSWER"
    NUMERICAL = "NUMERICAL"
    IP_ADDRESS = "IP_ADDRESS"
    CIDR = "CIDR"
    PACKET_ANALYSIS = "PACKET_ANALYSIS"
    LOG_ANALYSIS = "LOG_ANALYSIS"
    TIMELINE_ANALYSIS = "TIMELINE_ANALYSIS"
    SCENARIO = "SCENARIO"
    INVESTIGATION = "INVESTIGATION"
    MITRE_MAPPING = "MITRE_MAPPING"
    EVIDENCE_CORRELATION = "EVIDENCE_CORRELATION"
    SOC_ANALYSIS = "SOC_ANALYSIS"
    DETECTION_ENGINEERING = "DETECTION_ENGINEERING"
    ENDPOINT_SECURITY = "ENDPOINT_SECURITY"
    THREAT_HUNTING = "THREAT_HUNTING"


class ChallengeAttemptStatus(StrEnum):
    """State tracking for a student's challenge solving attempt."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SOLVED = "SOLVED"
    FAILED = "FAILED"
    ABANDONED = "ABANDONED"
    EXPIRED = "EXPIRED"


class ChallengeStageStatus(StrEnum):
    """Lifecycle state of an individual challenge stage in a multi-stage challenge."""

    LOCKED = "LOCKED"
    AVAILABLE = "AVAILABLE"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class SkillConfidence(StrEnum):
    """Confidence levels for cybersecurity skill competency estimations."""

    NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    MODERATE_CONFIDENCE = "MODERATE_CONFIDENCE"
    HIGH_CONFIDENCE = "HIGH_CONFIDENCE"


class PortfolioVisibility(StrEnum):
    """Access visibility tiers for student portfolios."""

    PRIVATE = "PRIVATE"
    UNLISTED = "UNLISTED"
    PUBLIC = "PUBLIC"


class ContentStatus(StrEnum):
    """Editorial and publication lifecycle for platform educational content."""

    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    UNPUBLISHED = "UNPUBLISHED"
    ARCHIVED = "ARCHIVED"


class AdminAuditAction(StrEnum):
    """Auditable actions logged for administrative interventions."""

    CONTENT_CREATED = "CONTENT_CREATED"
    CONTENT_UPDATED = "CONTENT_UPDATED"
    CONTENT_PUBLISHED = "CONTENT_PUBLISHED"
    CONTENT_UNPUBLISHED = "CONTENT_UNPUBLISHED"
    CONTENT_ARCHIVED = "CONTENT_ARCHIVED"
    USER_ROLE_CHANGED = "USER_ROLE_CHANGED"
    REPORT_GENERATED = "REPORT_GENERATED"
    PORTFOLIO_MODERATION = "PORTFOLIO_MODERATION"


class StudentActivityType(StrEnum):
    """Standardized activity types recorded in the student learning timeline."""

    LESSON = "LESSON"
    LAB = "LAB"
    MOCK_TEST = "MOCK_TEST"
    CHALLENGE = "CHALLENGE"
    SOC_SCENARIO = "SOC_SCENARIO"
    PCAP_ANALYSIS = "PCAP_ANALYSIS"
    THREAT_HUNT = "THREAT_HUNT"
    SIEM_ANALYSIS = "SIEM_ANALYSIS"
    ENDPOINT_INVESTIGATION = "ENDPOINT_INVESTIGATION"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"


class AssessmentRecommendationType(StrEnum):
    """Actionable recommendation categories for skill improvement."""

    REVIEW_LESSON = "REVIEW_LESSON"
    PRACTICE_LAB = "PRACTICE_LAB"
    TAKE_TOPIC_TEST = "TAKE_TOPIC_TEST"
    ATTEMPT_CHALLENGE = "ATTEMPT_CHALLENGE"
    REVIEW_INVESTIGATION = "REVIEW_INVESTIGATION"
    PRACTICE_SUBNETTING = "PRACTICE_SUBNETTING"
    REVIEW_PACKET_ANALYSIS = "REVIEW_PACKET_ANALYSIS"








