// gzc-portfolio-app\src\Portfolio.tsx
import React, { useState, useEffect } from "react";
import PortfolioMetrics from "./components/PortfolioMetrics";
import PortfolioFilters from "./components/PortfolioFilters";
import PortfolioTable from "./components/PortfolioTable";
import BlotterTable from "./components/BlotterTable";
import { PortfolioFilter } from "./types/portfolio";
import { useQuoteStream } from "./hooks/useQuoteStream";
import { useQuoteContext } from "@gzc/ui";
import { useAuthContext, AuthContext } from "@gzc/ui";

console.log("[Portfolio] 📦 AuthContext identity:", AuthContext);
console.log(
    "[Portfolio] 📦 process.env.SHELL_CONTEXT:",
    process.env.SHELL_CONTEXT
);

// You can verify if useAuthContext is working correctly by checking identity
const Portfolio = () => {
    const contextValue = useAuthContext();
    const { getToken } = contextValue;

    const { updateQuote } = useQuoteContext();

    useEffect(() => {
        console.log(
            "[Portfolio] 🔐 useAuthContext -> getToken identity:",
            getToken
        );
        console.log(
            "[Portfolio] 🔐 useAuthContext context value:",
            contextValue
        );
    }, [getToken, contextValue]);

    useQuoteStream("esp", updateQuote, true, getToken);

    const [filters, setFilters] = useState<PortfolioFilter>({
        symbol: "",
        fundId: undefined,
        trader: "",
        position: "",
    });

    return (
        <div className="min-h-screen bg-white text-black dark:bg-black dark:text-white p-4">
            <PortfolioMetrics isConnected={true} />
            <PortfolioFilters filters={filters} onFilterChange={setFilters} />
            <PortfolioTable filters={filters} />
            <BlotterTable />
        </div>
    );
};

export default Portfolio;
