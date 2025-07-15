import React from 'react';
import { motion } from 'framer-motion';

interface PanelProps {
  children: React.ReactNode;
  className?: string;
  animate?: boolean;
  animationDelay?: number;
}

interface PanelHeaderProps {
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
}

interface PanelContentProps {
  children: React.ReactNode;
  className?: string;
  scrollable?: boolean;
}

export const Panel: React.FC<PanelProps> = ({ 
  children, 
  className = "", 
  animate = false,
  animationDelay = 0 
}) => {
  const Component = animate ? motion.div : 'div';
  const animationProps = animate ? {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { delay: animationDelay }
  } : {};

  return (
    <Component className={`panel ${className}`} {...animationProps}>
      {children}
    </Component>
  );
};

export const PanelHeader: React.FC<PanelHeaderProps> = ({ 
  children, 
  className = "",
  actions 
}) => {
  return (
    <div className={`panel-header ${className}`}>
      <span>{children}</span>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
};

export const PanelContent: React.FC<PanelContentProps> = ({ 
  children, 
  className = "",
  scrollable = false 
}) => {
  return (
    <div className={`panel-content ${scrollable ? 'overflow-auto' : ''} ${className}`}>
      {children}
    </div>
  );
};