import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getItems, getItemUsage } from '../lib/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function UsagePage() {
  const [items, setItems] = useState<string[]>([]);
  const [selected, setSelected] = useState('');
  const [usage, setUsage] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return;
    getItems(token).then((data) => {
      const names = Object.keys(data);
      setItems(names);
      if (names.length) {
        setSelected(names[0]);
      }
    });
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token || !selected) return;
    getItemUsage(token, selected).then(setUsage).catch(() => setUsage([]));
  }, [selected]);

  const chartData = {
    labels: usage.map((u) => u.date),
    datasets: [
      {
        label: 'Issued',
        data: usage.map((u) => u.issued),
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
      {
        label: 'Returned',
        data: usage.map((u) => u.returned),
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
    ],
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Item Usage</h1>
      <Link href="/">Back</Link>
      <div style={{ margin: '20px 0' }}>
        <label htmlFor="item">Item: </label>
        <select
          id="item"
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
        >
          {items.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>
      <Line data={chartData} />
    </div>
  );
}
