# SentinelFlow SOAR API Reference

Interactive Swagger documentation is available at `/docs` and ReDoc at `/redoc`.

All protected endpoints require the HTTP header:
`Authorization: Bearer <access_token>`

---

## 1. Authentication (`/api/auth`)
- `POST /api/auth/login` — Authenticate user and receive JWT access token.
- `GET /api/auth/me` — Retrieve current authenticated user profile and assigned role.
- `POST /api/auth/users` — *(Admin only)* Provision a new user account with role.

## 2. Security Alerts (`/api/alerts`)
- `GET /api/alerts` — Query and filter normalized alerts (by status, severity, query).
- `GET /api/alerts/{id}` — Fetch detailed alert metadata with indicator context.
- `POST /api/alerts` — Ingest a new security alert into the SOAR pipeline.
- `PATCH /api/alerts/{id}` — Update alert status or analyst assignment.

## 3. Webhook Ingestion (`/api/webhooks`)
- `POST /api/webhooks/ids` — Ingest Suricata / Snort IDS alerts.
- `POST /api/webhooks/firewall` — Ingest Next-Gen Firewall connection / drop alerts.
- `POST /api/webhooks/auth` — Ingest Okta / IdP authentication telemetry.
- `POST /api/webhooks/edr` — Ingest CrowdStrike / Defender EDR detections.
- `POST /api/webhooks/email` — Ingest Proofpoint / Email Gateway phishing alerts.
- `POST /api/webhooks/generic` — Generic JSON alert ingestion with deduplication.

## 4. Incidents & Timelines (`/api/incidents`)
- `GET /api/incidents` — List security incidents with risk scores and statuses.
- `GET /api/incidents/{id}` — Get single incident with correlated alerts and timeline events.
- `PATCH /api/incidents/{id}` — Update incident status (`Open`, `Investigating`, `Contained`, `Eradicated`, `Resolved`, `Closed`).
- `POST /api/incidents/{id}/events` — Append a timeline event or analyst note.
- `GET /api/incidents/{id}/events` — Fetch incident event timeline.

## 5. Playbook Orchestration (`/api/playbooks`)
- `GET /api/playbooks` — List all automated playbooks and versions.
- `GET /api/playbooks/{id}` — Retrieve playbook step definition and execution history.
- `POST /api/playbooks/{id}/execute` — Manually or automatically trigger playbook workflow.
- `GET /api/playbooks/executions` — List global playbook execution telemetry (`duration_ms`, logs).
- `GET /api/playbooks/executions/{exec_id}` — Get detailed step-by-step execution logs.
- `PATCH /api/playbooks/{id}/status` — Enable, disable, or draft a playbook.

## 6. Human Approvals (`/api/approvals`)
- `GET /api/approvals` — List pending and historical human-in-the-loop approval requests.
- `POST /api/approvals/{id}/decision` — *(Admin/Analyst)* Authorize (`Approved`) or deny (`Rejected`) sensitive containment action.

## 7. Attack Simulator (`/api/simulation`)
- `POST /api/simulation/brute-force` — Ingest SSH/RDP brute force attack.
- `POST /api/simulation/phishing` — Ingest spear-phishing campaign.
- `POST /api/simulation/malicious-ip` — Ingest C2 beaconing connection.
- `POST /api/simulation/malware` — Ingest ransomware payload hash.
- `POST /api/simulation/suspicious-login` — Ingest impossible travel login anomaly.
- `POST /api/simulation/data-exfiltration` — Ingest abnormal high-volume egress transfer.
- `POST /api/simulation/powershell-activity` — Ingest obfuscated PowerShell execution.
- `POST /api/simulation/malicious-domain` — Ingest DGA algorithmic domain query.

## 8. Threat Intelligence (`/api/indicators`)
- `GET /api/indicators` — List threat indicators (IPs, Hashes, Domains, Emails).
- `POST /api/indicators/lookup` — Perform real-time enrichment via live/mock providers.
- `POST /api/indicators` — Register a manual indicator with reputation and tags.

## 9. Asset Inventory (`/api/assets`)
- `GET /api/assets` — List organizational assets with criticality ratings.
- `POST /api/assets/{id}/isolate` — *(Analyst/Admin)* Isolate or restore network access.
- `POST /api/assets` — Register a new monitored endpoint or server.

## 10. Investigation Cases (`/api/cases`)
- `GET /api/cases` — List multi-incident investigation cases.
- `GET /api/cases/{id}` — Get case details and linked evidence items.
- `POST /api/cases` — Create a new investigation case.
- `PATCH /api/cases/{id}` — Update case priority or status.
- `POST /api/cases/{id}/evidence` — Attach forensic evidence with calculated SHA-256 hash.

## 11. Security Reports (`/api/reports`)
- `GET /api/reports/executive-summary` — CISO executive security posture summary.
- `GET /api/reports/export-incidents-csv` — Export all incidents to CSV format.

## 12. Universal Search (`/api/search`)
- `GET /api/search?q={query}` — Global search across Alerts, Incidents, Indicators, Assets, Cases, and Playbooks.

## 13. System Health (`/api/health`)
- `GET /api/health` — Subsystem health checks (Database, Threat Intel, Playbook Engine, Sandbox).
