"""Educational Lessons & Question Bank Seeds for Step 18 SOAR & SOC Scenarios.

Seeds 15 comprehensive interactive lessons and 10+ Question Bank questions
covering Security Orchestration, Automation, Approval Gates, and 9-Stage Investigations.
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
from sqlalchemy.orm import Session


def seed_soar_lessons_and_questions(db: Session) -> dict[str, int]:
    """Seed or update Step 18 lessons and Question Bank questions."""

    # 1. Ensure Topic exists
    topic = db.query(Topic).filter(Topic.slug == "soar-and-soc-scenarios").first()
    if not topic:
        # Find or create Course and Module
        course = db.query(Course).first()
        if not course:
            course = Course(
                title="Advanced Cybersecurity Operations",
                slug="advanced-cybersecurity-operations",
                description="SOC engineering, threat analysis, and automated response.",
            )
            db.add(course)
            db.flush()

        module = (
            db.query(Module)
            .filter(Module.slug == "security-automation-and-scenarios")
            .first()
        )
        if not module:
            module = Module(
                course_id=course.id,
                title="Security Automation & SOC Investigation Scenarios",
                slug="security-automation-and-scenarios",
                description="Master SOAR playbooks, approval gates, and multi-stage investigative scenarios.",
                order_index=18,
                difficulty=DifficultyLevel.ADVANCED,
            )
            db.add(module)
            db.flush()

        topic = Topic(
            module_id=module.id,
            title="SOAR Security Automation & Advanced SOC Scenarios",
            slug="soar-and-soc-scenarios",
            description="Deep dive into SOAR orchestration, deterministic playbooks, and 9-stage SOC investigation scenarios.",
            difficulty=DifficultyLevel.ADVANCED,
            order_index=1,
            estimated_minutes=180,
            learning_objectives="- Understand SOAR architecture\n- Author branching playbooks\n- Master human-in-the-loop approvals\n- Execute 9-stage investigation methodology",
        )
        db.add(topic)
        db.flush()

    # 2. Seed 15 Lessons
    lessons_data = [
        {
            "slug": "soar-introduction-architecture",
            "title": "Introduction to SOAR: Security Orchestration, Automation, and Response",
            "description": "Understand what SOAR is, why modern SOCs require automation, and how orchestration unifies disparate tools.",
            "content": """# Introduction to SOAR

Modern Security Operations Centers (SOCs) face an overwhelming volume of alerts—often thousands per day. **SOAR** (Security Orchestration, Automation, and Response) addresses analyst fatigue, high Mean Time to Respond (MTTR), and repetitive manual tasks.

## The Three Pillars of SOAR

1. **Security Orchestration**: Unifies security tools (SIEM, EDR, Firewalls, Threat Intel feeds, Ticketing systems) into cohesive workflows via standard APIs and data formats.
2. **Security Automation**: Executes defined sequence of tasks without human intervention (e.g., querying VirusTotal, checking DNS logs, blocking malicious IP addresses).
3. **Security Response**: Coordinates post-incident containment, eradication, and lessons learned documentation.

## Educational Simulation Safety
In NexoraNet, all SOAR actions are strictly simulated non-destructively:
- No real OS commands are executed
- No real external network requests are sent
- Every automated containment action operates against synthetic entities with `simulation_only = True`.
""",
        },
        {
            "slug": "soar-vs-siem-differentiation",
            "title": "Orchestration vs Automation: Architectural Foundations",
            "description": "Examine the technical differences between alert detection (SIEM) and proactive remediation orchestration (SOAR).",
            "content": """# Orchestration vs Automation

While SIEM collects and correlates logs to **detect** suspicious events, SOAR **acts** upon those detections.

## The Automation Lifecycle

```
[ SIEM / Detection Alert ]
           ↓
[ Trigger: Alert Created ]
           ↓
[ SOAR Playbook Initiated ]
           ↓
[ Context Enrichment ]
           ↓
[ Branching Conditions Evaluated ]
           ↓
[ Response Action Simulated ]
```

## Why Pure Automation Can Be Dangerous
Without guardrails, automated playbooks can cause catastrophic self-inflicted Denial of Service (e.g., blocking internal domain controllers or isolating critical production database clusters). Hence, mature SOAR platforms implement **analyst approval gates**.
""",
        },
        {
            "slug": "declarative-playbook-engineering",
            "title": "Playbook Engineering: Linear vs Branching Decision Trees",
            "description": "Learn to model security workflows into structured, maintainable playbooks with conditional execution paths.",
            "content": """# Playbook Engineering

