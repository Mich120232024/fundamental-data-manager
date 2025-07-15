// FIX FOR CATEGORY DROPDOWN DRAG ISSUE - Specific to FRED Dashboard
console.log("🎯 Fixing FRED Dashboard Category Dropdown Drag Issue");

// 1. Find the specific dropdown causing issues
const findCategoryDropdown = () => {
    // Look for the Employment category dropdown
    const dropdowns = document.querySelectorAll('select, .dropdown, [role="combobox"]');
    let categoryDropdown = null;
    
    dropdowns.forEach(dropdown => {
        // Check if this is the category selector (contains "Employment" or similar)
        if (dropdown.value === 'Employment' || 
            dropdown.textContent?.includes('Employment') ||
            dropdown.options?.[0]?.text?.includes('Employment')) {
            categoryDropdown = dropdown;
            console.log("✅ Found category dropdown:", dropdown);
        }
    });
    
    return categoryDropdown;
};

// 2. Fix the drag behavior
const fixDragBehavior = (element) => {
    if (!element) return;
    
    console.log("🔧 Applying drag fix to element:", element);
    
    // Remove ALL event listeners by cloning
    const parent = element.parentNode;
    const newElement = element.cloneNode(true);
    parent.replaceChild(newElement, element);
    
    // Prevent ANY drag behavior
    newElement.style.userSelect = 'none';
    newElement.style.webkitUserSelect = 'none';
    newElement.style.userDrag = 'none';
    newElement.style.webkitUserDrag = 'none';
    newElement.draggable = false;
    
    // Fix positioning
    newElement.style.position = 'relative';
    newElement.style.transform = 'none';
    newElement.style.cursor = 'pointer';
    
    // Add proper click handler
    newElement.addEventListener('mousedown', function(e) {
        e.stopPropagation();
        e.preventDefault();
        
        // For select elements, let default behavior work
        if (this.tagName === 'SELECT') {
            return true;
        }
    }, true);
    
    // Prevent parent from interfering
    if (parent) {
        parent.style.userSelect = 'none';
        parent.style.position = 'relative';
    }
    
    return newElement;
};

// 3. Fix the entire component container
const fixComponentContainer = () => {
    // Find the FRED dashboard component
    const dashboard = document.querySelector('[class*="dashboard"], [class*="fred"], #fred-dashboard');
    if (dashboard) {
        console.log("🎯 Found dashboard container");
        
        // Prevent the entire component from being draggable
        dashboard.style.position = 'relative';
        dashboard.style.userSelect = 'none';
        dashboard.draggable = false;
        
        // Remove any transform on the container
        dashboard.style.transform = 'none';
        
        // Fix all child elements
        const allElements = dashboard.querySelectorAll('*');
        allElements.forEach(el => {
            if (el.style.position === 'absolute' && !el.classList.contains('dropdown-menu')) {
                el.style.position = 'relative';
            }
        });
    }
};

// 4. Apply comprehensive CSS fix
const applyCSS = () => {
    const style = document.createElement('style');
    style.id = 'fred-dropdown-fix';
    style.textContent = `
    /* Fix FRED Dashboard Dropdown Drag Issue */
    
    /* Prevent component dragging */
    [class*="dashboard"],
    [class*="fred"],
    .economic-indicators,
    .indicator-card {
        position: relative !important;
        transform: none !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        -webkit-user-drag: none !important;
    }
    
    /* Fix dropdowns specifically */
    select,
    .category-dropdown,
    [role="combobox"] {
        position: relative !important;
        cursor: pointer !important;
        user-select: none !important;
        -webkit-user-select: none !important;
        -webkit-user-drag: none !important;
        user-drag: none !important;
        transform: none !important;
    }
    
    /* Ensure dropdowns work properly */
    select:focus {
        outline: 2px solid #0078d4;
        outline-offset: 2px;
    }
    
    /* Prevent parent containers from being draggable */
    .category-container,
    .dropdown-container {
        position: relative !important;
        transform: none !important;
    }
    
    /* Fix any absolute positioned elements */
    .economic-indicators > * {
        position: relative !important;
    }
    `;
    
    // Remove old and add new
    const oldStyle = document.getElementById('fred-dropdown-fix');
    if (oldStyle) oldStyle.remove();
    document.head.appendChild(style);
    
    console.log("✅ Applied CSS fixes");
};

// 5. Monitor and prevent drag behavior
const preventDrag = () => {
    document.addEventListener('dragstart', function(e) {
        if (e.target.tagName === 'SELECT' || 
            e.target.classList.contains('dropdown') ||
            e.target.closest('.economic-indicators')) {
            e.preventDefault();
            console.log("🛑 Prevented drag on:", e.target);
            return false;
        }
    }, true);
    
    // Also prevent on mousedown
    document.addEventListener('mousedown', function(e) {
        if (e.target.tagName === 'SELECT') {
            e.stopPropagation();
            console.log("✅ Allowing normal select behavior");
        }
    }, true);
};

// 6. EXECUTE ALL FIXES
console.log("🚀 Applying all fixes...\n");

// Apply CSS first
applyCSS();

// Fix component container
fixComponentContainer();

// Find and fix the specific dropdown
const categoryDropdown = findCategoryDropdown();
if (categoryDropdown) {
    fixDragBehavior(categoryDropdown);
    console.log("✅ Fixed category dropdown");
} else {
    // Fix all dropdowns if specific one not found
    console.log("⚠️ Fixing all dropdowns...");
    document.querySelectorAll('select').forEach(select => {
        fixDragBehavior(select);
    });
}

// Prevent future drag behavior
preventDrag();

// Re-apply fixes after a delay (for dynamic content)
setTimeout(() => {
    const dropdown = findCategoryDropdown();
    if (dropdown) fixDragBehavior(dropdown);
    fixComponentContainer();
}, 1000);

console.log("\n✅ FRED DROPDOWN FIX COMPLETE");
console.log("📋 The Employment dropdown should now work properly");
console.log("📋 Component should no longer move with mouse");