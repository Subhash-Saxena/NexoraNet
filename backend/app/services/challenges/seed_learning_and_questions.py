"""Educational Lessons & Question Bank Seeds for Step 19 CTF Challenges.

Seeds interactive lessons and Question Bank questions covering
Capture-the-Flag methodologies, evidence correlation, flag validation, and defensive reasoning.
"""

from app.models.curriculum import Course, Lesson, Module, Topic
from app.models.enums import (
    CognitiveLevel,
    ContentType,
    DifficultyLevel,
    QuestionStatus,
    QuestionType,
)
from app.models.question import Question, QuestionOption
from sqlalchemy import select
from sqlalchemy.orm import Session

CHALLENGE_LESSONS = [
    {
        "title": "CTF Fundamentals for Defensive Cybersecurity",
        "slug": "ctf-fundamentals-for-defensive-cybersecurity",
        "order_index": 1,
        "estimated_minutes": 15,
        "difficulty": DifficultyLevel.BEGINNER,
        "content": """# CTF Fundamentals for Defensive Cybersecurity

Defensive Capture-the-Flag (CTF) competitions and labs challenge security analysts to solve practical puzzles using authentic telemetry, packet captures, and system audit logs.

## The CTF Methodology
1. **Discover & Scope:** Read the challenge brief, identify the scope, and understand the objective.
2. **Examine Evidence:** Inspect synthetic PCAPs, SIEM logs, detection alerts, or endpoint audit events.
3. **Hypothesize:** Formulate testable theories explaining how the anomaly or attack occurred.
4. **Isolate Artifacts:** Filter out benign background noise and extract relevant indicators of compromise (IOCs).
5. **Solve & Verify:** Derive the target flag or answer to confirm your conclusion.
6. **Post-Mortem Review:** Review the solution walkthrough to identify areas for defensive posture improvement.
"""
    },
    {
        "title": "Network Packet Forensics & Header Dissection",
        "slug": "network-packet-forensics-and-header-dissection",
        "order_index": 2,
        "estimated_minutes": 20,
        "difficulty": DifficultyLevel.BEGINNER,
        "content": """# Network Packet Forensics & Header Dissection

Deep packet inspection is a cornerstone of CTF packet analysis challenges.

## Key Inspection Points
- **Transport Flags:** TCP SYN/ACK/RST combinations uncover scanning behavior and connection health.
- **Protocol Quirks:** Unsolicited gratuitous ARPs indicate cache poisoning.
- **Port Profiling:** Non-standard ports (e.g. 4444) frequently house backdoor command shells.
- **Payload Inspection:** Hex/ASCII streams reveal unencrypted protocols (HTTP, Telnet, FTP).
"""
    },
    {
        "title": "DNS Anomalies, NXDOMAIN Spikes & Covert Exfiltration",
        "slug": "dns-anomalies-nxdomain-spikes-and-covert-exfiltration",
        "order_index": 3,
        "estimated_minutes": 20,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "content": """# DNS Anomalies, NXDOMAIN Spikes & Covert Exfiltration

DNS is universally permitted outbound, making it a favorite protocol for adversary communication and exfiltration.

## Common DNS Threat Patterns
- **DGA Malware:** Generates hundreds of failed (NXDOMAIN) queries to pseudo-random subdomains.
- **DNS Tunneling:** Encodes file chunks or commands into subdomain labels or TXT record queries.
- **Fast-Flux DNS:** Rapidly rotates A records across dynamic residential IP pools with short TTLs.
"""
    },
    {
        "title": "Endpoint Lineage & Process Parent-Child Investigation",
        "slug": "endpoint-lineage-and-process-parent-child-investigation",
        "order_index": 4,
        "estimated_minutes": 20,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "content": """# Endpoint Lineage & Process Parent-Child Investigation

Adversaries often execute commands through living-off-the-land binaries (LOLBAS).

## Suspicious Process Trees
- `WINWORD.EXE` $\\rightarrow$ `powershell.exe` (Weaponized macro document)
- `excel.exe` $\\rightarrow$ `cmd.exe` $\\rightarrow$ `certutil.exe` (Remote file ingress)
- `svchost.exe` without `-k` parameter or executing from outside `System32` (Masquerading)
"""
    },
    {
        "title": "Multi-Source Forensic Correlation & Attack Chains",
        "slug": "multi-source-forensic-correlation-and-attack-chains",
        "order_index": 5,
        "estimated_minutes": 25,
        "difficulty": DifficultyLevel.ADVANCED,
        "content": """# Multi-Source Forensic Correlation & Attack Chains

Advanced CTF challenges require correlating disparate data sources across the enterprise.

## Correlation Triad
- **Network Telemetry:** Identifies external IP destinations, packet sizes, and beacon intervals.
- **Host Endpoint Logs:** Confirms the exact Process ID, executed command line, and local file changes.
- **Identity & SIEM Logs:** Pinpoints compromised credentials, privilege escalations, and lateral movement.
"""
    }
]