A **Security Playbook** is a formal, standardized operating procedure translated into machine-executable logic.

## Step Architecture
Each step inside a NexoraNet playbook possesses:
- `step_order`: Execution sequence
- `action_type`: Strictly allowlisted action
- `parameters_json`: Static or interpolated arguments (`{{ioc_value}}`)
- `condition_json`: Boolean rule determining whether the step executes or is skipped
- `on_failure`: `STOP` or `CONTINUE`
- `retry_count`: Maximum automatic retries (capped at 2)

```json
{
  "operator": "greater_than_or_equal",
  "field": "threat_score",
  "value": 70
}
```
""",
        },
        {
            "slug": "safe-condition-evaluator-design",
            "title": "Condition Evaluator Design & AST Safety Invariants",
            "description": "Explore the design of safe, restricted condition evaluators that avoid dynamic code execution risks.",
            "content": """# Safe Condition Evaluators

In secure software design, executing dynamic conditions must never use dangerous functions like `eval()` or `exec()`.

## NexoraNet Whitelist Condition Engine
NexoraNet implements `SafeConditionEvaluator` supporting 13 strict operators:
- Equality: `equals`, `not_equals`
- String Matching: `contains`, `starts_with`, `ends_with`
- Numeric Comparison: `greater_than`, `less_than`, `gte`, `lte`
- Set Membership: `in`, `not_in`
- Existence: `exists`, `not_exists`

Nested logic (`and` / `or`) allows sophisticated decision rules while guaranteeing zero arbitrary code execution.
""",
        },
        {
            "slug": "analyst-approval-gates-workflows",
            "title": "Human-in-the-Loop: Analyst Authorization Gates",
            "description": "Understand why high-risk automated containment requires human-in-the-loop authorization gates.",
            "content": """# Analyst Approval Gates

Certain response actions carry severe operational risk:
- Host network isolation on a core ERP server
- Terminating user accounts of corporate executives
- Subnet-wide perimeter firewall blacklisting

## The Gate Workflow
1. Execution progresses through low-risk enrichment steps.
2. Engine encounters `requires_approval = True`.
3. Execution pauses and transitions to `WAITING_APPROVAL`.
4. Security analyst inspects alert context, evidence, and business impact.
5. Analyst clicks **Approve** or **Reject** with documented justification.
6. Engine resumes or cancels execution cleanly.
""",
        },
        {
            "slug": "idempotency-and-failure-handling",
            "title": "Idempotency & Failure Handling in Security Orchestration",
            "description": "Learn how idempotency keys and retry limits prevent duplicate tickets and cascade failures.",
            "content": """# Idempotency and Resilience

In automated operations, network blips or race conditions can cause duplicate triggers.

## Idempotency Keys
An **Idempotency Key** ensures an identical action triggered twice produces the same single result without duplicating records:
`idempotency_key = f"{playbook_id}:{trigger_source}:{source_id}"`

## Failure Semantics
When an action fails:
- Step retries up to 2 times
- If failure persists, engine evaluates `on_failure`:
  - `STOP`: Halts playbook, records error message, marks execution `FAILED`
  - `CONTINUE`: Logs error and allows subsequent steps to proceed
""",
        },
        {
            "slug": "phishing-auto-triage-playbook",
            "title": "Phishing Auto-Triage & URL Sandboxing Playbooks",
            "description": "Detailed walkthrough of automated phishing triage: indicator extraction, reputation scoring, and case escalation.",
            "content": """# Phishing Triage Playbook

Phishing represents over 80% of reported SOC security events.

## Step-by-Step Triage Flow
1. **Extract Indicators**: Parse domain, sender IP, embedded hyperlinks.
2. **Query Threat Intelligence**: Check domain age, reputation, and threat feed sightings.
3. **Simulated Sandboxing**: Inspect redirect hops and credential forms.
4. **Conditional Case Creation**: Open high-priority Incident Case only if threat score exceeds 60.
5. **Analyst Dispatch**: Notify Tier 1 triage analyst.
""",
        },
        {
            "slug": "endpoint-isolation-forensic-automation",
            "title": "Host Isolation & Volatile Forensic Snapshot Automation",
            "description": "Analyze automated endpoint containment workflows that preserve volatile forensic evidence before network cut.",
            "content": """# Endpoint Containment Playbooks

