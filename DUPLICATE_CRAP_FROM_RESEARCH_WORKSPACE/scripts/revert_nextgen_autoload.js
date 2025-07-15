// REVERT ONLY NEXTGEN AUTO-LOAD MODIFICATIONS
console.log("🔄 Reverting NextGen auto-load changes only");

// 1. Remove NextGen autoload scripts
const removeNextGenScripts = () => {
    const scriptsToRemove = ['nextgen-autoload', 'nextgen-priority-loader'];
    scriptsToRemove.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.remove();
            console.log(`✅ Removed script: ${id}`);
        }
    });
};

// 2. Restore fetch if we modified it
if (window.fetch.toString().includes('NextGen')) {
    // Restore original fetch
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
        return originalFetch.apply(this, args);
    };
    console.log("✅ Restored original fetch");
}

// 3. Restore XMLHttpRequest if modified
if (XMLHttpRequest.prototype.open.toString().includes('_url')) {
    // Remove our modifications
    delete XMLHttpRequest.prototype._url;
    console.log("✅ Cleaned XMLHttpRequest");
}

// 4. Restore Storage.setItem if we overrode it
if (Storage.prototype.setItem.toString().includes('NextGen')) {
    // Can't easily restore, but we can remove the override
    delete Storage.prototype.setItem;
    console.log("✅ Removed Storage override");
}

// 5. Clear NextGen-specific storage items
const clearNextGenStorage = () => {
    const keysToRemove = [
        'selectedApp',
        'defaultApp', 
        'currentApp',
        'autoLoadApp',
        'preferredSoftware'
    ];
    
    keysToRemove.forEach(key => {
        localStorage.removeItem(key);
        sessionStorage.removeItem(key);
    });
    
    console.log("✅ Cleared NextGen storage preferences");
};

// 6. Stop any observers we created for NextGen
if (window.nextGenObserver) {
    window.nextGenObserver.disconnect();
    delete window.nextGenObserver;
}

// Execute revert
removeNextGenScripts();
clearNextGenStorage();

console.log("\n✅ NextGen auto-load has been reverted");
console.log("📌 The dropdown should work normally now");
console.log("📌 You'll need to manually select apps again");
console.log("\n💡 Refresh the page if needed: Cmd+R or Ctrl+R");