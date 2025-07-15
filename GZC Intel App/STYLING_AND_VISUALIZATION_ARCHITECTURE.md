# STYLING AND VISUALIZATION ARCHITECTURE
*Comprehensive analysis of UI/UX elements from both platforms*
*Created: 2025-07-05*

---

## 🎨 STYLING ANALYSIS

### Port 3000 (PMN NextGen) - Better Buttons & UI Elements
**Strengths:**
- Professional button styling with depth and gradients
- Multiple dashboard styles (Professional, NextGen, Original)
- Better visual hierarchy
- Smooth hover states and transitions
- Card-based layouts with proper shadows

**Key UI Elements:**
```typescript
// Button styles from PMS NextGen
const buttonStyles = {
  primary: {
    background: 'linear-gradient(135deg, #95BD78CC 0%, #95BD7866 100%)',
    boxShadow: '0 2px 8px rgba(149, 189, 120, 0.3)',
    transition: 'all 0.2s ease',
    ':hover': {
      transform: 'translateY(-1px)',
      boxShadow: '0 4px 12px rgba(149, 189, 120, 0.4)'
    }
  }
};
```

### Port 3200 (Production Platform) - Correct Colors & Typography
**Strengths:**
- Professional quantum theme system
- Consistent color palette
- Typography hierarchy
- Grid-based layout system
- BUT: Only trading view implemented

**Theme System:**
```typescript
// From port 3200 theme/index.ts
const theme = {
  primary: "#95BD78",      // GZC Mid Green
  background: "#0a0a0a",   // Deep black
  surface: "#1a1918",      // Subtle brown undertone
  typography: {
    h1: { fontSize: "18px", fontWeight: "600" },
    body: { fontSize: "11px", fontWeight: "400" },
    numberLarge: { fontSize: "14px", fontWeight: "500" }
  }
};
```

---

## 📊 VISUALIZATION ENGINES

### Port 3000 - Advanced Visualization Components

#### 1. **Knowledge Graph Explorer**
- Uses `react-force-graph-2d`
- Interactive node/edge visualization
- Real-time updates
- Zoom/pan capabilities

#### 2. **G10 Yield Curve Animator**
- D3.js-based animations
- Time-series playback
- Multi-curve comparison
- Smooth transitions

#### 3. **FRED Economic Dashboard**
- Multiple chart types
- Real-time data integration
- Responsive grid layout
- Custom tooltips

#### 4. **Housing Market Monitor**
- Heat maps
- Trend analysis
- Regional comparisons
- Interactive filters

### Port 3200 - Backend Integration Components

#### 1. **Analytics Demo Page**
- Collapsible panels
- Virtual scrolling for performance
- Real-time WebSocket data
- Fullscreen mode

#### 2. **Portfolio Components**
- Direct Azure PostgreSQL integration
- Real-time position calculations
- FX price streaming
- Risk metrics

---

## 🏗️ UNIFIED STYLING ARCHITECTURE

### CSS Architecture for Patches
```scss
// Base theme layer
@layer base {
  :root {
    // Core variables from port 3200
    --primary: #95BD78;
    --background: #0a0a0a;
    --surface: #1a1918;
  }
}

// Component layer
@layer components {
  // Button styles from port 3000
  .btn-primary {
    @apply bg-gradient-to-br from-primary/80 to-primary/40;
    @apply shadow-lg hover:shadow-xl;
    @apply transition-all duration-200;
    @apply hover:-translate-y-0.5;
  }
  
  // Panel styles from port 3200
  .panel {
    @apply bg-surface border border-border;
    @apply rounded-lg p-4;
  }
}

// Theme patches layer
@layer patches {
  // Professional theme patch
  [data-theme="professional"] {
    --primary: #8FB377;
    --surface: #252321;
  }
  
  // NextGen theme patch
  [data-theme="nextgen"] {
    --primary: #95BD78;
    --gradient: linear-gradient(135deg, #95BD78CC 0%, #7FA060 35%);
  }
}
```

### Component Style System
```typescript
interface StyleSystem {
  // Base styles (port 3200)
  theme: ThemeConfiguration;
  typography: TypographySystem;
  spacing: SpacingScale;
  
  // Enhanced UI (port 3000)
  buttons: ButtonVariants;
  cards: CardStyles;
  animations: AnimationPresets;
  
  // Visualization styles
  charts: ChartTheme;
  graphs: GraphStyles;
  
  // Patches
  patches: Map<string, ThemePatch>;
}
```

---

## 🎯 IMPLEMENTATION STRATEGY

### 1. Base Layer (From Port 3200)
- Typography system
- Color palette
- Spacing scale
- Grid system

### 2. Enhancement Layer (From Port 3000)
- Button animations
- Card shadows
- Hover effects
- Visual depth

