import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  animate?: boolean;
  animationDelay?: number;
  onClick?: () => void;
}

export const Card: React.FC<CardProps> = ({ 
  children, 
  className = "", 
  hover = false,
  animate = false,
  animationDelay = 0,
  onClick 
}) => {
  const baseClasses = hover ? 'card-hover' : 'card';
  const Component = animate ? motion.div : 'div';
  
  const animationProps = animate ? {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    transition: { delay: animationDelay },
    ...(hover && {
      whileHover: { scale: 1.02 },
      whileTap: { scale: 0.98 }
    })
  } : {};

  return (
    <Component 
      className={`${baseClasses} ${className} ${onClick ? 'cursor-pointer' : ''}`}
      onClick={onClick}
      {...animationProps}
    >
      {children}
    </Component>
  );
};