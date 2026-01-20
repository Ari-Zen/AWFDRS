/**
 * Backend API Types
 *
 * Type definitions matching the backend API responses.
 * These are the authoritative schemas from the backend.
 */

export interface BackendIncident {
  id: string;
  tenant_id: string;
  vendor_id?: string;
  error_signature: string;
  status: string; // Backend: DETECTED, ANALYZING, RESOLVED, ESCALATED
  severity: string; // Backend: LOW, MEDIUM, HIGH, CRITICAL
  correlated_event_ids: string[];
  first_occurrence_at: string;
  last_occurrence_at: string;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface BackendEvent {
  id: string;
  event_type: string;
  occurred_at: string;
  payload: Record<string, any>;
}

export interface BackendAction {
  id: string;
  decision_id: string;
  action_type: string; // RETRY, ESCALATE, NOTIFY, etc.
  status: string; // PENDING, RUNNING, COMPLETED, FAILED
  parameters?: Record<string, any>;
  result?: Record<string, any>;
  error?: string;
  is_reversible: boolean;
  correlation_id: string;
  created_at: string;
}

export interface BackendHealthResponse {
  status: string;
  timestamp: string;
}

export interface BackendReadinessResponse {
  status: string;
  database: string;
  redis: string;
  timestamp: string;
}

export interface BackendEventSubmitRequest {
  tenant_id: string;
  workflow_id: string;
  event_type: string;
  payload: Record<string, any>;
  idempotency_key: string;
  occurred_at: string;
  schema_version: string;
}

export interface BackendEventSubmitResponse {
  event_id: string;
  status: string;
  message: string;
  correlation_id: string;
}
