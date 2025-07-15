# USER REQUIREMENTS & PROJECT GENEALOGY
*Created: 2025-07-05*
*Purpose: Document what the USER actually wants and the complete history of attempts*

---

## 🎯 WHAT THE USER WANTS

### Core Vision
A professional trading/analytics application with:
1. **Flexible Component System**
   - Drag, drop, resize, collapse, expand, maximize components
   - Save layouts (user-specific or global)
   - Dynamic loading from component registry

2. **Tab System Requirements** (from recovered prompts)
   - Content-agnostic templates
   - Components picked from repository via link on tab
   - Edit icon that expands to show full controller
   - Create tabs as either "global" or "user" specific
   - Tab name editing inline (not in menu)
   - Individual edit button per tab (NOT global)
   - Clean single-line tab bar with + button

3. **Component Registry**
   - Components from 3 sources:
     - Local (with application)
     - Container apps (generic global)
     - Kubernetes (user-specific backends)
   - User selects from list and loads into tabs

4. **Left Panel - AI Messaging** (NEW)
   - Multiple AI conversation tabs
   - Integration with workspace
   - Collapsible design

5. **Icon System**
   - Feather icons (already downloaded in /public/feather)
   - Support for gradient colors
   - Professional financial trading aesthetic

---

## 📚 PROJECT GENEALOGY - THE FULL STORY

### 1. **Original Vision** (Week 1)
- Started with idea of modular, flexible trading platform
- Wanted drag/drop functionality like professional trading systems
- Clean, modern UI with dark theme

### 2. **Port 3000 - PMN NextGen** (Reference Model)
- ✅ PERFECT navigation and flexibility
- ✅ Drag/drop/resize works beautifully
- ✅ Grid layout with persistence
- ❌ BUT: Not modular architecture
- **Status**: FORBIDDEN TO CHANGE - Reference only

### 3. **Production Engine** (4-Module Architecture)
- Created by Alex
- Clean separation:
  - Shell (main container)
  - UI (shared components)
  - Portfolio (feature module)
  - FX Client (trading module)
- ✅ Good architecture pattern
- ❌ BUT: Uses Webpack, complex module federation

### 4. **Port 3200 - First Integration Attempt**
- Tried to merge modular architecture with good UI
- ✅ Has correct styling
- ✅ Analytics demo works
- ❌ BUT: Navigation broken, dual providers issue
- **Status**: Still running, partially working

### 5. **Port 3600 - Second Attempt** (DELETED)
- User quote: "i confirm i will completely delete your entire work on this project"
- Why deleted:
  - Agent "repeatedly ignored systematic task requests"
  - "deviated from requirements without transparency"
  - Lost user trust
- **Status**: DELETED by user

### 6. **Port 3500 - Current GZC Intel App**
- Latest attempt, currently active
- Has same "Port 3200 Pattern":
  - Dual theme providers
  - Hardcoded mock auth
  - 8 layers of provider nesting
- **Status**: At risk of deletion if not fixed

---

## 🔴 WHY PREVIOUS ATTEMPTS FAILED

### Pattern 1: "Over-Engineering"
- Agents added complexity instead of solving simple problems
- Created multiple versions instead of fixing one
- Lost sight of user requirements

### Pattern 2: "Ignoring User Requests"
- User asked for specific features
- Agents did something "better" instead
- Result: User's actual needs not met

### Pattern 3: "Provider Hell"
- Multiple theme providers
- Nested contexts 7-8 levels deep
- Hardcoded mocks preventing real implementation

### Pattern 4: "Navigation Breakdown"
- Working navigation from Port 3000 got broken
- Instead of preserving what worked, created new problems
- Lost the core functionality user loved

---

## 📋 SPECIFIC USER QUOTES TO REMEMBER

1. **On Tab System**:
   > "for the tabs i will nee to add a new tab at uyer request this is a template to howst ocmponenet fro mthe repositry"

2. **On Components**:
   > "for the componeents they will come fro mthe registry and these will be either hosted wit hthe applciation in container app for the genric global ones or running on separate back ends on k8s"

3. **On Edit Controls**:
   > "ok and the edit button you made at the top should not exist - we should have one in each tab to edit the componeent list"

4. **On Tab Creation**:
   > "we need to insiert the tabe name before closing or saving"

5. **On Icons**:
   > "ok the ikon are in public inside hte project do you see them /Users/mikaeleage/Projects Container/GZC Intel App/gzc-intel/public/feather"

6. **On Left Panel**:
   > "i want ot drag the componeent collapse expand and maximise them - so i would suggest o completely first ananyls thise requriements , create a porject md file and then ananyle all the others point by point to udnerstnd what is the correct architecture for this - i want hte left panel but inside will be ai messaging with several tabs"

---

## ⚠️ CRITICAL LESSONS

1. **PRESERVE WHAT WORKS**
   - Port 3000 navigation is perfect - replicate it exactly
   - Don't "improve" - implement what's requested

2. **COMPLETE USER REQUESTS**
   - If user asks for inline editing, don't put it in a menu
   - If user wants individual controls, don't make them global
   - If user specifies exact behavior, deliver it exactly

3. **AVOID COMPLEXITY**
   - Single theme provider, not dual
   - Real auth, not mocks
   - Clean architecture, not 8-level nesting

4. **TRANSPARENCY**
   - Tell user exactly what you're doing
   - Don't deviate without asking
   - Complete one thing before moving to next

---

## 🎯 SUCCESS LOOKS LIKE

1. **Navigation**: Works exactly like Port 3000 (drag/drop/resize)
2. **Architecture**: Clean modules like Production Engine but with Vite
3. **Styling**: Professional like Port 3200 but without the bugs
4. **Tabs**: Dynamic system exactly as user described
5. **Components**: Registry-based loading from 3 sources
6. **Left Panel**: AI messaging with multiple tabs
7. **Icons**: Feather icons with gradients
8. **Trust**: User can rely on implementation matching requirements

---

## 🚫 WHAT NOT TO DO

1. Don't create multiple versions - fix the one that exists
2. Don't add features user didn't ask for
3. Don't use complex patterns (module federation, dual providers)
4. Don't claim success without user verification
5. Don't move on until current feature works completely

---

## 📊 CURRENT STATE SUMMARY

- **Port 3000**: Reference implementation (don't touch)
- **Port 3200**: Partially working, has styling
- **Port 3500**: Current attempt, has critical issues
- **Port 3600**: Deleted due to agent failures
- **User Trust**: Damaged, needs rebuilding through exact delivery

---

## 🎯 NEXT STEPS

1. Understand EXACTLY what user wants for each feature
2. Analyze WHY previous attempts failed
3. Create implementation plan that:
   - Preserves working features
   - Implements user requirements exactly
   - Avoids all identified anti-patterns
   - Rebuilds trust through transparency

---

*The key to success: Listen to what the user ACTUALLY wants, not what we think they need*

—SOFTWARE_RESEARCH_ANALYST