import { useState, useEffect } from "react";
import { Card, CardContent } from "@gzc/ui";

interface PortfolioMetricsProps {
    isConnected: boolean;
}

const PortfolioMetrics = ({ isConnected }: PortfolioMetricsProps) => {
    const [connectionStatus, setConnectionStatus] = useState("Disconnected");

    useEffect(() => {
        setConnectionStatus(isConnected ? "Connected" : "Disconnected");
    }, [isConnected]);

    return (
        <Card className="mb-4">
            <CardContent className="flex flex-col gap-2 p-4">
                <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold">Metrics</h2>
                    <div
                        className={`text-sm font-medium px-3 py-1 rounded-full border ${
                            isConnected
                                ? "text-lime-400 border-lime-400"
                                : "text-red-500 border-red-500"
                        }`}
                    >
                        {connectionStatus}
                    </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div className="text-sm">
                        <span className="block text-muted-foreground">
                            Total Exposure
                        </span>
                        <span className="font-bold">$45.3M</span>
                    </div>
                    <div className="text-sm">
                        <span className="block text-muted-foreground">
                            Net P&L
                        </span>
                        <span className="font-bold text-lime-400">+$1.8M</span>
                    </div>
                    <div className="text-sm">
                        <span className="block text-muted-foreground">
                            Open Trades
                        </span>
                        <span className="font-bold">24</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default PortfolioMetrics;
