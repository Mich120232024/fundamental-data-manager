// src/components/TradeExecutions_Styled.tsx
import React from "react";
import { useTradeExecutions } from "../context/TradeExecutionContext";
import { motion } from "framer-motion";
import { theme } from "../theme";

const TradeExecutions_Styled: React.FC = () => {
    const { executions } = useTradeExecutions();

    return (
        <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
            <h3 style={{ 
                fontSize: "12px", 
                fontWeight: "500", 
                color: theme.text,
                margin: "0 0 12px 0"
            }}>
                Trade Executions
            </h3>
            
            <div style={{ 
                flex: 1,
                overflowY: "auto",
                overflowX: "hidden"
            }}>
                <div style={{
                    display: "grid",
                    gridTemplateColumns: "1fr 0.8fr 0.5fr 0.8fr 0.8fr 0.8fr",
                    gap: "4px",
                    padding: "8px",
                    background: theme.surfaceAlt,
                    borderRadius: "6px",
                    marginBottom: "6px",
                    fontSize: "10px",
                    fontWeight: "600",
                    textTransform: "uppercase",
                    color: theme.textSecondary,
                    letterSpacing: "0.5px"
                }}>
                    <div>Order ID</div>
                    <div>Symbol</div>
                    <div>Side</div>
                    <div>Price</div>
                    <div>Qty</div>
                    <div>Status</div>
                </div>

                {executions.map((execution, index) => (
                    <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        whileHover={{ backgroundColor: `${theme.primary}10` }}
                        style={{
                            display: "grid",
                            gridTemplateColumns: "1fr 0.8fr 0.5fr 0.8fr 0.8fr 0.8fr",
                            gap: "4px",
                            padding: "10px 8px",
                            borderBottom: `1px solid ${theme.border}`,
                            fontSize: "11px",
                            cursor: "pointer",
                            transition: "background-color 0.2s ease"
                        }}
                    >
                        <div style={{ 
                            color: theme.text,
                            fontFamily: "monospace",
                            fontSize: "10px"
                        }}>
                            {execution.order_id.substring(0, 8)}...
                        </div>
                        <div style={{ 
                            color: theme.text,
                            fontWeight: "500"
                        }}>
                            {execution.symbol}
                        </div>
                        <div style={{ 
                            color: execution.side === "1" ? theme.success : theme.danger,
                            fontWeight: "600"
                        }}>
                            {execution.side === "1" ? "BUY" : "SELL"}
                        </div>
                        <div style={{ 
                            color: theme.text,
                            fontFamily: "monospace"
                        }}>
                            {execution.price}
                        </div>
                        <div style={{ 
                            color: theme.text,
                            fontFamily: "monospace"
                        }}>
                            {Number(execution.quantity).toLocaleString()}
                        </div>
                        <div style={{ 
                            display: "flex",
                            justifyContent: "center"
                        }}>
                            <span style={{ 
                                fontSize: "10px",
                                padding: "2px 8px",
                                borderRadius: "3px",
                                background: execution.ord_status === "2" ? `${theme.success}20` : `${theme.warning}20`,
                                color: execution.ord_status === "2" ? theme.success : theme.warning,
                                fontWeight: "500",
                                display: "inline-block"
                            }}>
                                {execution.ord_status === "2" ? "FILLED" : "PENDING"}
                            </span>
                        </div>
                    </motion.div>
                ))}

                {executions.length === 0 && (
                    <div style={{
                        textAlign: "center",
                        padding: "40px",
                        color: theme.textSecondary,
                        fontSize: "12px"
                    }}>
                        No executions yet
                    </div>
                )}
            </div>
        </div>
    );
};

export default TradeExecutions_Styled;