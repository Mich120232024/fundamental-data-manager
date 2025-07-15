import React from 'react';
import { Outlet } from 'react-router-dom';

export const TabbedLayout: React.FC = () => {
  return (
    <div style={{ height: 'calc(100vh - 64px)', overflow: 'hidden' }}>
      <Outlet />
    </div>
  );
};