import React, { Suspense } from 'react';
import { ThemeAdapter } from '../adapters/ThemeAdapter';
import { AuthBridge } from '../adapters/AuthBridge';
import { useAuthStore } from '../store/authStore';

// Import GZC contexts and providers
import { ThemeProvider, DateProvider, QuoteProvider } from '../shared/gzc-ui';

/**
 * GZCIntegration Component
 * 
 * This integrates GZC modules into OUR navigation structure
 * We keep our ProfessionalHeader and DashboardContainer
 * But load GZC modules as content within our tabs
 */
export const GZCIntegration: React.FC<{ activeTab: string }> = ({ activeTab }) => {
  const { token } = useAuthStore();

  // Dynamically load GZC modules based on active tab
  const renderGZCModule = () => {
    switch (activeTab) {
      case 'portfolio':
        const Portfolio = React.lazy(() => import('../modules/portfolio-app/Portfolio'));
        return (
          <Suspense fallback={<div>Loading Portfolio Module...</div>}>
            <Portfolio />
          </Suspense>
        );
      
      case 'trading':
        const FxClient = React.lazy(() => import('../modules/fx-client/App'));
        return (
          <Suspense fallback={<div>Loading FX Trading Module...</div>}>
            <FxClient />
          </Suspense>
        );
      
      default:
        return <div>Select a module from the navigation</div>;
    }
  };

  return (
    <ThemeAdapter>
      <AuthBridge msalToken={token}>
        <ThemeProvider>
          <DateProvider>
            <QuoteProvider>
              {/* Render GZC module within our structure */}
              {renderGZCModule()}
            </QuoteProvider>
          </DateProvider>
        </ThemeProvider>
      </AuthBridge>
    </ThemeAdapter>
  );
};

/**
 * Individual module loaders for development
 * These allow testing modules in isolation
 */
export const GZCPortfolioOnly: React.FC = () => {
  const Portfolio = React.lazy(() => import('../modules/portfolio-app/Portfolio'));
  
  return (
    <ThemeAdapter>
      <Suspense fallback={<div>Loading Portfolio Module...</div>}>
        <Portfolio />
      </Suspense>
    </ThemeAdapter>
  );
};

export const GZCFxClientOnly: React.FC = () => {
  const FxClient = React.lazy(() => import('../modules/fx-client/App'));
  
  return (
    <ThemeAdapter>
      <Suspense fallback={<div>Loading FX Client Module...</div>}>
        <FxClient />
      </Suspense>
    </ThemeAdapter>
  );
};