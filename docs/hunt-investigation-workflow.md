# NexoraNet Hunt Investigation Workflow & Rubric

## 1. Investigation Lifecycle

The **NexoraNet Investigation Workflow** guides students through a structured methodology used in Tier 2/Tier 3 SOC investigations and proactive threat hunting teams.

```text
1. Formulate Hypothesis
   └── Define expected adversary behavior, target systems, and observables.
2. Interrogate Telemetry
   └── Run HQL queries, inspect packet details, and review alert context.
3. Graph & Pivot Entities
   └── Expand the blast radius across IPs, Domains, Ports, and Signatures.
4. Bind & Categorize Evidence
   └── Attach events as Supporting, Contradicting, or Contextual evidence.
5. Synthesize Findings
   └── Group validated evidence into structured findings tagged with MITRE ATT&CK.
6. Validate / Refute Hypothesis
   └── Update hypothesis status with objective technical justification.
7. Record Journal Notes
   └── Document chronological findings, command outputs, and milestones.
8. Submit Conclusion & Receive Score
   └── Choose disposition, provide executive summary, and evaluate against rubric.
```

---

## 2. Hypothesis Management

Threat hunting is hypothesis-driven. An investigation starts with an educated assumption grounded in threat intelligence or unusual network baselines.

### Hypothesis Lifecycle States
- `PROPOSED`: Initial hypothesis drafted; investigative queries pending.
- `INVESTIGATING`: Active telemetry filtering and evidence collection underway.
- `CONFIRMED`: Discovered evidence unequivocally supports the adversary behavior.
- `REFUTED`: Evidence demonstrates traffic was benign, normal administrative activity, or an expected baseline.
- `INCONCLUSIVE`: Insufficient telemetry available to reach a high-confidence determination.

### Confidence Ratings
- `LOW`: Anecdotal or single-point telemetry match; high risk of misinterpretation.
- `MEDIUM`: Multiple corroborating events; basic timeline alignment.
- `HIGH`: Multi-source corroboration (e.g. packet payload + IOC threat feed + process beacon pattern).

---

## 3. Evidence Collection & Binding

Analysts must not jump directly from an alert to a conclusion. Every claim must be tethered to specific raw events.

### Evidence Types & Relevance
1. **Supporting Evidence**: Directly proves the adversary's actions (e.g. outbound HTTP POST to known C2 IP with anomalous user-agent).
2. **Contradicting Evidence**: Disproves the hypothesis or points to legitimate administrative tooling (e.g. source IP belongs to vulnerability scanner or authorized backup script).
3. **Contextual Evidence**: Establishes network baselines, timestamps, DHCP leases, or DNS resolutions surrounding the event.

Analysts must supply a `relevance_note` explaining *why* the bound event matters to the investigation.

---

## 4. Entity Correlation & Pivoting

### Graph Explorer
The investigation graph visualizes relationship topology centered on the investigation's seed entities.
- **Node Types**: `IP`, `DOMAIN`, `PORT`, `ALERT`, `PCAP`.
- **Edge Types**: `COMMUNICATED_WITH`, `RESOLVED_TO`, `CONNECTED_ON`, `TRIGGERED`.
- **Bounded Expansion**: Maximum traversal depth $\le 2$ and maximum node count $\le 50$ to maintain clarity and prevent browser lag.

### Pivoting Actions
- **IP Pivot**: Surfaces all domains resolved, ports contacted, alerts triggered, and concurrent communicating nodes.
- **Domain Pivot**: Highlights resolving IP history, hosting infrastructure, and frequency of client queries.
- **Port Pivot**: Identifies all hosts receiving connections on standard (e.g. 445/SMB, 88/Kerberos) or abnormal ports.

---

## 5. Educational Scoring Rubric (100 Points)

When an analyst submits a hunt conclusion, the engine computes an educational score across 5 essential dimensions:

```text
┌────────────────────────────────────────────────────────────┐
│                    Scoring Breakdown (100 pts)              │
├───────────────────────────────────────────────────┬────────┤
│ 1. Hypothesis Formulation & Rigor                 │ 20 pts │
│ 2. Evidence Collection & Relevance                │ 25 pts │
│ 3. Pivot & Correlation Depth                      │ 20 pts │
│ 4. Finding Identification & ATT&CK Mapping        │ 20 pts │
│ 5. Conclusion, Rationale & Remediation            │ 15 pts │
└───────────────────────────────────────────────────┴────────┘
```

### Rubric Breakdown

#### 1. Hypothesis Formulation & Rigor (Max: 20 pts)
- **At least 1 hypothesis formulated**: 10 pts
- **Multiple hypotheses tested or status updated (Confirmed/Refuted)**: +5 pts
- **Clear test methodology and rationale documented**: +5 pts

#### 2. Evidence Collection & Relevance (Max: 25 pts)
- **Minimum 2 pieces of bound evidence**: 10 pts
- **5+ pieces of bound evidence**: +5 pts
- **Multiple evidence types used (Supporting + Contextual/Contradicting)**: +5 pts
- **High-quality analyst relevance notes attached**: +5 pts

#### 3. Pivot & Correlation Depth (Max: 20 pts)
- **Multiple unique queries executed**: 10 pts
- **Multi-field AST filtering used**: +5 pts
- **Pivoting across IPs and Domains explored**: +5 pts

#### 4. Finding Identification & ATT&CK Mapping (Max: 20 pts)
- **Formal findings synthesized**: 10 pts
- **MITRE ATT&CK technique IDs tagged (e.g. T1071.004)**: +5 pts
- **Severity properly assigned**: +5 pts

#### 5. Conclusion, Rationale & Remediation (Max: 15 pts)
- **Disposition selected (`MALICIOUS_CONFIRMED`, `BENIGN_FALSE_POSITIVE`, etc.)**: 5 pts
- **Detailed executive summary provided (> 50 characters)**: +5 pts
- **Actionable remediation guidance documented**: +5 pts

### Grading Scale
- **90 - 100**: Grade **A** (Exemplary Threat Hunter)
- **80 - 89**: Grade **B** (Proficient Analyst)
- **70 - 79**: Grade **C** (Developing Analyst)
- **60 - 69**: Grade **D** (Needs Remediation)
- **< 60**: Grade **F** (Incomplete Investigation)
