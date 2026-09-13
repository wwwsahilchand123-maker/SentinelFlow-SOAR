# Security Policy & Safeguards

SentinelFlow is a defensive security engineering demonstration for controlled and authorized environments.

## Authentication & access control

- Passwords are stored using the project's configured password-hashing mechanism.
- JWTs must use a strong server-side secret and an appropriate expiration.
- Authorization is enforced through the documented RBAC model; do not rely on UI controls alone.

## Response safeguards

- Destructive response actions are simulated by default.
- High-risk automated actions should remain behind explicit human approval.
- Every response should be auditable and clearly distinguish simulation from live integration.

## Evidence integrity

- Treat uploaded evidence as untrusted input.
- Preserve integrity metadata for investigation artifacts.
- Do not commit real incident evidence, credentials, tokens, or personally identifying data.

## Reporting vulnerabilities

Do not publish sensitive exploit details or private data in a public issue. Report suspected vulnerabilities through an appropriate private channel and include the affected component, impact, safe reproduction context, and remediation guidance.
