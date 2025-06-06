import { useEffect } from 'react';
import { useRouter } from 'next/router';
import StockDashboard from '@/components/stock-dashboard';
import { useAuth } from '@/lib/auth-context';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  return <StockDashboard />;
}
