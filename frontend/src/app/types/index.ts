export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';
export type IncidentStatus = 'active' | 'investigating' | 'recovering' | 'resolved' | 'escalated';
export type WorkflowStatus = 'healthy' | 'degraded' | 'failing' | 'offline';
export type VendorStatus = 'operational' | 'degraded' | 'outage' | 'maintenance';
export type RecoveryAction = 'retry' | 'rollback' | 'escalate' | 'manual-intervention' | 'failover';

export interface Incident {
  id: string;
  title: string;
  severity: SeverityLevel;
  status: IncidentStatus;
  workflowsAffected: string[];
  detectedAt: string;
  lastUpdated: string;
  impactedUsers?: number;
  impactedTransactions?: number;
  description: string;
  aiHypotheses: AIHypothesis[];
  timeline: TimelineEvent[];
  recoveryActions?: RecoveryActionItem[];
}

export interface AIHypothesis {
  id: string;
  hypothesis: string;
  confidence: number; // 0-100
  evidence: string[];
  suggestedAction?: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  event: string;
  type: 'detection' | 'analysis' | 'action' | 'update' | 'resolution';
  actor?: string;
}

export interface RecoveryActionItem {
  id: string;
  action: RecoveryAction;
  description: string;
  risk: 'low' | 'medium' | 'high';
  requiresApproval: boolean;
  estimatedImpact?: string;
}

export interface Workflow {
  id: string;
  name: string;
  status: WorkflowStatus;
  category: string;
  lastRun: string;
  successRate: number; // 0-100
  avgDuration: number; // in seconds
  dependencies: string[];
  vendor?: string;
  activeIncidents: number;
}

export interface Vendor {
  id: string;
  name: string;
  status: VendorStatus;
  lastStatusChange: string;
  integrationType: string;
  workflowsConnected: number;
  uptime: number; // 0-100
  avgResponseTime: number; // in ms
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  actor: string;
  action: string;
  resource: string;
  result: 'success' | 'failure';
  metadata?: Record<string, unknown>;
}

export interface SystemMetrics {
  totalWorkflows: number;
  healthyWorkflows: number;
  activeIncidents: number;
  criticalIncidents: number;
  avgRecoveryTime: number; // in minutes
  uptime: number; // 0-100
}
