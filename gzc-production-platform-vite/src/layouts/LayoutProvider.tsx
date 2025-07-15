import React, { createContext, useContext, useEffect } from 'react';
import { useLayoutStore } from '@store/layoutStore';

interface LayoutContextValue {
  isLoading: boolean;
  error: string | null;
}

const LayoutContext = createContext<LayoutContextValue | undefined>(undefined);

export const useLayout = () => {
  const context = useContext(LayoutContext);
  if (!context) {
    throw new Error('useLayout must be used within LayoutProvider');
  }
  return context;
};

interface LayoutProviderProps {
  children: React.ReactNode;
}

export const LayoutProvider: React.FC<LayoutProviderProps> = ({ children }) => {
  const { isLoading, error, clearError } = useLayoutStore();

  useEffect(() => {
    // Clear any errors on mount
    clearError();
  }, [clearError]);

  const value: LayoutContextValue = {
    isLoading,
    error,
  };

  return (
    <LayoutContext.Provider value={value}>
      {children}
    </LayoutContext.Provider>
  );
};