When malware executes on an internal endpoint, seconds matter to prevent lateral movement.

## Forensic Ordering
Crucial rule: **Never reboot or power off the machine!**
Powering down destroys:
- Active network socket states
- Running process memory and injected DLLs
- Decryption keys held in RAM

SOAR automates capturing volatile memory triage packages before applying firewall network isolation.
""",
        },
        {
            "slug": "credential-stuffing-response-workflow",
            "title": "Credential Stuffing & Impossible Travel SOAR Workflows",
            "description": "Automating identity defense against impossible travel and credential spraying attacks.",
            "content": """# Identity Defense Automation

Impossible travel occurs when an account successfully authenticates from geographically distant locations within a time frame that is physically impossible.

## Automated Response Playbook
1. Correlate authentication logs across past 60 minutes.
2. Enrich attacking IP (check proxy/VPN exit status).
3. Block source IP on perimeter edge.
4. Terminate active OAuth sessions across all devices.
5. Enforce password reset upon next login.
""",
        },
        {
            "slug": "nine-stage-investigation-methodology",
            "title": "The 9-Stage Incident Investigation Methodology",
            "description": "Master the structured 9-stage investigative methodology from initial signal to post-incident review.",
            "content": """# The 9-Stage Investigation Methodology

NexoraNet structured investigation methodology:
1. **Initial Signal**: Triage alert severity and scope.
2. **Evidence Selection**: Filter signal from noise distractors.
3. **Correlation**: Link events across logs and network streams.
4. **Hypothesis**: Formulate competing attack theories.
5. **Validation**: Test hypothesis against verifiable evidence.
6. **MITRE ATT&CK Mapping**: Attribute tactics and techniques.
7. **Response Decision**: Deploy containment and eradication.
8. **Outcome**: Review simulated impact and collateral damage.
9. **Lessons Learned**: Document detection gaps and policy improvements.
""",
        },
        {
            "slug": "evidence-selection-signal-vs-noise",
            "title": "Evidence Selection: Balancing Recall and Noise Distraction",
            "description": "Learn to distinguish crucial forensic indicators from benign background system noise.",
            "content": """# Evidence Selection: Signal vs Noise

Junior analysts often collect every available log entry, creating forensic clutter that obscures the attack vector.

## Identifying Noise Distractors
Common benign background activity:
- NTP daemon time sync packets
- Chrome/Edge browser cache purges
- Windows Update catalog checks
- Printer spooler discovery broadcasts

Accurate investigation requires high **precision** (selecting only pertinent evidence) and high **recall** (not missing critical IOCs).
""",
        },
        {
            "slug": "cross-source-correlation-techniques",
            "title": "Cross-Data Source Event Correlation in Multi-Stage Attacks",
            "description": "Connecting dots between firewall drops, DNS queries, Sysmon process spawns, and directory authentications.",
            "content": """# Cross-Source Event Correlation

Adversaries do not operate in a single telemetry silo.

## Correlation Anchors
- **Timestamps**: Align UTC timestamps across disparate sources.
- **Process IDs (PID) & Hashes**: Trace parent-child execution lineages.
- **IP & MAC Addresses**: Track DHCP lease history across VLANs.
- **User Accounts & SIDs**: Identify compromised account usage across domain members.
""",
        },
        {
            "slug": "hypothesis-testing-and-validation",
            "title": "Hypothesis Testing & Validation in Advanced Threat Hunting",
            "description": "Apply the scientific method to cybersecurity investigations through structured hypothesis testing.",
            "content": """# Hypothesis Testing & Validation

Rather than jumping to premature conclusions, effective analysts formulate verifiable hypotheses:

## Competing Hypotheses Framework
- Hypothesis A: Phishing link delivered secondary Cobalt Strike payload.
- Hypothesis B: Authorized IT administrator ran Sysinternals PsExec script.
- Hypothesis C: Automated third-party penetration test scheduled by compliance.

Test each hypothesis against the gathered evidence: which facts confirm or invalidate each premise?
""",
        },
        {
            "slug": "mitre-attack-mapping-attribution",
            "title": "MITRE ATT&CK Attribution & Technique Mapping",
            "description": "Standardize adversary behaviors using MITRE ATT&CK enterprise tactics, techniques, and procedures.",
            "content": """# MITRE ATT&CK Attribution

