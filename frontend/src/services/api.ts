import axios from 'axios';
import {
  User,
  Alert,
  Incident,
  IncidentEvent,
  Playbook,
  PlaybookExecution,
  Indicator,
  Asset,
  AutomationRule,
  AuditLog,
  NotificationItem,
  DashboardStats,
  Case,
  CaseEvidence,
  ApprovalRequest
} from '../types';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to inject JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('soar_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && !window.location.pathname.includes('/login')) {
      localStorage.removeItem('soar_token');
      localStorage.removeItem('soar_user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth Service
export const authService = {
  login: async (credentials: { username: string; password: string }) => {
    const res = await api.post<{ access_token: string; token_type: string; user: User }>('/auth/login', credentials);
    return res.data;
  },
  getCurrentUser: async () => {
    const res = await api.get<User>('/auth/me');
    return res.data;
  },
};

// Dashboard Service
export const dashboardService = {
  getStats: async () => {
    const res = await api.get<DashboardStats>('/dashboard/stats');
    return res.data;
  },
  getAlertsOverTime: async (days: number = 7) => {
    const res = await api.get<Array<{ date: string; count: number }>>(`/dashboard/alerts-over-time?days=${days}`);
    return res.data;
  },
  getIncidentsBySeverity: async () => {
    const res = await api.get<Array<{ severity: string; count: number }>>('/dashboard/incidents-by-severity');
    return res.data;
  },
  getAlertSources: async () => {
    const res = await api.get<Array<{ source: string; count: number }>>('/dashboard/alert-sources');
    return res.data;
  },
  getIncidentStatusDist: async () => {
    const res = await api.get<Array<{ status: string; count: number }>>('/dashboard/incident-status-distribution');
    return res.data;
  },
  getRecentActivity: async (limit: number = 15) => {
    const res = await api.get<Array<any>>(`/dashboard/recent-activity?limit=${limit}`);
    return res.data;
  },
};

// Alerts Service
export const alertService = {
  getAlerts: async (params?: { status?: string; severity?: string; search?: string }) => {
    const res = await api.get<Alert[]>('/alerts', { params });
    return res.data;
  },
  getAlert: async (id: number) => {
    const res = await api.get<Alert>(`/alerts/${id}`);
    return res.data;
  },
  updateAlert: async (id: number, data: Partial<Alert>) => {
    const res = await api.patch<Alert>(`/alerts/${id}`, data);
    return res.data;
  },
  createAlert: async (data: Partial<Alert>) => {
    const res = await api.post<Alert>('/alerts', data);
    return res.data;
  },
};

// Incidents Service
export const incidentService = {
  getIncidents: async (params?: { status?: string; severity?: string }) => {
    const res = await api.get<Incident[]>('/incidents', { params });
    return res.data;
  },
  getIncident: async (id: number) => {
    const res = await api.get<Incident>(`/incidents/${id}`);
    return res.data;
  },
  updateIncident: async (id: number, data: Partial<Incident>) => {
    const res = await api.patch<Incident>(`/incidents/${id}`, data);
    return res.data;
  },
  addEvent: async (incidentId: number, event: { event_type: string; description: string }) => {
    const res = await api.post<IncidentEvent>(`/incidents/${incidentId}/events`, {
      ...event,
      incident_id: incidentId
    });
    return res.data;
  },
  getEvents: async (incidentId: number) => {
    const res = await api.get<IncidentEvent[]>(`/incidents/${incidentId}/events`);
    return res.data;
  },
};

// Playbooks Service
export const playbookService = {
  getPlaybooks: async () => {
    const res = await api.get<Playbook[]>('/playbooks');
    return res.data;
  },
  getPlaybook: async (id: number) => {
    const res = await api.get<Playbook>(`/playbooks/${id}`);
    return res.data;
  },
  executePlaybook: async (id: number, triggerData: Record<string, any>) => {
    const res = await api.post<PlaybookExecution>(`/playbooks/${id}/execute`, triggerData);
    return res.data;
  },
  getAllExecutions: async () => {
    const res = await api.get<PlaybookExecution[]>('/playbooks/executions');
    return res.data;
  },
  getPlaybookExecutions: async (playbookId: number) => {
    const res = await api.get<PlaybookExecution[]>(`/playbooks/${playbookId}/executions`);
    return res.data;
  },
  getExecution: async (execId: string) => {
    const res = await api.get<PlaybookExecution>(`/playbooks/executions/${execId}`);
    return res.data;
  },
  toggleStatus: async (id: number, status: string) => {
    const res = await api.patch(`/playbooks/${id}/status?status=${status}`);
    return res.data;
  },
};

// Human Approvals Service
export const approvalService = {
  getApprovals: async (status?: string) => {
    const res = await api.get<ApprovalRequest[]>('/approvals', { params: { status } });
    return res.data;
  },
  processDecision: async (id: number, decision: 'Approved' | 'Rejected', notes?: string) => {
    const res = await api.post<ApprovalRequest>(`/approvals/${id}/decision`, { decision, notes });
    return res.data;
  },
};

// Simulation Service
export const simulationService = {
  triggerScenario: async (scenario: string) => {
    const res = await api.post(`/simulation/${scenario}`);
    return res.data;
  },
};

// Threat Intel Service
export const threatIntelService = {
  getIndicators: async (params?: { type?: string; reputation?: string }) => {
    const res = await api.get<Indicator[]>('/indicators', { params });
    return res.data;
  },
  lookup: async (value: string) => {
    const res = await api.post('/indicators/lookup', null, { params: { value } });
    return res.data;
  },
  createIndicator: async (data: Partial<Indicator>) => {
    const res = await api.post<Indicator>('/indicators', data);
    return res.data;
  },
};

// Assets Service
export const assetService = {
  getAssets: async (params?: { status?: string; criticality?: string }) => {
    const res = await api.get<Asset[]>('/assets', { params });
    return res.data;
  },
  toggleIsolate: async (id: number, isolate: boolean) => {
    const res = await api.post<Asset>(`/assets/${id}/isolate?isolate=${isolate}`);
    return res.data;
  },
  createAsset: async (data: Partial<Asset>) => {
    const res = await api.post<Asset>('/assets', data);
    return res.data;
  }
};

// Cases & Evidence Service
export const caseService = {
  getCases: async (params?: { status?: string; priority?: string }) => {
    const res = await api.get<Case[]>('/cases', { params });
    return res.data;
  },
  getCase: async (id: number) => {
    const res = await api.get<Case>(`/cases/${id}`);
    return res.data;
  },
  createCase: async (data: Partial<Case>) => {
    const res = await api.post<Case>('/cases', data);
    return res.data;
  },
  updateCase: async (id: number, data: Partial<Case>) => {
    const res = await api.patch<Case>(`/cases/${id}`, data);
    return res.data;
  },
  addEvidence: async (caseId: number, evidence: Partial<CaseEvidence>) => {
    const res = await api.post<CaseEvidence>(`/cases/${caseId}/evidence`, evidence);
    return res.data;
  },
};

// Automation Rules Service
export const automationService = {
  getRules: async () => {
    const res = await api.get<AutomationRule[]>('/automation/rules');
    return res.data;
  },
  createRule: async (data: Partial<AutomationRule>) => {
    const res = await api.post<AutomationRule>('/automation/rules', data);
    return res.data;
  },
  updateRule: async (id: number, data: Partial<AutomationRule>) => {
    const res = await api.patch<AutomationRule>(`/automation/rules/${id}`, data);
    return res.data;
  },
  deleteRule: async (id: number) => {
    const res = await api.delete(`/automation/rules/${id}`);
    return res.data;
  },
};

// Audit Log Service
export const auditService = {
  getLogs: async (params?: { action?: string }) => {
    const res = await api.get<AuditLog[]>('/audit', { params });
    return res.data;
  },
};

// Notification Service
export const notificationService = {
  getNotifications: async () => {
    const res = await api.get<NotificationItem[]>('/notifications');
    return res.data;
  },
  markRead: async (id: number) => {
    const res = await api.post(`/notifications/${id}/read`);
    return res.data;
  },
  markAllRead: async () => {
    const res = await api.post('/notifications/read-all');
    return res.data;
  },
};

// Health Service
export const healthService = {
  getHealth: async () => {
    const res = await api.get('/health');
    return res.data;
  },
};

// Global Search Service
export const searchService = {
  search: async (q: string) => {
    const res = await api.get('/search', { params: { q } });
    return res.data;
  },
};

// Reports Service
export const reportService = {
  getExecutiveSummary: async (days: number = 30) => {
    const res = await api.get('/reports/executive-summary', { params: { days } });
    return res.data;
  },
  exportCsvUrl: `${API_BASE}/reports/export-incidents-csv`,
};
