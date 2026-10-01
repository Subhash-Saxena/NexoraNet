# NexoraNet — Student Portfolio & Educational Showcase

**“Learn. Simulate. Analyze. Defend.”**

## 1. Overview
The Student Portfolio allows students to document, showcase, and export their practical defensive accomplishments, hands-on lab investigations, and custom tools.

## 2. Privacy & Visibility Controls
Portfolios feature a 3-tier visibility model:
- **`PRIVATE` (Default):** Accessible only to the logged-in student. Public URL returns `404 Not Found`.
- **`UNLISTED`:** Accessible only via direct unique slug link. Not indexed by search engines.
- **`PUBLIC`:** Accessible to external viewers via public slug.

## 3. Security & Injection Protection
To prevent XSS, phishing, or malicious script execution:
- All external project links (repository URL, demo URL) are validated strictly against allowed schemes (`http://`, `https://`).
- Dangerous URI schemes (`javascript:`, `data:`, `vbscript:`, `file:`) are rejected with `HTTP 400 Bad Request`.
- Bio and project descriptions are HTML-sanitized before public rendering.

## 4. Zero Sensitive Data Leakage
Public portfolio views strictly exclude:
- Student email addresses
- Password hashes and authentication credentials
- Private internal instructor notes or administrative comments
- Student quiz answer keys, question codes, or CTF flags
