import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { theme } from '../../theme';
import OrderManagement from '../../components/OrderManagement';

interface Order {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  status: 'PENDING' | 'FILLED' | 'CANCELLED';
  timestamp: string;
}

// EXACT styles from WebSocketRFS_Styled.tsx - matching your week of design work
const selectStyle = {
  background: theme.surface,
  border: `1px solid ${theme.border}`,
  borderRadius: "6px",
  padding: "6px 10px",
  color: theme.text,
  fontSize: "11px",
  cursor: "pointer",
  minWidth: "100px"
};

const labelStyle = {
  fontSize: "10px",
  color: theme.textSecondary,
  fontWeight: "600",
  textTransform: "uppercase" as const,
  letterSpacing: "0.5px"
};

const tableStyle = {
  width: '100%',
  fontSize: '11px',
  borderCollapse: 'collapse' as const
};

const headerCellStyle = {
  padding: '8px 12px',
  textAlign: 'left' as const,
  borderBottom: `1px solid ${theme.border}`,
  background: theme.surfaceAlt,
  color: theme.textSecondary,
  fontWeight: '600' as const,
  fontSize: '10px',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px'
};

const cellStyle = {
  padding: '8px 12px',
  borderBottom: `1px solid ${theme.border}`,
  color: theme.text,
  fontSize: '11px'
};

export const TradingOperationsView: React.FC = () => {
  const [orders] = useState<Order[]>([
    { id: '1', symbol: 'EUR/USD', side: 'BUY', quantity: 100000, price: 1.0850, status: 'PENDING', timestamp: '10:30:15' },
    { id: '2', symbol: 'GBP/USD', side: 'SELL', quantity: 50000, price: 1.2150, status: 'FILLED', timestamp: '10:25:42' },
    { id: '3', symbol: 'USD/JPY', side: 'BUY', quantity: 75000, price: 149.85, status: 'PENDING', timestamp: '10:28:33' },
    { id: '4', symbol: 'AUD/USD', side: 'SELL', quantity: 200000, price: 0.6515, status: 'FILLED', timestamp: '10:32:18' },
    { id: '5', symbol: 'NZD/USD', side: 'BUY', quantity: 150000, price: 0.5875, status: 'CANCELLED', timestamp: '10:35:22' },
  ]);

  // EXACT button style from WebSocketRFS_Styled.tsx
  const buttonStyle = {
    background: `${theme.primary}66`, // More transparent primary color
    border: `1px solid ${theme.primary}40`,
    borderRadius: "4px",
    padding: "8px 16px",
    color: theme.text,
    fontWeight: "500",
    fontSize: "12px",
    cursor: "pointer",
    transition: "all 0.2s ease"
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', padding: '16px', gap: '20px' }}>
      {/* EXACT Order Management Component from your fx-client */}
      <OrderManagement />

      {/* Orders Table */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <th style={headerCellStyle}>Symbol</th>
              <th style={headerCellStyle}>Side</th>
              <th style={{...headerCellStyle, textAlign: 'right'}}>Qty</th>
              <th style={{...headerCellStyle, textAlign: 'right'}}>Price</th>
              <th style={headerCellStyle}>Status</th>
              <th style={headerCellStyle}>Time</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order, index) => (
              <motion.tr
                key={order.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                style={{
                  background: 'transparent',
                  transition: 'background 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = theme.surfaceAlt;
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                }}
              >
                <td style={{...cellStyle, fontWeight: '500'}}>{order.symbol}</td>
                <td style={{
                  ...cellStyle, 
                  fontWeight: '500',
                  color: order.side === 'BUY' ? theme.success : theme.danger
                }}>
                  {order.side}
                </td>
                <td style={{...cellStyle, textAlign: 'right'}}>{order.quantity.toLocaleString()}</td>
                <td style={{...cellStyle, textAlign: 'right'}}>{order.price.toFixed(4)}</td>
                <td style={cellStyle}>
                  <span style={{
                    padding: '2px 6px',
                    borderRadius: '3px',
                    fontSize: '9px',
                    fontWeight: '600',
                    textTransform: 'uppercase' as const,
                    letterSpacing: '0.5px',
                    background: order.status === 'FILLED' ? `${theme.success}22` : 
                               order.status === 'PENDING' ? `${theme.warning}22` : 
                               `${theme.danger}22`,
                    color: order.status === 'FILLED' ? theme.success : 
                           order.status === 'PENDING' ? theme.warning : 
                           theme.danger,
                    border: `1px solid ${order.status === 'FILLED' ? theme.success : 
                                         order.status === 'PENDING' ? theme.warning : 
                                         theme.danger}40`
                  }}>
                    {order.status}
                  </span>
                </td>
                <td style={{...cellStyle, color: theme.textSecondary}}>{order.timestamp}</td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};