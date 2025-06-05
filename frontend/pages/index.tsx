import { useEffect, useState } from 'react';
import Link from 'next/link';
import { getItems, exportAuditCSV } from '../lib/api';

export default function Home() {
  const [items, setItems] = useState<any[]>([]);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    getItems(token)
      .then(setItems)
      .catch(() => setError('Failed to load inventory'));
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/users/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((res) => {
      if (res.ok) setIsAdmin(true);
    });
  }, []);

  async function handleDownload() {
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      const csv = await exportAuditCSV(token);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'audit_log.csv';
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      alert('Failed to download CSV');
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
      {isAdmin && (
        <button onClick={handleDownload} style={{ marginBottom: 20 }}>
          Download Audit CSV
        </button>
      )}
      {error && <p>{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Available</th>
            <th>In Use</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.name}>
              <td>{item.name}</td>
              <td>{item.available}</td>
              <td>{item.in_use}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

