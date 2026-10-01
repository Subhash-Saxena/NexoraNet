from fastapi import APIRouter

from app.api.v1.endpoints import (
    achievements,
    adaptive,
    adaptive_tests,
    admin,
    analytics,
    auth,
    automation,
    certificates,
    challenges,
    courses,
    detection,
    endpoint_security,
    incident_response,
    lab_attempts,
    labs,
    learning,
    lessons,
    mock_test_attempts,
    mock_tests,
    modules,
    packet_analysis,
    portfolio,
    progress,
    questions,
    recommendations,
    reports,
    siem,
    simulator,
    skills,
    soc,
    soc_scenarios,
    threat_hunting,
    threat_intel,
    topics,
)

api_v1_router = APIRouter()

api_v1_router.include_router(courses.router, prefix="/courses", tags=["Courses"])
api_v1_router.include_router(modules.router, prefix="/modules", tags=["Modules"])
api_v1_router.include_router(topics.router, prefix="/topics", tags=["Topics"])
api_v1_router.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
api_v1_router.include_router(learning.router, prefix="/learning", tags=["Learning"])
api_v1_router.include_router(labs.router, prefix="/labs", tags=["Labs"])
api_v1_router.include_router(
    lab_attempts.router, prefix="/lab-attempts", tags=["Lab Attempts"]
)
api_v1_router.include_router(
    mock_tests.router, prefix="/mock-tests", tags=["Mock Tests"]
)
api_v1_router.include_router(
    mock_test_attempts.router,
    prefix="/mock-test-attempts",
    tags=["Mock Test Attempts"],
)
api_v1_router.include_router(questions.router, prefix="/questions", tags=["Questions"])
api_v1_router.include_router(
    packet_analysis.router, prefix="/packet-analysis", tags=["Packet Analysis"]
)
api_v1_router.include_router(simulator.router, prefix="/simulator", tags=["Simulator"])
api_v1_router.include_router(
    detection.router, prefix="/detection", tags=["Detection Engineering"]
)
api_v1_router.include_router(soc.router, prefix="/soc", tags=["Mini SOC"])
api_v1_router.include_router(progress.router, prefix="/progress", tags=["Progress"])
api_v1_router.include_router(
    adaptive.router, prefix="/adaptive", tags=["Adaptive Testing & Recommendations"]
)
api_v1_router.include_router(
    adaptive_tests.router,
    prefix="/adaptive-tests",
    tags=["Adaptive Practice Sessions"],
)
api_v1_router.include_router(
    threat_intel.router,
    prefix="/threat-intel",
    tags=["Threat Intelligence"],
)
api_v1_router.include_router(
    threat_hunting.router,
    prefix="/threat-hunting",
    tags=["Threat Hunting & Investigation"],
)
api_v1_router.include_router(
    siem.router,
    prefix="/siem",
    tags=["SIEM & Security Log Analysis"],
)
api_v1_router.include_router(
    endpoint_security.router,
    prefix="/endpoint-security",
    tags=["Endpoint Security & Host Investigation"],
)
api_v1_router.include_router(
    incident_response.router,
    prefix="/incidents",
    tags=["Incident Response & Case Management"],
)
api_v1_router.include_router(
    incident_response.mitre_router,
    prefix="/mitre",
    tags=["MITRE ATT&CK Framework"],
)
api_v1_router.include_router(
    incident_response.playbook_router,
    prefix="/playbooks",
    tags=["Incident Response Playbooks"],
)
api_v1_router.include_router(
    automation.router,
    prefix="/automation",
    tags=["SOAR Security Automation"],
)
api_v1_router.include_router(
    soc_scenarios.router,
    prefix="/soc-scenarios",
    tags=["Advanced SOC Scenarios"],
)
api_v1_router.include_router(
    challenges.router,
    prefix="/challenges",
    tags=["CTF Challenges & Advanced Training"],
)
api_v1_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Student Analytics & Progress Telemetry"],
)
api_v1_router.include_router(
    skills.router,
    prefix="/skills",
    tags=["Cybersecurity Skills & Competency Matrix"],
)
api_v1_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["Pedagogical Recommendations"],
)
api_v1_router.include_router(
    reports.router,
    prefix="/reports",
    tags=["Assessment Reports"],
)
api_v1_router.include_router(
    certificates.router,
    prefix="/certificates",
    tags=["Educational Completion Certificates"],
)
api_v1_router.include_router(
    portfolio.router,
    prefix="/portfolio",
    tags=["Student Portfolio & Showcase"],
)
api_v1_router.include_router(
    achievements.router,
    prefix="/achievements",
    tags=["Educational Milestone Achievements"],
)
api_v1_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Administrative & Content Operations"],
)
api_v1_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Authentication & Security"],
)



