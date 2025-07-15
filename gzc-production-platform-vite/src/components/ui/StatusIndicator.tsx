import React from 'react';
import { motion } from 'framer-motion';

interface StatusIndicatorProps {
  status: 'positive' | 'negative' | 'neutral' | 'live' | 'processing';
  label?: string;
  animate?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ 
  status, 
  label,
  animate = false,
  size = 'md' 
}) => {
  const statusConfig = {
    positive: { color: 'bg-secondary', textColor: 'status-positive' },
    negative: { color: 'bg-danger', textColor: 'status-negative' },
    neutral: { color: 'bg-gray-400', textColor: 'status-neutral' },
    live: { color: 'bg-secondary', textColor: 'status-positive' },
    processing: { color: 'bg-info', textColor: 'text-info' }
  };

  const sizeConfig = {
    sm: { dot: 'w-1.5 h-1.5', text: 'text-xs' },
    md: { dot: 'w-2 h-2', text: 'text-xs' },
    lg: { dot: 'w-3 h-3', text: 'text-sm' }
  };

  const config = statusConfig[status];
  const sizes = sizeConfig[size];
  const shouldAnimate = animate && (status === 'live' || status === 'processing');

  const DotComponent = shouldAnimate ? motion.div : 'div';
  const animationProps = shouldAnimate ? {
    animate: { opacity: [0.5, 1, 0.5] },
    transition: { duration: 2, repeat: Infinity }
  } : {};

  return (
    <div className="flex items-center gap-1.5">
      <DotComponent 
        className={`${sizes.dot} ${config.color} rounded-full ${shouldAnimate ? 'live-indicator' : ''}`}
        {...animationProps}
      />
      {label && (
        <span className={`${sizes.text} ${config.textColor}`}>
          {label}
        </span>
      )}
    </div>
  );
};