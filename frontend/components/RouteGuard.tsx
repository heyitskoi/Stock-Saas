'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/lib/auth-context';

// Define routes that only specific roles can access
const adminOnlyRoutes = ['/admin', '/users', '/settings'];
const managerAndAdminRoutes = ['/reports', '/inventory-management'];
const staffRestrictedPaths = ['/edit', '/add', '/delete', '/transfer']; // Paths that staff cannot access

interface RouteGuardProps {
  children: React.ReactNode;
}

export default function RouteGuard({ children }: RouteGuardProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [authorized, setAuthorized] = useState(false);
  const { user, isAuthenticated } = useAuth();

  useEffect(() => {
    // Function to check if user is authorized for this route
    const authCheck = () => {
      // If not authenticated, redirect to login
      if (!isAuthenticated) {
        setAuthorized(false);
        router.push('/login');
        return;
      }
      
      // Check role-based permissions
      const isAdmin = user?.is_admin === true;
      
      // Admin-only routes check
      if (adminOnlyRoutes.some(route => pathname?.startsWith(route)) && !isAdmin) {
        setAuthorized(false);
        router.push('/dashboard');
        return;
      }
      
      // Manager and admin routes check
      if (managerAndAdminRoutes.some(route => pathname?.startsWith(route)) && !isAdmin) {
        setAuthorized(false);
        router.push('/dashboard');
        return;
      }
      
      // Staff restrictions check - prevent access to edit/add/delete paths
      if (
        user?.role === 'staff' && 
        staffRestrictedPaths.some(path => pathname?.includes(path))
      ) {
        setAuthorized(false);
        router.push('/dashboard');
        return;
      }
      
      // If we got here, user is authorized
      setAuthorized(true);
    };

    authCheck();
  }, [isAuthenticated, pathname, router, user]);

  return authorized ? <>{children}</> : null;
}
