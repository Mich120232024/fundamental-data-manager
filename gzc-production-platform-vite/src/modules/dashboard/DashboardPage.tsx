import React from 'react';
import { LayoutEngine } from '@layouts/LayoutEngine';

export const DashboardPage: React.FC = () => {
  return (
    <div className="h-full p-4">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h2>
        <p className="text-gray-600 dark:text-gray-400">Customize your trading dashboard layout</p>
      </div>
      <div className="h-[calc(100%-80px)]">
        <LayoutEngine layoutId="main-dashboard" />
      </div>
    </div>
  );
};