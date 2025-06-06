import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getOverallUsage, getItems } from '../lib/api';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function UsagePage() {
  const [usage, setUsage] = useState<any[]>([]);
  const [tenantId, setTenantId] = useState(1);
  const [start, setStart] = useState('');
  const [end, setEnd] = useState('');
  const [topIssued, setTopIssued] = useState<any[]>([]);

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
    const token = localStorage.getItem('token');
    if (!token || !start || !end) return;
    getOverallUsage(token, {
      tenant_id: tenantId,
      start: start,
      end: end,
    })
      .then(setUsage)
      .catch(() => setUsage([]));
    getItems(token)
      .then((items) => {
        return Promise.all(
          items.map((it: any) =>
            getOverallUsage(token, {
              tenant_id: tenantId,
              start: start,
              end: end,
              item_name: it.name,
            }).then((data) => ({
              name: it.name,
              total: data.reduce((acc: number, d: any) => acc + d.issued, 0),
            }))
          )
        );
      })
      .then((results) => {
        results.sort((a, b) => b.total - a.total);
        setTopIssued(results.slice(0, 5));
      })
      .catch(() => setTopIssued([]));
  }, [tenantId, start, end]);

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

  const topData = {
    labels: topIssued.map((t) => t.name),
    datasets: [
      {
        label: 'Issued',
        data: topIssued.map((t) => t.total),
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
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
      {topIssued.length > 0 && (
        <div style={{ marginTop: 40 }}>
          <h2>Top Issued Items</h2>
          <Bar data={topData} />
        </div>
      )}
    </div>
  );
}
