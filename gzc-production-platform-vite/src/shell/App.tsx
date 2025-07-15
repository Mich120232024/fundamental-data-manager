// gzc-main-shell/src/App.tsx
import React, { Suspense, useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { MsalProvider } from "@azure/msal-react";
import { msalInstance } from "./components/auth/msalConfig";
import { AuthContext } from "@gzc/ui"; // ✅ Moved to gzc-ui shared lib
import { ThemeProvider, DateProvider, QuoteProvider } from "@gzc/ui";
import Header from "./components/layout/Header";
import Sidebar from "./components/layout/Sidebar";
import PageSelector from "./components/layout/PageSelector";
import useAuthToken from "./hooks/useAuthToken";
import Portfolio from "gzc_portfolio_app/Portfolio"; // ✅ Direct import from federated module

// ✅ Wrapped App to wait for MSAL to be ready and handle login if needed
const MsalReadyApp = () => {
    const [ready, setReady] = useState(false); // ✅ State for MSAL readiness
    const [checking, setChecking] = useState(true); // ✅ Internal loading state
    const { getToken } = useAuthToken();

    useEffect(() => {
        const waitForMsalInitAndLogin = async () => {
            try {
                await msalInstance.initialize(); // ✅ Ensure MSAL is initialized

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

                    console.warn(
                        "[MSAL] ❌ No logged-in user found. Triggering login."
                    );
                    await msalInstance.loginRedirect(); // ✅ Enforce login only when needed
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

    if (checking || !ready) return <div>⏳ Waiting for MSAL login...</div>; // ✅ Loading UI

    return (
        <AuthContext.Provider value={{ getToken }}>
            <ThemeProvider>
                <DateProvider>
                    <Router>
                        <div className="min-h-screen bg-gzc-white dark:bg-gzc-black grid grid-cols-[240px_1fr] grid-rows-[60px_1fr]">
                            <Header />
                            <Sidebar />
                            <main className="col-span-1 row-span-1 p-6">
                                <PageSelector />
                                <Routes>
                                    <Route
                                        path="/portfolio"
                                        element={
                                            <Suspense
                                                fallback={
                                                    <div>
                                                        Loading Portfolio...
                                                    </div>
                                                }
                                            >
                                                <QuoteProvider>
                                                    <Portfolio />
                                                </QuoteProvider>
                                            </Suspense>
                                        }
                                    />
                                </Routes>
                            </main>
                        </div>
                    </Router>
                </DateProvider>
            </ThemeProvider>
        </AuthContext.Provider>
    );
};

// ✅ Entry export wrapped with MsalProvider
const App = () => (
    <MsalProvider instance={msalInstance}>
        <MsalReadyApp />
    </MsalProvider>
);

export default App;
