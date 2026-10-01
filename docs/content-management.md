# NexoraNet — Curriculum & Content Lifecycle Management

**“Learn. Simulate. Analyze. Defend.”**

## 1. Content State Machine
All instructional and practical assets (Courses, Modules, Topics, Lessons, Labs, Questions, Scenarios, Challenges) traverse a state lifecycle:

$$\text{DRAFT} \longleftrightarrow \text{REVIEW} \longrightarrow \text{PUBLISHED} \longrightarrow \text{ARCHIVED}$$

## 2. Validation Rules Before Publishing
To maintain curriculum integrity, assets cannot be transitioned to `PUBLISHED` if validation fails:
- **Modules:** Must contain at least one valid topic.
- **Topics:** Must contain at least one published lesson.
- **Lessons:** Must have title, slug, and non-empty instructional markdown content.
- **Labs:** Must contain at least one structured verification step.
- **Questions:** Must contain at least 2 distinct option answers with exactly 1 designated correct option.
- **Challenges:** Must feature a title, valid category, synthetic scenario, and synthetic flag.

## 3. Version History
Modifications to content create immutable snapshot records in `content_versions` tracking:
- Version sequence integer
- Full JSON content snapshot
- Editor user reference
- Change summary
