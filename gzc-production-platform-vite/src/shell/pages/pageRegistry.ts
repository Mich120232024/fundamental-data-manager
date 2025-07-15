import React from "react";
console.log("ShellContext from global in global:", process.env.SHELL_CONTEXT);
export const pageRegistry = [
    {
        name: "Portfolio",
        path: "/portfolio",
        component: React.lazy(() => import("gzc_portfolio_app/Portfolio")),
        shellOnly: false,
        withQuoteProvider: true,
    },
];
