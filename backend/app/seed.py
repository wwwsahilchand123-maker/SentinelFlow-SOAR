from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import (
    User, RoleEnum,
    Alert, AlertStatus, AlertSeverity,
    Incident, IncidentEvent, IncidentStatus, IncidentSeverity,
    Indicator, IndicatorType, IndicatorReputation,
    Asset, AssetCriticality, AssetStatus, AssetType,
    Playbook, PlaybookStep, PlaybookExecution, ExecutionLog, PlaybookStatus, PlaybookVersion,
    AutomationRule,
    Case, CaseEvidence, CasePriority, CaseStatus,
    Notification, NotificationSeverity,
    AuditLog,
    MitreTechnique,
    ApprovalRequest, ApprovalStatus
)
from app.core.security import get_password_hash
from datetime import datetime, timedelta, timezone
import random
import hashlib

def seed_database():
    """Seed the database with comprehensive initial data for demonstration and testing"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("Clearing existing records...")
        db.query(AuditLog).delete()
        db.query(ApprovalRequest).delete()
        db.query(ExecutionLog).delete()
        db.query(PlaybookExecution).delete()
        db.query(PlaybookStep).delete()
        db.query(PlaybookVersion).delete()
        db.query(Playbook).delete()
        db.query(AutomationRule).delete()
        db.query(IncidentEvent).delete()
        db.query(Alert).delete()
        db.query(Incident).delete()
        db.query(Indicator).delete()
        db.query(Asset).delete()
        db.query(CaseEvidence).delete()
        db.query(Case).delete()
        db.query(Notification).delete()
        db.query(MitreTechnique).delete()
        db.query(User).delete()
        db.commit()
        
        print("Creating users...")
        admin = User(
            username="admin",
            email="admin@soar.local",
            full_name="SOC Administrator",
            hashed_password=get_password_hash("admin123"),
            role=RoleEnum.ADMIN,
            is_active=True
        )
        analyst = User(
            username="analyst",
            email="analyst@soar.local",
            full_name="Lead SOC Analyst",
            hashed_password=get_password_hash("analyst123"),
            role=RoleEnum.SOC_ANALYST,
            is_active=True
        )
        viewer = User(
            username="viewer",
            email="viewer@soar.local",
            full_name="Security Auditor",
            hashed_password=get_password_hash("viewer123"),
            role=RoleEnum.VIEWER,
            is_active=True
        )
        db.add_all([admin, analyst, viewer])
        db.commit()
        db.refresh(admin)
        db.refresh(analyst)
        db.refresh(viewer)
        
        print("Creating MITRE ATT&CK techniques...")
        techniques = [
            MitreTechnique(technique_id="T1110", technique_name="Brute Force", tactic="Credential Access", description="Adversaries may use brute force techniques to gain access to accounts."),
            MitreTechnique(technique_id="T1566", technique_name="Phishing", tactic="Initial Access", description="Adversaries may send phishing messages to gain initial access."),
            MitreTechnique(technique_id="T1059", technique_name="Command and Scripting Interpreter", tactic="Execution", description="Adversaries may abuse command and script interpreters to execute commands."),
            MitreTechnique(technique_id="T1486", technique_name="Data Encrypted for Impact", tactic="Impact", description="Adversaries may encrypt data on target systems to disrupt operations."),
            MitreTechnique(technique_id="T1071", technique_name="Application Layer Protocol", tactic="Command and Control", description="Adversaries may communicate using application layer protocols to avoid detection."),
            MitreTechnique(technique_id="T1048", technique_name="Exfiltration Over Alternative Protocol", tactic="Exfiltration", description="Adversaries may steal data by exfiltrating it over an alternative protocol."),
            MitreTechnique(technique_id="T1078", technique_name="Valid Accounts", tactic="Defense Evasion", description="Adversaries may obtain and abuse credentials of existing accounts."),
            MitreTechnique(technique_id="T1568", technique_name="Dynamic Resolution", tactic="Command and Control", description="Adversaries may dynamically establish connections to C2 servers using DGA.")
        ]
        db.add_all(techniques)
        db.commit()
        
        print("Creating enterprise assets...")
        assets = [
            Asset(asset_id="AST-001", hostname="DC-PRIMARY-01", ip_address="192.168.1.10", asset_type=AssetType.SERVER, operating_system="Windows Server 2022", owner="IT Infrastructure", criticality=AssetCriticality.CRITICAL, status=AssetStatus.ONLINE, tags="ActiveDirectory,DomainController"),
            Asset(asset_id="AST-002", hostname="WEB-PORTAL-01", ip_address="192.168.1.50", asset_type=AssetType.SERVER, operating_system="Ubuntu 22.04 LTS", owner="DevOps Team", criticality=AssetCriticality.HIGH, status=AssetStatus.ONLINE, tags="Production,Nginx"),
            Asset(asset_id="AST-003", hostname="DB-CLUSTER-MASTER", ip_address="192.168.1.100", asset_type=AssetType.DATABASE, operating_system="RHEL 9", owner="Database Engineering", criticality=AssetCriticality.CRITICAL, status=AssetStatus.ONLINE, tags="PostgreSQL,PCI-DSS"),
            Asset(asset_id="AST-004", hostname="WORKSTATION-042", ip_address="192.168.2.42", asset_type=AssetType.WORKSTATION, operating_system="Windows 11 Pro", owner="Finance (jsmith)", criticality=AssetCriticality.MEDIUM, status=AssetStatus.ONLINE, tags="Endpoint,Finance"),
            Asset(asset_id="AST-005", hostname="MAIL-GATEWAY-01", ip_address="192.168.1.25", asset_type=AssetType.SERVER, operating_system="Debian 12", owner="SecOps", criticality=AssetCriticality.HIGH, status=AssetStatus.ONLINE, tags="Email,Postfix"),
            Asset(asset_id="AST-006", hostname="PAYMENT-GATEWAY-API", ip_address="10.0.4.15", asset_type=AssetType.SERVER, operating_system="Alpine Linux", owner="Fintech SecOps", criticality=AssetCriticality.CRITICAL, status=AssetStatus.ONLINE, tags="Payment,PCI"),
            Asset(asset_id="AST-007", hostname="FIREWALL-EDGE-01", ip_address="192.168.1.1", asset_type=AssetType.FIREWALL, operating_system="Palo Alto PAN-OS", owner="NetOps", criticality=AssetCriticality.CRITICAL, status=AssetStatus.ONLINE, tags="Firewall,Perimeter"),
            Asset(asset_id="AST-008", hostname="DEV-WORKBENCH-09", ip_address="192.168.2.89", asset_type=AssetType.WORKSTATION, operating_system="macOS Sonoma", owner="Engineering", criticality=AssetCriticality.LOW, status=AssetStatus.ONLINE, tags="Development"),
            Asset(asset_id="AST-009", hostname="VPN-CONCENTRATOR-01", ip_address="192.168.1.5", asset_type=AssetType.ROUTER, operating_system="Cisco ASA", owner="NetOps", criticality=AssetCriticality.HIGH, status=AssetStatus.ONLINE, tags="VPN,RemoteAccess"),
            Asset(asset_id="AST-010", hostname="K8S-WORKER-NODE-03", ip_address="10.0.12.103", asset_type=AssetType.SERVER, operating_system="CoreOS", owner="Platform Eng", criticality=AssetCriticality.HIGH, status=AssetStatus.ONLINE, tags="Kubernetes,Production")
        ]
        db.add_all(assets)
        db.commit()
        
        print("Creating threat indicators...")
        indicators = [
            Indicator(value="185.220.101.45", indicator_type=IndicatorType.IPV4, reputation=IndicatorReputation.MALICIOUS, confidence=95.0, source="AbuseIPDB", tags="tor,scanner,bruteforce", is_simulation=True),
            Indicator(value="185.220.102.8", indicator_type=IndicatorType.IPV4, reputation=IndicatorReputation.MALICIOUS, confidence=92.0, source="Firewall Intelligence", tags="c2,malicious_ip", is_simulation=True),
            Indicator(value="malicious-domain.xyz", indicator_type=IndicatorType.DOMAIN, reputation=IndicatorReputation.MALICIOUS, confidence=88.0, source="URLHaus", tags="phishing,credential_harvester", is_simulation=True),
            Indicator(value="deadbeef1234567890abcdefdeadbeef1234567890abcdefdeadbeef12345678", indicator_type=IndicatorType.SHA256, reputation=IndicatorReputation.MALICIOUS, confidence=100.0, source="VirusTotal", tags="ransomware,trojan", is_simulation=True),
            Indicator(value="198.51.100.23", indicator_type=IndicatorType.IPV4, reputation=IndicatorReputation.SUSPICIOUS, confidence=68.0, source="CrowdStrike Feed", tags="scanner,reconnaissance", is_simulation=True),
            Indicator(value="198.51.100.99", indicator_type=IndicatorType.IPV4, reputation=IndicatorReputation.MALICIOUS, confidence=85.0, source="AlienVault OTX", tags="exfiltration,c2", is_simulation=True),
            Indicator(value="dga-botnet-update.net", indicator_type=IndicatorType.DOMAIN, reputation=IndicatorReputation.MALICIOUS, confidence=91.0, source="ThreatConnect", tags="dga,malware", is_simulation=True),
            Indicator(value="8.8.8.8", indicator_type=IndicatorType.IPV4, reputation=IndicatorReputation.BENIGN, confidence=10.0, source="Google DNS", tags="dns,trusted", is_simulation=False),
            Indicator(value="1.1.1.1", indicator_type=IndicatorType.IPV4, reputation=IndicatorReputation.BENIGN, confidence=5.0, source="Cloudflare DNS", tags="dns,trusted", is_simulation=False),
            Indicator(value="phishing-invoice-update.org", indicator_type=IndicatorType.DOMAIN, reputation=IndicatorReputation.MALICIOUS, confidence=84.0, source="Spamhaus", tags="phishing", is_simulation=True),
        ]
        db.add_all(indicators)
        db.commit()
        
        print("Creating automated playbooks with versions and steps...")
        # 1. Brute Force Playbook
        pb1 = Playbook(name="Brute Force Response Playbook", description="Automated triage, risk calculation, firewall IP blocking, and analyst dispatch for brute force attempts.", trigger_type="brute_force", status=PlaybookStatus.ENABLED, version="1.0.0")
        db.add(pb1)
        db.commit()
        db.refresh(pb1)
        
        pv1 = PlaybookVersion(playbook_id=pb1.id, version="1.0.0", definition={"steps": ["extract", "lookup", "risk", "incident", "block_ip", "notify"]})
        db.add(pv1)
        
        pb1_steps = [
            PlaybookStep(playbook_id=pb1.id, order=1, name="Extract IP Indicator", action="extract_indicator", parameters={}),
            PlaybookStep(playbook_id=pb1.id, order=2, name="Threat Intel Enrichment", action="threat_intelligence_lookup", parameters={}),
            PlaybookStep(playbook_id=pb1.id, order=3, name="Deterministic Risk Calculation", action="calculate_risk", parameters={}),
            PlaybookStep(playbook_id=pb1.id, order=4, name="Incident Escalation", action="create_incident", parameters={}),
            PlaybookStep(playbook_id=pb1.id, order=5, name="Perimeter Firewall Block", action="block_ip_simulation", parameters={"duration_minutes": 120}),
            PlaybookStep(playbook_id=pb1.id, order=6, name="SOC Analyst Notification", action="notify_analyst", parameters={}),
            PlaybookStep(playbook_id=pb1.id, order=7, name="Immutable Audit Logging", action="create_audit_log", parameters={}),
        ]
        db.add_all(pb1_steps)
        
        # 2. Malicious IP Quarantine
        pb2 = Playbook(name="Malicious IP Quarantine Playbook", description="Enriches C2 connection attempts and enforces immediate perimeter blocklist actions.", trigger_type="malicious_ip", status=PlaybookStatus.ENABLED, version="1.0.0")
        db.add(pb2)
        db.commit()
        db.refresh(pb2)
        
        pb2_steps = [
            PlaybookStep(playbook_id=pb2.id, order=1, name="Extract C2 Indicator", action="extract_indicator", parameters={}),
            PlaybookStep(playbook_id=pb2.id, order=2, name="Query AbuseIPDB & VT", action="threat_intelligence_lookup", parameters={}),
            PlaybookStep(playbook_id=pb2.id, order=3, name="Compute Threat Score", action="calculate_risk", parameters={}),
            PlaybookStep(playbook_id=pb2.id, order=4, name="Create Security Incident", action="create_incident", parameters={}),
            PlaybookStep(playbook_id=pb2.id, order=5, name="Block Traffic in Firewall", action="block_ip_simulation", parameters={}),
            PlaybookStep(playbook_id=pb2.id, order=6, name="Alert On-Call SOC", action="notify_analyst", parameters={}),
        ]
        db.add_all(pb2_steps)
        
        # 3. Phishing Containment
        pb3 = Playbook(name="Phishing Campaign Containment", description="Extracts domains/senders from phishing alerts and triggers simulated mailbox quarantine.", trigger_type="phishing", status=PlaybookStatus.ENABLED, version="1.0.0")
        db.add(pb3)
        db.commit()
        db.refresh(pb3)
        
        pb3_steps = [
            PlaybookStep(playbook_id=pb3.id, order=1, name="Extract URL & Domain", action="extract_indicator", parameters={}),
            PlaybookStep(playbook_id=pb3.id, order=2, name="URLhaus Reputation Check", action="threat_intelligence_lookup", parameters={}),
            PlaybookStep(playbook_id=pb3.id, order=3, name="Calculate Phishing Score", action="calculate_risk", parameters={}),
            PlaybookStep(playbook_id=pb3.id, order=4, name="Create Phishing Incident", action="create_incident", parameters={}),
            PlaybookStep(playbook_id=pb3.id, order=5, name="Purge Mailbox Messages", action="quarantine_email_simulation", parameters={}),
            PlaybookStep(playbook_id=pb3.id, order=6, name="Send Security Alert", action="notify_analyst", parameters={}),
        ]
        db.add_all(pb3_steps)
        
        # 4. Malware EDR Isolation
        pb4 = Playbook(name="Malware Detection & EDR Isolation", description="Triages infected hashes and isolates vulnerable endpoints from network access with approval safeguards.", trigger_type="malware", status=PlaybookStatus.ENABLED, version="1.0.0")
        db.add(pb4)
        db.commit()
        db.refresh(pb4)
        
        pb4_steps = [
            PlaybookStep(playbook_id=pb4.id, order=1, name="Extract Payload Hash", action="extract_indicator", parameters={}),
            PlaybookStep(playbook_id=pb4.id, order=2, name="VirusTotal Hash Lookup", action="threat_intelligence_lookup", parameters={}),
            PlaybookStep(playbook_id=pb4.id, order=3, name="Compute Malware Risk", action="calculate_risk", parameters={}),
            PlaybookStep(playbook_id=pb4.id, order=4, name="Create Critical Incident", action="create_incident", parameters={}),
            PlaybookStep(playbook_id=pb4.id, order=5, name="Isolate Host via EDR", action="isolate_endpoint_simulation", requires_approval=True, parameters={}),
            PlaybookStep(playbook_id=pb4.id, order=6, name="Dispatch Incident Commander", action="notify_analyst", parameters={}),
        ]
        db.add_all(pb4_steps)
        
        # 5. Impossible Travel Account Lock
        pb5 = Playbook(name="Impossible Travel & Identity Response", description="Detects impossible geographic velocity and triggers password reset + session revocation.", trigger_type="suspicious_login", status=PlaybookStatus.ENABLED, version="1.0.0")
        db.add(pb5)
        db.commit()
        db.refresh(pb5)
        
        pb5_steps = [
            PlaybookStep(playbook_id=pb5.id, order=1, name="Extract Identity & GeoIP", action="extract_indicator", parameters={}),
            PlaybookStep(playbook_id=pb5.id, order=2, name="Assess Velocity Anomaly", action="calculate_risk", parameters={}),
            PlaybookStep(playbook_id=pb5.id, order=3, name="Create Identity Incident", action="create_incident", parameters={}),
            PlaybookStep(playbook_id=pb5.id, order=4, name="Revoke Active IdP Tokens", action="revoke_user_sessions", parameters={}),
            PlaybookStep(playbook_id=pb5.id, order=5, name="Alert User & SecOps", action="notify_analyst", parameters={}),
        ]
        db.add_all(pb5_steps)
        
        # 6. Data Exfiltration Mitigation
        pb6 = Playbook(name="Data Exfiltration Auto-Block", description="Sever external egress transfer session and block recipient IP.", trigger_type="data_exfiltration", status=PlaybookStatus.ENABLED, version="1.0.0")
        db.add(pb6)
        db.commit()
        db.refresh(pb6)
        
        pb6_steps = [
            PlaybookStep(playbook_id=pb6.id, order=1, name="Extract Destination IP", action="extract_indicator", parameters={}),
            PlaybookStep(playbook_id=pb6.id, order=2, name="IP Threat Intel Lookup", action="threat_intelligence_lookup", parameters={}),
            PlaybookStep(playbook_id=pb6.id, order=3, name="Score Data Loss Severity", action="calculate_risk", parameters={}),
            PlaybookStep(playbook_id=pb6.id, order=4, name="Create DLP Incident", action="create_incident", parameters={}),
            PlaybookStep(playbook_id=pb6.id, order=5, name="Enforce Perimeter IP Drop", action="block_ip_simulation", requires_approval=True, parameters={}),
            PlaybookStep(playbook_id=pb6.id, order=6, name="Notify Compliance & SOC", action="notify_analyst", parameters={}),
        ]
        db.add_all(pb6_steps)
        db.commit()
        
        print("Creating automation rules...")
        rule1 = AutomationRule(
            name="Auto-respond to Brute Force Attacks",
            description="Executes Brute Force Response Playbook when repeated authentication failures occur",
            conditions={"all": [{"field": "alert_type", "operator": "equals", "value": "Brute Force Attack"}]},
            actions=[{"type": "trigger_playbook", "playbook_id": pb1.id}],
            enabled=True,
            priority=100
        )
        rule2 = AutomationRule(
            name="Auto-respond to Malicious IP Connections",
            description="Blocks outbound and inbound connections from high-reputation threat IPs",
            conditions={"all": [{"field": "alert_type", "operator": "equals", "value": "Malicious IP Connection"}]},
            actions=[{"type": "trigger_playbook", "playbook_id": pb2.id}],
            enabled=True,
            priority=90
        )
        rule3 = AutomationRule(
            name="Auto-quarantine Phishing Emails",
            description="Purges active spear-phishing messages targeting users",
            conditions={"all": [{"field": "alert_type", "operator": "equals", "value": "Phishing Email"}]},
            actions=[{"type": "trigger_playbook", "playbook_id": pb3.id}],
            enabled=True,
            priority=85
        )
        rule4 = AutomationRule(
            name="Auto-isolate Malware Infected Hosts",
            description="Executes endpoint containment upon detection of high-confidence malicious payload",
            conditions={"all": [{"field": "alert_type", "operator": "equals", "value": "Malware Detection"}]},
            actions=[{"type": "trigger_playbook", "playbook_id": pb4.id}],
            enabled=True,
            priority=95
        )
        rule5 = AutomationRule(
            name="Auto-lock Impossible Travel Accounts",
            description="Triggers identity containment upon impossible travel verification",
            conditions={"all": [{"field": "alert_type", "operator": "equals", "value": "Suspicious Login"}]},
            actions=[{"type": "trigger_playbook", "playbook_id": pb5.id}],
            enabled=True,
            priority=80
        )
        rule6 = AutomationRule(
            name="Auto-mitigate High Volume Data Exfiltration",
            description="Terminates data exfiltration sessions and blocks target IP",
            conditions={"all": [{"field": "alert_type", "operator": "equals", "value": "Data Exfiltration"}]},
            actions=[{"type": "trigger_playbook", "playbook_id": pb6.id}],
            enabled=True,
            priority=95
        )
        db.add_all([rule1, rule2, rule3, rule4, rule5, rule6])
        db.commit()
        
        print("Creating sample alerts...")
        now = datetime.now(timezone.utc)
        sample_alerts_def = [
            {"source": "CrowdStrike Falcon", "type": "Brute Force Attack", "cat": "Authentication", "sev": AlertSeverity.HIGH, "ip": "185.220.101.45", "user": "admin", "desc": "25 failed SSH login attempts in under 60 seconds", "mitre": "T1110"},
            {"source": "Palo Alto Firewall", "type": "Malicious IP Connection", "cat": "Network", "sev": AlertSeverity.CRITICAL, "ip": "185.220.102.8", "desc": "Inbound TCP connection attempt to database subnet", "mitre": "T1071"},
            {"source": "Proofpoint EOP", "type": "Phishing Email", "cat": "Email", "sev": AlertSeverity.HIGH, "ind": "malicious-domain.xyz", "desc": "Spear phishing email impersonating CEO payroll request", "mitre": "T1566"},
            {"source": "Microsoft Defender ATP", "type": "Malware Detection", "cat": "Endpoint", "sev": AlertSeverity.CRITICAL, "host": "WORKSTATION-042", "ind": "deadbeef1234567890abcdefdeadbeef1234567890abcdefdeadbeef12345678", "desc": "Trojan-Dropper.Win32 detected in %APPDATA%", "mitre": "T1204"},
            {"source": "Suricata IDS", "type": "Port Scan", "cat": "Network", "sev": AlertSeverity.MEDIUM, "ip": "198.51.100.23", "desc": "SYN Stealth Scan across ports 22, 80, 443, 8080", "mitre": "T1046"},
            {"source": "Auth0 Gateway", "type": "Suspicious Login", "cat": "Authentication", "sev": AlertSeverity.MEDIUM, "user": "jsmith", "desc": "Impossible travel detection between UK and Ukraine", "mitre": "T1078"},
            {"source": "Cloudflare WAF", "type": "SQL Injection Attempt", "cat": "Application", "sev": AlertSeverity.HIGH, "ip": "203.0.113.50", "desc": "UNION SELECT pattern injected into search parameters", "mitre": "T1190"},
            {"source": "Varonis DLP", "type": "Data Exfiltration", "cat": "Data Loss", "sev": AlertSeverity.CRITICAL, "user": "jdoe", "ip": "198.51.100.99", "desc": "8.5 GB transfer to unsanctioned Dropbox storage", "mitre": "T1048"},
            {"source": "DNS Armor", "type": "DGA Domain Lookup", "cat": "DNS", "sev": AlertSeverity.HIGH, "ind": "dga-botnet-update.net", "desc": "Suspicious algorithmic domain query burst", "mitre": "T1568"},
            {"source": "Okta Identity Cloud", "type": "MFA Fatigue Attack", "cat": "Authentication", "sev": AlertSeverity.HIGH, "user": "finance_exec", "desc": "12 repeated MFA push notification denials", "mitre": "T1621"}
        ]
        
        for i, item in enumerate(sample_alerts_def):
            for day in range(4):
                ts = now - timedelta(days=day, hours=random.randint(1, 20), minutes=random.randint(5, 50))
                alert = Alert(
                    alert_id=f"ALT-{10000 + i * 10 + day}",
                    timestamp=ts,
                    source=item["source"],
                    alert_type=item["type"],
                    category=item.get("cat", "General"),
                    severity=item["sev"],
                    source_ip=item.get("ip"),
                    username=item.get("user"),
                    host=item.get("host"),
                    indicator=item.get("ind"),
                    mitre_technique_id=item.get("mitre"),
                    description=item["desc"],
                    status=random.choice([AlertStatus.NEW, AlertStatus.INVESTIGATING, AlertStatus.RESOLVED])
                )
                db.add(alert)
        db.commit()
        
        print("Creating sample incidents...")
        inc1 = Incident(
            incident_id="INC-2026-001",
            title="Active Brute Force Campaign from Tor Exit 185.220.101.45",
            description="Repeated credential stuffing attempts against administrative portals.",
            severity=IncidentSeverity.HIGH,
            risk_score=85.0,
            status=IncidentStatus.INVESTIGATING,
            source="Automated SOAR Engine",
            mitre_technique_id="T1110",
            assigned_analyst_id=analyst.id
        )
        inc2 = Incident(
            incident_id="INC-2026-002",
            title="Finance Department Targeted Phishing Campaign",
            description="Spear phishing email lure containing deceptive link to credential harvesting portal.",
            severity=IncidentSeverity.MEDIUM,
            risk_score=68.0,
            status=IncidentStatus.CONTAINED,
            source="Email Security Pipeline",
            mitre_technique_id="T1566",
            assigned_analyst_id=analyst.id
        )
        inc3 = Incident(
            incident_id="INC-2026-003",
            title="Trojan Payload on WORKSTATION-042",
            description="Ransomware dropper binary detected; endpoint quarantined automatically.",
            severity=IncidentSeverity.CRITICAL,
            risk_score=94.0,
            status=IncidentStatus.ERADICATED,
            source="EDR Alert Automation",
            mitre_technique_id="T1204",
            assigned_analyst_id=admin.id
        )
        inc4 = Incident(
            incident_id="INC-2026-004",
            title="C2 Beaconing from DB-CLUSTER-MASTER Subnet",
            description="Persistent outbound beaconing over HTTPS to IP 185.220.102.8.",
            severity=IncidentSeverity.CRITICAL,
            risk_score=91.0,
            status=IncidentStatus.CONTAINED,
            source="Perimeter Firewall",
            mitre_technique_id="T1071",
            assigned_analyst_id=analyst.id
        )
        inc5 = Incident(
            incident_id="INC-2026-005",
            title="Mass Data Exfiltration Spike",
            description="8.5 GB encrypted data upload to unsanctioned external cloud endpoint.",
            severity=IncidentSeverity.HIGH,
            risk_score=88.0,
            status=IncidentStatus.OPEN,
            source="Cloud DLP",
            mitre_technique_id="T1048",
            assigned_analyst_id=None
        )
        db.add_all([inc1, inc2, inc3, inc4, inc5])
        db.commit()
        db.refresh(inc1)
        db.refresh(inc2)
        db.refresh(inc3)
        db.refresh(inc4)
        db.refresh(inc5)
        
        # Add timeline events
        events = [
            IncidentEvent(incident_id=inc1.id, event_type="Incident Ingested", description="Alert ALT-10000 correlated and escalated to High Severity Incident.", created_by_id=analyst.id),
            IncidentEvent(incident_id=inc1.id, event_type="Automated Action", description="[SIMULATED] IP 185.220.101.45 blocked in perimeter firewall ACLs for 120 minutes.", created_by_id=None),
            IncidentEvent(incident_id=inc1.id, event_type="Analyst Note", description="Verified no successful authentications occurred. Monitoring ingress logs.", created_by_id=analyst.id),
            IncidentEvent(incident_id=inc2.id, event_type="Incident Ingested", description="Phishing campaign detected across 14 recipient inboxes.", created_by_id=analyst.id),
            IncidentEvent(incident_id=inc2.id, event_type="Containment Action", description="[SIMULATED] Email messages and domain malicious-domain.xyz purged from gateway.", created_by_id=analyst.id),
            IncidentEvent(incident_id=inc3.id, event_type="Containment Action", description="[SIMULATED] WORKSTATION-042 isolated from corporate network via EDR agent.", created_by_id=admin.id),
            IncidentEvent(incident_id=inc3.id, event_type="Eradication", description="Malicious binary deleted and persistence registry keys scrubbed.", created_by_id=admin.id),
            IncidentEvent(incident_id=inc4.id, event_type="Automated Action", description="[SIMULATED] IP 185.220.102.8 added to perimeter firewall drop rules.", created_by_id=None),
        ]
        db.add_all(events)
        
        print("Creating investigation cases...")
        case1 = Case(
            case_id="CASE-2026-001",
            title="Q3 Targeted Ransomware & Intrusion Campaign Investigation",
            description="Unified case tracking multi-vector intrusion attempting lateral movement and ransomware staging.",
            priority=CasePriority.CRITICAL,
            status=CaseStatus.INVESTIGATING,
            assigned_analyst_id=analyst.id
        )
        case2 = Case(
            case_id="CASE-2026-002",
            title="Executive Credential Harvest & Phishing Wave",
            description="Broad credential phishing campaign aimed at C-Suite and Finance personnel.",
            priority=CasePriority.HIGH,
            status=CaseStatus.OPEN,
            assigned_analyst_id=analyst.id
        )
        db.add_all([case1, case2])
        db.commit()
        db.refresh(case1)
        db.refresh(case2)
        
        sample_hash1 = hashlib.sha256(b"memory_dump_workstation042_artifact").hexdigest()
        sample_hash2 = hashlib.sha256(b"pcap_c2_session_capture").hexdigest()
        
        evidence1 = CaseEvidence(case_id=case1.id, filename="workstation042_ram.raw", file_type="Memory Dump", file_size_bytes=4194304, sha256_hash=sample_hash1, description="Volatile RAM dump from WORKSTATION-042 containing injected DLL payload", uploaded_by_id=analyst.id)
        evidence2 = CaseEvidence(case_id=case1.id, filename="c2_stream.pcap", file_type="PCAP Capture", file_size_bytes=131072, sha256_hash=sample_hash2, description="Full packet capture of C2 beacon handshake with 185.220.102.8", uploaded_by_id=analyst.id)
        db.add_all([evidence1, evidence2])
        
        print("Creating sample approval requests...")
        app_req1 = ApprovalRequest(
            request_id="APP-001",
            action_type="ISOLATE_HOST",
            target="WORKSTATION-042",
            risk_score=94.0,
            reason="High-confidence ransomware signature detected. Requires host isolation.",
            status=ApprovalStatus.APPROVED,
            playbook_id=pb4.id,
            requested_by_id=analyst.id,
            approved_by_id=admin.id,
            decision_notes="Approved immediate containment of finance workstation."
        )
        app_req2 = ApprovalRequest(
            request_id="APP-002",
            action_type="BLOCK_IP",
            target="198.51.100.99",
            risk_score=88.0,
            reason="High-volume data exfiltration target IP. Requires firewall block.",
            status=ApprovalStatus.PENDING,
            playbook_id=pb6.id,
            requested_by_id=analyst.id
        )
        db.add_all([app_req1, app_req2])
        
        print("Creating audit logs...")
        sample_audit_actions = [
            ("USER_LOGIN", "auth", "admin", "Success"),
            ("ALERT_CREATED", "alert", "ALT-10001", "Success"),
            ("PLAYBOOK_EXECUTED", "playbook", "1", "Success"),
            ("INCIDENT_CREATED", "incident", "INC-2026-001", "Success"),
            ("INCIDENT_UPDATED", "incident", "INC-2026-001", "Success"),
            ("ASSET_QUARANTINED", "asset", "WORKSTATION-042", "Success"),
            ("APPROVAL_GRANTED", "approval", "APP-001", "Success")
        ]
        for action, resource, res_id, result in sample_audit_actions:
            db.add(AuditLog(
                user_id=analyst.id,
                action=action,
                resource=resource,
                resource_id=res_id,
                result=result,
                ip_address="192.168.1.15"
            ))
            
        print("Creating initial notifications...")
        db.add(Notification(
            user_id=admin.id,
            title="Critical Incident Detected",
            message="Trojan payload detected on WORKSTATION-042 (Risk Score: 94/100)",
            severity=NotificationSeverity.CRITICAL,
            link=f"/incidents/{inc3.id}"
        ))
        db.add(Notification(
            user_id=analyst.id,
            title="High Severity Alert Escalation",
            message="Brute force campaign automatically blocked and escalated.",
            severity=NotificationSeverity.HIGH,
            link=f"/incidents/{inc1.id}"
        ))
        db.add(Notification(
            user_id=analyst.id,
            title="Pending Human Approval Required",
            message="Playbook execution waiting for approval to block 198.51.100.99.",
            severity=NotificationSeverity.MEDIUM,
            link="/approvals"
        ))
        
        db.commit()
        print("Database seeded successfully with enterprise SOAR data!")
        print("Demo credentials:")
        print(" - Admin: admin / admin123")
        print(" - SOC Analyst: analyst / analyst123")
        print(" - Viewer: viewer / viewer123")
    except Exception as e:
        db.rollback()
        print(f"Error during seeding: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
