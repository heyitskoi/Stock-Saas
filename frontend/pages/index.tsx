import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { getItems, deleteItem } from '../lib/api';

export default function Home() {
  const router = useRouter();
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    getItems(token)
      .then(setItems)
      .catch(() => setError('Failed to load inventory'));
  }, []);

  async function handleDelete(name: string) {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await deleteItem(token, name);
      setItems(items.filter((it) => it.name !== name));
    } catch {
      setError('Failed to delete item');
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Inventory Dashboard</h1>
      <nav style={{ marginBottom: 20 }}>
        <Link href="/add" style={{ marginRight: 10 }}>Add Item</Link>
        <Link href="/issue" style={{ marginRight: 10 }}>Issue Item</Link>
        <Link href="/return">Return Item</Link>
      </nav>
      {error && <p>{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Available</th>
            <th>In Use</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.name}>
              <td>{item.name}</td>
              <td>{item.available}</td>
              <td>{item.in_use}</td>
              <td>
                <button onClick={() => router.push(`/edit?name=${item.name}`)}>
                  Edit
                </button>
                <button onClick={() => handleDelete(item.name)} style={{ marginLeft: 5 }}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
