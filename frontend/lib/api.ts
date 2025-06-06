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

export async function addItem(
  token: string,
  item: { name: string; quantity: number; threshold: number }
) {
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

export async function issueItem(
  token: string,
  item: { name: string; quantity: number; threshold: number }
) {
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

export async function returnItem(
  token: string,
  item: { name: string; quantity: number; threshold: number }
) {
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

export async function updateItemApi(
  token: string,
  item: { name: string; new_name?: string; threshold?: number }
) {
  const res = await fetch(`${API_URL}/items/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(item),
  });
  if (!res.ok) {
    throw new Error('Failed to update item');
  }
  return res.json();
}

export async function deleteItem(token: string, name: string) {
  const res = await fetch(`${API_URL}/items/delete`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) {
    throw new Error('Failed to delete item');
  }
  return res.json();
}

export async function exportAuditCSV(token: string, limit = 100): Promise<string> {
  const res = await fetch(`${API_URL}/analytics/audit/export?limit=${limit}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error('Failed to export CSV');
  }
  return res.text();
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

export async function updateUser(
  token: string,
  user: { id: number; username?: string; password?: string; role?: string }
) {
  const res = await fetch(`${API_URL}/users/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(user),
  });
  if (!res.ok) {
    throw new Error('Failed to update user');
  }
  return res.json();
}

export async function deleteUser(token: string, id: number) {
  const res = await fetch(`${API_URL}/users/delete`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ id }),
  });
  if (!res.ok) {
    throw new Error('Failed to delete user');
  }
  return res.json();
}

export async function getItemUsage(
  token: string,
  name: string,
  days = 30
) {
  const res = await fetch(
    `${API_URL}/analytics/usage/${name}?days=${days}`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  if (!res.ok) {
    throw new Error('Failed to load usage');
  }
  return res.json();
}

export async function getOverallUsage(
  token: string,
  opts: {
    start?: string;
    end?: string;
    tenant_id?: number;
    days?: number;
    item_name?: string;
    user_id?: number;
  } = {}
) {
  const params = new URLSearchParams();
  if (opts.days !== undefined) params.append('days', String(opts.days));
  if (opts.start) params.append('start_date', opts.start);
  if (opts.end) params.append('end_date', opts.end);
  if (opts.tenant_id !== undefined)
    params.append('tenant_id', String(opts.tenant_id));
  if (opts.item_name) params.append('item_name', opts.item_name);
  if (opts.user_id !== undefined)
    params.append('user_id', String(opts.user_id));

  const res = await fetch(`${API_URL}/analytics/usage?${params.toString()}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) {
    throw new Error('Failed to load usage');
  }
  return res.json();
}
