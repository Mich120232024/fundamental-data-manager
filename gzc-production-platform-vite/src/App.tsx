import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { MsalProvider } from '@azure/msal-react';
import { ThemeProvider } from '@store/ThemeProvider';
import { msalInstance } from '@services/auth/msal';
import { theme } from './theme';
import { ProfessionalHeader } from './components/ProfessionalHeader';
import { DashboardContainer } from './components/DashboardContainer';
import { QuotesProvider } from './context/QuotesContext';
import { TradeExecutionProvider } from './context/TradeExecutionContext';
// import { GZCShellIntegration } from './components/GZCShellIntegration';
import '@modules/registry'; // This will register all components
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import './components/DropdownFix.css';

// Check if we should use GZC shell mode
const USE_GZC_SHELL = process.env.REACT_APP_USE_GZC_SHELL === 'true' || window.location.search.includes('gzc=true');

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      gcTime: 5 * 60 * 1000, // 5 minutes
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Component to handle routing logic
function AppContent() {
  const location = useLocation();
  const [activeTab, setActiveTab] = useState('admin');
  const [portfolioValue, setPortfolioValue] = useState(2453932.42);
  const [dailyPnL, setDailyPnL] = useState(12497.97);

  // Update activeTab based on URL path
  useEffect(() => {
    const path = location.pathname;
    if (path === '/operations') {
      setActiveTab('operations');
    } else if (path === '/admin') {
      setActiveTab('admin');
    } else if (path === '/trading-dashboard') {
      setActiveTab('trading-dashboard');
    } else if (path === '/risk') {
      setActiveTab('risk');
    } else if (path === '/macro') {
      setActiveTab('macro');
    } else if (path === '/analytics') {
      setActiveTab('analytics');
    } else {
      setActiveTab('admin'); // default
    }
  }, [location.pathname]);

  // Simulate portfolio value updates
  useEffect(() => {
    const interval = setInterval(() => {
      setPortfolioValue(prev => prev + (Math.random() - 0.5) * 1000);
      setDailyPnL(prev => prev + (Math.random() - 0.5) * 100);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ 
      background: theme.background,
      color: theme.text,
      minHeight: '100vh',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <ProfessionalHeader
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        portfolioValue={portfolioValue}
        dailyPnL={dailyPnL}
      />
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <DashboardContainer activeTab={activeTab} />
      </div>
    </div>
  );
}

function App() {
  // Otherwise render our enhanced UI
  return (
    <MsalProvider instance={msalInstance}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeProvider>
            <QuotesProvider>
              <TradeExecutionProvider>
                <AppContent />
              </TradeExecutionProvider>
            </QuotesProvider>
          </ThemeProvider>
        </BrowserRouter>
        <ReactQueryDevtools initialIsOpen={false} />
      </QueryClientProvider>
    </MsalProvider>
  );
}

export default App;