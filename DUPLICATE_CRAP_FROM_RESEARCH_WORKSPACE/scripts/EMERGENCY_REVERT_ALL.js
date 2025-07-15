// EMERGENCY REVERT - Undo all modifications
console.log("🚨 EMERGENCY REVERT - Removing all modifications");

// 1. Remove all injected styles
const removeAllStyles = () => {
    // Remove our custom style elements
    const customStyles = [
        'global-dropdown-fix',
        'rendering-fixes',
        'nextgen-autoload',
        'trading-default-override',
        'nextgen-trading-defaults'
    ];
    
    customStyles.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
            console.log(`✅ Removed style: ${id}`);
        }
    });
    
    // Also remove any style tags we might have added
    document.querySelectorAll('style').forEach(style => {
        if (style.textContent.includes('GLOBAL DROPDOWN') || 
            style.textContent.includes('Trading Operations') ||
            style.textContent.includes('NextGen')) {
            style.remove();
            console.log("✅ Removed injected style tag");
        }
    });
};

// 2. Restore original functions
const restoreOriginalFunctions = () => {
    // Restore fetch if we modified it
    if (window.originalFetch) {
        window.fetch = window.originalFetch;
        delete window.originalFetch;
        console.log("✅ Restored original fetch");
    }
    
    // Restore React hooks if modified
    if (window.React && window.originalUseState) {
        window.React.useState = window.originalUseState;
        delete window.originalUseState;
        console.log("✅ Restored React.useState");
    }
    
    // Restore localStorage.setItem if modified
    if (Storage.prototype.originalSetItem) {
        Storage.prototype.setItem = Storage.prototype.originalSetItem;
        delete Storage.prototype.originalSetItem;
        console.log("✅ Restored Storage.setItem");
    }
    
    // Restore XMLHttpRequest if modified
    if (XMLHttpRequest.prototype.originalOpen) {
        XMLHttpRequest.prototype.open = XMLHttpRequest.prototype.originalOpen;
        XMLHttpRequest.prototype.send = XMLHttpRequest.prototype.originalSend;
        delete XMLHttpRequest.prototype.originalOpen;
        delete XMLHttpRequest.prototype.originalSend;
        console.log("✅ Restored XMLHttpRequest");
    }
};

// 3. Remove event listeners and observers
const removeObservers = () => {
    // Stop all mutation observers we created
    if (window.dropdownObserver) {
        window.dropdownObserver.disconnect();
        delete window.dropdownObserver;
        console.log("✅ Removed dropdown observer");
    }
    
    if (window.customObservers) {
        window.customObservers.forEach(obs => obs.disconnect());
        delete window.customObservers;
        console.log("✅ Removed custom observers");
    }
};

// 4. Clear localStorage modifications
const clearStorageModifications = () => {
    // Remove our custom keys
    const keysToRemove = [
        'defaultTab',
        'defaultTabIndex',
        'defaultTabName',
        'defaultApp',
        'defaultSoftware',
        'preferredSoftware',
        'preferredLayout',
        'layoutMode',
        'selectedApp',
        'currentApp',
        'autoLoadApp'
    ];
    
    keysToRemove.forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
    });
    
    console.log("✅ Cleared storage modifications");
};

// 5. Remove global functions we added
const removeGlobalFunctions = () => {
    const functionsToRemove = [
        'debugDropdowns',
        'resetDropdownFixes',
        'setDefaultTab',
        'loadFREDData',
        'debugLoadData',
        'quickRenderFix'
    ];
    
    functionsToRemove.forEach(func => {
        if (window[func]) {
            delete window[func];
            console.log(`✅ Removed function: ${func}`);
        }
    });
};

// 6. Reset inline styles we modified
const resetInlineStyles = () => {
    // Remove forced styles on components
    document.querySelectorAll('[style]').forEach(element => {
        // Check if we modified this element
        if (element.style.cssText.includes('!important') && 
            (element.style.height === 'auto' || 
             element.style.overflow === 'visible' ||
             element.style.cursor === 'pointer')) {
            
            // Remove our modifications
            element.style.height = '';
            element.style.overflow = '';
            element.style.cursor = '';
            element.style.pointerEvents = '';
            element.style.userSelect = '';
            element.style.minHeight = '';
            element.style.maxHeight = '';
        }
    });
    
    console.log("✅ Reset inline styles");
};

// 7. Reload clean state
const reloadCleanState = () => {
    console.log("\n🔄 Preparing to reload page for clean state...");
    console.log("⚠️  Press OK to reload the page");
    
    if (confirm("Reload page to complete revert?")) {
        // Clear everything and reload
        sessionStorage.clear();
        location.reload(true); // Force reload from server
    }
};

// EXECUTE ALL REVERT ACTIONS
console.log("🔧 Starting revert process...\n");

removeAllStyles();
restoreOriginalFunctions();
removeObservers();
clearStorageModifications();
removeGlobalFunctions();
resetInlineStyles();

console.log("\n✅ REVERT COMPLETE");
console.log("📌 All custom modifications have been removed");
console.log("📌 Original functionality should be restored");
console.log("\n💡 If issues persist, reload the page (Cmd+R or Ctrl+R)");

// Option to force reload
setTimeout(() => {
    console.log("\n❓ Still having issues?");
    console.log("💡 Type: location.reload(true) to force a clean reload");
}, 2000);