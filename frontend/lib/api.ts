const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type ApiFetchOptions = RequestInit & { body?: any };

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
  if (body && typeof body === 'object' && !(body instanceof FormData)) {
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
