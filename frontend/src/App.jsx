import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';

// Components & Pages
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import DataManagement from './pages/DataManagement';
import DataQuality from './pages/DataQuality';
import Profitability from './pages/Profitability';
import Forecasting from './pages/Forecasting';
import AnomalyDetection from './pages/AnomalyDetection';
import CustomerIntelligence from './pages/CustomerIntelligence';
import Inventory from './pages/Inventory';
import Marketing from './pages/Marketing';
import FinancialRisk from './pages/FinancialRisk';
import AIAdvisor from './pages/AIAdvisor';
import Reports from './pages/Reports';
import ModelPerformance from './pages/ModelPerformance';
import Settings from './pages/Settings';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth();
  if (loading) return null;
  // If user is not logged in, redirect to login
  if (!user && !localStorage.getItem('nexoraiq_token')) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="data" element={<DataManagement />} />
              <Route path="quality" element={<DataQuality />} />
              <Route path="profitability" element={<Profitability />} />
              <Route path="forecasting" element={<Forecasting />} />
              <Route path="anomalies" element={<AnomalyDetection />} />
              <Route path="customers" element={<CustomerIntelligence />} />
              <Route path="inventory" element={<Inventory />} />
              <Route path="marketing" element={<Marketing />} />
              <Route path="finance" element={<FinancialRisk />} />
              <Route path="advisor" element={<AIAdvisor />} />
              <Route path="reports" element={<Reports />} />
              <Route path="explainability" element={<ModelPerformance />} />
              <Route path="settings" element={<Settings />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

