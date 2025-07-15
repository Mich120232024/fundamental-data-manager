//gzc-portfolio-app\src\App.tsx
import React from "react";
import Portfolio from "./Portfolio"; // This should point to your entry Portfolio component
import { QuoteProvider } from "@gzc/ui";
import { DateProvider, DateSelector, useDateContext } from "@gzc/ui"; // Ensure this path is correct
import { ThemeProvider, useTheme } from "@gzc/ui"; // uses fallback if shell not present
import { AuthContext } from "@gzc/ui"; // Ensure this path is correct
console.log("Stand alone AuthContext identity:", AuthContext);
const mockGetToken = async () => {
    console.warn("[Portfolio] Using mock token.");
    return process.env.MOCK_AUTH_TOKEN || "mock-token";
};
const PortfolioWithDateSelector = () => {
    const { currentDate, setCurrentDate } = useDateContext();

    return (
        <div className="space-y-6">
            <DateSelector
                currentDate={currentDate}
                setCurrentDate={setCurrentDate}
            />
            <Portfolio />
        </div>
    );
};
const App = () => {
    return (
        <AuthContext.Provider value={{ getToken: mockGetToken }}>
            <ThemeProvider>
                <DateProvider>
                    <QuoteProvider>
                        <PortfolioWithDateSelector />
                    </QuoteProvider>
                </DateProvider>
            </ThemeProvider>
        </AuthContext.Provider>
    );
};

export default App;
