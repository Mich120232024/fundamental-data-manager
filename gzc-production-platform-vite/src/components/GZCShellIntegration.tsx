import React, { Suspense, useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MsalProvider } from '@azure/msal-react';
import { msalInstance } from '../shell/components/auth/msalConfig';
import { AuthContext, ThemeProvider, DateProvider, QuoteProvider } from '../shared/gzc-ui';
import { ThemeAdapter } from '../adapters/ThemeAdapter';
import { ProfessionalHeader } from './ProfessionalHeader';
import useAuthToken from '../shell/hooks/useAuthToken';

// Use our local portfolio component directly
const Portfolio = React.lazy(() => import('../modules/portfolio-app/Portfolio'));
const FxClient = React.lazy(() => import('../modules/fx-client/App'));

/**
 * GZCShellIntegration - Complete GZC shell with our navigation
 * 
 * This preserves:
 * - ALL GZC authentication flow (MSAL)
 * - ALL Module Federation architecture
 * - ALL WebSocket connections
 * - ALL backend integration
 * 
 * But replaces:
 * - Their static navigation with our ProfessionalHeader
 * - Their layout with our flexible dashboard
 */
const MsalReadyApp = () => {
    const [ready, setReady] = useState(false);
    const [checking, setChecking] = useState(true);
    const [activeTab, setActiveTab] = useState('portfolio');
    const [portfolioValue, setPortfolioValue] = useState(2453932.42);
    const [dailyPnL, setDailyPnL] = useState(12497.97);
    const { getToken } = useAuthToken();

    // GZC's exact MSAL initialization logic
    useEffect(() => {
        const waitForMsalInitAndLogin = async () => {
            try {
                await msalInstance.initialize();

                const pollAccounts = async (retries = 10, delay = 300) => {
                    for (let i = 0; i < retries; i++) {
                        const accounts = msalInstance.getAllAccounts();
                        if (accounts.length > 0) {
                            console.log("[MSAL] ✅ Logged in user detected.");
                            setReady(true);
                            return;
                        }
                        await new Promise((res) => setTimeout(res, delay));
                    }

                    console.warn("[MSAL] ❌ No logged-in user found. Triggering login.");
                    await msalInstance.loginRedirect();
                };

                await pollAccounts();
            } catch (err) {
                console.error("[MSAL Initialization Error]", err);
            } finally {
                setChecking(false);
            }
        };

        waitForMsalInitAndLogin();
    }, []);

    if (checking || !ready) {
        return (
            <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center', 
                height: '100vh' 
            }}>
                <div>⏳ Waiting for MSAL login...</div>
            </div>
        );
    }

    return (
        <AuthContext.Provider value={{ getToken }}>
            <ThemeAdapter>
                <ThemeProvider>
                    <DateProvider>
                        <Router>
                            <div style={{ 
                                minHeight: '100vh', 
                                display: 'flex', 
                                flexDirection: 'column',
                                background: 'var(--gzc-background)'
                            }}>
                                {/* Our navigation instead of GZC's */}
                                <ProfessionalHeader
                                    activeTab={activeTab}
                                    setActiveTab={setActiveTab}
                                    portfolioValue={portfolioValue}
                                    dailyPnL={dailyPnL}
                                />
                                
                                {/* Dynamic content based on our navigation */}
                                <main style={{ flex: 1, padding: '20px' }}>
                                    <Suspense fallback={<div>Loading module...</div>}>
                                        <QuoteProvider>
                                            {activeTab === 'portfolio' && (
                                                <Portfolio />
                                            )}
                                            {activeTab === 'trading' && (
                                                <FxClient />
                                            )}
                                            {activeTab === 'analytics' && (
                                                <div>Analytics module (can be GZC or ours)</div>
                                            )}
                                            {activeTab === 'risk' && (
                                                <div>Risk module (can be GZC or ours)</div>
                                            )}
                                        </QuoteProvider>
                                    </Suspense>
                                </main>
                            </div>
                        </Router>
                    </DateProvider>
                </ThemeProvider>
            </ThemeAdapter>
        </AuthContext.Provider>
    );
};

export const GZCShellIntegration = () => (
    <MsalProvider instance={msalInstance}>
        <MsalReadyApp />
    </MsalProvider>
);