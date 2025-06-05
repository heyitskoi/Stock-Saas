import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';
import { updateItemApi } from '../lib/api';

export default function EditItemPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [newName, setNewName] = useState('');
  const [threshold, setThreshold] = useState<number | ''>('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (typeof router.query.name === 'string') {
      setName(router.query.name);
    }
  }, [router.query.name]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const token = localStorage.getItem('token');
    if (!token) {
      setError('Not authenticated');
      return;
    }
    try {
      await updateItemApi(token, {
        name,
        new_name: newName || undefined,
        threshold: threshold === '' ? undefined : Number(threshold),
      });
      router.push('/');
    } catch {
      setError('Failed to update item');
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Edit Item</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="newName">New Name</label>
          <input id="newName" value={newName} onChange={(e) => setNewName(e.target.value)} />
        </div>
        <div>
          <label htmlFor="threshold">Threshold</label>
          <input id="threshold" type="number" value={threshold} onChange={(e) => setThreshold(parseInt(e.target.value))} />
        </div>
        <button type="submit">Update</button>
      </form>
      {error && <p>{error}</p>}
    </div>
  );
}
