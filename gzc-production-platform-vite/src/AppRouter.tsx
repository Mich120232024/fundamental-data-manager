import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { TabbedLayout } from '@layouts/TabbedLayout';
import { DashboardPage } from '@modules/dashboard/DashboardPage';
import { PortfolioComponent } from '@modules/portfolio/PortfolioComponent';
import { LoginPage } from '@modules/auth/LoginPage';
import { ProtectedRoute } from '@components/ProtectedRoute';
import { TradingOperationsView } from '@modules/trading/TradingOperationsView';
import { RiskManagementView } from '@modules/risk/RiskManagementView';

const AnalyticsPage = () => <div className="h-full flex flex-col p-4"><h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Analytics</h3><div className="fx-card"><p>Advanced Analytics Dashboard</p></div></div>;

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <TabbedLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/trading" replace />} />
        <Route path="trading" element={<TradingOperationsView />} />
        <Route path="risk" element={<RiskManagementView />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="portfolio" element={<PortfolioComponent />} />
        <Route path="analytics" element={<AnalyticsPage />} />
      </Route>
    </Routes>
  );
};