import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { getSettings, updateSettings } from '@/lib/api';
import { useAuth } from '@/lib/auth-context';

export default function SettingsPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [key, setKey] = useState('');
  const [value, setValue] = useState('');

  useEffect(() => {
    if (!token) {
      router.replace('/login');
    } else {
      getSettings(token).then(setSettings).catch(() => {});
    }
  }, [token, router]);

  if (!token) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    const newSettings = { ...settings, [key]: value };
    const updated = await updateSettings(token, newSettings);
    setSettings(updated);
    setKey('');
    setValue('');
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>Settings</h1>
      <ul>
        {Object.entries(settings).map(([k, v]) => (
          <li key={k}>
            {k}: {v}
          </li>
        ))}
      </ul>
      <form onSubmit={handleSubmit} style={{ marginTop: 20 }}>
        <input
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="key"
        />
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="value"
        />
        <button type="submit">Save</button>
      </form>
    </div>
  );
}

