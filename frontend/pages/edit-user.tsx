import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { updateUser } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function EditUserPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [id, setId] = useState<number | null>(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('user');
  const [error, setError] = useState('');

  useEffect(() => {
    if (typeof router.query.id === 'string') {
      setId(parseInt(router.query.id));
    }
    if (typeof router.query.username === 'string') {
      setUsername(router.query.username);
    }
    if (typeof router.query.role === 'string') {
      setRole(router.query.role);
    }
  }, [router.query]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token || id === null) {
      setError('Not authenticated');
      return;
    }
    try {
      await updateUser(token, {
        id,
        username: username || undefined,
        password: password || undefined,
        role: role || undefined,
      });
      router.push('/users');
    } catch {
      setError('Failed to update user');
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Edit User</h1>
      <form onSubmit={handleSubmit}>
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
        <button type="submit">Update User</button>
      </form>
      {error && <p>{error}</p>}
    </div>
  );
}
