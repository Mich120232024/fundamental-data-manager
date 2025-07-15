import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useViewMemory, FilterPreset } from '../hooks/useViewMemory';
import { theme } from '../theme';

interface ViewMemoryManagerProps {
  currentFilters?: any;
  onLoadPreset?: (filters: any) => void;
}

export const ViewMemoryManager: React.FC<ViewMemoryManagerProps> = ({ 
  currentFilters,
  onLoadPreset 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [presetName, setPresetName] = useState('');
  
  const {
    filterPresets,
    activeFilterPreset,
    saveFilterPreset,
    deleteFilterPreset,
    setActiveFilterPreset,
    resetLayouts
  } = useViewMemory();

  const handleSavePreset = () => {
    if (presetName && currentFilters) {
      const newPreset: FilterPreset = {
        id: `custom-${Date.now()}`,
        name: presetName,
        filters: currentFilters
      };
      saveFilterPreset(newPreset);
      setShowSaveDialog(false);
      setPresetName('');
    }
  };

  const handleLoadPreset = (preset: FilterPreset) => {
    setActiveFilterPreset(preset.id);
    if (onLoadPreset) {
      onLoadPreset(preset.filters);
    }
  };

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        whileHover={{ scale: 1.01, opacity: 0.9 }}
        whileTap={{ scale: 0.99 }}
        onClick={() => setIsOpen(!isOpen)}
        style={{
          background: `${theme.surfaceAlt}CC`,
          border: `1px solid ${theme.border}`,
          borderRadius: '6px',
          padding: '6px 10px',
          color: theme.text,
          fontSize: '11px',
          fontWeight: '400',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          opacity: 0.85
        }}
      >
        <div style={{
          width: '3px',
          height: '3px',
          borderRadius: '50%',
          background: theme.primary,
          opacity: 0.8
        }} />
        Memory
      </motion.button>

      {/* Memory Manager Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '8px',
              background: theme.surface,
              border: `1px solid ${theme.border}`,
              borderRadius: '8px',
              padding: '16px',
              minWidth: '320px',
              maxHeight: '500px',
              overflow: 'auto',
              zIndex: 9999,
              boxShadow: `0 8px 32px ${theme.background}CC`
            }}
          >
            <h3 style={{ 
              fontSize: '11px', 
              fontWeight: '500', 
              color: theme.text,
              marginBottom: '12px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              Saved Views
            </h3>

            {/* Filter Presets Section */}
            <div style={{ marginBottom: '16px' }}>
              <div style={{ 
                fontSize: '10px', 
                color: theme.textSecondary,
                marginBottom: '8px',
                fontWeight: '500'
              }}>
                SAVED FILTER SETS
              </div>
              
              {filterPresets.map(preset => (
                <motion.div
                  key={preset.id}
                  whileHover={{ backgroundColor: theme.surfaceAlt }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px',
                    marginBottom: '4px',
                    borderRadius: '4px',
                    border: activeFilterPreset === preset.id ? `1px solid ${theme.primary}40` : 'none',
                    background: activeFilterPreset === preset.id ? `${theme.primary}10` : 'transparent',
                    cursor: 'pointer'
                  }}
                  onClick={() => handleLoadPreset(preset)}
                >
                  <span style={{ fontSize: '11px', color: theme.text }}>
                    {preset.name}
                  </span>
                  <div style={{ display: 'flex', gap: '4px' }}>
                    {activeFilterPreset === preset.id && (
                      <span style={{ fontSize: '10px', color: theme.primary }}>✓</span>
                    )}
                    {!preset.id.startsWith('default') && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteFilterPreset(preset.id);
                        }}
                        style={{
                          background: 'transparent',
                          border: 'none',
                          color: theme.danger,
                          fontSize: '10px',
                          cursor: 'pointer',
                          padding: '2px 4px'
                        }}
                      >
                        ✕
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}

              {/* Save Current Filters Button */}
              {currentFilters && (
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => setShowSaveDialog(true)}
                  style={{
                    width: '100%',
                    marginTop: '8px',
                    background: `${theme.primary}20`,
                    border: `1px solid ${theme.primary}40`,
                    borderRadius: '4px',
                    padding: '6px',
                    color: theme.primary,
                    fontSize: '11px',
                    cursor: 'pointer'
                  }}
                >
                  Save Current Filters
                </motion.button>
              )}
            </div>

            {/* Save Dialog */}
            {showSaveDialog && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                style={{
                  position: 'absolute',
                  top: '50%',
                  left: '50%',
                  transform: 'translate(-50%, -50%)',
                  background: theme.surface,
                  border: `1px solid ${theme.border}`,
                  borderRadius: '8px',
                  padding: '16px',
                  zIndex: 10000,
                  minWidth: '250px'
                }}
              >
                <h4 style={{ fontSize: '12px', color: theme.text, marginBottom: '12px' }}>
                  Save Filter Preset
                </h4>
                <input
                  type="text"
                  value={presetName}
                  onChange={(e) => setPresetName(e.target.value)}
                  placeholder="Preset name..."
                  style={{
                    width: '100%',
                    padding: '8px',
                    background: theme.surfaceAlt,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '4px',
                    color: theme.text,
                    fontSize: '11px',
                    marginBottom: '12px'
                  }}
                />
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    onClick={handleSavePreset}
                    style={{
                      flex: 1,
                      padding: '6px',
                      background: theme.primary,
                      border: 'none',
                      borderRadius: '4px',
                      color: theme.background,
                      fontSize: '11px',
                      cursor: 'pointer'
                    }}
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setShowSaveDialog(false);
                      setPresetName('');
                    }}
                    style={{
                      flex: 1,
                      padding: '6px',
                      background: theme.surfaceAlt,
                      border: `1px solid ${theme.border}`,
                      borderRadius: '4px',
                      color: theme.text,
                      fontSize: '11px',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                </div>
              </motion.div>
            )}

            {/* Quick Actions */}
            <div style={{ 
              marginTop: '16px',
              paddingTop: '16px',
              borderTop: `1px solid ${theme.border}`
            }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={resetLayouts}
                  style={{
                    flex: 1,
                    background: theme.surfaceAlt,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '4px',
                    padding: '6px',
                    color: theme.textSecondary,
                    fontSize: '10px',
                    cursor: 'pointer'
                  }}
                >
                  Reset Layout
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.01 }}
                  whileTap={{ scale: 0.99 }}
                  onClick={() => setActiveFilterPreset(undefined)}
                  style={{
                    flex: 1,
                    background: theme.surfaceAlt,
                    border: `1px solid ${theme.border}`,
                    borderRadius: '4px',
                    padding: '6px',
                    color: theme.textSecondary,
                    fontSize: '10px',
                    cursor: 'pointer'
                  }}
                >
                  Clear Filters
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};