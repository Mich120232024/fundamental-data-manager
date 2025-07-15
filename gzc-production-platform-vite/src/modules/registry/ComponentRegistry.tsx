import React from 'react';
import { v4 as uuidv4 } from 'uuid';

export interface ComponentDefinition {
  type: string;
  displayName: string;
  description: string;
  category: 'trading' | 'analytics' | 'portfolio' | 'utility';
  defaultProps: Record<string, any>;
  icon?: string;
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
}

export interface RegisteredComponent extends ComponentDefinition {
  component: React.ComponentType<any>;
}

class ComponentRegistryClass {
  private components: Map<string, RegisteredComponent> = new Map();
  private initialized = false;

  initialize() {
    if (this.initialized) return;
    
    // Register default components
    this.register({
      type: 'placeholder',
      displayName: 'Placeholder',
      description: 'Empty placeholder component',
      category: 'utility',
      defaultProps: {},
      component: PlaceholderComponent,
    });

    this.initialized = true;
  }

  register(component: RegisteredComponent) {
    if (this.components.has(component.type)) {
      console.warn(`Component ${component.type} is already registered`);
      return;
    }
    this.components.set(component.type, component);
  }

  unregister(type: string) {
    this.components.delete(type);
  }

  get(type: string): RegisteredComponent | undefined {
    return this.components.get(type);
  }

  getAll(): RegisteredComponent[] {
    return Array.from(this.components.values());
  }

  getByCategory(category: string): RegisteredComponent[] {
    return this.getAll().filter(c => c.category === category);
  }

  createComponent(type: string, props?: Record<string, any>) {
    const definition = this.get(type);
    if (!definition) {
      console.error(`Component type ${type} not found in registry`);
      return null;
    }

    return {
      id: uuidv4(),
      type,
      props: { ...definition.defaultProps, ...props },
    };
  }

  renderComponent(type: string, props: Record<string, any>) {
    const definition = this.get(type);
    if (!definition) {
      return <div>Component type "{type}" not found</div>;
    }

    const Component = definition.component;
    return <Component {...props} />;
  }
}

// Placeholder component
const PlaceholderComponent: React.FC<{ title?: string }> = ({ title = 'Component' }) => {
  return (
    <div className="flex items-center justify-center h-full bg-gray-100 dark:bg-gray-800 rounded-lg">
      <p className="text-gray-500 dark:text-gray-400">{title}</p>
    </div>
  );
};

// Export singleton instance
export const ComponentRegistry = new ComponentRegistryClass();