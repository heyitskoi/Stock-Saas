import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getOverallUsage } from '../lib/api';
import { useAuth } from '../lib/AuthContext';
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
  const [usage, setUsage] = useState<any[]>([]);
  const [tenantId, setTenantId] = useState(1);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const { token } = useAuth();

  useEffect(() => {
    const now = new Date();
    const until = now.toISOString().slice(0, 10);
    const since = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
      .toISOString()
      .slice(0, 10);
    setStart(since);
    setEnd(until);
  }, []);

  useEffect(() => {
    if (!token || !start || !end) return;
    getOverallUsage(token, {
      tenant_id: tenantId,
      start: start,
      end: end,
    })
      .then(setUsage)
      .catch(() => setUsage([]));
  }, [tenantId, start, end, token]);

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
      <h1>Usage Analytics</h1>
      <Link href="/">Back</Link>
      <div style={{ margin: '20px 0' }}>
        <label style={{ marginRight: 10 }}>
          Tenant ID:
          <input
            type="number"
            value={tenantId}
            onChange={(e) => setTenantId(Number(e.target.value))}
            style={{ marginLeft: 5 }}
          />
        </label>
        <label style={{ marginRight: 10 }}>
          Start:
          <input
            type="date"
            value={start}
            onChange={(e) => setStart(e.target.value)}
            style={{ marginLeft: 5 }}
          />
        </label>
        <label>
          End:
          <input
            type="date"
            value={end}
            onChange={(e) => setEnd(e.target.value)}
            style={{ marginLeft: 5 }}
          />
        </label>
      </div>
      <Line data={chartData} />
    </div>
  );
}
