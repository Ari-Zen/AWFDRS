/**
 * API Error Handling
 *
 * Comprehensive error types and handling for all failure scenarios.
 * NEVER swallows errors silently - all errors are surfaced with actionable messages.
 */

export enum ErrorType {
  // Client errors (4xx)
  BAD_REQUEST = 'BAD_REQUEST',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  RATE_LIMITED = 'RATE_LIMITED',

  // Server errors (5xx)
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  GATEWAY_TIMEOUT = 'GATEWAY_TIMEOUT',

  // Network errors
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT = 'TIMEOUT',

  // Unknown
  UNKNOWN = 'UNKNOWN',
}

export interface APIError {
  type: ErrorType;
  message: string; // User-facing message
  detail?: string; // Technical details for developers
  statusCode?: number;
  timestamp: string;
  correlationId?: string;
}

/**
 * Parse HTTP response errors into structured APIError
 */
export function parseHTTPError(
  status: number,
  responseBody: any,
  correlationId?: string
): APIError {
  const timestamp = new Date().toISOString();

  // 4xx errors
  if (status === 400) {
    return {
      type: ErrorType.BAD_REQUEST,
      message: 'Invalid request data. Please check your input.',
      detail: responseBody?.detail || 'Bad request',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 401) {
    return {
      type: ErrorType.UNAUTHORIZED,
      message: 'Authentication required. Please log in again.',
      detail: responseBody?.detail || 'Unauthorized',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 403) {
    return {
      type: ErrorType.FORBIDDEN,
      message: 'Access denied. You do not have permission to perform this action.',
      detail: responseBody?.detail || 'Forbidden',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 404) {
    return {
      type: ErrorType.NOT_FOUND,
      message: 'The requested resource was not found.',
      detail: responseBody?.detail || 'Not found',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 409) {
    return {
      type: ErrorType.CONFLICT,
      message: 'Request conflicts with current state. Please refresh and try again.',
      detail: responseBody?.detail || 'Conflict',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 422) {
    return {
      type: ErrorType.VALIDATION_ERROR,
      message: 'Validation failed. Please check your input.',
      detail: responseBody?.detail || 'Validation error',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 429) {
    return {
      type: ErrorType.RATE_LIMITED,
      message: 'Too many requests. Please wait before trying again.',
      detail: responseBody?.detail || 'Rate limit exceeded',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  // 5xx errors
  if (status === 500) {
    return {
      type: ErrorType.INTERNAL_SERVER_ERROR,
      message: 'An internal server error occurred. Our team has been notified.',
      detail: responseBody?.detail || 'Internal server error',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 503) {
    return {
      type: ErrorType.SERVICE_UNAVAILABLE,
      message: 'Service temporarily unavailable. Please try again later.',
      detail: responseBody?.detail || 'Service unavailable',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  if (status === 504) {
    return {
      type: ErrorType.GATEWAY_TIMEOUT,
      message: 'Request timed out. Please try again.',
      detail: responseBody?.detail || 'Gateway timeout',
      statusCode: status,
      timestamp,
      correlationId,
    };
  }

  // Default for unknown status codes
  return {
    type: ErrorType.UNKNOWN,
    message: 'An unexpected error occurred.',
    detail: responseBody?.detail || `HTTP ${status}`,
    statusCode: status,
    timestamp,
    correlationId,
  };
}

/**
 * Parse network errors
 */
export function parseNetworkError(error: Error): APIError {
  const timestamp = new Date().toISOString();

  if (error.name === 'AbortError' || error.message.includes('timeout')) {
    return {
      type: ErrorType.TIMEOUT,
      message: 'Request timed out. Please check your connection and try again.',
      detail: error.message,
      timestamp,
    };
  }

  return {
    type: ErrorType.NETWORK_ERROR,
    message: 'Network error. Please check your internet connection.',
    detail: error.message,
    timestamp,
  };
}

/**
 * Log structured error for developer visibility
 */
export function logError(error: APIError, context?: Record<string, unknown>): void {
  console.error('[API Error]', {
    type: error.type,
    message: error.message,
    detail: error.detail,
    statusCode: error.statusCode,
    timestamp: error.timestamp,
    correlationId: error.correlationId,
    context,
  });
}