CHALLENGE_QUESTIONS = [
    {
        "code": "CTF-001",
        "text": "In a defensive CTF packet challenge, you observe 150 consecutive DNS queries returning RCODE 3 (NXDOMAIN) within two minutes. What is the most likely adversarial technique?",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "cognitive_level": CognitiveLevel.ANALYZE,
        "points": 10,
        "explanation": "A high ratio of NXDOMAIN responses indicates a Domain Generation Algorithm (DGA) attempting to establish communication with a rendezvous C2 server.",
        "options": [
            {"text": "Domain Generation Algorithm (DGA) rendezvous attempt", "is_correct": True},
            {"text": "Standard web browser pre-fetching", "is_correct": False},
            {"text": "BGP route poisoning", "is_correct": False},
            {"text": "DHCP lease renewal exhaustion", "is_correct": False},
        ]
    },
    {
        "code": "CTF-002",
        "text": "When investigating a suspected PsExec lateral movement challenge, which Windows service name and share are typically observed in the telemetry?",
        "difficulty": DifficultyLevel.ADVANCED,
        "cognitive_level": CognitiveLevel.UNDERSTAND,
        "points": 10,
        "explanation": "PsExec uploads an executable to the ADMIN$ share and starts a remote service named PSEXESVC recorded in Event ID 7045.",
        "options": [
            {"text": "ADMIN$ share and PSEXESVC service name", "is_correct": True},
            {"text": "NETLOGON share and LSASS service name", "is_correct": False},
            {"text": "SYSVOL share and DNS service name", "is_correct": False},
            {"text": "C$ share and WinDefend service name", "is_correct": False},
        ]
    },
    {
        "code": "CTF-003",
        "text": "What characteristic of a Kerberos Ticket Granting Service (TGS) request indicates potential Kerberoasting activity?",
        "difficulty": DifficultyLevel.ADVANCED,
        "cognitive_level": CognitiveLevel.APPLY,
        "points": 10,
        "explanation": "Attackers request encryption type 0x17 (RC4-HMAC) for service tickets because RC4 hashes are drastically faster to crack offline than AES.",
        "options": [
            {"text": "Ticket Encryption Type downgrade to 0x17 (RC4)", "is_correct": True},
            {"text": "Enforcing AES-256 encryption on all requests", "is_correct": False},
            {"text": "Requesting tickets only for disabled accounts", "is_correct": False},
            {"text": "Using IPv6 transport exclusively", "is_correct": False},
        ]
    },
    {
        "code": "CTF-004",
        "text": "In endpoint challenge investigation, which parent-child process relationship is considered highly anomalous on a user workstation?",
        "difficulty": DifficultyLevel.BEGINNER,
        "cognitive_level": CognitiveLevel.UNDERSTAND,
        "points": 10,
        "explanation": "Microsoft Word (WINWORD.EXE) spawning PowerShell or cmd.exe is strongly indicative of weaponized macro execution.",
        "options": [
            {"text": "WINWORD.EXE spawning powershell.exe", "is_correct": True},
            {"text": "explorer.exe spawning chrome.exe", "is_correct": False},
            {"text": "services.exe spawning svchost.exe", "is_correct": False},
            {"text": "system spawning smss.exe", "is_correct": False},
        ]
    },
    {
        "code": "CTF-005",
        "text": "What distinguishes an adversary's Golden Ticket attack from legitimate Kerberos ticket issuance?",
        "difficulty": DifficultyLevel.ADVANCED,
        "cognitive_level": CognitiveLevel.ANALYZE,
        "points": 15,
        "explanation": "Golden Tickets forged with the KRBTGT key typically specify arbitrary long lifespans, such as 10 years, compared to the standard 10-hour domain default.",
        "options": [
            {"text": "Unusually long ticket validity lifetime (e.g. 10 years)", "is_correct": True},
            {"text": "Requiring two-factor authentication on every hop", "is_correct": False},
            {"text": "Issued exclusively through smartcard logon", "is_correct": False},
            {"text": "Valid only during non-business hours", "is_correct": False},
        ]
    }
]


