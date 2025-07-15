# GZC Production Engine - System Architecture Overview

**Analysis Date**: 2025-07-01  
**Analyst**: SOFTWARE_RESEARCH_ANALYST

## System Architecture

The GZC Production Engine is a **micro-frontend architecture** built with modern web technologies, implementing a modular trading/portfolio management platform.

## Core Components

### 1. gzc-main-shell (Host Application)
- **Role**: Main container/orchestrator
- **Technology**: React 19, Webpack 5 Module Federation
- **Key Features**:
  - Azure AD authentication (MSAL)
  - Dynamic micro-frontend loading
  - Routing infrastructure (React Router v7)
  - Shared UI component consumption

### 2. gzc-portfolio-app (Micro Frontend)
- **Role**: Portfolio management module
- **Technology**: React 19, TypeScript, Webpack 5
- **Key Features**:
  - Standalone capability for development
  - Module Federation remote exposure
  - Data table management (@tanstack/react-table)
  - API state management (Alova)

### 3. fx-client (Trading Client)
- **Role**: FX trading interface
- **Technology**: React 19, TypeScript, Create React App
- **Key Features**:
  - WebSocket integration (react-use-websocket)
  - Backend proxy to fxspotstream-backend:5000
  - Bootstrap UI components
  - Axios for HTTP communications

### 4. gzc-ui (Component Library)
- **Role**: Shared UI components and design system
- **Technology**: TypeScript, React 18+, Tailwind CSS
- **Key Features**:
  - Published as @gzc/ui package
  - Tree-shakeable ESM/CJS builds
  - TypeScript definitions
  - Tailwind-based styling

## Architecture Pattern: Micro-Frontend

```
┌─────────────────────────────────────────────────────────┐
│                   gzc-main-shell                        │
│  (Host Application - Module Federation Host)            │
│                                                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Router    │  │ Auth (MSAL)  │  │  Navigation  │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │ Dynamic Import
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼────────┐              ┌────────▼────────┐
│ gzc-portfolio  │              │   fx-client     │
│   (Remote)     │              │  (Standalone)   │
└────────────────┘              └─────────────────┘
        │                                 │
        └────────────┬────────────────────┘
                     │
              ┌──────▼──────┐
              │   @gzc/ui   │
              │ (Component  │
              │  Library)   │
              └─────────────┘
```

## Technology Stack Summary

### Frontend Frameworks
- **React**: v19.x (latest)
- **TypeScript**: v5.x
- **Webpack**: v5.x with Module Federation

### Styling
- **Tailwind CSS**: v3.4.x
- **PostCSS**: v8.x
- **Bootstrap**: v5.x (fx-client only)

### State Management
- **Alova**: HTTP state management (portfolio-app)
- **React Context**: Likely for shared state

### Authentication
- **Azure MSAL**: v4.x for Azure AD integration

### Build Tools
- **tsup**: Component library bundling
- **Webpack**: Module bundling and federation
- **Babel**: JavaScript transpilation

## Key Architectural Decisions

1. **Micro-Frontend Architecture**: Enables independent deployment and development
2. **Module Federation**: Runtime integration of micro-frontends
3. **Shared Component Library**: Consistent UI across applications
4. **TypeScript First**: Type safety across all repositories
5. **Modern React**: Using latest React 19 features

## Integration Points

1. **Module Federation**: gzc-main-shell imports gzc-portfolio-app at runtime
2. **Shared UI**: All apps consume @gzc/ui components
3. **Backend Services**: fx-client proxies to fxspotstream-backend:5000
4. **Authentication**: Centralized through main-shell MSAL integration

## Next Analysis Steps

1. Examine webpack configurations for Module Federation setup
2. Analyze component library structure and exports
3. Map API communication patterns
4. Document deployment and build processes
5. Create local development setup guide

—SOFTWARE_RESEARCH_ANALYST