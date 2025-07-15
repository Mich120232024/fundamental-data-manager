import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import { useViewMemory } from '../../hooks/useViewMemory';

interface FilterState {
  timeRange: '1H' | '1D' | '1W' | '1M' | '1Y';
  currencies: string[];
  aggregation: 'tick' | '1m' | '5m' | '15m' | '1h' | '1d';
  dateRange: { start: Date; end: Date };
}

interface FilterContextType extends FilterState {
  updateFilter: <K extends keyof FilterState>(key: K, value: FilterState[K]) => void;
  resetFilters: () => void;
  loadPreset: (preset: any) => void;
  getAllFilters: () => FilterState;
}

const defaultFilters: FilterState = {
  timeRange: '1D',
  currencies: ['EUR/USD', 'GBP/USD'],
  aggregation: '1m',
  dateRange: {
    start: new Date(Date.now() - 24 * 60 * 60 * 1000),
    end: new Date()
  }
};

const FilterContext = createContext<FilterContextType | null>(null);

export const useSharedFilters = () => {
  const context = useContext(FilterContext);
  if (!context) throw new Error('useSharedFilters must be used within FilterProvider');
  return context;
};

export const SharedFilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { activeFilterPreset, filterPresets } = useViewMemory();
  const [filters, setFilters] = useState<FilterState>(defaultFilters);

  // Load active filter preset on mount and when it changes
  useEffect(() => {
    if (activeFilterPreset) {
      const preset = filterPresets.find(p => p.id === activeFilterPreset);
      if (preset && preset.filters) {
        setFilters(prev => ({
          ...prev,
          ...preset.filters,
          dateRange: prev.dateRange // Keep computed dateRange
        }) as FilterState);
      }
    }
  }, [activeFilterPreset, filterPresets]);

  const updateFilter = <K extends keyof FilterState>(key: K, value: FilterState[K]) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => setFilters(defaultFilters);

  const loadPreset = (preset: any) => {
    if (preset) {
      setFilters(prev => ({
        ...prev,
        ...preset,
        dateRange: prev.dateRange // Keep computed dateRange
      }) as FilterState);
    }
  };

  const getAllFilters = () => filters;

  return (
    <FilterContext.Provider value={{ ...filters, updateFilter, resetFilters, loadPreset, getAllFilters }}>
      {children}
    </FilterContext.Provider>
  );
};