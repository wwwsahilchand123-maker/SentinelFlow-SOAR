# SentinelFlow SOAR Platform Architecture

SentinelFlow is engineered with an enterprise-grade, modular, decoupled architecture providing reliable orchestration, real-time threat intelligence correlation, auditable execution telemetry, and safe containment simulation.

---

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    subgraph Ingestion_Layer["1. Ingestion Layer"]
        A1["IDS / Suricata"] --> W["/api/webhooks"]
        A2["Firewalls / WAF"] --> W
        A3["Okta IdP / Auth"] --> W
        A4["CrowdStrike EDR"] --> W
        A5["Email Gateway"] --> W
        A6["SOC Analyst / Manual"] --> AL["/api/alerts"]
        A7["Attack Simulator"] --> SIM["/api/simulation"]
    end

    subgraph Processing_Layer["2. Correlation & Triage Engine"]
        W --> CORR["Correlation Engine<br/>(Deduplication & Sliding Window)"]
        AL --> CORR
        SIM --> CORR
        CORR --> TI["Threat Intelligence Layer<br/>(VirusTotal, AbuseIPDB, Cache)"]
        TI --> RS["Deterministic Risk Scoring<br/>(5-Factor Mathematical Model)"]
    end

    subgraph Automation_Layer["3. Automation & SOAR Playbook Engine"]
        RS --> AUTO["Automation Rules Evaluator"]
        AUTO --> PB["Playbook Engine<br/>(Versioned DAG Execution & Telemetry)"]
        PB --> APP["Human-in-the-Loop Approval<br/>(Risk Score >= 80 Threshold)"]
        PB --> SIM_RESP["Simulated Safe Sandbox<br/>(Firewall, EDR, IdP, Mailbox)"]
    end

    subgraph Management_Layer["4. Incident Management & Analytics"]
        PB --> INC["Incident Lifecycle & Timeline"]
        INC --> CASES["Multi-Incident Cases & SHA256 Evidence"]
        PB --> AUDIT["Append-Only Audit Log"]
        PB --> NOTIF["Notification Dispatcher"]
    end

    subgraph Presentation_Layer["5. Frontend Presentation (React 18 + TS)"]
        DASH["SOC Dashboard & Metrics"] <--> API["FastAPI REST Endpoints (JWT RBAC)"]
        API <--> DB[("PostgreSQL 15 / SQLite Pool")]
    end
```

---

## 2. End-to-End SOAR Execution Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor Attacker as Threat Actor / Simulator
    participant Ingest as Ingestion & Webhooks
    participant Corr as Correlation Engine
    participant Intel as Threat Intel Layer
    participant Risk as Risk Scoring Engine
    participant Auto as Automation Rules
    participant Playbook as Playbook Engine
    participant Approval as Human Approvals
    participant Sandbox as Response Sandbox
    participant SOC as Lead SOC Analyst
    participant Audit as Audit Service

    Attacker->>Ingest: Ingest Security Event / Attack
    Ingest->>Corr: Check SHA-256 Deduplication Hash
    Corr->>Corr: Aggregate Sliding Window Events
    Corr->>Intel: Query Indicators (IP / Hash / Domain)
    Intel-->>Corr: Reputation, Confidence & Tags
    Corr->>Risk: Compute 5-Factor Risk Score (0-100)
    Risk-->>Corr: Risk Score & Factor Breakdown
    Corr->>Auto: Evaluate Trigger Conditions
    Auto->>Playbook: Dispatch Enabled Playbook
    
    alt High Risk Action (Requires Approval)
        Playbook->>Approval: Pause & Create Approval Request
        Approval->>SOC: Dispatch Pending Approval Notification
        SOC->>Approval: Authorize Containment Action
        Approval->>Playbook: Resume Playbook Execution
    end

    Playbook->>Sandbox: Execute Response Action (Tagged [SIMULATED])
    Playbook->>Audit: Append Immutable Audit Record
    Playbook->>SOC: Push Real-Time In-App Alert
```

---

## 3. Database Schema & Relationships

- **Users (`users`)**: Accounts with RBAC roles (`ADMIN`, `SOC_ANALYST`, `VIEWER`).
- **Alerts (`alerts`)**: Raw normalized alerts with `dedup_hash`, severity, source IP, host, and MITRE IDs.
- **Incidents (`incidents`)**: Triaged security incidents with risk scores, assigned analysts, status, and MITRE matrix links.
- **Incident Events (`incident_events`)**: Chronological audit trail of investigation notes and automated containment actions.
- **Playbooks (`playbooks`)**: Orchestration workflows with status toggle and versions.
- **Playbook Steps (`playbook_steps`)**: Ordered actions with parameters, approval flags, and retry thresholds.
- **Playbook Executions (`playbook_executions`)**: Execution telemetry tracking `duration_ms`, step outputs, and failures.
- **Approval Requests (`approval_requests`)**: Human authorization records tracking decision notes and approving user.
- **Cases (`cases`)**: Multi-incident investigation containers.
- **Case Evidence (`case_evidence`)**: Digital forensics artifacts with calculated SHA-256 integrity hashes.
- **Threat Indicators (`indicators`)**: Known IOCs with reputation, confidence, and source attribution.
- **Assets (`assets`)**: Infrastructure assets with criticality scores and isolation status.
- **Audit Logs (`audit_logs`)**: Tamper-evident append-only operation log.

---

## 4. Security & Safety Principles

1. **Deterministic Risk Calculations**: No random numbers for risk assessment; formula strictly produces 0–100 based on quantifiable factors.
2. **Safe Response Simulation**: All containment operations (Firewall IP blocks, host isolation, mailbox purges) execute within a memory-backed simulation sandbox and are clearly marked `[SIMULATED]`.
3. **Pluggable Live Intel with Mock Fallback**: Live VirusTotal v3 and AbuseIPDB v2 integrations when configured with API keys; high-fidelity realistic simulated intelligence when unconfigured.
4. **Append-Only Auditing**: Every system action, login attempt, configuration change, and containment authorization is indelibly recorded.
