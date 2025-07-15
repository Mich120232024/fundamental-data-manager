import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { theme } from '../theme';
import { ViewMemoryManager } from './ViewMemoryManager';
import { useViewMemory } from '../hooks/useViewMemory';

interface ProfessionalHeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  portfolioValue: number;
  dailyPnL: number;
}

export const ProfessionalHeader: React.FC<ProfessionalHeaderProps> = ({
  activeTab,
  setActiveTab,
  portfolioValue,
  dailyPnL
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { saveTabOrder, tabOrder, saveActiveTab } = useViewMemory();
  
  const [tabs, setTabs] = useState([
    { name: "GZC Portfolio", id: "portfolio", path: "/portfolio" },
    { name: "Risk Analytics", id: "risk", path: "/risk" },
    { name: "Macro Analytics", id: "macro", path: "/macro" },
    { name: "Operations", id: "operations", path: "/operations" },
    { name: "Admin", id: "admin", path: "/admin" },
    { name: "Analytics Demo", id: "analytics", path: "/analytics" },
    { name: "Trading Dashboard", id: "trading-dashboard", path: "/trading-dashboard" }
  ]);
  
  const [draggedTab, setDraggedTab] = useState<number | null>(null);
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null);
  
  // Load saved tab order from view memory
  useEffect(() => {
    if (tabOrder && tabOrder.length > 0) {
      const defaultTabs = tabs;
      const orderedTabs = tabOrder.map(id => 
        defaultTabs.find(tab => tab.id === id)
      ).filter(Boolean);
      
      // Add any new tabs that aren't in the saved order
      const remainingTabs = defaultTabs.filter(tab => 
        !tabOrder.includes(tab.id)
      );
      
      setTabs([...orderedTabs, ...remainingTabs] as typeof tabs);
    }
  }, []);
  
  // Save tab order when it changes
  useEffect(() => {
    const tabIds = tabs.map(tab => tab.id);
    saveTabOrder(tabIds);
  }, [tabs, saveTabOrder]);
  
  const handleTabClick = (tab: typeof tabs[0]) => {
    setActiveTab(tab.id);
    saveActiveTab(tab.id);
    navigate(tab.path);
  };
  
  const handleDragStart = (e: React.DragEvent, index: number) => {
    setDraggedTab(index);
    e.dataTransfer.effectAllowed = 'move';
  };
  
  const handleDragOver = (e: React.DragEvent, index: number) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverIndex(index);
  };
  
  const handleDragLeave = () => {
    setDragOverIndex(null);
  };
  
  const handleDrop = (e: React.DragEvent, dropIndex: number) => {
    e.preventDefault();
    if (draggedTab === null || draggedTab === dropIndex) return;
    
    const draggedItem = tabs[draggedTab];
    const newTabs = [...tabs];
    
    // Remove dragged item
    newTabs.splice(draggedTab, 1);
    
    // Insert at new position
    const insertIndex = draggedTab < dropIndex ? dropIndex - 1 : dropIndex;
    newTabs.splice(insertIndex, 0, draggedItem);
    
    setTabs(newTabs);
    setDraggedTab(null);
    setDragOverIndex(null);
  };
  
  const handleDragEnd = () => {
    setDraggedTab(null);
    setDragOverIndex(null);
  };

  return (
    <motion.div
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      style={{
        backgroundColor: theme.surface,
        borderBottom: `1px solid ${theme.border}`,
        padding: "6px 12px",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        height: "64px",
        backdropFilter: "blur(12px)",
        background: `${theme.surface}ee`,
        position: "relative",
        zIndex: 1000
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
        <motion.div
          whileHover={{ scale: 1.02 }}
          style={{
            fontSize: "20px",
            fontWeight: "700",
            background: theme.gradient,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: "12px"
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <motion.div
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              style={{ 
                width: "8px", 
                height: "8px", 
                borderRadius: "50%",
                background: theme.headerColor
              }}
            />
            <span>GZC Intel</span>
          </div>
        </motion.div>
        
        <nav style={{ display: "flex", gap: "8px" }}>
          {tabs.map((tab, index) => (
            <motion.button
              key={tab.id}
              draggable
              onDragStart={(e) => handleDragStart(e, index)}
              onDragOver={(e) => handleDragOver(e, index)}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, index)}
              onDragEnd={handleDragEnd}
              initial={{ opacity: 0, x: -20 }}
              animate={{ 
                opacity: draggedTab === index ? 0.5 : 1, 
                x: 0,
                scale: dragOverIndex === index ? 1.05 : 1
              }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleTabClick(tab)}
              style={{
                background: activeTab === tab.id ? `${theme.primary}20` : "transparent",
                color: activeTab === tab.id ? theme.primary : theme.textSecondary,
                border: dragOverIndex === index ? `2px solid ${theme.primary}` : "none",
                padding: "6px 12px",
                fontSize: "12px",
                fontWeight: "400",
                borderRadius: "8px",
                cursor: draggedTab !== null ? "move" : "pointer",
                transition: "all 0.2s ease",
                userSelect: "none"
              }}
            >
              {tab.name}
            </motion.button>
          ))}
        </nav>
      </div>
      
      <div style={{ display: "flex", alignItems: "center", gap: "16px", fontSize: "13px" }}>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{ display: "flex", alignItems: "center", gap: "16px" }}
        >
          <span style={{ fontSize: "10px", color: theme.textSecondary }}>Month to Date P&L:</span>
          <span style={{ fontSize: "11px", fontWeight: "500", color: portfolioValue > 0 ? theme.success : theme.danger }}>
            {portfolioValue > 0 ? "+" : ""}${Math.abs(portfolioValue).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
          <span style={{ color: theme.textSecondary, opacity: 0.5 }}>|</span>
          <span style={{ fontSize: "10px", color: theme.textSecondary }}>Daily P&L:</span>
          <span style={{ fontSize: "11px", fontWeight: "400", color: theme.text }}>
            {dailyPnL > 0 ? "+" : ""}${Math.abs(dailyPnL).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </span>
        </motion.div>
        
        {/* View Memory Manager */}
        <div style={{ position: 'relative', zIndex: 5000 }}>
          <ViewMemoryManager />
        </div>
        
        {/* Theme Selector */}
        <motion.div
          whileHover={{ scale: 1.01 }}
          style={{ position: 'relative' }}
        >
          <select
            value="Trading Operations"
            onChange={() => {}}
            style={{
              background: `linear-gradient(to bottom, ${theme.surfaceAlt}CC, ${theme.surface}EE)`,
              border: `1px solid ${theme.border}`,
              borderRadius: "6px",
              padding: "6px 28px 6px 10px",
              color: theme.text,
              fontSize: theme.typography.body.fontSize,
              fontWeight: theme.typography.body.fontWeight,
              cursor: "pointer",
              outline: "none",
              appearance: "none",
              backdropFilter: "blur(8px)",
              transition: "all 0.2s ease"
            }}
          >
            <option value="Trading Operations">Trading Operations</option>
          </select>
          <div style={{
            position: 'absolute',
            right: '8px',
            top: '50%',
            transform: 'translateY(-50%)',
            pointerEvents: 'none'
          }}>
            <svg width="10" height="6" viewBox="0 0 10 6" fill="none">
              <path d="M1 1L5 5L9 1" stroke={theme.textSecondary} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
};