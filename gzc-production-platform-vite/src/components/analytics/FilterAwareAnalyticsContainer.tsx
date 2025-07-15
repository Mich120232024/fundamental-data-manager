import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { SharedFilterProvider } from './SharedFilterContext';
import { FilterBar } from './FilterBar';
import { SimpleFilterAwareChart } from './SimpleFilterAwareChart';
import { theme } from '../../theme';

export const FilterAwareAnalyticsContainer: React.FC = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);

  // Handle ESC key to exit fullscreen
  React.useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isMaximized) {
        setIsMaximized(false);
      }
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isMaximized]);

  return (
    <SharedFilterProvider>
      <>
        {/* Fullscreen backdrop */}
        <AnimatePresence>
          {isMaximized && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              style={{
                position: 'fixed',
                inset: 0,
                background: `${theme.background}EE`,
                zIndex: 998,
                backdropFilter: 'blur(4px)'
              }}
              onClick={() => setIsMaximized(false)}
            />
          )}
        </AnimatePresence>

        <motion.div
        layout
        animate={{
          scale: isMaximized ? 1 : 1,
          opacity: 1
        }}
        style={{ 
          marginTop: '16px',
          marginBottom: '16px',
          padding: '16px',
          background: theme.surfaceAlt,
          borderRadius: '8px',
          border: `1px solid ${theme.border}`,
          maxHeight: isMaximized ? 'calc(100vh - 40px)' : isCollapsed ? 'auto' : '600px',
          display: 'flex',
          flexDirection: 'column',
          position: isMaximized ? 'fixed' : 'relative',
          inset: isMaximized ? '20px' : 'auto',
          zIndex: isMaximized ? 999 : 'auto',
          boxShadow: isMaximized ? `0 20px 60px ${theme.background}CC` : 'none'
        }}
      >
        {/* Header with collapse/expand controls */}
        <div 
          onClick={() => !isMaximized && setIsCollapsed(!isCollapsed)}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: isCollapsed ? 0 : '12px',
            cursor: 'pointer'
          }}
        >
          <h3 
            style={{ 
              fontSize: theme.typography.h4.fontSize, 
              fontWeight: theme.typography.h4.fontWeight, 
              color: theme.text,
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              flex: 1
            }}
          >
            Horizontal Analytics View
            {isMaximized && (
              <span style={{ 
                fontSize: theme.typography.bodyTiny.fontSize, 
                color: theme.textSecondary, 
                marginLeft: '8px',
                fontWeight: '400',
                textTransform: 'none'
              }}>
                (Press ESC to exit)
              </span>
            )}
          </h3>

          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }} onClick={(e) => e.stopPropagation()}>
            {/* Collapse/Expand button */}
            <motion.button
              whileHover={{ scale: 1.1, backgroundColor: `${theme.primary}20` }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                setIsCollapsed(!isCollapsed);
              }}
              style={{
                background: 'transparent',
                border: 'none',
                borderRadius: '4px',
                width: '28px',
                height: '28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: theme.textSecondary,
                padding: '4px'
              }}
            >
              <motion.svg
                animate={{ rotate: isCollapsed ? 180 : 0 }}
                transition={{ duration: 0.2 }}
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
              >
                <path
                  d="M3 5L7 9L11 5"
                  stroke="currentColor"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </motion.svg>
            </motion.button>

            {/* Maximize button */}
            <motion.button
              whileHover={{ scale: 1.1, backgroundColor: `${theme.primary}20` }}
              whileTap={{ scale: 0.9 }}
              onClick={(e) => {
                e.stopPropagation();
                setIsMaximized(!isMaximized);
                if (!isMaximized && isCollapsed) {
                  setIsCollapsed(false);
                }
              }}
              style={{
                background: 'transparent',
                border: 'none',
                borderRadius: '4px',
                width: '28px',
                height: '28px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                color: theme.textSecondary,
                padding: '4px'
              }}
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 14 14"
                fill="none"
              >
                {isMaximized ? (
                  <path
                    d="M10 2L8 4M6 10L4 12M4 2L6 4M10 12L8 10"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                ) : (
                  <path
                    d="M8 2H12V6M12 2L8 6M6 12H2V8M2 12L6 8"
                    stroke="currentColor"
                    strokeWidth="1.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}
              </svg>
            </motion.button>
          </div>
        </div>
        
        {/* Collapsible content */}
        <AnimatePresence initial={false}>
          {!isCollapsed && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
              style={{ 
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                gap: '12px'
              }}
            >
              {/* Filter Bar inside the container */}
              <FilterBar />
              
              {/* Horizontal scrollable charts */}
              <div style={{ 
                flex: 1,
                display: 'flex',
                overflowX: 'auto',
                overflowY: 'hidden',
                gap: '16px',
                paddingBottom: '8px',
                WebkitOverflowScrolling: 'touch'
              }}>
                {[
                  "EUR/USD Analysis",
                  "GBP/USD Analysis", 
                  "USD/JPY Analysis",
                  "Cross Pair Correlation",
                  "Market Microstructure",
                  "Order Book Imbalance",
                  "Volatility Surface",
                  "Term Structure",
                  "Price History",
                  "Volume Analysis",
                  "Volatility Metrics",
                  "Order Flow",
                  "Market Depth",
                  "Spread Analysis"
                ].map((title) => (
                  <div key={title} style={{ 
                    minWidth: isMaximized ? '400px' : '300px',
                    height: isMaximized ? '450px' : '350px',
                    flexShrink: 0
                  }}>
                    <SimpleFilterAwareChart title={title} />
                  </div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  </SharedFilterProvider>
  );
};