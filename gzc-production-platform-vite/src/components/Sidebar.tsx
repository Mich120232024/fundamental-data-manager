import React from 'react';
import { NavLink } from 'react-router-dom';
import { theme } from '../theme';

interface SidebarProps {
  isOpen: boolean;
}

const navItems = [
  { path: '/trading', label: 'Trading Operations', icon: '📈' },
  { path: '/risk', label: 'Risk Management', icon: '🛡️' },
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/portfolio', label: 'Portfolio', icon: '💼' },
  { path: '/analytics', label: 'Analytics', icon: '📉' },
];

export const Sidebar: React.FC<SidebarProps> = ({ isOpen }) => {
  return (
    <aside
      style={{
        position: 'fixed',
        left: 0,
        top: '64px',
        height: 'calc(100vh - 64px)',
        width: isOpen ? '256px' : '0px',
        background: theme.surface,
        borderRight: `1px solid ${theme.border}`,
        transition: 'all 0.3s ease',
        zIndex: 40,
        overflow: 'hidden'
      }}
    >
      <nav style={{ padding: '16px' }}>
        <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
          {navItems.map(({ path, label, icon }) => (
            <li key={path} style={{ marginBottom: '8px' }}>
              <NavLink
                to={path}
                style={({ isActive }) => ({
                  display: 'flex',
                  alignItems: 'center',
                  padding: '12px 16px',
                  borderRadius: '6px',
                  textDecoration: 'none',
                  transition: 'all 0.2s ease',
                  background: isActive ? theme.primary : 'transparent',
                  color: isActive ? '#ffffff' : theme.text,
                  fontSize: '14px',
                  fontWeight: '500'
                })}
                onMouseEnter={(e) => {
                  if (!e.currentTarget.classList.contains('active')) {
                    e.currentTarget.style.background = theme.surfaceAlt;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!e.currentTarget.classList.contains('active')) {
                    e.currentTarget.style.background = 'transparent';
                  }
                }}
              >
                <span style={{ marginRight: '12px', fontSize: '16px' }}>{icon}</span>
                <span>{label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};