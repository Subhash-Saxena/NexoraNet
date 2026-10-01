# NexoraNet — Learning System Architecture

> **NexoraNet**: *"Learn. Simulate. Analyze. Defend."*  
> **Component**: Step 3 — Learning System & Curriculum Architecture

---

## 1. Executive Overview

The **NexoraNet Learning System** transforms the foundational database architecture established in Step 2 into an interactive, pedagogical, and cybersecurity-centric learning experience.

Rather than presenting static text, the learning system is structured around the philosophy:
```
LEARN ➔ UNDERSTAND ➔ VISUALIZE ➔ PRACTICE ➔ OBSERVE ➔ APPLY ➔ TEST ➔ DEFEND
```

Every foundational networking concept is directly tied to:
1. **Plain-English Explanations ("BCA Simple")** for beginners and undergraduate computer science students.
2. **Technical Deep-Dives** covering RFC specifications, frame formats, and bit-level header offsets.
3. **Offensive Exploit Vectors** showing how adversaries weaponize protocol behaviors (e.g., SYN floods, ARP spoofing, DNS cache poisoning, rogue DHCP).
4. **Defensive Hardening Controls** demonstrating blue-team remediations (e.g., SYN cookies, Dynamic ARP Inspection, DHCP Snooping, DNSSEC).
5. **Interactive Protocol Visualizers** rendering SVG and dynamic state-machine diagrams natively in the browser without external image dependencies.

---

## 2. API Endpoints Specification

All learning endpoints are versioned under `/api/v1/` and enforce server-side state integrity.

### 2.1 Curriculum Modules & Topics
| Endpoint | Method | Response Schema | Description |
|---|---|---|---|
| `/api/v1/modules/{module_id}` | `GET` | `ModuleDetail` | Returns module info, order index, difficulty, and child topics list. Accepts numeric ID or slug. |
| `/api/v1/topics` | `GET` | `List[TopicBrief]` | Filterable by `module_id` and `difficulty`. |
| `/api/v1/topics/{topic_id}` | `GET` | `TopicDetailExtended` | Topic detail with prerequisites, learning objectives, security relevance, child lessons with progress, and next/prev topic links. |
| `/api/v1/topics/{topic_id}/lessons`| `GET` | `List[LessonBriefWithProgress]` | All lessons in topic with student completion status and bookmark state. |

### 2.2 Lesson Reading & Navigation
| Endpoint | Method | Response Schema | Description |
|---|---|---|---|
| `/api/v1/lessons/{lesson_id}` | `GET` | `LessonDetailExtended` | Full lesson reading model with markdown content, difficulty, breadcrumbs, next/previous lesson, and related lab/test links. |
| `/api/v1/lessons/{lesson_id}/next` | `GET` | `LessonBrief` or `null` | Traverses within the topic or seamlessly leaps to the first lesson of the next topic. |
| `/api/v1/lessons/{lesson_id}/previous`| `GET` | `LessonBrief` or `null` | Traverses to prior lesson or last lesson of prior topic. |
| `/api/v1/lessons/{lesson_id}/start` | `POST` | `LessonActionResponse` | Idempotently sets lesson progress to `IN_PROGRESS` and updates `last_accessed_at`. |
| `/api/v1/lessons/{lesson_id}/complete` | `POST` | `LessonActionResponse` | Sets lesson status to `COMPLETED`, records `completed_at`, and triggers atomic topic progress recalculation. |

### 2.3 Progress Telemetry & Discovery
| Endpoint | Method | Response Schema | Description |
|---|---|---|---|
| `/api/v1/learning/progress` | `GET` | `LearningProgressResponse` | Computes overall completion %, level progress (Beginner, Intermediate, Advanced), remaining counts, and resolves the next uncompleted lesson (`continue_learning`). |
| `/api/v1/learning/search` | `GET` | `LearningSearchResponse` | Multi-entity curriculum search matching lessons, topics, and modules with case-insensitive difficulty filters. |
| `/api/v1/learning/bookmarks` | `GET` | `List[BookmarkItem]` | Returns all lessons saved by the current user ordered by most recently saved. |
| `/api/v1/lessons/{lesson_id}/bookmark` | `POST` | `{"message": "...", "bookmarked": true}` | Bookmarks a lesson for quick access. |
| `/api/v1/lessons/{lesson_id}/bookmark` | `DELETE` | `{"message": "...", "bookmarked": false}`| Removes bookmark. |

---

## 3. Database Schema Enhancements (Alembic Migration: `749a1792479c`)

