import React from 'react';
import { ComponentRegistry } from '@modules/registry/ComponentRegistry';
import { LayoutComponent } from '@store/layoutStore';

interface ComponentWrapperProps {
  component: LayoutComponent;
  isEditing: boolean;
  onRemove: () => void;
}

export const ComponentWrapper: React.FC<ComponentWrapperProps> = ({
  component,
  isEditing,
  onRemove,
}) => {
  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    onRemove();
  };

  return (
    <div className="relative h-full w-full group">
      {isEditing && (
        <div className="absolute top-2 right-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleRemove}
            className="p-1.5 bg-red-500 text-white rounded hover:bg-red-600 shadow-lg"
            title="Remove component"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
      
      <div className="h-full w-full overflow-hidden">
        {ComponentRegistry.renderComponent(component.type, component.props)}
      </div>
    </div>
  );
};