import { useState } from 'react';
import { useRouter } from 'next/router';
import { returnItem } from '../lib/api';
import { useAuth } from '@/lib/auth-context';

export default function ReturnItemPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState(0);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) {
      setError('Not authenticated');
      return;
    }
    try {
      await returnItem(token, { name, quantity: Number(quantity), threshold: 0 });
      router.push('/');
    } catch {
      setError('Failed to return item');
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Return Item</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Name</label>
          <input id="name" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label htmlFor="quantity">Quantity</label>
          <input id="quantity" type="number" value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value))} />
        </div>
        <button type="submit">Return</button>
      </form>
      {error && <p>{error}</p>}
    </div>
  );
}
