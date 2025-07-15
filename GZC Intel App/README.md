# GZC Intel App

## Project Structure

```
GZC Intel App/
├── gzc-intel/           # Main platform project
├── reference/           # Reference implementations
│   └── alex-repos/      # Alex's original repositories
│       ├── fx-client/
│       ├── gzc-main-shell/
│       ├── gzc-portfolio-app/
│       └── gzc-ui/
└── README.md
```

## Overview

GZC Intel is a modular trading intelligence platform that combines:
- Clean UI design from genealogy project (port 3000)
- Modular architecture concepts from Alex's repos
- Simplified component registry without webpack federation
- Independent K8s deployments per component

## Architecture Goals

1. **Modular Components**: Each component can run standalone or integrated
2. **User Flexibility**: Users control their workspace layout and components
3. **Developer Friendly**: Simple templates for creating new components
4. **Production Ready**: Proper structure for enterprise deployment

## Component Philosophy

- Start as standalone app with own backend
- Test in isolation with full functionality
- Package as reusable component
- Register in component inventory
- Users select from available components

—SOFTWARE_RESEARCH_ANALYST