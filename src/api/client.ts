const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export function getAuthToken(): string | null {
  return localStorage.getItem('kirana_auth_token');
}

export function setAuthToken(token: string | null) {
  if (token) {
    localStorage.setItem('kirana_auth_token', token);
  } else {
    localStorage.removeItem('kirana_auth_token');
  }
}

export function getSelectedShopId(): string | null {
  return localStorage.getItem('kirana_selected_shop_id');
}

export function setSelectedShopId(shopId: string | null) {
  if (shopId) {
    localStorage.setItem('kirana_selected_shop_id', shopId);
  } else {
    localStorage.removeItem('kirana_selected_shop_id');
  }
}

export interface APIErrorResponse {
  code: string;
  message: string;
  details?: any;
}

export class APIError extends Error {
  code: string;
  status: number;
  details?: any;

  constructor(message: string, code: string = 'API_ERROR', status: number = 400, details?: any) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.status = status;
    this.details = details;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${BASE_URL}${endpoint}`;
  
  const token = getAuthToken();
  const shopId = getSelectedShopId();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (shopId) {
    headers['X-Shop-Id'] = shopId;
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 204) {
      return {} as T;
    }

    const json = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status === 401) {
        // Token expired or invalid
        setAuthToken(null);
      }
      const errorMsg = json?.error?.message || json?.detail || `HTTP error ${response.status}`;
      const errorCode = json?.error?.code || 'HTTP_ERROR';
      throw new APIError(errorMsg, errorCode, response.status, json?.error?.details);
    }

    // Extract data payload if standardized APIResponse { success: true, data: ... }
    if (json && typeof json === 'object' && 'success' in json && 'data' in json) {
      return json.data as T;
    }

    return json as T;
  } catch (error: any) {
    if (error instanceof APIError) {
      throw error;
    }
    const msg = error.message === 'Failed to fetch'
      ? 'Cannot connect to backend server. Please verify FastAPI backend server is running on http://localhost:8000.'
      : (error.message || 'Network communication error');
    throw new APIError(msg, 'NETWORK_ERROR', 0);
  }
}

export const api = {
  get: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'GET' }),
  post: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'POST', body: body ? JSON.stringify(body) : undefined }),
  patch: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'PATCH', body: body ? JSON.stringify(body) : undefined }),
  put: <T>(endpoint: string, body?: any, options?: RequestInit) =>
    request<T>(endpoint, { ...options, method: 'PUT', body: body ? JSON.stringify(body) : undefined }),
  delete: <T>(endpoint: string, options?: RequestInit) => request<T>(endpoint, { ...options, method: 'DELETE' }),
};
