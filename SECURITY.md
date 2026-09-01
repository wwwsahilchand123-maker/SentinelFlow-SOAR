# Security Policy & Safeguards

## 1. Authentication & Session Management
- **Password Security**: Passwords hashed using bcrypt / PBKDF2 with salt.
- **JWT Authorization**: Signed JSON Web Tokens (`HS256`) with strict 24-hour expiration.
- **Header Injection**: Requests authenticated via standard HTTP `Authorization: Bearer <token>` headers.

## 2. Role-Based Access Control (RBAC) Matrix

| Resource / Endpoint | ADMIN | SOC_ANALYST | VIEWER |
|---------------------|:-----:|:-----------:|:------:|
| View Dashboards & Stats | Read | Read | Read |
| View Alerts & Incidents | Read | Read | Read |
| Triage & Update Incidents | Write | Write | Denied |
| Trigger Attack Simulation | Write | Write | Denied |
| Execute Playbooks | Write | Write | Denied |
| Approve / Reject Containment | Write | Write | Denied |
| Manage Automation Rules | Write | Write | Denied |
| Isolate / Restore Assets | Write | Write | Denied |
| User Provisioning & System Config | Write | Denied | Denied |
| View Append-Only Audit Logs | Read | Read | Read |

## 3. Containment Sandbox & Execution Safeguards
- **Simulated Response Actions**: All destructive actions (e.g. firewall blocking, EDR isolation, user revocation) are executed in a safe, memory-backed simulation environment. No live enterprise networks or machines are impacted.
- **UI & Telemetry Tagging**: Every simulated response action is stamped with `[SIMULATED]` badges across incident timelines, logs, and notification feeds.
- **Human-in-the-Loop Safeguard**: When an automated playbook evaluates an action with Risk Score $\ge 80$, it is halted in a `Waiting Approval` state until verified and authorized by a credentialed analyst.

## 4. Digital Forensics Evidence Integrity
- All evidence artifacts linked to investigation cases undergo cryptographic SHA-256 hash calculation upon ingestion.
- Integrity hashes are indexed and displayed in the analyst workspace for chain-of-custody verification.

## 5. Reporting Vulnerabilities
To report vulnerabilities or security issues regarding SentinelFlow, please file a security advisory or email `security@sentinelflow.io`.
