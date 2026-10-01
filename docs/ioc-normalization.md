# IOC Normalization, Canonicalization & Defanging

## 1. Why Normalization is Essential

In operational security analytics, indicators arrive from heterogeneous sources:
- Threat analyst blogs with defanged URLs (`hxxp://malicious[.]test/path`)
- Sensor logs with mixed casing or trailing dots (`C2-SERVER.test.`)
- Firewalls recording non-canonical IPv6 addresses (`2001:0db8:0000:0000:0000:ff00:0042:8329`)
- URL paths containing embedded credentials (`http://admin:secret@host.test/path`)

Without strict normalization:
- Database deduplication fails.
- Correlation engines miss connections between related events.
- Queries against threat databases produce false negatives.

NexoraNet maintains three distinct representations for every indicator:
1. **`value`**: The original raw string ingested from the analyst or sensor.
2. **`normalized_value`**: The canonical indexed string used for database lookups and correlation.
3. **`display_value`**: A clean, human-readable representation for analyst review.

---

## 2. Defanging Neutralization

Security researchers intentionally defang indicators to prevent accidental clicking or automatic hyperlinking. `NormalizationService` safely parses and neutralizes these patterns:

| Defanged Convention | Neutralized Form |
| :--- | :--- |
| `hxxp://` or `hxxps://` | `http://` or `https://` |
| `me[.]domain[.]test` | `me.domain.test` |
| `198[.]51[.]100[.]25` | `198.51.100.25` |
| `2001[:]db8[:]:::1` | `2001:db8::1` |
| `user[at]phishing[.]test` | `user@phishing.test` |
| `domain(dot)test` | `domain.test` |

---

## 3. Canonicalization Standards

### IP Addresses
- Validated via standard IPv4 / IPv6 parsers.
- Re-encoded into standard compressed form (e.g., IPv6 zero-compression `2001:db8::ff00:42:8329`).
- Invalid octets or non-numeric fragments are rejected with descriptive validation errors.

### Domain Names
- Converted to lowercase.
- Internationalized Domain Names (IDN) normalized to Punycode/ASCII.
- Trailing root zone dots (`.`) stripped.

### URLs
- Parsed into discrete URI components: `scheme`, `netloc`, `path`, `query`.
- Schemes normalized to lowercase.
- Embedded user credentials (`http://user:password@host/path`) are automatically redacted to prevent credential leakage.
- Default ports (80 for HTTP, 443 for HTTPS) preserved or normalized consistently.

### Cryptographic Hashes
- Length validation against known digest sizes:
  - **MD5**: 32 hex characters
  - **SHA-1**: 40 hex characters
  - **SHA-256**: 64 hex characters
  - **SHA-512**: 128 hex characters
- All hexadecimal characters converted to lowercase. Non-hex characters immediately rejected.

### Email Addresses
- Split into `user` and `domain` components.
- Domain component canonicalized according to domain normalization rules.
- Combined into lowercase `user@domain`.
