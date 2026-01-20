/**
 * API Client
 *
 * HTTP client for backend communication with comprehensive error handling.
 * Follows strict integration constraints from system prompt.
 */

import { API_CONFIG } from './config';
import { parseHTTPError, parseNetworkError, logError, type APIError } from './errors';

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  headers?: Record<string, string>;
  timeout?: number;
  signal?: AbortSignal;
}

export interface APIResponse<T> {
  data?: T;
  error?: APIError;
  correlationId?: string;
}

/**
 * Make HTTP request to backend with comprehensive error handling
 */
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<APIResponse<T>> {
  const {
    method = 'GET',
    body,
    headers = {},
    timeout = API_CONFIG.timeout,
    signal,
  } = options;

  // Create abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  // Merge signal if provided
  if (signal) {
    signal.addEventListener('abort', () => controller.abort());
  }

  try {
    const url = `${API_CONFIG.baseURL}${endpoint}`;

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Extract correlation ID from response headers
    const correlationId = response.headers.get('X-Correlation-ID') || undefined;

    // Handle non-2xx responses
    if (!response.ok) {
      let responseBody: any;
      try {
        responseBody = await response.json();
      } catch {
        responseBody = { detail: response.statusText };
      }

      const error = parseHTTPError(response.status, responseBody, correlationId);
      logError(error, { endpoint, method });

      return { error, correlationId };
    }

    // Handle empty responses (204 No Content)
    if (response.status === 204) {
      return { data: undefined as T, correlationId };
    }

    // Parse successful response
    const data = await response.json();

    return { data, correlationId };
  } catch (error) {
    clearTimeout(timeoutId);

    // Handle network errors
    if (error instanceof Error) {
      const apiError = parseNetworkError(error);
      logError(apiError, { endpoint, method });
      return { error: apiError };
    }

    // Handle unknown errors
    const unknownError: APIError = {
      type: 'UNKNOWN' as any,
      message: 'An unexpected error occurred',
      detail: String(error),
      timestamp: new Date().toISOString(),
    };
    logError(unknownError, { endpoint, method });
    return { error: unknownError };
  }
}

/**
 * API Client
 */
export const apiClient = {
  /**
   * GET request
   */
  get<T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(endpoint, { ...options, method: 'GET' });
  },

  /**
   * POST request
   */
  post<T>(endpoint: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(endpoint, { ...options, body, method: 'POST' });
  },

  /**
   * PUT request
   */
  put<T>(endpoint: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(endpoint, { ...options, body, method: 'PUT' });
  },

  /**
   * PATCH request
   */
  patch<T>(endpoint: string, body?: unknown, options?: Omit<RequestOptions, 'method'>) {
    return request<T>(endpoint, { ...options, body, method: 'PATCH' });
  },

  /**
   * DELETE request
   */
  delete<T>(endpoint: string, options?: Omit<RequestOptions, 'method' | 'body'>) {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  },
};
