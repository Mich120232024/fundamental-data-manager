import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { theme } from '../theme';
import OrderManagement from './OrderManagement';
import TradeExecutions_Styled from './TradeExecutions_Styled';
import { AnalyticsDashboardExample } from './analytics/AnalyticsDashboardExample';
import { useViewMemory } from '../hooks/useViewMemory';
import { GZCIntegration } from './GZCIntegration';
import { GZCPortfolioComponent } from './GZCPortfolioComponent';
import { FXPositionsComponent } from './FXPositionsComponent';

// Check if GZC modules are enabled
const USE_GZC_MODULES = window.location.search.includes('gzc-modules=true');

const ResponsiveGridLayout = WidthProvider(Responsive);

interface DashboardContainerProps {
    activeTab: string;
}

export const DashboardContainer: React.FC<DashboardContainerProps> = ({ activeTab }) => {
    const { saveLayout, getLayout } = useViewMemory();
    const [layouts, setLayouts] = useState<any>({});
    const [activeRiskTab, setActiveRiskTab] = useState("VaR");

    // Load saved layout for current tab
    useEffect(() => {
        const savedLayout = getLayout(activeTab);
        if (savedLayout) {
            setLayouts((prev: any) => ({ ...prev, [activeTab]: savedLayout }));
        }
    }, [activeTab, getLayout]);

    // Default layouts for dashboard - matching reference
    const defaultLayouts = {
        lg: [
            { i: "ai-insights", x: 0, y: 0, w: 4, h: 6, minW: 3, minH: 3 },
            { i: "orders", x: 4, y: 0, w: 4, h: 6, minW: 3, minH: 3 },
            { i: "executions", x: 8, y: 0, w: 4, h: 6, minW: 3, minH: 3 },
            { i: "rfs-quotes", x: 0, y: 6, w: 6, h: 4, minW: 4, minH: 3 },
            { i: "esp-quotes", x: 6, y: 6, w: 6, h: 4, minW: 4, minH: 3 }
        ],
        md: [
            { i: "ai-insights", x: 0, y: 0, w: 5, h: 4 },
            { i: "orders", x: 5, y: 0, w: 5, h: 4 },
            { i: "executions", x: 0, y: 4, w: 10, h: 3 },
            { i: "rfs-quotes", x: 0, y: 7, w: 5, h: 3 },
            { i: "esp-quotes", x: 5, y: 7, w: 5, h: 3 }
        ],
        sm: [
            { i: "ai-insights", x: 0, y: 0, w: 6, h: 3 },
            { i: "orders", x: 0, y: 3, w: 6, h: 3 },
            { i: "executions", x: 0, y: 6, w: 6, h: 3 },
            { i: "rfs-quotes", x: 0, y: 9, w: 6, h: 3 },
            { i: "esp-quotes", x: 0, y: 12, w: 6, h: 3 }
        ]
    };

    // Widget components
    const widgets: Record<string, React.ReactNode> = {
        "ai-insights": (
            <div 
                key="ai-insights"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        AI TRADING INSIGHTS
                    </div>
                    <motion.div
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        style={{
                            width: "8px",
                            height: "8px",
                            borderRadius: "50%",
                            backgroundColor: theme.success
                        }}
                    />
                </div>
                <div style={{ padding: '16px' }}>
                    <div style={{
                        background: theme.surfaceAlt,
                        borderRadius: "8px",
                        padding: "12px",
                        marginBottom: "12px",
                        border: `1px solid ${theme.border}`,
                        position: "relative",
                        overflow: "hidden"
                    }}>
                        <div style={{ fontSize: "9px", color: theme.textSecondary, marginBottom: "8px" }}>
                            LSTM Model Output (98.2% Accuracy)
                        </div>
                        <div style={{ fontSize: "11px", color: theme.text }}>
                            <span style={{ color: theme.warning }}>⚠️</span> Regime change detected in 
                            <span style={{ color: theme.primary, fontWeight: "600" }}> EUR/USD</span>
                        </div>
                        <div style={{ fontSize: "10px", color: theme.textSecondary, marginTop: "4px" }}>
                            Volatility expected to increase by 34% in next 24h
                        </div>
                    </div>
                </div>
            </div>
        ),
        "orders": (
            <div
                key="orders"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        ORDER MANAGEMENT
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                        <motion.div
                            animate={{ 
                                backgroundColor: theme.success
                            }}
                            style={{
                                width: "8px",
                                height: "8px",
                                borderRadius: "50%"
                            }}
                        />
                        <span style={{ fontSize: "10px", color: theme.textSecondary }}>Live</span>
                    </div>
                </div>
                <div style={{ padding: '16px', height: 'calc(100% - 60px)', overflow: 'auto' }}>
                    <OrderManagement />
                </div>
            </div>
        ),
        "executions": (
            <div
                key="executions"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        TRADE EXECUTIONS
                    </div>
                    <motion.button
                        className="no-drag"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        style={{
                            background: `${theme.headerColor}66`,
                            color: theme.text,
                            border: `1px solid ${theme.headerColor}40`,
                            borderRadius: "4px",
                            padding: "4px 16px",
                            fontSize: "11px",
                            cursor: "pointer",
                            fontWeight: "400",
                            transition: "all 0.2s ease",
                            opacity: 0.85
                        }}
                    >
                        Export CSV
                    </motion.button>
                </div>
                <div style={{ padding: "12px", height: "calc(100% - 60px)", overflow: "auto" }}>
                    <TradeExecutions_Styled />
                </div>
            </div>
        ),
        "market-data": (
            <div
                key="market-data"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        MARKET DATA
                    </div>
                    <motion.div
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        style={{
                            width: "8px",
                            height: "8px",
                            borderRadius: "50%",
                            backgroundColor: theme.info
                        }}
                    />
                </div>
                <div style={{ padding: '16px' }}>
                    <div style={{ color: theme.textSecondary, fontSize: "11px" }}>
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                        >
                            EUR/USD: 1.0852 <span style={{ color: theme.success }}>+0.12%</span>
                        </motion.div>
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                        >
                            GBP/USD: 1.2156 <span style={{ color: theme.danger }}>-0.08%</span>
                        </motion.div>
                    </div>
                </div>
            </div>
        ),
        "portfolio-overview": (
            <div
                key="portfolio-overview"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        PORTFOLIO OVERVIEW
                    </div>
                </div>
                <div style={{ padding: '16px' }}>
                    <div style={{ color: theme.textSecondary, fontSize: "12px" }}>
                        Portfolio performance metrics...
                    </div>
                </div>
            </div>
        ),
        "risk-metrics": (
            <div
                key="risk-metrics"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        RISK METRICS
                    </div>
                    <div style={{
                        display: "flex",
                        gap: "8px"
                    }}>
                        {["VaR", "Greeks", "Exposure", "Correlations", "Stress Test"].map((tab) => (
                            <motion.button
                                key={tab}
                                className="no-drag"
                                whileHover={{ y: -2 }}
                                whileTap={{ scale: 0.95 }}
                                onClick={() => setActiveRiskTab(tab)}
                                style={{
                                    background: activeRiskTab === tab ? `${theme.primary}20` : "transparent",
                                    color: activeRiskTab === tab ? theme.primary : theme.textSecondary,
                                    border: "none",
                                    padding: "4px 10px",
                                    fontSize: "10px",
                                    fontWeight: "400",
                                    borderRadius: "6px",
                                    cursor: "pointer",
                                    transition: "all 0.2s ease"
                                }}
                            >
                                {tab}
                            </motion.button>
                        ))}
                    </div>
                </div>
                <div style={{ padding: '16px' }}>
                    {activeRiskTab === "VaR" && (
                        <div style={{ color: theme.textSecondary, fontSize: "12px" }}>
                            VaR metrics content...
                        </div>
                    )}
                    {activeRiskTab === "Greeks" && (
                        <div style={{ color: theme.textSecondary, fontSize: "12px" }}>
                            Greeks content...
                        </div>
                    )}
                </div>
            </div>
        ),
        "trade-history": (
            <div
                key="trade-history"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        TRADE HISTORY
                    </div>
                </div>
                <div style={{ padding: '16px' }}>
                    <div style={{ color: theme.textSecondary, fontSize: "12px" }}>
                        Recent trade executions...
                    </div>
                </div>
            </div>
        ),
        "rfs-quotes": (
            <div
                key="rfs-quotes"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        RFS STREAMING
                    </div>
                    <motion.div
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                        }}
                    >
                        <div style={{
                            width: "8px",
                            height: "8px",
                            backgroundColor: theme.success,
                            borderRadius: "50%"
                        }} />
                        <span style={{ fontSize: "11px", color: theme.textSecondary }}>Live</span>
                    </motion.div>
                </div>
                <div style={{ padding: '16px' }}>
                    <div style={{ color: theme.textSecondary, fontSize: "12px", textAlign: "center" }}>
                        RFS Quotes Component
                    </div>
                </div>
            </div>
        ),
        "esp-quotes": (
            <div
                key="esp-quotes"
                style={{
                    background: theme.surface,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '8px',
                    overflow: 'hidden',
                    height: '100%'
                }}
            >
                <div style={{
                    background: theme.surfaceAlt,
                    padding: '12px 16px',
                    borderBottom: `1px solid ${theme.border}`,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}>
                    <div style={{ fontSize: '11px', fontWeight: '500', color: theme.text }}>
                        ESP STREAMING
                    </div>
                    <motion.div
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                        style={{
                            display: "flex",
                            alignItems: "center",
                            gap: "6px"
                        }}
                    >
                        <div style={{
                            width: "8px",
                            height: "8px",
                            backgroundColor: theme.info,
                            borderRadius: "50%"
                        }} />
                        <span style={{ fontSize: "11px", color: theme.textSecondary }}>Connected</span>
                    </motion.div>
                </div>
                <div style={{ padding: '16px' }}>
                    <div style={{ color: theme.textSecondary, fontSize: "12px", textAlign: "center" }}>
                        ESP Quotes Component
                    </div>
                </div>
            </div>
        ),
        "gzc-portfolio": (
            <GZCPortfolioComponent key="gzc-portfolio" />
        ),
        "fx-positions": (
            <FXPositionsComponent key="fx-positions" />
        )
    };

    // Different layouts for different tabs
    const getLayoutForTab = () => {
        switch (activeTab) {
            case 'trading-dashboard':
                return defaultLayouts;
            case 'risk':
                return {
                    lg: [
                        { i: "risk-metrics", x: 0, y: 0, w: 12, h: 10 },
                        { i: "market-data", x: 0, y: 10, w: 12, h: 6 }
                    ]
                };
            case 'macro':
                return {
                    lg: [
                        { i: "market-data", x: 0, y: 0, w: 12, h: 8 },
                        { i: "ai-insights", x: 0, y: 8, w: 12, h: 8 }
                    ]
                };
            case 'operations':
                return {
                    lg: [
                        { i: "orders", x: 0, y: 0, w: 6, h: 8 },
                        { i: "executions", x: 6, y: 0, w: 6, h: 8 },
                        { i: "rfs-quotes", x: 0, y: 8, w: 6, h: 8 },
                        { i: "esp-quotes", x: 6, y: 8, w: 6, h: 8 }
                    ]
                };
            case 'admin':
                return {
                    lg: [
                        { i: "gzc-portfolio", x: 0, y: 0, w: 12, h: 16 }
                    ]
                };
            default:
                return defaultLayouts;
        }
    };

    const currentLayout = getLayoutForTab();

    // Show analytics demo when on analytics tab
    if (activeTab === 'analytics') {
        return <AnalyticsDashboardExample />;
    }

    // Show the original trading dashboard with grid layout
    if (activeTab === 'trading-dashboard') {
        return (
            <div style={{ padding: "6px", height: "calc(100vh - 76px)", background: theme.background }}>
                <ResponsiveGridLayout
                    className="layout"
                    layouts={layouts[activeTab] || defaultLayouts}
                    onLayoutChange={(_layout: any, layouts: any) => {
                        setLayouts((prev: any) => ({ ...prev, [activeTab]: layouts }));
                        saveLayout(activeTab, layouts);
                    }}
                    breakpoints={{ lg: 1200, md: 996, sm: 768 }}
                    cols={{ lg: 12, md: 10, sm: 6 }}
                    rowHeight={60}
                    margin={[6, 6]}
                    isDraggable={true}
                    isResizable={true}
                    compactType="vertical"
                    preventCollision={false}
                >
                    {(currentLayout.lg || []).map((layoutItem: any) => {
                        const widget = widgets[layoutItem.i];
                        return widget ? (
                            <div key={layoutItem.i}>
                                <AnimatePresence mode="wait">
                                    {widget}
                                </AnimatePresence>
                            </div>
                        ) : null;
                    })}
                </ResponsiveGridLayout>
            </div>
        );
    }

    // GZC modules integration commented out for stability
    // if (USE_GZC_MODULES && (activeTab === 'portfolio' || activeTab === 'trading')) {
    //     return (
    //         <div style={{ padding: "20px", height: "calc(100vh - 76px)", background: theme.background }}>
    //             <GZCIntegration activeTab={activeTab} />
    //         </div>
    //     );
    // }

    return (
        <div style={{ padding: "6px", height: "calc(100vh - 76px)", background: theme.background }}>
            <ResponsiveGridLayout
                className="layout"
                layouts={layouts[activeTab] || currentLayout}
                onLayoutChange={(_layout: any, layouts: any) => {
                    setLayouts((prev: any) => ({ ...prev, [activeTab]: layouts }));
                    saveLayout(activeTab, layouts);
                }}
                breakpoints={{ lg: 1200, md: 996, sm: 768 }}
                cols={{ lg: 12, md: 10, sm: 6 }}
                rowHeight={60}
                margin={[6, 6]}
                containerPadding={[0, 0]}
                isDraggable={true}
                isResizable={true}
                draggableCancel=".no-drag"
                compactType="vertical"
                preventCollision={false}
            >
                {(currentLayout.lg || []).map((layoutItem: any) => {
                    const widget = widgets[layoutItem.i];
                    return widget ? (
                        <div key={layoutItem.i}>
                            <AnimatePresence mode="wait">
                                {widget}
                            </AnimatePresence>
                        </div>
                    ) : null;
                })}
            </ResponsiveGridLayout>
        </div>
    );
};