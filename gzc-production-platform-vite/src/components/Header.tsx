import React from 'react';
import { useTheme } from '@store/ThemeProvider';
import { useMsal } from '@azure/msal-react';
import { theme as professionalTheme } from '../theme';

interface HeaderProps {
  onMenuClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { theme, toggleTheme } = useTheme();
  const { instance, accounts } = useMsal();
  
  const handleLogout = () => {
    instance.logoutRedirect();
  };

  const buttonStyle = {
    padding: '8px 12px',
    borderRadius: '6px',
    border: 'none',
    background: 'transparent',
    color: professionalTheme.text,
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    fontSize: '14px'
  };

  const buttonHoverHandler = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.background = professionalTheme.surfaceAlt;
  };

  const buttonLeaveHandler = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.currentTarget.style.background = 'transparent';
  };

  return (
    <header style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      height: '64px',
      background: professionalTheme.surface,
      borderBottom: `1px solid ${professionalTheme.border}`,
      zIndex: 50
    }}>
      <div style={{
        height: '100%',
        padding: '0 16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={onMenuClick}
            style={buttonStyle}
            onMouseEnter={buttonHoverHandler}
            onMouseLeave={buttonLeaveHandler}
          >
            <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <h1 style={{
            fontSize: '18px',
            fontWeight: '600',
            color: professionalTheme.text,
            margin: 0
          }}>
            GZC Production Platform
          </h1>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={toggleTheme}
            style={buttonStyle}
            onMouseEnter={buttonHoverHandler}
            onMouseLeave={buttonLeaveHandler}
            title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
          >
            {theme === 'light' ? (
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            ) : (
              <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            )}
          </button>
          
          {accounts.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{
                fontSize: '12px',
                color: professionalTheme.textSecondary
              }}>
                {accounts[0].username}
              </span>
              <button
                onClick={handleLogout}
                style={{
                  ...buttonStyle,
                  background: professionalTheme.surfaceAlt,
                  border: `1px solid ${professionalTheme.border}`,
                  fontSize: '12px'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = professionalTheme.border;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = professionalTheme.surfaceAlt;
                }}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};