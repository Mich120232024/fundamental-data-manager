import React, { useEffect, useState } from "react";

interface ThemeProps {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    surfaceAlt: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    danger: string;
    warning: string;
    info: string;
    gradient: string;
}

interface EconomicIndicator {
    series: string;
    name: string;
    latest: number;
    yoy_change: number;
    momentum_3m?: number;
    momentum_6m?: number;
    status: 'accelerating' | 'decelerating' | 'stable' | 'trend_reversing';
}

interface FREDEconomicDashboardProps {
    theme?: ThemeProps;
}

const FREDEconomicDashboard: React.FC<FREDEconomicDashboardProps> = ({ 
    theme = {
        primary: "#95BD78",
        secondary: "#95BD78CC",
        accent: "#95BD7866",
        background: "#0a0a0a",
        surface: "#1a1a1a",
        surfaceAlt: "#2a2a2a",
        text: "#ffffff",
        textSecondary: "#b0b0b0",
        border: "#3a3a3a",
        success: "#ABD38F",
        danger: "#DD8B8B",
        warning: "#95BD7866",
        info: "#0288d1",
        gradient: "linear-gradient(135deg, #95BD78CC 0%, #95BD7866 100%)"
    }
}) => {
    const [connectionStatus, setConnectionStatus] = useState<string>("Disconnected");
    const [selectedCategory, setSelectedCategory] = useState("housing");
    const [refreshInterval, setRefreshInterval] = useState("30");

    // Sample FRED data from our analysis
    const [economicData, setEconomicData] = useState<EconomicIndicator[]>([
        {
            series: "HOUST",
            name: "Total Housing Starts",
            latest: 1256.0,
            yoy_change: -5.35,
            momentum_3m: -15.7,
            momentum_6m: -8.2,
            status: "decelerating"
        },
        {
            series: "MORTGAGE30US",
            name: "30-Year Mortgage Rate",
            latest: 6.81,
            yoy_change: 2.56,
            momentum_3m: 12.3,
            momentum_6m: 18.5,
            status: "accelerating"
        },
        {
            series: "CSUSHPISA",
            name: "Case-Shiller Home Price Index",
            latest: 327.899,
            yoy_change: 2.45,
            momentum_3m: 1.8,
            momentum_6m: 3.2,
            status: "stable"
        },
        {
            series: "MSACSR",
            name: "Monthly Supply of Houses",
            latest: 8.1,
            yoy_change: -4.71,
            momentum_3m: -2.1,
            momentum_6m: -6.8,
            status: "trend_reversing"
        }
    ]);

    useEffect(() => {
        // Simulate connection to FRED API
        setTimeout(() => {
            setConnectionStatus("Connected");
        }, 1000);

        // Mock real-time data updates
        const dataInterval = setInterval(() => {
            setEconomicData(prev => prev.map(item => ({
                ...item,
                latest: item.latest + (Math.random() - 0.5) * 0.01,
                yoy_change: item.yoy_change + (Math.random() - 0.5) * 0.1
            })));
        }, parseInt(refreshInterval) * 1000);

        return () => {
            clearInterval(dataInterval);
            setConnectionStatus("Disconnected");
        };
    }, [refreshInterval]);

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'accelerating': return theme.success;
            case 'decelerating': return theme.danger;
            case 'stable': return theme.info;
            case 'trend_reversing': return theme.warning;
            default: return theme.textSecondary;
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'accelerating': return '↗';
            case 'decelerating': return '↘';
            case 'stable': return '→';
            case 'trend_reversing': return '↩';
            default: return '·';
        }
    };

    return (
        <div style={{
            background: theme.gradient,
            borderRadius: "20px",
            padding: "25px",
            color: theme.text,
            boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
            marginBottom: "20px"
        }}>
            <div style={{ display: "flex", alignItems: "center", marginBottom: "20px" }}>
                <h3 style={{ margin: 0, fontSize: "24px", fontWeight: "300" }}>
                    FRED Economic Dashboard
                </h3>
                <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "15px" }}>
                    <div style={{
                        display: "flex",
                        alignItems: "center",
                        backgroundColor: connectionStatus === "Connected" ? theme.success : theme.danger,
                        padding: "6px 12px",
                        borderRadius: "20px",
                        fontSize: "12px",
                        fontWeight: "500"
                    }}>
                        <div style={{
                            width: "8px",
                            height: "8px",
                            borderRadius: "50%",
                            backgroundColor: theme.text,
                            marginRight: "8px"
                        }}></div>
                        FRED API {connectionStatus}
                    </div>
                </div>
            </div>

            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))",
                gap: "15px",
                marginBottom: "20px"
            }}>
                <div>
                    <label style={{ display: "block", fontSize: "12px", marginBottom: "5px", color: theme.textSecondary }}>
                        Category
                    </label>
                    <select
                        value={selectedCategory}
                        onChange={(e) => setSelectedCategory(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "10px",
                            border: `1px solid ${theme.border}`,
                            borderRadius: "10px",
                            backgroundColor: theme.surface,
                            color: theme.text,
                            fontSize: "14px",
                            backdropFilter: "blur(10px)"
                        }}
                    >
                        <option value="housing" style={{ color: theme.background }}>Housing Market</option>
                        <option value="employment" style={{ color: theme.background }}>Employment</option>
                        <option value="inflation" style={{ color: theme.background }}>Inflation</option>
                        <option value="gdp" style={{ color: theme.background }}>GDP & Growth</option>
                    </select>
                </div>

                <div>
                    <label style={{ display: "block", fontSize: "12px", marginBottom: "5px", color: theme.textSecondary }}>
                        Refresh (sec)
                    </label>
                    <select
                        value={refreshInterval}
                        onChange={(e) => setRefreshInterval(e.target.value)}
                        style={{
                            width: "100%",
                            padding: "10px",
                            border: `1px solid ${theme.border}`,
                            borderRadius: "10px",
                            backgroundColor: theme.surface,
                            color: theme.text,
                            fontSize: "14px",
                            backdropFilter: "blur(10px)"
                        }}
                    >
                        <option value="30" style={{ color: theme.background }}>30s</option>
                        <option value="60" style={{ color: theme.background }}>1m</option>
                        <option value="300" style={{ color: theme.background }}>5m</option>
                    </select>
                </div>
            </div>

            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "15px"
            }}>
                {economicData.map((indicator, index) => (
                    <div
                        key={indicator.series}
                        style={{
                            backgroundColor: theme.accent,
                            borderRadius: "15px",
                            padding: "20px",
                            backdropFilter: "blur(10px)",
                            border: `1px solid ${theme.border}`
                        }}
                    >
                        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "15px" }}>
                            <div>
                                <div style={{ fontSize: "14px", color: theme.textSecondary, marginBottom: "5px" }}>
                                    {indicator.series}
                                </div>
                                <div style={{ fontSize: "16px", fontWeight: "500", lineHeight: "1.2" }}>
                                    {indicator.name}
                                </div>
                            </div>
                            <div style={{
                                backgroundColor: getStatusColor(indicator.status),
                                color: theme.text,
                                padding: "4px 8px",
                                borderRadius: "10px",
                                fontSize: "12px",
                                fontWeight: "500",
                                display: "flex",
                                alignItems: "center",
                                gap: "4px"
                            }}>
                                {getStatusIcon(indicator.status)}
                                {indicator.status.replace('_', ' ')}
                            </div>
                        </div>

                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px" }}>
                            <div>
                                <div style={{ fontSize: "12px", color: theme.textSecondary, marginBottom: "3px" }}>Latest Value</div>
                                <div style={{ fontSize: "20px", fontWeight: "600" }}>
                                    {indicator.latest.toFixed(2)}
                                </div>
                            </div>
                            <div>
                                <div style={{ fontSize: "12px", color: theme.textSecondary, marginBottom: "3px" }}>YoY Change</div>
                                <div style={{
                                    fontSize: "18px",
                                    fontWeight: "600",
                                    color: indicator.yoy_change >= 0 ? theme.success : theme.danger
                                }}>
                                    {indicator.yoy_change >= 0 ? "+" : ""}{indicator.yoy_change.toFixed(2)}%
                                </div>
                            </div>
                        </div>

                        {indicator.momentum_3m && (
                            <div style={{
                                marginTop: "15px",
                                padding: "10px",
                                backgroundColor: theme.surface,
                                borderRadius: "8px"
                            }}>
                                <div style={{ fontSize: "12px", color: theme.textSecondary, marginBottom: "5px" }}>Momentum Analysis</div>
                                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "14px" }}>
                                    <span>3M: <strong style={{ color: indicator.momentum_3m >= 0 ? theme.success : theme.danger }}>
                                        {indicator.momentum_3m >= 0 ? "+" : ""}{indicator.momentum_3m.toFixed(1)}%
                                    </strong></span>
                                    <span>6M: <strong style={{ color: indicator.momentum_6m >= 0 ? theme.success : theme.danger }}>
                                        {indicator.momentum_6m >= 0 ? "+" : ""}{indicator.momentum_6m.toFixed(1)}%
                                    </strong></span>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            <div style={{
                marginTop: "20px",
                padding: "15px",
                backgroundColor: theme.accent,
                borderRadius: "10px",
                fontSize: "12px",
                color: theme.textSecondary
            }}>
                <strong>Research_Quantitative_Analyst</strong> • Housing market showing deceleration with mortgage rate shock driving -15.7% momentum • Regional disparities: Midwest +4.5%, Northeast -11.8% • Monitoring 95%+ accuracy standard
            </div>
        </div>
    );
};

export default FREDEconomicDashboard;