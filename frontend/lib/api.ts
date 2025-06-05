const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function login(username: string, password: string): Promise<string> {
  const res = await fetch(`${API_URL}/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: new URLSearchParams({ username, password }),
  });

  if (!res.ok) {
    throw new Error('Login failed');
  }
  const data = await res.json();
  return data.access_token as string;
}

export async function getItems(token: string) {
  const res = await fetch(`${API_URL}/items/status`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error('Failed to load');
  }
  return res.json();
}
