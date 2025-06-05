import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { listUsers, createUser } from '../lib/api';

export default function UsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<any[]>([]);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    listUsers(token)
      .then(setUsers)
      .catch(() => router.push('/login'));
  }, [router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Not authenticated');
      return;
    }
    try {
      await createUser(token, { username, password, role });
      const updated = await listUsers(token);
      setUsers(updated);
      setUsername('');
      setPassword('');
      setRole('user');
    } catch {
      setError('Failed to create user');
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Manage Users</h1>
      <form onSubmit={handleSubmit} style={{ marginBottom: 20 }}>
        <div>
          <label htmlFor="username">Username</label>
          <input id="username" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <div>
          <label htmlFor="role">Role</label>
          <select id="role" value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="admin">admin</option>
            <option value="manager">manager</option>
            <option value="user">user</option>
          </select>
        </div>
        <button type="submit">Create User</button>
      </form>
      {error && <p>{error}</p>}
      <h2>Existing Users</h2>
      <ul>
        {users.map((u) => (
          <li key={u.id}>{u.username} - {u.role}</li>
        ))}
      </ul>
    </div>
  );
}
