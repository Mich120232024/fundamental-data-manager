import React, { useState, useCallback, useEffect } from 'react';
import { Responsive, WidthProvider, Layout } from 'react-grid-layout';
import { motion, AnimatePresence } from 'framer-motion';
import { useLayoutStore } from '@store/layoutStore';
import { ComponentRegistry } from '@modules/registry/ComponentRegistry';
import { LayoutToolbar } from './LayoutToolbar';
import { ComponentWrapper } from './ComponentWrapper';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface LayoutEngineProps {
  layoutId: string;
  readOnly?: boolean;
}

export const LayoutEngine: React.FC<LayoutEngineProps> = ({ layoutId, readOnly = false }) => {
  const { 
    layouts, 
    components, 
    updateLayout, 
    addComponent, 
    removeComponent,
    saveLayout,
    loadLayout 
  } = useLayoutStore();

  const [isEditing, setIsEditing] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    loadLayout(layoutId);
  }, [layoutId, loadLayout]);

  const handleLayoutChange = useCallback((
    _currentLayout: Layout[],
    allLayouts: { [key: string]: Layout[] }
  ) => {
    if (!readOnly && isEditing) {
      updateLayout(layoutId, allLayouts);
    }
  }, [layoutId, readOnly, isEditing, updateLayout]);

  const handleAddComponent = useCallback((componentType: string) => {
    const newComponent = ComponentRegistry.createComponent(componentType);
    if (newComponent) {
      addComponent(layoutId, newComponent);
    }
  }, [layoutId, addComponent]);

  const handleRemoveComponent = useCallback((componentId: string) => {
    removeComponent(layoutId, componentId);
  }, [layoutId, removeComponent]);

  const handleSave = useCallback(async () => {
    await saveLayout(layoutId);
    setIsEditing(false);
  }, [layoutId, saveLayout]);

  if (!mounted) {
    return <div className="flex items-center justify-center h-full">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
  }

  const currentLayout = layouts[layoutId] || {};
  const layoutComponents = components[layoutId] || [];

  return (
    <div className="layout-engine h-full flex flex-col">
      {!readOnly && (
        <LayoutToolbar
          isEditing={isEditing}
          onToggleEdit={() => setIsEditing(!isEditing)}
          onAddComponent={handleAddComponent}
          onSave={handleSave}
        />
      )}
      
      <div className="flex-1 overflow-auto bg-gray-50 dark:bg-gray-900">
        <ResponsiveGridLayout
          className="layout"
          layouts={currentLayout}
          onLayoutChange={handleLayoutChange}
          isDraggable={isEditing && !readOnly}
          isResizable={isEditing && !readOnly}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
          cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
          rowHeight={100}
          margin={[16, 16]}
          containerPadding={[16, 16]}
          useCSSTransforms={true}
          transformScale={1}
          preventCollision={false}
          compactType="vertical"
        >
          <AnimatePresence mode="popLayout">
            {layoutComponents.map((component) => (
              <motion.div
                key={component.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.8 }}
                transition={{ duration: 0.3 }}
              >
                <ComponentWrapper
                  component={component}
                  isEditing={isEditing}
                  onRemove={() => handleRemoveComponent(component.id)}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </ResponsiveGridLayout>
      </div>
    </div>
  );
};