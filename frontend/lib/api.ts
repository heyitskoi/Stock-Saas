const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Allow using plain objects for the request body by removing the
// `body` property from `RequestInit` and redefining it with a looser type.
export type ApiFetchOptions = Omit<RequestInit, 'body'> & { body?: any };

export const isAuthenticated = () =>
  typeof window !== 'undefined' && !!localStorage.getItem('token');

export async function apiFetch<T>(
  path: string,
  opts: ApiFetchOptions = {}
): Promise<T> {
  const headers = new Headers(opts.headers || {});
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let body = opts.body;
  if (
    body &&
    typeof body === 'object' &&
    !(body instanceof FormData) &&
    !(body instanceof URLSearchParams)
  ) {
    headers.set('Content-Type', 'application/json');
    body = JSON.stringify(body);
  }

  const res = await fetch(`${API_URL}${path}`, {
    ...opts,
    headers,
    body,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }

  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    return res.json();
  }

  return (await res.text()) as unknown as T;
}

export const apiGet = <T>(path: string, options?: ApiFetchOptions) =>
  apiFetch<T>(path, { method: 'GET', ...(options || {}) });

export const apiPost = <T>(path: string, body?: any, options?: ApiFetchOptions) =>
  apiFetch<T>(path, { method: 'POST', body, ...(options || {}) });

export async function login(username: string, password: string) {
  const body = new URLSearchParams();
  body.set('username', username);
  body.set('password', password);
  const res = await apiPost<{ access_token: string }>('/token', body);
  return res.access_token;
}

// Inventory APIs
export const addItem = (token: string, data: any) =>
  apiPost<any>('/items/add', { ...data, tenant_id: 1 });

export const issueItem = (token: string, data: any) =>
  apiPost<any>('/items/issue', { ...data, tenant_id: 1 });

export const returnItem = (token: string, data: any) =>
  apiPost<any>('/items/return', { ...data, tenant_id: 1 });

export const updateItemApi = (token: string, data: any) =>
  apiFetch<any>('/items/update', {
    method: 'PUT',
    body: { ...data, tenant_id: 1 },
  });

export const getItems = (token: string) =>
  apiGet<any[]>('/items/status?tenant_id=1');

// Analytics
export const getOverallUsage = (
  token: string,
  params: Record<string, string | number>
) => {
  const query = new URLSearchParams(params as any).toString();
  return apiGet<any[]>(`/analytics/usage?${query}`);
};

// User management
export const listUsers = (token: string) =>
  apiGet<any[]>('/users/?tenant_id=1');

export const createUser = (token: string, data: any) =>
  apiPost<any>('/users/', { ...data, tenant_id: 1 });

export const updateUser = (token: string, data: any) =>
  apiFetch<any>('/users/update', {
    method: 'PUT',
    body: data,
  });

export const deleteUser = (token: string, id: number) =>
  apiFetch<any>('/users/delete', {
    method: 'DELETE',
    body: { id },
  });
