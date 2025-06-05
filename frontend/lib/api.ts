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

export async function addItem(token: string, item: { name: string; quantity: number; threshold: number }) {
  const res = await fetch(`${API_URL}/items/add`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(item),
  });
  if (!res.ok) {
    throw new Error('Failed to add item');
  }
  return res.json();
}

export async function issueItem(token: string, item: { name: string; quantity: number; threshold: number }) {
  const res = await fetch(`${API_URL}/items/issue`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(item),
  });
  if (!res.ok) {
    throw new Error('Failed to issue item');
  }
  return res.json();
}

export async function returnItem(token: string, item: { name: string; quantity: number; threshold: number }) {
  const res = await fetch(`${API_URL}/items/return`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(item),
  });
  if (!res.ok) {
    throw new Error('Failed to return item');
  }
  return res.json();
}

export async function createUser(
  token: string,
  user: { username: string; password: string; role: string }
) {
  const res = await fetch(`${API_URL}/users/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(user),
  });
  if (!res.ok) {
    throw new Error('Failed to create user');
  }
  return res.json();
}

export async function listUsers(token: string) {
  const res = await fetch(`${API_URL}/users/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error('Failed to load users');
  }
  return res.json();
}