Mapping observed actions to MITRE ATT&CK provides a shared taxonomy across security teams:

## Key Tactics
- **Initial Access**: T1566 (Phishing), T1190 (Exploit Public-Facing App)
- **Execution**: T1059.001 (PowerShell), T1204 (User Execution)
- **Persistence**: T1053.005 (Scheduled Task), T1546.003 (WMI Subscriptions)
- **Privilege Escalation**: T1055 (Process Injection), T1548 (Abuse Elevation Control)
- **Defense Evasion**: T1027 (Obfuscated Files), T1036 (Masquerading)
- **Credential Access**: T1003 (OS Credential Dumping), T1558 (Kerberoasting)
- **Lateral Movement**: T1021.002 (SMB Admin Shares / PsExec)
""",
        },
        {
            "slug": "post-incident-lessons-learned-governance",
            "title": "Post-Incident Reflection: Lessons Learned & Security Governance",
            "description": "Transform investigation outcomes into durable defense posture improvements and detection rules.",
            "content": """# Lessons Learned & Post-Mortem

The incident lifecycle is never complete until the organization hardens itself against recurrence.

## The Post-Incident Review
1. **Root Cause Analysis**: How did the adversary gain initial footholds?
2. **Detection Gaps**: Why didn't existing IDS/SIEM rules catch the stager earlier?
3. **Response Efficacy**: Did automated playbooks contain lateral spread within SLA?
4. **Actionable Recommendations**: Deploy canary tripwires, enforce MFA, or restrict outbound egress ports.
""",
        },
    ]

    lessons_seeded = 0
    for idx, l_data in enumerate(lessons_data, start=1):
        existing_l = (
            db.query(Lesson)
            .filter(Lesson.topic_id == topic.id, Lesson.slug == l_data["slug"])
            .first()
        )
        if existing_l:
            existing_l.title = l_data["title"]
            existing_l.description = l_data["description"]
            existing_l.content = l_data["content"]
            existing_l.order_index = idx
        else:
            new_l = Lesson(
                topic_id=topic.id,
                title=l_data["title"],
                slug=l_data["slug"],
                description=l_data["description"],
                content=l_data["content"],
                content_type=ContentType.LESSON,
                order_index=idx,
                estimated_minutes=15,
                difficulty=DifficultyLevel.ADVANCED,
                is_published=True,
            )
            db.add(new_l)
        lessons_seeded += 1

    # 3. Seed Question Bank Questions for QuestionType.SOAR and QuestionType.SOC_SCENARIO
    questions_data = [
        {
            "code": "SOAR-QB-001",
            "type": QuestionType.SOAR,
            "text": "Which of the following describes the primary architectural purpose of a human-in-the-loop approval gate in a SOAR playbook?",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "cognitive": CognitiveLevel.ANALYZE,
            "explanation": "Approval gates require explicit analyst authorization before executing high-impact response actions (such as host isolation or account revocation) to prevent business disruption from false positives.",
            "points": 2,
            "options": [
                {"text": "To pause execution on high-risk containment actions until a security analyst authorizes the response", "is_correct": True},
                {"text": "To compile Python scripts into executable machine code", "is_correct": False},
                {"text": "To bypass SIEM log ingestion filters", "is_correct": False},
                {"text": "To speed up linear execution without logging state transitions", "is_correct": False},
            ],
        },
        {
            "code": "SOAR-QB-002",
            "type": QuestionType.SOAR,
            "text": "Why is idempotency essential when designing automated security response playbooks?",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "cognitive": CognitiveLevel.UNDERSTAND,
            "explanation": "Idempotency ensures that if an identical alert or event triggers a playbook multiple times, subsequent executions do not create duplicate tickets or perform redundant containment actions.",
            "points": 2,
            "options": [
                {"text": "It guarantees that executing the same playbook multiple times with the same input produces the same single outcome without duplicate side effects", "is_correct": True},
                {"text": "It encrypts all volatile RAM memory before network isolation", "is_correct": False},
                {"text": "It automatically converts PowerShell commands into Bash scripts", "is_correct": False},
                {"text": "It permits playbooks to execute arbitrary unvalidated user commands", "is_correct": False},
            ],
        },
        {
            "code": "SOAR-QB-003",
            "type": QuestionType.SOAR,
            "text": "When an automated endpoint containment playbook responds to confirmed ransomware, which action should precede network isolation?",
            "difficulty": DifficultyLevel.ADVANCED,
            "cognitive": CognitiveLevel.ANALYZE,
            "explanation": "Collecting endpoint telemetry and capturing volatile memory triage snapshots before cutting connectivity ensures vital volatile evidence (process injection, encryption keys) is preserved for forensic analysis.",
            "points": 3,
            "options": [
                {"text": "Capturing volatile memory and endpoint process triage telemetry before network cut", "is_correct": True},
                {"text": "Powering off the machine at the wall outlet", "is_correct": False},
                {"text": "Formatting the hard drive immediately", "is_correct": False},
                {"text": "Flushing DNS caches and rebooting the operating system", "is_correct": False},
            ],
        },
        {
            "code": "SOAR-QB-004",
            "type": QuestionType.SOAR,
            "text": "In a secure SOAR condition evaluator, why is dynamic code execution (eval/exec) strictly avoided in favor of AST/whitelist comparison operators?",
            "difficulty": DifficultyLevel.ADVANCED,
            "cognitive": CognitiveLevel.UNDERSTAND,
            "explanation": "Dynamic code evaluation (eval/exec) exposes the automation engine to Remote Code Execution (RCE) if untrusted alert metadata is injected into condition strings.",
            "points": 2,
            "options": [
                {"text": "It prevents arbitrary code execution and command injection vulnerabilities from untrusted alert payloads", "is_correct": True},
                {"text": "It reduces memory consumption of SQLite databases", "is_correct": False},
                {"text": "It disables network firewalls during dry runs", "is_correct": False},
                {"text": "It forces playbooks to run on multithreaded GPUs", "is_correct": False},
            ],
        },
        {
            "code": "SOAR-QB-005",
            "type": QuestionType.SOAR,
            "text": "Which status transition occurs in a SOAR execution engine when a playbook step fails and its configured 'on_failure' setting is 'STOP'?",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "cognitive": CognitiveLevel.APPLY,
            "explanation": "When a step fails and on_failure is set to STOP, the engine halts further step processing, logs the error, and marks the execution status as FAILED.",
            "points": 2,
            "options": [
                {"text": "Execution halts immediately, audit logs are recorded, and execution status is set to FAILED", "is_correct": True},
                {"text": "The playbook skips the error and marks execution COMPLETED", "is_correct": False},
                {"text": "The database deletes all previous step logs", "is_correct": False},
                {"text": "The engine enters an infinite loop waiting for manual reboot", "is_correct": False},
            ],
        },
        {
            "code": "SOC-SCEN-001",
            "type": QuestionType.SOC_SCENARIO,
            "text": "In the 9-stage investigation methodology, what is the primary risk of selecting irrelevant distractor evidence during Stage 2 (Evidence Selection)?",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "cognitive": CognitiveLevel.ANALYZE,
            "explanation": "Selecting noise distractors dilutes analyst focus, leads to false correlations, wastes investigative triage time, and incurs score penalties in structured evaluations.",
            "points": 2,
            "options": [
                {"text": "It dilutes focus with benign background noise, leads to flawed hypotheses, and wastes critical containment time", "is_correct": True},
                {"text": "It automatically crashes the SIEM database", "is_correct": False},
                {"text": "It immediately triggers a false positive alert to the FBI", "is_correct": False},
                {"text": "It forces the operating system to reformat the primary drive", "is_correct": False},
            ],
        },
        {
            "code": "SOC-SCEN-002",
            "type": QuestionType.SOC_SCENARIO,
            "text": "During Stage 3 (Correlation), an analyst observes high-entropy DNS subdomains (e.g., d9a1b8.tunnel-exfil.xyz) alongside outbound UDP/53 bursts. What is the most plausible hypothesis?",
            "difficulty": DifficultyLevel.ADVANCED,
            "cognitive": CognitiveLevel.ANALYZE,
            "explanation": "High-entropy subdomains combined with rapid UDP/53 queries are characteristic of DNS tunneling for covert C2 beaconing or data exfiltration.",
            "points": 3,
            "options": [
                {"text": "DNS tunneling is being used as a covert channel for data exfiltration or C2 communication", "is_correct": True},
                {"text": "A standard user is browsing legitimate high-traffic news websites", "is_correct": False},
                {"text": "The recursive resolver is performing routine DNSSEC key signing maintenance", "is_correct": False},
                {"text": "A network printer is requesting a dynamic DHCP IP address", "is_correct": False},
            ],
        },
        {
            "code": "SOC-SCEN-003",
            "type": QuestionType.SOC_SCENARIO,
            "text": "When investigating an Active Directory Kerberoasting incident (Event 4769), which encryption type requested in the TGS ticket signifies an offline cracking attempt?",
            "difficulty": DifficultyLevel.ADVANCED,
            "cognitive": CognitiveLevel.ANALYZE,
            "explanation": "Encryption type 0x17 (RC4-HMAC) represents legacy Kerberos encryption that adversaries deliberately request because RC4 ticket hashes can be easily cracked offline using tools like hashcat.",
            "points": 3,
            "options": [
                {"text": "0x17 (RC4-HMAC) legacy downgrade ticket", "is_correct": True},
                {"text": "0x12 (AES-256-CTS-HMAC-SHA1-96)", "is_correct": False},
                {"text": "0x11 (AES-128-CTS-HMAC-SHA1-96)", "is_correct": False},
                {"text": "0x01 (DES-CBC-CRC)", "is_correct": False},
            ],
        },
        {
            "code": "SOC-SCEN-004",
            "type": QuestionType.SOC_SCENARIO,
            "text": "In Stage 7 (Response Decision), why is immediate host power-off classified as a harmful response for an in-memory process hollowing infection?",
            "difficulty": DifficultyLevel.ADVANCED,
            "cognitive": CognitiveLevel.ANALYZE,
            "explanation": "Powering off the computer wipes volatile RAM memory, destroying unbacked injected shellcode, decryption keys, and network socket traces necessary for attribution and root-cause analysis.",
            "points": 3,
            "options": [
                {"text": "It completely wipes volatile RAM, destroying unbacked memory injection artifacts and active C2 socket states", "is_correct": True},
                {"text": "It accelerates file encryption across connected mapped network shares", "is_correct": False},
                {"text": "It bypasses BIOS boot passwords on the next startup", "is_correct": False},
                {"text": "It sends an alert to the adversary informing them of the discovery", "is_correct": False},
            ],
        },
        {
            "code": "SOC-SCEN-005",
            "type": QuestionType.SOC_SCENARIO,
            "text": "Which MITRE ATT&CK technique correctly attributes an attacker using certutil.exe to download a malicious payload via -urlcache?",
            "difficulty": DifficultyLevel.INTERMEDIATE,
            "cognitive": CognitiveLevel.APPLY,
            "explanation": "Using built-in system tools like certutil or bitsadmin to download external tools into an environment is mapped to T1105 (Ingress Tool Transfer).",
            "points": 2,
            "options": [
                {"text": "T1105 - Ingress Tool Transfer", "is_correct": True},
                {"text": "T1486 - Data Encrypted for Impact", "is_correct": False},
                {"text": "T1059.001 - PowerShell", "is_correct": False},
                {"text": "T1110 - Brute Force", "is_correct": False},
            ],
        },
    ]

    questions_seeded = 0
    for q_data in questions_data:
        existing_q = db.query(Question).filter(Question.code == q_data["code"]).first()
        if existing_q:
            existing_q.question_text = q_data["text"]
            existing_q.explanation = q_data["explanation"]
            existing_q.points = q_data["points"]
            question_obj = existing_q
        else:
            question_obj = Question(
                code=q_data["code"],
                question_text=q_data["text"],
                question_type=q_data["type"],
                topic_id=topic.id,
                difficulty=q_data["difficulty"],
                cognitive_level=q_data["cognitive"],
                explanation=q_data["explanation"],
                points=q_data["points"],
                estimated_seconds=60,
                status=QuestionStatus.PUBLISHED,
            )
            db.add(question_obj)
            db.flush()

        # Update options
        db.query(QuestionOption).filter(QuestionOption.question_id == question_obj.id).delete()
        for idx, opt in enumerate(q_data["options"]):
            db.add(
                QuestionOption(
                    question_id=question_obj.id,
                    option_text=opt["text"],
                    is_correct=opt["is_correct"],
                    order_index=idx,
                )
            )
        questions_seeded += 1

    db.commit()
    return {"lessons_seeded": lessons_seeded, "questions_seeded": questions_seeded}
