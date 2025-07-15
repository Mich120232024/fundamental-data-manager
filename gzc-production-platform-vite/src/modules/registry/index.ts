import { ComponentRegistry } from './ComponentRegistry';
import { PortfolioComponent } from '@modules/portfolio/PortfolioComponent';

// Register all available components
export function registerComponents() {
  // Portfolio Components
  ComponentRegistry.register({
    type: 'portfolio-overview',
    displayName: 'Portfolio Overview',
    description: 'Display portfolio positions and P&L',
    category: 'portfolio',
    defaultProps: {},
    component: PortfolioComponent,
    minWidth: 4,
    minHeight: 3,
  });

  // Add more components here as they are created
}

// Initialize and register all components
registerComponents();