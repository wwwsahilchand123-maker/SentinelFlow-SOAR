export type RoleEnum = 'ADMIN' | 'SOC_ANALYST' | 'VIEWER';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: RoleEnum;
  is_active: boolean;
  created_at?: string;
}

export type AlertSeverity = 'Critical' | 'High' | 'Medium' | 'Low' | 'Informational';
export type AlertStatus = 'New' | 'Investigating' | 'Escalated' | 'Resolved' | 'False Positive';

export interface Alert {
  id: number;
  alert_id: string;
  timestamp: string;
  source: string;
  alert_type: string;
  category?: string;
  severity: AlertSeverity;
  source_ip?: string;
  destination_ip?: string;
  username?: string;
  host?: string;
  indicator?: string;
  mitre_technique_id?: string;
  description?: string;
  status: AlertStatus;
  assigned_analyst_id?: number;
  incident_id?: number;
  created_at?: string;
  updated_at?: string;
}

export type IncidentSeverity = 'Critical' | 'High' | 'Medium' | 'Low';
export type IncidentStatus = 'Open' | 'Investigating' | 'Contained' | 'Eradicated' | 'Resolved' | 'Closed';

export interface IncidentEvent {
  id: number;
  incident_id: number;
  timestamp: string;
  event_type: string;
  description: string;
  created_by_id?: number;
  details?: string;
}

export interface Incident {
  id: number;
  incident_id: string;
  title: string;
  description?: string;
  severity: IncidentSeverity;
  risk_score: number;
  status: IncidentStatus;
  assigned_analyst_id?: number;
  source?: string;
  mitre_technique_id?: string;
  mitre_tactic?: string;
  created_at?: string;
  updated_at?: string;
  events?: IncidentEvent[];
}

export type PlaybookStatus = 'Enabled' | 'Disabled' | 'Draft';
export type ExecutionStatus = 'Pending' | 'Running' | 'Completed' | 'Failed' | 'Partially Completed' | 'Cancelled' | 'Waiting Approval';

export interface PlaybookStep {
  id: number;
  order: number;
  name: string;
  action: string;
  requires_approval?: boolean;
  retry_count?: number;
  parameters?: Record<string, any>;
}

export interface Playbook {
  id: number;
  name: string;
  description?: string;
  trigger?: string;
  trigger_type?: string;
  version?: string;
  status: PlaybookStatus;
  created_at?: string;
  updated_at?: string;
  steps: PlaybookStep[];
}

export interface ExecutionLog {
  id: number;
  timestamp: string;
  step_name: string;
  status: string;
  message?: string;
  duration_ms?: number;
  metadata_info?: Record<string, any>;
}

export interface PlaybookExecution {
  id: number;
  execution_id: string;
  playbook_id: number;
  playbook_version?: string;
  status: ExecutionStatus;
  trigger_source?: string;
  started_at: string;
  completed_at?: string;
  duration_ms?: number;
  logs: ExecutionLog[];
}

export type IndicatorType = 'ipv4' | 'ipv6' | 'domain' | 'url' | 'sha256' | 'md5' | 'sha1' | 'email';
export type IndicatorReputation = 'Malicious' | 'Suspicious' | 'Benign' | 'Unknown';

export interface Indicator {
  id: number;
  value: string;
  indicator_type: IndicatorType;
  reputation: IndicatorReputation;
  confidence: number;
  first_seen?: string;
  last_seen?: string;
  source?: string;
  tags?: string;
  is_simulation?: boolean;
  raw_data?: Record<string, any>;
}

export type AssetCriticality = 'Critical' | 'High' | 'Medium' | 'Low';
export type AssetStatus = 'Online' | 'Offline' | 'Quarantined' | 'Isolated' | 'Maintenance';
export type AssetType = 'Server' | 'Workstation' | 'Firewall' | 'Router' | 'Database' | 'Cloud Resource';

export interface Asset {
  id: number;
  asset_id: string;
  hostname: string;
  asset_type?: AssetType;
  ip_address?: string;
  operating_system?: string;
  owner?: string;
  criticality: AssetCriticality;
  status: AssetStatus;
  last_seen?: string;
  tags?: string;
}

export interface AutomationRule {
  id: number;
  name: string;
  description?: string;
  conditions: Record<string, any>;
  actions: Array<Record<string, any>>;
  enabled: boolean;
  priority: number;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  user_id?: number;
  action: string;
  resource: string;
  resource_id?: string;
  result: string;
  ip_address?: string;
  metadata_info?: Record<string, any>;
}

export interface NotificationItem {
  id: number;
  title: string;
  message: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low' | 'Info';
  is_read: boolean;
  link?: string;
  created_at?: string;
}

export interface DashboardStats {
  total_alerts: number;
  critical_alerts: number;
  open_incidents: number;
  resolved_incidents: number;
  mean_time_to_respond: number;
  mean_time_to_resolve: number;
  automated_actions: number;
  blocked_indicators: number;
  playbook_executions: number;
  high_risk_assets: number;
}

export interface CaseEvidence {
  id: number;
  case_id: number;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  sha256_hash: string;
  description?: string;
  uploaded_by_id?: number;
  created_at?: string;
}

export interface CaseNote {
  id: number;
  case_id: number;
  author_id?: number;
  content: string;
  created_at?: string;
}

export interface Case {
  id: number;
  case_id: string;
  title: string;
  description?: string;
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  status: 'Open' | 'Investigating' | 'Pending' | 'Resolved' | 'Closed';
  assigned_analyst_id?: number;
  created_at?: string;
  updated_at?: string;
  evidence?: CaseEvidence[];
  notes?: CaseNote[];
}

export interface ApprovalRequest {
  id: number;
  request_id: string;
  action_type: string;
  target: string;
  risk_score: number;
  reason?: string;
  status: 'Pending' | 'Approved' | 'Rejected' | 'Expired';
  playbook_id?: number;
  execution_id?: number;
  incident_id?: number;
  requested_by_id?: number;
  approved_by_id?: number;
  decision_notes?: string;
  created_at?: string;
  decided_at?: string;
}
