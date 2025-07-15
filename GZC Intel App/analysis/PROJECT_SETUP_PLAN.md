# GZC Intel Project Setup Plan

## Analysis Date: 2025-07-03
**Port Assignment**: 3500 (clean separation from existing projects)
**Policy**: Read/copy from existing projects, no modifications to source

## 🚢 Port Strategy

### Port Allocation:
- **Port 3000**: fx-client-reproduction (untouched - reference only)
- **Port 3200**: gzc-production-platform-vite (untouched - reference only)
- **Port 3500**: **GZC Intel** (our new platform)

### Benefits of Port 3500:
- ✅ **Clean isolation** - No conflicts with existing projects
- ✅ **Reference preservation** - Can compare side-by-side during development
- ✅ **Safe development** - No risk of breaking working projects
- ✅ **Easy testing** - Can run multiple projects simultaneously for comparison

## 📋 Setup Implementation Plan

### Phase 1: Project Initialization
```bash
cd "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel"

# Initialize Vite React TypeScript project
npm create vite@latest . -- --template react-ts

# Install styling dependencies (exact versions from analysis)
npm install bootstrap@^5.3.7 \
            framer-motion@^12.19.1 \
            react-grid-layout@^1.5.1 \
            react-force-graph-2d@^1.27.1 \
            lightweight-charts@^5.0.7

# Install Tailwind and PostCSS
npm install -D tailwindcss@^3.4.0 \
               @tailwindcss/forms@^0.5.7 \
               @tailwindcss/typography@^0.5.10 \
               autoprefixer@^10.4.16 \
               postcss@^8.4.32

# Configure Vite for port 3500
```

### Phase 2: Vite Configuration
```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3500,
    host: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@ui': path.resolve(__dirname, './src/ui-library'),
      '@themes': path.resolve(__dirname, './src/themes'),
      '@registry': path.resolve(__dirname, './src/registry')
    }
  },
  css: {
    postcss: './postcss.config.js'
  }
})
```

### Phase 3: Directory Structure
```
gzc-intel/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── src/
│   ├── main.tsx              # Entry point
│   ├── App.tsx               # Main app component
│   ├── themes/               # Theme system (from port 3000)
│   │   ├── index.ts
│   │   ├── professional.ts
│   │   ├── institutional.ts
│   │   └── enterprise.ts
│   ├── ui-library/           # Shared components (from gzc-ui)
│   │   ├── components/
│   │   ├── context/
│   │   └── types/
│   ├── components/           # Main application components
│   │   ├── layout/
│   │   ├── dashboard/
│   │   └── widgets/
│   ├── registry/             # Component registry system
│   │   ├── index.ts
│   │   ├── ComponentRegistry.tsx
│   │   └── types.ts
│   ├── styles/               # Global styles
│   │   ├── globals.css
│   │   ├── bootstrap-overrides.css
│   │   └── tailwind.css
│   └── utils/                # Utility functions
└── public/                   # Static assets
```

### Phase 4: Copy Strategy (Read-Only from Sources)

#### From Port 3000 (fx-client-reproduction):
```bash
# Copy theme system
cp -r "/Users/mikaeleage/Projects Container/fx-client-reproduction/src/themes/" \
      "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/src/themes/"

# Copy component patterns
cp "/Users/mikaeleage/Projects Container/fx-client-reproduction/src/components/KnowledgeGraphExplorer.tsx" \
   "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/src/components/"

# Copy styling approach
cp "/Users/mikaeleage/Projects Container/fx-client-reproduction/src/index.css" \
   "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/src/styles/reference.css"
```

#### From Port 3200 (gzc-production-platform-vite):
```bash
# Copy Tailwind configuration
cp "/Users/mikaeleage/Projects Container/gzc-production-platform-vite/tailwind.config.js" \
   "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/"

# Copy PostCSS configuration  
cp "/Users/mikaeleage/Projects Container/gzc-production-platform-vite/postcss.config.js" \
   "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/"

# Copy component structure patterns
cp -r "/Users/mikaeleage/Projects Container/gzc-production-platform-vite/src/components/DashboardContainer.tsx" \
      "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/src/components/"
```

#### From Alex's Repos (reference/alex-repos):
```bash
# Copy UI library components
cp -r "/Users/mikaeleage/Projects Container/GZC Intel App/reference/alex-repos/gzc-ui/src/" \
      "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/src/ui-library/"

# Copy TypeScript interfaces
cp "/Users/mikaeleage/Projects Container/GZC Intel App/reference/alex-repos/gzc-portfolio-app/src/types/" \
   "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/src/types/"
```

## 🔧 Development Workflow

### Daily Development:
1. **Start GZC Intel**: `cd gzc-intel && npm run dev` (port 3500)
2. **Reference comparison**: Open port 3000 and 3200 in other tabs
3. **Copy components**: Read from source projects, adapt for GZC Intel
4. **Test in isolation**: All testing happens on port 3500

### Component Migration Process:
```typescript
// 1. Identify component in source project
// Port 3000: KnowledgeGraphExplorer.tsx

// 2. Create in GZC Intel with registry integration
// src/components/KnowledgeGraphExplorer/index.tsx
export const KnowledgeGraphExplorer = () => {
  // Copy implementation from port 3000
  // Adapt for GZC Intel theme system
  // Add to component registry
}

// 3. Register component
// src/registry/components.ts
export const componentManifest = {
  'knowledge-graph': {
    name: 'Knowledge Graph Explorer',
    load: () => import('../components/KnowledgeGraphExplorer'),
    category: 'Analytics'
  }
}
```

## 📊 Progress Tracking

### Development Phases:
- [ ] **Phase 1**: Project setup on port 3500
- [ ] **Phase 2**: Theme system migration (from port 3000)
- [ ] **Phase 3**: UI library setup (from Alex's gzc-ui)
- [ ] **Phase 4**: Component registry implementation
- [ ] **Phase 5**: First component migration (Knowledge Graph)
- [ ] **Phase 6**: Dashboard layout (from port 3200)
- [ ] **Phase 7**: Animation system (from port 3000)
- [ ] **Phase 8**: Grid system integration

### Success Criteria:
- ✅ GZC Intel runs smoothly on port 3500
- ✅ All styling from port 3000 and 3200 preserved
- ✅ Component registry works with dynamic loading
- ✅ No modifications to source projects
- ✅ Side-by-side comparison possible

## 🚀 Next Steps

1. **Initialize project** on port 3500
2. **Configure Vite** with proper aliases and settings
3. **Set up styling pipeline** (Bootstrap + Tailwind)
4. **Create base theme system**
5. **Implement component registry**
6. **Begin component migration**

---

**Analysis By**: SOFTWARE_RESEARCH_ANALYST  
**Port**: 3500 (GZC Intel exclusive)  
**Policy**: Read-only access to source projects, clean development environment