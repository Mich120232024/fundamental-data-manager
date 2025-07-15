# GZC Production Engine - Local Development Setup Guide

**Created**: 2025-07-01  
**Author**: SOFTWARE_RESEARCH_ANALYST

## Prerequisites

### Required Software
- **Node.js**: v18+ (for React 19 compatibility)
- **npm**: v8+ or yarn
- **Git**: For repository access
- **Azure AD App Registration**: For authentication (MSAL)

### Development Tools
- **VS Code** or similar IDE
- **React Developer Tools** browser extension
- **ModuleFederation DevTools** (optional)

## Setup Sequence

The setup must follow a specific order due to dependencies:

```
1. gzc-ui (Component Library)
   ↓
2. gzc-main-shell (Host Application)
   ↓
3. gzc-portfolio-app (Micro Frontend)
   ↓
4. fx-client (Standalone App)
```

## Step-by-Step Setup

### 1. Clone and Structure

```bash
# Already completed in your case
cd /Users/mikaeleage/Projects\ Container/gzc-production-engine/repositories
```

### 2. Setup Component Library (gzc-ui)

```bash
cd gzc-ui
npm install
npm run build  # Creates dist/ folder with compiled library
```

This creates the @gzc/ui package that other apps depend on.

### 3. Setup Main Shell

```bash
cd ../gzc-main-shell

# Create .env file (required)
cat > .env << EOF
REACT_APP_AZURE_CLIENT_ID=your-azure-client-id
REACT_APP_AZURE_TENANT_ID=your-azure-tenant-id
REACT_APP_AZURE_REDIRECT_URI=http://localhost:3000
EOF

# Install dependencies
npm install

# Link local @gzc/ui if not automatically resolved
npm link ../gzc-ui
```

### 4. Setup Portfolio App

```bash
cd ../gzc-portfolio-app

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=your-api-url
REACT_APP_WS_URL=your-websocket-url
EOF

# Install dependencies
npm install
```

### 5. Setup FX Client

```bash
cd ../fx-client

# Create .env file
cat > .env << EOF
REACT_APP_API_URL=http://localhost:5000
EOF

# Install dependencies
npm install
```

## Running the System

### Option 1: Full Micro-Frontend Mode

Start in this order:

```bash
# Terminal 1: Component Library (watch mode)
cd gzc-ui
npm run dev

# Terminal 2: Portfolio App (port 3001)
cd gzc-portfolio-app
npm run dev

# Terminal 3: Main Shell (port 3000)
cd gzc-main-shell
npm run dev

# Terminal 4: FX Client (needs port change)
cd fx-client
PORT=3002 npm start
```

Access the integrated system at: http://localhost:3000

### Option 2: Standalone Development

Each app can run independently:

```bash
# Portfolio App standalone
cd gzc-portfolio-app
npm run dev
# Access at http://localhost:3001

# FX Client standalone
cd fx-client
npm start
# Access at http://localhost:3000
```

## Configuration Details

### Azure AD Configuration (Main Shell)

Required MSAL configuration in `.env`:
- `REACT_APP_AZURE_CLIENT_ID`: Your Azure AD app client ID
- `REACT_APP_AZURE_TENANT_ID`: Your Azure AD tenant ID
- `REACT_APP_AZURE_REDIRECT_URI`: Must match Azure AD app settings

### Module Federation URLs

Default configuration expects:
- Main Shell: http://localhost:3000
- Portfolio App: http://localhost:3001

To change, modify webpack configurations:
- `gzc-main-shell/webpack.common.js` - Update remotes URL
- `gzc-portfolio-app/webpack.common.js` - Update port in devServer

### Environment Detection

Apps detect if running in shell or standalone via:
```javascript
process.env.SHELL_CONTEXT // true in shell, false standalone
```

## Common Issues and Solutions

### Issue: "Cannot find module '@gzc/ui'"
**Solution**: Ensure gzc-ui is built (`npm run build`) and properly linked

### Issue: "Failed to fetch dynamically imported module"
**Solution**: 
1. Check all apps are running on correct ports
2. Verify CORS headers in webpack dev server config
3. Clear browser cache

### Issue: "MSAL authentication errors"
**Solution**: 
1. Verify Azure AD configuration
2. Ensure redirect URI matches exactly
3. Check browser console for specific MSAL errors

### Issue: Port conflicts
**Solution**: Use environment variables to change ports:
```bash
PORT=3002 npm start  # For CRA apps
# Or modify webpack.dev.js for webpack apps
```

## Development Workflow

### Making UI Component Changes
1. Edit component in `gzc-ui/src/components`
2. Component auto-rebuilds if running `npm run dev`
3. Changes reflect in all consuming apps

### Adding New Micro-Frontend
1. Create new app with Module Federation setup
2. Expose components in webpack config
3. Add remote to main shell webpack config
4. Create route in main shell

### Testing Integration
1. Start all required services
2. Navigate through main shell
3. Verify shared state (auth, theme, quotes)
4. Check network tab for remote loading

## Architecture Validation

To verify the setup is working correctly:

1. **Module Federation**: Check browser DevTools Network tab for `remoteEntry.js` loads
2. **Shared Dependencies**: Verify only one React instance in React DevTools
3. **Authentication**: Confirm MSAL token in Portfolio app's useAuthContext
4. **Shared UI**: Theme toggle should affect all apps
5. **WebSocket**: Quote updates should flow to Portfolio table

## Production Build

```bash
# Build all apps for production
cd gzc-ui && npm run build
cd ../gzc-portfolio-app && npm run build
cd ../gzc-main-shell && npm run build
cd ../fx-client && npm run build
```

Build outputs:
- gzc-ui: `dist/` (npm package)
- Others: `dist/` or `build/` folders with static assets

## Next Steps

1. Configure backend services (fxspotstream-backend)
2. Set up WebSocket connections for real-time data
3. Implement CI/CD pipelines
4. Configure production Azure AD app
5. Set up monitoring and error tracking

—SOFTWARE_RESEARCH_ANALYST