1. **Prerequisite Dependency Graph**:
   - `topic_prerequisites` association table with foreign keys `(topic_id, prerequisite_id)` and composite primary key.
   - `Topic` model augmented with `estimated_minutes`, `learning_objectives` (JSON array of strings), `security_relevance` (text), and self-referential many-to-many relationship `prerequisites`.

2. **Temporal Lesson Progress**:
   - `lesson_progress` table extended with `started_at` (`DateTime(timezone=True)`) and `last_accessed_at` (`DateTime(timezone=True)`).
   - Server-enforced progress state machine:
     ```
     NOT_STARTED ➔ IN_PROGRESS ➔ COMPLETED
     ```

3. **Curriculum Bookmarking**:
   - `lesson_bookmarks` table:
     - `id` (Integer PK)
     - `user_id` (FK to `users.id` with `ondelete="CASCADE"`)
     - `lesson_id` (FK to `lessons.id` with `ondelete="CASCADE"`)
     - `created_at` (DateTime timestamp)
     - Unique constraint: `uq_user_lesson_bookmark (user_id, lesson_id)`

---

## 4. Interactive Protocol Visualizers

NexoraNet features 5 self-contained, interactive protocol diagrams built with pure React, SVG, and CSS without third-party chart libraries:

1. **`OSIStackDiagram`** (`/learning` & embedded in L1-L7 lessons):
   - Interactive 7-layer stack (Application down to Physical).
   - Displays PDU mapping (Data, Segment, Packet, Frame, Bits), header fields, and common protocols.
   - Toggle between Encapsulation (L7 ➔ L1) and Decapsulation (L1 ➔ L7).
   - Dedicated Offensive Threat Vector & Defensive Hardening breakdowns per layer.

2. **`TCPHandshakeDiagram`** (`/learning` & embedded in transport lessons):
   - Interactive 4-step state machine stepper (Step 0: LISTEN ➔ Step 1: SYN [Seq=1000] ➔ Step 2: SYN-ACK [Seq=5000, Ack=1001] ➔ Step 3: ACK [Seq=1001, Ack=5001] ➔ ESTABLISHED).
   - Interactive **SYN Flood Simulation Mode**: demonstrates half-open TCP connection exhaustion in kernel backlog queue and SYN Cookies (`syncookies=1`) cryptographic defense.

3. **`DNSResolutionDiagram`** (`/learning` & embedded in DNS lessons):
   - 6-step recursive resolution pipeline: Client Browser ➔ Recursive Resolver ➔ Root (`.`) Nameserver ➔ TLD (`.com`) Nameserver ➔ Authoritative Nameserver ➔ Client Cache.
   - Interactive **Kaminsky DNS Cache Poisoning Mode**: demonstrates 16-bit transaction ID race conditions, forged NS delegations, and DNSSEC digital signature verification.

4. **`DHCPSequenceDiagram`** (`/learning` & embedded in DHCP lessons):
   - 4-stage DORA process (Discover ➔ Offer ➔ Request ➔ Acknowledge) with IP/Port/Flag breakdowns.
   - Interactive **Rogue DHCP Server Mode**: demonstrates default gateway hijacking (MITM) and Cisco DHCP Snooping port trust mitigations.

5. **`EncapsulationDiagram`** (`/learning` & embedded in framing lessons):
   - Interactive packet inspector showing layered data framing: Ethernet II Header (14B) ➔ IPv4 Header (20B) ➔ TCP Header (20B) ➔ Payload ➔ FCS Trailer (4B).
   - Field-by-field inspector showing exact bit sizes, values, and Wireshark dissection tips.

---

## 5. Educational Content Components

- **`CalloutCard`**: Multi-perspective container supporting:
  - *BCA Simple*: Real-world analogies for high conceptual retention.
  - *Technical Deep-Dive*: Strict RFC details and low-level mechanics.
  - *Security & Attack Relevance*: CVEs, exploit vectors, and blue-team detections.
  - *Exam & Interview Note*: High-frequency interview traps and certification pointers.
- **`ScenarioCard`**: Incident investigation walkthrough with reported symptoms, forensic workflow, and root cause resolution.
- **`QuickRevisionCard`**: Port tables, CIDR notation cheat sheets, and core takeaways.
- **`LearningRoadmap`**: Interactive visual progression track through Beginner, Intermediate, and Advanced tiers.
- **`MarkdownContent`**: Custom, zero-dependency Markdown parser rendering headers, code blocks with copy-to-clipboard, tables, lists, callouts, and inline diagram shortcodes (`[DIAGRAM:<name>]`).
