import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { ReactNode } from 'react';

export const ProtectedRoute = ({ children }: { children: ReactNode }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <div className="loading">Загрузка...</div>;
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
};