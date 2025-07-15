// src/context/TradeExecutionContext.tsx
import React, { createContext, useContext, useState, useEffect } from "react";

interface ExecutionResult {
  order_id: string;
  cl_ord_id: string;
  exec_type: string;
  ord_status: string;
  symbol: string;
  side: string;
  price: string;
  quantity: string;
  last_price: string;
  last_quantity: string;
  session_type: string;
}

// Mock data
const mockExecutions: ExecutionResult[] = [
  {
    order_id: "ORD_001",
    cl_ord_id: "CLIENT_001",
    exec_type: "F",
    ord_status: "2",
    symbol: "EUR/USD",
    side: "1",
    price: "1.0845",
    quantity: "1000000",
    last_price: "1.0845",
    last_quantity: "1000000",
    session_type: "ESP"
  }
];

// Define context type
interface TradeExecutionContextType {
  executions: ExecutionResult[];
  addExecution: (execution: ExecutionResult) => void;
}

// Create context
const TradeExecutionContext = createContext<TradeExecutionContextType | undefined>(undefined);

// Context Provider Component
export const TradeExecutionProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [executions, setExecutions] = useState<ExecutionResult[]>(mockExecutions);

  const addExecution = (execution: ExecutionResult) => {
    setExecutions(prev => [execution, ...prev]);
  };

  // Simulate receiving new executions
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly add a new execution
      if (Math.random() > 0.8) {
        const newExecution: ExecutionResult = {
          order_id: `ORD_${Date.now()}`,
          cl_ord_id: `CLIENT_${Date.now()}`,
          exec_type: "F",
          ord_status: "2",
          symbol: Math.random() > 0.5 ? "EUR/USD" : "USD/JPY",
          side: Math.random() > 0.5 ? "1" : "2",
          price: (1.0845 + (Math.random() - 0.5) * 0.01).toFixed(4),
          quantity: "1000000",
          last_price: (1.0845 + (Math.random() - 0.5) * 0.01).toFixed(4),
          last_quantity: "1000000",
          session_type: Math.random() > 0.5 ? "ESP" : "RFS"
        };
        setExecutions(prev => [newExecution, ...prev]);
      }
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <TradeExecutionContext.Provider value={{ executions, addExecution }}>
      {children}
    </TradeExecutionContext.Provider>
  );
};

// Custom hook to use execution context
export const useTradeExecutions = () => {
  const context = useContext(TradeExecutionContext);
  if (!context) {
    throw new Error("useTradeExecutions must be used within a TradeExecutionProvider");
  }
  return context;
};