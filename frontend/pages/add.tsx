import { useState } from 'react';
import { useRouter } from 'next/router';
import { addItem } from '../lib/api';
import { useAuth } from '../lib/AuthContext';

export default function AddItemPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [name, setName] = useState('');
  const [quantity, setQuantity] = useState(0);
  const [threshold, setThreshold] = useState(0);
  const [error, setError] = useState('');

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) {
      setError('Not authenticated');
      return;
    }
    try {
      await addItem(token, { name, quantity: Number(quantity), threshold: Number(threshold) });
      router.push('/');
    } catch {
      setError('Failed to add item');
    }
  }

  return (
    <div style={{ padding: 20 }}>
      <h1>Add Item</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="name">Name</label>
          <input id="name" value={name} onChange={(e) => setName(e.target.value)} />
        </div>
        <div>
          <label htmlFor="quantity">Quantity</label>
          <input id="quantity" type="number" value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value))} />
        </div>
        <div>
          <label htmlFor="threshold">Threshold</label>
          <input id="threshold" type="number" value={threshold} onChange={(e) => setThreshold(parseInt(e.target.value))} />
        </div>
        <button type="submit">Add</button>
      </form>
      {error && <p>{error}</p>}
    </div>
  );
}
