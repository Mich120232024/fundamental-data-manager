# EXACT USER REQUIREMENTS - GZC INTEL APP
*Based on actual user prompts and recovered work*
*Created: 2025-07-05*

---

## 🎯 CORE CONCEPT - IN USER'S WORDS

> "ok now there is soem conventions to use - for me the tab is agnostic of content we cna create a tab with a template , a component will be picked in the repo from a link on hte tab to open and load component into the tab and the nsave the structure with a name for the table and the full layout memorise for the user or global , when we create the tab we cna choose global or user"

---

## 📋 EXACT REQUIREMENTS FROM USER PROMPTS

### 1. TAB SYSTEM SPECIFICATIONS

#### Core Functionality
- **Content-agnostic tabs**: Tab is just a container, doesn't care about content
- **Template-based**: Create tab with a template
- **Component selection**: Pick component from repository via link on the tab
- **Save structure**: Save with name for the tab and full layout
- **Scope options**: Choose "global" or "user" when creating tab

#### UI Requirements
- **Single line tab bar**: "ok first we need all on one line"
- **Plus button placement**: "the editor you made is supposet to be the + next to current tabs"
- **Edit button per tab**: "ok and the edit button you made at the top should not exist - we should have one in each tab to edit the componeent list"
- **Inline editing**: "no i want to edit the tabe inside the tab not in the menu"
- **Name before save**: "we need to insiert the tabe name before closing or saving"

#### What NOT to do
- "whn i click on + tab then i still see he bad componenet - i dotn wnat to select toher tabs here but create a new one"
- Don't show existing tabs when creating new one
- Don't put edit in top menu
- Don't use menu for tab editing

### 2. COMPONENT REGISTRY SYSTEM

> "for the componeents they will come fro mthe registry and these will be either hosted wit hthe applciation in container app for the genric global ones or running on separate back ends on k8s - the user should be able to select them fo mthe list and load them in"

#### Three Component Sources:
1. **Local**: Hosted with the application
2. **Container Apps**: Generic global components
3. **Kubernetes**: Running on separate backends

#### Loading Mechanism:
- User selects from list
- Component loads into tab
- Registry maintains available components

### 3. EDIT ICON FUNCTIONALITY

> "let make this all under and edit icon that we cna expand and show us the full controler to fill and edit"

- Edit icon that expands
- Shows full controller when expanded
- Used to fill and edit tab configuration

### 4. ICON SYSTEM

- **Location**: "/Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/public/feather"
- **Requirements**: 
  - "what i need now is to find a good suite of ikons ofr financila tradign apps"
  - "cna we set gradient colors"
  - "ok the ikon are in public inside hte project do you see them"

### 5. NAVIGATION REQUIREMENTS

From PMS NextGen (Port 3000):
> "i want ot drag the componeent collapse expand and maximise them"

- Drag components
- Collapse components
- Expand components
- Maximize components

### 6. LEFT PANEL - AI MESSAGING

> "i want hte left panel but inside will be ai messaging with several tabs"

- Left panel for AI messaging
- Multiple tabs within the panel
- Integration with main workspace

### 7. ANALYTICS COMPONENT MIGRATION

> "first i wanted to import the componeents i wnat and this is not the populatio nwe have i nthe anayltics table of the other - please import them"

- Import analytics components from production platform
- Fix resize issues: "the componenet dynamic is not very fleunt like on the other"
- Need smooth transitions: "we need to adjust hte seetting in the new one as it was smooth there and really sharp flshign on resolution when rendering new size"

---

## 🚫 COMMON MISTAKES TO AVOID

### 1. Creating New Versions
> "now we need to clean up the project there are too many version"

DON'T create multiple versions - fix the one that exists

### 2. Ignoring Specific Requests
When user says:
- "edit button you made at the top should not exist" - REMOVE IT
- "i want to edit the tabe inside the tab" - PUT IT INSIDE
- "we need to insiert the tabe name before closing" - REQUIRE NAME FIRST

### 3. Component Loading Errors
User experienced:
- "Failed to load component: AnalyticsDashboardExample"
- "This site can't be reached localhost refused to connect"

Must ensure components load properly

---

## ✅ DEFINITION OF SUCCESS

1. **Tab System**
   - ✓ Single-line tab bar with + button at end
   - ✓ Click + creates new empty tab (not selection menu)
   - ✓ Each tab has own edit icon
   - ✓ Edit expands to show controller inline
   - ✓ Must name tab before saving
   - ✓ Can mark as "global" or "user" scope

2. **Components**
   - ✓ Load from registry (3 sources)
   - ✓ User selects from list
   - ✓ Component loads into tab
   - ✓ No loading errors

3. **Navigation**
   - ✓ Drag/drop like Port 3000
   - ✓ Collapse/expand
   - ✓ Maximize/minimize
   - ✓ Smooth transitions

4. **Layout**
   - ✓ Left panel with AI messaging tabs
   - ✓ Main area with component tabs
   - ✓ Professional styling
   - ✓ Feather icons with gradients

5. **Architecture**
   - ✓ Modular (like 4-module engine)
   - ✓ Vite build (not webpack)
   - ✓ Single theme provider
   - ✓ Real authentication

---

## 🎯 USER'S ULTIMATE VISION

A professional trading/analytics platform where:
1. Users can add tabs dynamically
2. Each tab loads components from a registry
3. Components can be local, containerized, or K8s-based
4. Everything is draggable, resizable, collapsible
5. Layouts persist (user or global)
6. AI messaging integrated in left panel
7. Clean, professional financial UI
8. No complexity - just what works

---

## 📝 IMPLEMENTATION PRIORITY

1. **First**: Get tab system working exactly as described
2. **Second**: Component registry and loading
3. **Third**: Drag/drop/resize functionality
4. **Fourth**: AI messaging panel
5. **Fifth**: Polish and optimization

Remember: "lets do this first" - Start with tab system!

---

*The key: Implement EXACTLY what the user asked for, not what we think is better*

—SOFTWARE_RESEARCH_ANALYST