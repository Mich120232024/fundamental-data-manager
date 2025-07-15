# Module Federation Architecture Analysis

**Analysis Date**: 2025-07-01  
**Analyst**: SOFTWARE_RESEARCH_ANALYST

## Module Federation Configuration

The GZC Production Engine implements Webpack 5 Module Federation for runtime integration of micro-frontends.

## Architecture Pattern

```
┌────────────────────────────────────────────┐
│         gzc-main-shell (Host)              │
│         Port: 3000                         │
│  ┌────────────────────────────────────┐    │
│  │ ModuleFederationPlugin              │    │
│  │ name: "gzc_main_shell"             │    │
│  │ remotes: {                         │    │
│  │   gzc_portfolio_app: :3001         │    │
│  │ }                                  │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
                    ⬇️ Runtime Import
┌────────────────────────────────────────────┐
│      gzc-portfolio-app (Remote)            │
│      Port: 3001                            │
│  ┌────────────────────────────────────┐    │
│  │ ModuleFederationPlugin              │    │
│  │ name: "gzc_portfolio_app"          │    │
│  │ exposes: {                         │    │
│  │   "./Portfolio": "./src/Portfolio" │    │
│  │ }                                  │    │
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

## Key Configuration Details

### Host Application (gzc-main-shell)
```javascript
{
  name: "gzc_main_shell",
  filename: "remoteEntry.js",
  remotes: {
    gzc_portfolio_app: "gzc_portfolio_app@http://localhost:3001/remoteEntry.js"
  },
  shared: {
    react: { singleton: true, requiredVersion: deps.react },
    "react-dom": { singleton: true, requiredVersion: deps["react-dom"] },
    "@gzc/ui": { singleton: true, requiredVersion: deps["@gzc/ui"] }
  }
}
```

### Remote Application (gzc-portfolio-app)
```javascript
{
  name: "gzc_portfolio_app",
  filename: "remoteEntry.js",
  exposes: {
    "./Portfolio": "./src/Portfolio"
  },
  remotes: {
    gzc_main_shell: "gzc_main_shell@http://localhost:3000/remoteEntry.js"
  },
  shared: {
    react: { singleton: true, requiredVersion: deps.react, eager: true },
    "react-dom": { singleton: true, requiredVersion: deps["react-dom"], eager: true },
    "@gzc/ui": { singleton: true, eager: false, requiredVersion: "*" }
  }
}
```

## Shared Dependencies Strategy

### Singleton Pattern
All shared dependencies use `singleton: true` to ensure only one instance exists:
- **react**: Single React instance across all micro-frontends
- **react-dom**: Single DOM renderer
- **@gzc/ui**: Shared component library

### Eager Loading
Portfolio app marks React dependencies as `eager: true` for standalone capability.

### Version Management
- Host uses exact versions from package.json dependencies
- Remote accepts any version for @gzc/ui (`requiredVersion: "*"`)

## Bidirectional Communication

Interesting pattern: Both apps can act as remotes to each other:
- **gzc-main-shell** imports from gzc_portfolio_app
- **gzc-portfolio-app** imports from gzc_main_shell

This enables:
1. Shared context/hooks from main shell
2. Common authentication state
3. Cross-app navigation

## Environment Variables

Both applications use:
- **process.env.SHELL_CONTEXT**: Differentiates between shell (true) and standalone (false) mode
- **.env files**: Configuration management
- **webpack.DefinePlugin**: Injects env vars into bundles

## Development Ports

- **Main Shell**: http://localhost:3000
- **Portfolio App**: http://localhost:3001
- **FX Client**: http://localhost:3000 (CRA default, potential conflict)

## Key Findings

### Strengths
1. **True micro-frontend architecture**: Independent deployment possible
2. **Shared dependencies optimization**: Prevents duplicate React instances
3. **Development flexibility**: Apps can run standalone or integrated
4. **Type safety**: TypeScript throughout

### Potential Issues
1. **Port conflicts**: FX Client and Main Shell both default to port 3000
2. **Tight coupling**: Bidirectional remotes create interdependencies
3. **Version coordination**: Need careful dependency version management
4. **CORS configuration**: Required for cross-origin module loading

## Integration Flow

1. User accesses main shell at http://localhost:3000
2. Main shell loads its bundle and remoteEntry.js
3. When Portfolio route accessed, dynamically imports from :3001/remoteEntry.js
4. Portfolio module loaded with shared React instance
5. UI components from @gzc/ui shared across apps

## Next Steps

1. Analyze the actual Portfolio component export
2. Check authentication flow through MSAL
3. Examine FX Client integration strategy (not using Module Federation)
4. Create deployment configuration analysis

—SOFTWARE_RESEARCH_ANALYST