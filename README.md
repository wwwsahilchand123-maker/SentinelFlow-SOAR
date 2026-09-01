# SentinelFlow SOAR Platform

**Enterprise Security Orchestration, Automation & Response (SOAR) Platform**

SentinelFlow is a production-grade, full-stack SOAR platform designed for modern Security Operations Centers (SOC). Built with **FastAPI**, **React 18**, **TypeScript**, and **PostgreSQL**, it delivers enterprise-grade security event ingestion, alert correlation, threat intelligence enrichment, deterministic risk scoring, automated playbook orchestration with versioning and execution telemetry, human-in-the-loop approval workflows, and digital evidence integrity tracking.

---

## Key Enterprise Capabilities

### 1. Alert Ingestion & Correlation Engine
- **Normalized Ingestion**: Multi-source ingestion via REST and webhooks (IDS, Next-Gen Firewall, Okta IdP, CrowdStrike EDR, Email Gateway, Cloud DLP).
- **Deduplication**: SHA-256 fingerprinting on `source + alert_type + source_ip + host` to suppress redundant alerts within sliding 15-minute windows.
- **Sliding-Window Correlation**: Automatically correlates temporal events across IP addresses, subnets, and hostnames to prevent alert fatigue and auto-escalate correlated attack waves.

### 2. Threat Intelligence Layer (Live & Pluggable Sandbox)
- **Pluggable Architecture**: Adapters for **VirusTotal v3** and **AbuseIPDB v2** with in-memory TTL caching.
- **Realistic Fallback**: When API keys are unconfigured, uses realistic mock intelligence clearly tagged with `[SIMULATED DATA]` badges.
- **Reputation Scoring**: Deterministic confidence scoring and classification (`Malicious`, `Suspicious`, `Benign`, `Unknown`).

### 3. Deterministic 5-Factor Risk Scoring
- Mathematical risk score computed from 0 to 100 with auditable factor breakdowns:
  $$\text{Risk Score} = \min(100, \text{Severity} (35) + \text{Threat Intel} (35) + \text{Asset Criticality} (20) + \text{Behavior Velocity} (20) + \text{Incident History} (10))$$
- Predictable, non-random security decisions across all automated playbooks.

### 4. SOAR Playbook Engine & Execution Telemetry
- **Step-by-Step Execution**: Tracks `duration_ms`, inputs/outputs, retries, and errors per step.
- **Playbook Versioning**: Immutable version history for audit compliance.
- **Safe Response Sandbox**: Real simulated actions across perimeter firewall, EDR agents, IdP session revocation, and mailbox purges (`[SIMULATED]` tagged).
- **Human-in-the-Loop Approvals**: Automatically pauses high-risk containment actions (Risk Score $\ge 80$) until authorized by a SOC Analyst or Admin.

### 5. Investigation Cases & Evidence Integrity
- **Multi-Incident Case Grouping**: Link related alerts, incidents, and analysts into unified investigation cases.
- **SHA-256 Evidence Hashing**: Every attached artifact (PCAPs, RAM dumps, logs) is verified and hashed with cryptographic integrity checks.

### 6. Append-Only Audit Logging & Role-Based Access Control (RBAC)
- **Granular RBAC**: Three distinct roles (`ADMIN`, `SOC_ANALYST`, `VIEWER`) enforced across all API routes.
- **Append-Only Audit Trail**: Immutable logging of all analyst decisions, simulations, playbook triggers, and user logins.

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic |
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite, Lucide Icons, Recharts |
| **Database** | PostgreSQL 15 (Production) / SQLite (Dev Fallback with Connection Pooling) |
| **Security** | JWT Authentication (HS256), Password Hashing (Passlib / Bcrypt) |
| **Testing** | Pytest (27+ Unit, Integration & E2E Pipeline Tests) |
| **Containers** | Docker, Multi-Stage Dockerfile, Docker Compose with Healthchecks |

---

## Quick Start Guide

### Option 1: Docker Compose (Recommended for Full Stack with PostgreSQL)

```bash
# Clone the repository
git clone https://github.com/your-username/sentinelflow-soar.git
cd sentinelflow-soar

# Start PostgreSQL, Backend, and Frontend containers
docker-compose up --build
```

Access the services:
- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Backend API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### Option 2: Local Windows Development Setup

#### 1. Backend Setup
```powershell
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install requirements
pip install -r requirements.txt

# Seed the enterprise database with realistic sample data
python -m app.seed

# Start the FastAPI server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 2. Frontend Setup
```powershell
cd frontend

# Install node dependencies
npm install

# Run Vite development server
npm run dev
```

---

## Demo Credentials

| Role | Username | Password | Permissions |
|------|----------|----------|-------------|
| **SOC Administrator** | `admin` | `admin123` | Full access, user management, playbook edits, approval decisions |
| **Lead SOC Analyst** | `analyst` | `analyst123` | Alert triage, incident response, case investigation, approvals |
| **Security Auditor** | `viewer` | `viewer123` | Read-only access to dashboards, audit logs, and reports |

---

## Attack Simulation Scenarios

Test the end-to-end automated pipeline by triggering realistic attacks from the **Attack Simulation** tab or REST endpoints:

1. **SSH / RDP Brute Force** (`/api/simulation/brute-force`) — Generates 25 rapid failed login events $\rightarrow$ Correlates $\rightarrow$ Scores Risk $\rightarrow$ Triggers Brute Force Playbook $\rightarrow$ Simulates Firewall Block.
2. **Spear Phishing Campaign** (`/api/simulation/phishing`) — Ingests email alert with malicious URL $\rightarrow$ VirusTotal enrichment $\rightarrow$ Simulates mailbox quarantine.
3. **C2 Beaconing Connection** (`/api/simulation/malicious-ip`) — Triggers high-confidence C2 alert $\rightarrow$ Enforces perimeter IP drop rule.
4. **Ransomware Dropper** (`/api/simulation/malware`) — Detects malicious payload hash $\rightarrow$ Flags for Human Approval $\rightarrow$ Isolates infected endpoint upon approval.
5. **Impossible Travel Login** (`/api/simulation/suspicious-login`) — Detects UK to Ukraine concurrent login $\rightarrow$ Triggers IdP session revocation.
6. **Data Exfiltration** (`/api/simulation/data-exfiltration`) — Detects 8.5 GB unauthorized egress transfer $\rightarrow$ Flags high-risk containment approval.

---

## Running the Automated Test Suite

```bash
cd backend
python -m pytest -v
```

All 27 test cases test:
- Authentication & JWT token issuance
- RBAC authorization barriers
- Deterministic 5-factor risk scoring formula
- Threat intelligence caching & mock providers
- Full End-to-End SOAR pipeline (Alert $\rightarrow$ Correlation $\rightarrow$ Automation $\rightarrow$ Playbook $\rightarrow$ Approvals $\rightarrow$ Incidents $\rightarrow$ Notifications $\rightarrow$ Audit Log)

---

## MITRE ATT&CK Matrix Coverage

- **Initial Access**: `T1566` (Phishing)
- **Execution**: `T1059` (Command & Scripting Interpreter)
- **Credential Access**: `T1110` (Brute Force)
- **Defense Evasion**: `T1078` (Valid Accounts)
- **Command & Control**: `T1071` (Application Layer Protocol), `T1568` (Dynamic Resolution / DGA)
- **Exfiltration**: `T1048` (Exfiltration Over Alternative Protocol)
- **Impact**: `T1486` (Data Encrypted for Impact)

---

## License

Enterprise Portfolio Project under the MIT License.
