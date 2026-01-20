/**
 * Data Adapters
 *
 * Transform backend responses to frontend types.
 * Backend is the source of truth - we adapt their schema to our UI needs.
 */

import type { Incident, SeverityLevel, IncidentStatus, RecoveryActionItem, TimelineEvent } from '@/app/types';
import type { BackendIncident, BackendEvent, BackendAction } from './types';

/**
 * Map backend severity to frontend severity
 */
function mapSeverity(backendSeverity: string): SeverityLevel {
  const mapping: Record<string, SeverityLevel> = {
    CRITICAL: 'critical',
    HIGH: 'high',
    MEDIUM: 'medium',
    LOW: 'low',
  };
  return mapping[backendSeverity.toUpperCase()] || 'medium';
}

/**
 * Map backend status to frontend status
 */
function mapStatus(backendStatus: string): IncidentStatus {
  const mapping: Record<string, IncidentStatus> = {
    DETECTED: 'active',
    ANALYZING: 'investigating',
    RESOLVED: 'resolved',
    ESCALATED: 'escalated',
    RECOVERING: 'recovering',
  };
  return mapping[backendStatus.toUpperCase()] || 'active';
}

/**
 * Generate title from error signature or metadata
 */
function generateTitle(incident: BackendIncident): string {
  // Check metadata for title
  if (incident.metadata?.title) {
    return incident.metadata.title;
  }

  // Generate from error signature
  const signature = incident.error_signature
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase());

  return signature;
}

/**
 * Build timeline from events and metadata
 */
function buildTimeline(
  incident: BackendIncident,
  events?: BackendEvent[],
  actions?: BackendAction[]
): TimelineEvent[] {
  const timeline: TimelineEvent[] = [];

  // Add detection event
  timeline.push({
    id: `timeline-${incident.id}-detected`,
    timestamp: incident.first_occurrence_at,
    event: `Incident detected: ${incident.error_signature}`,
    type: 'detection',
    actor: 'System',
  });

  // Add events from correlated events
  if (events && events.length > 0) {
    events.slice(0, 5).forEach((event, idx) => {
      timeline.push({
        id: `timeline-${incident.id}-event-${idx}`,
        timestamp: event.occurred_at,
        event: `Event: ${event.event_type}`,
        type: 'analysis',
        actor: 'System',
      });
    });
  }

  // Add actions
  if (actions && actions.length > 0) {
    actions.forEach((action) => {
      timeline.push({
        id: `timeline-${incident.id}-action-${action.id}`,
        timestamp: action.created_at,
        event: `Action ${action.status}: ${action.action_type}`,
        type: action.status === 'COMPLETED' ? 'resolution' : 'action',
        actor: 'System',
      });
    });
  }

  // Add resolution event if resolved
  if (incident.status === 'RESOLVED') {
    timeline.push({
      id: `timeline-${incident.id}-resolved`,
      timestamp: incident.updated_at,
      event: 'Incident marked as RESOLVED',
      type: 'resolution',
      actor: 'System',
    });
  }

  // Sort by timestamp
  timeline.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());

  return timeline;
}

/**
 * Map backend actions to recovery action items
 */
function mapRecoveryActions(actions: BackendAction[]): RecoveryActionItem[] {
  return actions.map((action) => {
    // Map action type
    let actionType: RecoveryActionItem['action'] = 'retry';
    if (action.action_type === 'ESCALATE') actionType = 'escalate';
    else if (action.action_type === 'ROLLBACK') actionType = 'rollback';
    else if (action.action_type === 'MANUAL') actionType = 'manual-intervention';

    // Determine risk based on action type
    let risk: 'low' | 'medium' | 'high' = 'low';
    if (action.action_type === 'ROLLBACK' || action.action_type === 'FAILOVER') {
      risk = 'high';
    } else if (action.action_type === 'ESCALATE') {
      risk = 'medium';
    }

    return {
      id: action.id,
      action: actionType,
      description: action.parameters?.description || `Execute ${action.action_type}`,
      risk,
      requiresApproval: risk === 'high',
      estimatedImpact: action.parameters?.estimated_impact || undefined,
    };
  });
}

/**
 * Adapt backend incident to frontend incident
 */
export function adaptIncident(
  backendIncident: BackendIncident,
  events?: BackendEvent[],
  actions?: BackendAction[]
): Incident {
  return {
    id: backendIncident.id,
    title: generateTitle(backendIncident),
    severity: mapSeverity(backendIncident.severity),
    status: mapStatus(backendIncident.status),
    workflowsAffected: backendIncident.metadata?.workflows_affected || [],
    detectedAt: backendIncident.first_occurrence_at,
    lastUpdated: backendIncident.updated_at,
    impactedUsers: backendIncident.metadata?.impacted_users || undefined,
    impactedTransactions: backendIncident.metadata?.impacted_transactions || undefined,
    description: backendIncident.metadata?.description ||
                 `Error signature: ${backendIncident.error_signature}. First detected at ${backendIncident.first_occurrence_at}.`,

    // AI Hypotheses - from metadata or empty (backend may provide via Decision table)
    aiHypotheses: backendIncident.metadata?.ai_hypotheses || [],

    // Timeline - built from events and actions
    timeline: buildTimeline(backendIncident, events, actions),

    // Recovery actions - mapped from backend actions
    recoveryActions: actions ? mapRecoveryActions(actions) : [],
  };
}

/**
 * Adapt list of backend incidents
 */
export function adaptIncidents(backendIncidents: BackendIncident[]): Incident[] {
  return backendIncidents.map((incident) => adaptIncident(incident));
}
