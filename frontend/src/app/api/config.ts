/**
 * API Configuration
 *
 * Centralizes API configuration and ensures no hardcoded values.
 */

export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  version: import.meta.env.VITE_API_VERSION || 'v1',
  timeout: 30000, // 30 seconds
  retryAttempts: 0, // No automatic retries (backend must document retry safety)
} as const;

export const API_ENDPOINTS = {
  // Health
  health: '/api/v1/health',
  healthReady: '/api/v1/health/ready',

  // Events
  events: '/api/v1/events',

  // Incidents
  incidents: '/api/v1/incidents',
  incidentDetail: (id: string) => `/api/v1/incidents/${id}`,
  incidentEvents: (id: string) => `/api/v1/incidents/${id}/events`,
  incidentActions: (id: string) => `/api/v1/incidents/${id}/actions`,
  incidentUpdateStatus: (id: string) => `/api/v1/incidents/${id}/status`,
  incidentIgnore: (id: string) => `/api/v1/incidents/${id}/ignore`,

  // Actions
  actions: '/api/v1/actions',
  actionDetail: (id: string) => `/api/v1/actions/${id}`,
  actionReverse: (id: string) => `/api/v1/actions/${id}/reverse`,
} as const;