def seed_challenge_lessons_and_questions(db: Session) -> dict[str, int]:
    """Seed CTF learning lessons and Question Bank entries."""
    course = db.scalars(select(Course)).first()
    if not course:
        course = Course(
            title="Advanced Cybersecurity Operations",
            slug="advanced-cybersecurity-operations",
            description="SOC engineering, threat analysis, and automated response.",
        )
        db.add(course)
        db.flush()

    module = db.scalars(
        select(Module).where(Module.slug == "ctf-and-advanced-training")
    ).first()
    if not module:
        module = Module(
            course_id=course.id,
            title="CTF & Advanced Defensive Cybersecurity Training",
            slug="ctf-and-advanced-training",
            description="Hands-on challenge methodologies, packet dissection, and defensive problem solving.",
            order_index=19,
            difficulty=DifficultyLevel.ADVANCED,
        )
        db.add(module)
        db.flush()

    topic = db.scalars(
        select(Topic).where(Topic.slug == "ctf-methodology-and-practice")
    ).first()
    if not topic:
        topic = Topic(
            module_id=module.id,
            title="CTF Defensive Methodologies & Forensics",
            slug="ctf-methodology-and-practice",
            description="Learn how to approach, investigate, and solve complex cybersecurity challenges.",
            difficulty=DifficultyLevel.ADVANCED,
            order_index=1,
            estimated_minutes=120,
        )
        db.add(topic)
        db.flush()

    # Seed Lessons
    lessons_added = 0
    for l_data in CHALLENGE_LESSONS:
        existing = db.scalars(
            select(Lesson).where(Lesson.slug == l_data["slug"])
        ).first()
        if not existing:
            lesson = Lesson(
                topic_id=topic.id,
                title=l_data["title"],
                slug=l_data["slug"],
                content_type=ContentType.LESSON,
                order_index=l_data["order_index"],
                estimated_minutes=l_data["estimated_minutes"],
                difficulty=l_data["difficulty"],
                content=l_data["content"],
            )
            db.add(lesson)
            lessons_added += 1

    # Seed Questions
    questions_added = 0
    for q_data in CHALLENGE_QUESTIONS:
        existing_q = db.scalars(
            select(Question).where(Question.code == q_data["code"])
        ).first()
        if not existing_q:
            q = Question(
                topic_id=topic.id,
                code=q_data["code"],
                question_text=q_data["text"],
                question_type=QuestionType.CTF_CHALLENGE,
                difficulty=q_data["difficulty"],
                cognitive_level=q_data["cognitive_level"],
                points=q_data["points"],
                status=QuestionStatus.PUBLISHED,
                explanation=q_data["explanation"],
            )
            db.add(q)
            db.flush()

            for idx, opt in enumerate(q_data["options"], 1):
                option = QuestionOption(
                    question_id=q.id,
                    option_text=opt["text"],
                    is_correct=opt["is_correct"],
                    order_index=idx,
                )
                db.add(option)
            questions_added += 1

    db.commit()
    return {"lessons_added": lessons_added, "questions_added": questions_added}
