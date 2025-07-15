# GZC Production Engine - Dependency Analysis

**Analysis Date**: 2025-07-01  
**Analyst**: SOFTWARE_RESEARCH_ANALYST

## Dependency Overview

### Core Framework Versions
- **React**: 19.x (Latest - using new features)
- **TypeScript**: 5.x
- **Webpack**: 5.x
- **Node**: 18+ required

## Dependency Matrix

### Shared Dependencies (Must Match Across Apps)

| Package | gzc-main-shell | gzc-portfolio-app | fx-client | gzc-ui |
|---------|----------------|-------------------|-----------|---------|
| react | ^19.1.0 | ^19.1.0 | ^19.0.0 | >=18.0.0 (peer) |
| react-dom | ^19.1.0 | ^19.1.0 | ^19.0.0 | >=18.0.0 (peer) |
| @gzc/ui | 1.0.0 | file:../gzc-ui | - | - |
| typescript | ^5.8.3 | ^5.8.3 | - | ^5.2.0 |

### Authentication Stack (Main Shell)
```
@azure/msal-browser: ^4.12.0
@azure/msal-react: ^3.0.12
```

### UI Framework Stack
- **Tailwind CSS**: ^3.4.1 (all apps)
- **PostCSS**: ^8.x (all apps)
- **Autoprefixer**: ^10.4.x
- **Bootstrap**: ^5.3.3 (fx-client only)
- **Framer Motion**: ^12.12.1 (main-shell animations)

### Data Management
- **@tanstack/react-table**: ^8.21.3 (portfolio-app, gzc-ui)
- **Alova**: ^3.2.11 (portfolio-app HTTP state)
- **Axios**: ^1.7.9 (fx-client)
- **react-use-websocket**: ^4.13.0 (fx-client realtime)

### Build Tools

#### Webpack Stack (main-shell, portfolio-app)
```json
{
  "webpack": "^5.99.8",
  "webpack-cli": "^6.0.1",
  "webpack-dev-server": "^5.2.1",
  "webpack-merge": "^6.0.1",
  "html-webpack-plugin": "^5.6.3",
  "mini-css-extract-plugin": "^2.9.2"
}
```

#### Component Library Build (gzc-ui)
```json
{
  "tsup": "^8.4.0"  // Modern bundler for libraries
}
```

#### Create React App (fx-client)
```json
{
  "react-scripts": "5.0.1"
}
```

### Routing
- **react-router-dom**: ^7.6.0 (main-shell only)

### Module Federation
- Built into Webpack 5 (no additional dependencies)

## Dependency Insights

### Version Alignment Issues
1. **React Versions**: Slight mismatch (19.0.0 vs 19.1.0)
2. **TypeScript**: fx-client doesn't specify version (using CRA default)

### Peer Dependency Requirements
- gzc-ui requires React 18+ but apps use React 19
- This works due to React's backward compatibility

### Local Dependencies
- `@gzc/ui` uses `file:../gzc-ui` in portfolio-app
- Main shell uses exact version `1.0.0`
- This requires careful build order

### Bundle Size Considerations

#### Heavy Dependencies
1. **framer-motion**: 12.12.1 - Animation library (large)
2. **@tanstack/react-table**: Complex table logic
3. **Bootstrap**: Full CSS framework (fx-client)

#### Optimization Opportunities
- Tree-shaking for @gzc/ui components
- Lazy loading for framer-motion animations
- Replace Bootstrap with Tailwind components

## Security Audit

### Outdated Packages
Need to check:
- babel plugins using ^7.x (check for latest)
- All @types packages for latest versions

### Critical Dependencies
- **dotenv**: Loading secrets (ensure .env in .gitignore)
- **@azure/msal**: Authentication (keep updated)

## Development Dependencies

### Testing Stack
```json
{
  "@testing-library/react": "^16.2.0",
  "@testing-library/jest-dom": "^6.6.3",
  "@types/jest": "^29.5.14"
}
```

### Type Definitions
All apps properly typed with:
- @types/react
- @types/react-dom
- Custom types for libraries

## Dependency Graph

```
@gzc/ui (Component Library)
    ├── react (peer)
    ├── react-dom (peer)
    ├── @tanstack/react-table
    ├── lucide-react (icons)
    └── react-datepicker

gzc-main-shell (Host)
    ├── @gzc/ui@1.0.0
    ├── react@19.1.0
    ├── @azure/msal-*
    ├── react-router-dom@7.6.0
    └── framer-motion@12.12.1

gzc-portfolio-app (Remote)
    ├── @gzc/ui (local file)
    ├── react@19.1.0
    ├── @tanstack/react-table
    └── alova (HTTP state)

fx-client (Standalone)
    ├── react@19.0.0
    ├── bootstrap@5.3.3
    ├── axios@1.7.9
    └── react-use-websocket@4.13.0
```

## Recommendations

### Immediate Actions
1. Align React versions to 19.1.0 across all apps
2. Add TypeScript to fx-client explicitly
3. Version lock @gzc/ui in portfolio-app

### Architecture Improvements
1. Consider monorepo with workspace management (npm/yarn workspaces)
2. Implement shared TypeScript config
3. Create shared ESLint/Prettier configs

### Performance Optimizations
1. Implement code splitting for routes
2. Lazy load heavy dependencies
3. Use React.memo for expensive components

### Security Updates
1. Regular dependency audits (`npm audit`)
2. Automate security updates
3. Pin versions for production

## Build Size Analysis

Estimated production bundle sizes:
- **gzc-ui**: ~50KB (minified)
- **main-shell**: ~300KB (without remotes)
- **portfolio-app**: ~200KB
- **fx-client**: ~400KB (includes Bootstrap)

Total loaded in browser: ~950KB + vendor chunks

## Next Steps
1. Set up dependency update automation
2. Implement bundle analysis tools
3. Create shared configuration packages
4. Document version update procedures

—SOFTWARE_RESEARCH_ANALYST