### 3. Visualization Layer
```typescript
// Standardized visualization config
const visualizationConfig = {
  colors: {
    primary: theme.primary,
    secondary: theme.secondary,
    gradient: theme.gradient,
    // Chart-specific colors
    positive: theme.success,
    negative: theme.danger,
    neutral: theme.textSecondary
  },
  
  animations: {
    duration: 300,
    easing: 'easeInOutQuad',
    stagger: 50
  },
  
  interactions: {
    hover: { scale: 1.02, opacity: 0.9 },
    active: { scale: 0.98 },
    selected: { outline: `2px solid ${theme.primary}` }
  }
};
```

### 4. Backend Integration Points
```typescript
// From port 3200
interface BackendIntegrations {
  portfolio: {
    endpoint: '/api/fx-positions',
    websocket: 'ws://localhost:8000/ws',
    polling: false
  },
  
  analytics: {
    endpoint: '/api/analytics',
    cache: 'redis',
    refresh: 5000
  },
  
  pricing: {
    source: 'azure-redis',
    symbols: ['EUR/USD', 'GBP/USD'],
    frequency: 'realtime'
  }
}
```

---

## 🔄 STYLE SWITCHING MECHANISM

### Dynamic Theme Loading
```typescript
class ThemeManager {
  private currentTheme: string = 'professional';
  private patches: Map<string, ThemePatch> = new Map();
  
  async loadThemePatch(themeName: string): Promise<void> {
    // Load CSS variables
    document.documentElement.setAttribute('data-theme', themeName);
    
    // Load component overrides
    const patch = await import(`./themes/${themeName}.patch.ts`);
    this.patches.set(themeName, patch.default);
    
    // Apply to visualization engines
    this.updateVisualizationTheme(patch.default);
  }
  
  private updateVisualizationTheme(patch: ThemePatch): void {
    // Update D3 scales
    // Update chart colors
    // Update graph themes
  }
}
```

---

## 📐 COMPONENT MAPPING

### Which Components From Where

#### From Port 3000 (Visualization Focus):
1. KnowledgeGraphExplorer
2. G10YieldCurveAnimator
3. FREDEconomicDashboard
4. HousingMarketMonitor
5. Button styles and animations
6. Card layouts

#### From Port 3200 (Integration Focus):
1. AnalyticsDashboardExample
2. GZCPortfolioComponent
3. CollapsiblePanel
4. VirtualizedPriceList
5. Theme system
6. Backend connections

#### New Components Needed:
1. Unified style switcher
2. Theme patch loader
3. Visualization wrapper
4. Backend adapter layer

---

## 🎨 FINAL STYLING RULES

### Typography Hierarchy
```scss
// Professional trading UI standards
.heading-primary { @apply text-lg font-semibold; }    // 18px
.heading-secondary { @apply text-sm font-semibold; }  // 14px
.body-text { @apply text-xs font-normal; }            // 11px
.label-text { @apply text-[9px] font-medium uppercase tracking-wider; }
.number-large { @apply text-sm font-medium tabular-nums; }
```

### Color Usage
```scss
// Semantic colors
.profit { color: var(--success); }
.loss { color: var(--danger); }
.neutral { color: var(--text-secondary); }
.highlight { color: var(--primary); }
```

### Animation Standards
```scss
// Consistent animations
.transition-standard { @apply transition-all duration-200 ease-in-out; }
.hover-lift { @apply hover:-translate-y-0.5 hover:shadow-lg; }
.active-press { @apply active:scale-[0.98]; }
```

---

## 📊 VISUALIZATION STANDARDS

### Chart Configuration
```typescript
const chartDefaults = {
  margins: { top: 20, right: 30, bottom: 40, left: 50 },
  transitions: { duration: 300, easing: 'easeInOutQuad' },
  colors: d3.scaleOrdinal()
    .domain(['primary', 'secondary', 'tertiary'])
    .range([theme.primary, theme.secondary, theme.accent]),
  grid: {
    stroke: theme.border,
    strokeOpacity: 0.3,
    strokeDasharray: '2,2'
  }
};
```

### Interactive Elements
```typescript
const interactionStandards = {
  tooltip: {
    background: theme.surface,
    border: `1px solid ${theme.border}`,
    padding: '8px 12px',
    borderRadius: '4px',
    fontSize: '10px'
  },
  
  hover: {
    stroke: theme.primary,
    strokeWidth: 2,
    opacity: 0.8
  },
  
  selection: {
    fill: `${theme.primary}33`,
    stroke: theme.primary,
    strokeWidth: 1
  }
};
```

---

*This architecture ensures we capture the best styling from both platforms while maintaining flexibility for future theme patches*

—SOFTWARE_RESEARCH_ANALYST