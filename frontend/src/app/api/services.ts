/**
 * API Services
 *
 * High-level API service functions that handle business logic and data transformation.
 * Each function returns data or error in a consistent format.
 */

import { apiClient } from './client';
import { API_ENDPOINTS } from './config';
import { adaptIncident, adaptIncidents } from './adapters';
import type { APIResponse } from './client';
import type { BackendIncident, BackendEvent, BackendAction, BackendHealthResponse, BackendReadinessResponse } from './types';
import type { Incident } from '@/app/types';

/**
 * Health Check Services
 */
export const healthService = {
  /**
   * Basic health check
   */
  async checkHealth(): Promise<APIResponse<{ status: string }>> {
    return apiClient.get<BackendHealthResponse>(API_ENDPOINTS.health);
  },

  /**
   * Readiness check (verifies database and Redis connectivity)
   */
  async checkReadiness(): Promise<APIResponse<BackendReadinessResponse>> {
    return apiClient.get<BackendReadinessResponse>(API_ENDPOINTS.healthReady);
  },
};

/**
 * Incident Services
 */
export const incidentService = {
  /**
   * List all incidents with optional filters
   */
  async listIncidents(filters?: {
    tenant_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<Incident[]>> {
    const queryParams = new URLSearchParams();
    if (filters?.tenant_id) queryParams.append('tenant_id', filters.tenant_id);
    if (filters?.status) queryParams.append('status', filters.status);
    if (filters?.limit) queryParams.append('limit', String(filters.limit));
    if (filters?.offset) queryParams.append('offset', String(filters.offset));

    const query = queryParams.toString();
    const endpoint = query ? `${API_ENDPOINTS.incidents}?${query}` : API_ENDPOINTS.incidents;

    const response = await apiClient.get<BackendIncident[]>(endpoint);

    if (response.error) {
      return { error: response.error, correlationId: response.correlationId };
    }

    // Adapt backend data to frontend types
    const incidents = response.data ? adaptIncidents(response.data) : [];

    return { data: incidents, correlationId: response.correlationId };
  },

  /**
   * Get incident details with related events and actions
   */
  async getIncidentDetail(incidentId: string): Promise<APIResponse<Incident>> {
    // Fetch incident
    const incidentResponse = await apiClient.get<BackendIncident>(
      API_ENDPOINTS.incidentDetail(incidentId)
    );

    if (incidentResponse.error) {
      return {
        error: incidentResponse.error,
        correlationId: incidentResponse.correlationId,
      };
    }

    // Fetch related events (non-blocking)
    const eventsPromise = apiClient.get<BackendEvent[]>(
      API_ENDPOINTS.incidentEvents(incidentId)
    );

    // Fetch related actions (non-blocking)
    const actionsPromise = apiClient.get<BackendAction[]>(
      API_ENDPOINTS.incidentActions(incidentId)
    );

    // Wait for all
    const [eventsResponse, actionsResponse] = await Promise.all([
      eventsPromise,
      actionsPromise,
    ]);

    // Adapt incident with events and actions
    const incident = adaptIncident(
      incidentResponse.data!,
      eventsResponse.data || [],
      actionsResponse.data || []
    );

    return { data: incident, correlationId: incidentResponse.correlationId };
  },

  /**
   * Update incident status
   */
  async updateStatus(
    incidentId: string,
    status: string,
    notes?: string
  ): Promise<APIResponse<Incident>> {
    const response = await apiClient.patch<BackendIncident>(
      API_ENDPOINTS.incidentUpdateStatus(incidentId),
      { status, notes }
    );

    if (response.error) {
      return { error: response.error, correlationId: response.correlationId };
    }

    // Adapt response
    const incident = response.data ? adaptIncident(response.data) : undefined;

    return { data: incident, correlationId: response.correlationId };
  },

  /**
   * Ignore incident
   */
  async ignoreIncident(
    incidentId: string,
    reason: string
  ): Promise<APIResponse<Incident>> {
    const response = await apiClient.post<BackendIncident>(
      API_ENDPOINTS.incidentIgnore(incidentId),
      { reason }
    );

    if (response.error) {
      return { error: response.error, correlationId: response.correlationId };
    }

    const incident = response.data ? adaptIncident(response.data) : undefined;

    return { data: incident, correlationId: response.correlationId };
  },
};

/**
 * Action Services
 */
export const actionService = {
  /**
   * List all actions with optional filters
   */
  async listActions(filters?: {
    status?: string;
    action_type?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<BackendAction[]>> {
    const queryParams = new URLSearchParams();
    if (filters?.status) queryParams.append('status', filters.status);
    if (filters?.action_type) queryParams.append('action_type', filters.action_type);
    if (filters?.limit) queryParams.append('limit', String(filters.limit));
    if (filters?.offset) queryParams.append('offset', String(filters.offset));

    const query = queryParams.toString();
    const endpoint = query ? `${API_ENDPOINTS.actions}?${query}` : API_ENDPOINTS.actions;

    return apiClient.get<BackendAction[]>(endpoint);
  },

  /**
   * Get action details
   */
  async getAction(actionId: string): Promise<APIResponse<BackendAction>> {
    return apiClient.get<BackendAction>(API_ENDPOINTS.actionDetail(actionId));
  },

  /**
   * Reverse an action
   */
  async reverseAction(
    actionId: string,
    reason?: string
  ): Promise<APIResponse<BackendAction>> {
    return apiClient.post<BackendAction>(
      API_ENDPOINTS.actionReverse(actionId),
      { reason }
    );
  },
};
