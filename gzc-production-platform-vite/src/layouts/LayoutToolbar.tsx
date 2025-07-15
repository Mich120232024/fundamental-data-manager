import React, { useState } from 'react';
import { ComponentRegistry } from '@modules/registry/ComponentRegistry';
import { clsx } from 'clsx';

interface LayoutToolbarProps {
  isEditing: boolean;
  onToggleEdit: () => void;
  onAddComponent: (type: string) => void;
  onSave: () => void;
}

export const LayoutToolbar: React.FC<LayoutToolbarProps> = ({
  isEditing,
  onToggleEdit,
  onAddComponent,
  onSave,
}) => {
  const [showComponentMenu, setShowComponentMenu] = useState(false);
  const components = ComponentRegistry.getAll();

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleEdit}
            className={clsx(
              'px-4 py-2 rounded-lg font-medium transition-colors',
              isEditing
                ? 'bg-primary text-white'
                : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
            )}
          >
            {isEditing ? 'Editing' : 'Edit Layout'}
          </button>

          {isEditing && (
            <div className="relative">
              <button
                onClick={() => setShowComponentMenu(!showComponentMenu)}
                className="px-4 py-2 bg-secondary text-white rounded-lg font-medium hover:bg-opacity-90"
              >
                Add Component
              </button>

              {showComponentMenu && (
                <div className="absolute top-full left-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
                  <div className="p-2">
                    {components.map((comp) => (
                      <button
                        key={comp.type}
                        onClick={() => {
                          onAddComponent(comp.type);
                          setShowComponentMenu(false);
                        }}
                        className="w-full text-left px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700"
                      >
                        <div className="font-medium text-gray-900 dark:text-white">
                          {comp.displayName}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {comp.description}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {isEditing && (
          <button
            onClick={onSave}
            className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
          >
            Save Layout
          </button>
        )}
      </div>
    </div>
  );
};