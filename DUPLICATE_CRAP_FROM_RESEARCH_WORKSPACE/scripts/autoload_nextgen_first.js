// AUTO-LOAD NEXTGEN FIRST - Run NextGen immediately on page load
console.log("🚀 Auto-loading NextGen Website First");

// PART 1: Force NextGen selection and trigger load
const forceNextGenLoad = () => {
    console.log("⚡ Forcing NextGen to load immediately...");
    
    // Find the software/app selector
    const selectors = document.querySelectorAll('select, .dropdown, [role="combobox"]');
    
    selectors.forEach(selector => {
        // Check if this contains NextGen option
        let nextGenOption = null;
        let nextGenValue = null;
        
        if (selector.tagName === 'SELECT') {
            // Standard select dropdown
            for (let i = 0; i < selector.options.length; i++) {
                const option = selector.options[i];
                const text = option.text || option.innerText || '';
                if (text.includes('NextGen') || text === 'PMS NextGen') {
                    nextGenOption = option;
                    nextGenValue = option.value;
                    
                    // Set it immediately
                    selector.value = nextGenValue;
                    option.selected = true;
                    
                    console.log(`✅ Selected NextGen: ${text}`);
                    
                    // Trigger all possible events to force load
                    ['change', 'input', 'select'].forEach(eventType => {
                        const event = new Event(eventType, { 
                            bubbles: true, 
                            cancelable: true 
                        });
                        selector.dispatchEvent(event);
                    });
                    
                    // Also trigger React/Vue events
                    if (selector._valueTracker) {
                        selector._valueTracker.setValue('');
                    }
                    selector.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    break;
                }
            }
        } else {
            // Custom dropdown - find and click NextGen
            const items = selector.parentElement.querySelectorAll('.dropdown-item, [role="option"]');
            items.forEach(item => {
                const text = item.innerText || item.textContent || '';
                if (text.includes('NextGen') || text === 'PMS NextGen') {
                    // Click it immediately
                    item.click();
                    console.log(`✅ Clicked NextGen option: ${text}`);
                    
                    // Also trigger mousedown/mouseup for better compatibility
                    ['mousedown', 'mouseup', 'click'].forEach(eventType => {
                        item.dispatchEvent(new MouseEvent(eventType, {
                            bubbles: true,
                            cancelable: true
                        }));
                    });
                }
            });
        }
    });
    
    // Also try to find and trigger any load/submit buttons
    const loadButtons = document.querySelectorAll('button[type="submit"], button:contains("Load"), button:contains("Go"), button:contains("Apply")');
    loadButtons.forEach(button => {
        const text = button.innerText || button.textContent || '';
        if (text.match(/load|go|apply|submit/i)) {
            setTimeout(() => {
                button.click();
                console.log(`✅ Clicked load button: ${text}`);
            }, 100);
        }
    });
};

// PART 2: Override page initialization
const overrideInit = () => {
    console.log("🔧 Overriding page initialization...");
    
    // Intercept common initialization patterns
    
    // Override jQuery ready
    if (window.$ && window.$.fn) {
        const originalReady = window.$.fn.ready;
        window.$.fn.ready = function(fn) {
            const wrappedFn = function() {
                forceNextGenLoad(); // Run our code first
                if (fn) fn.apply(this, arguments);
            };
            return originalReady.call(this, wrappedFn);
        };
    }
    
    // Override DOMContentLoaded
    const originalAddEventListener = document.addEventListener;
    document.addEventListener = function(type, listener, options) {
        if (type === 'DOMContentLoaded') {
            const wrappedListener = function(event) {
                forceNextGenLoad(); // Run our code first
                listener.call(this, event);
            };
            return originalAddEventListener.call(this, type, wrappedListener, options);
        }
        return originalAddEventListener.call(this, type, listener, options);
    };
    
    // Override React useEffect for initial load
    if (window.React && window.React.useEffect) {
        const originalUseEffect = window.React.useEffect;
        let firstEffect = true;
        window.React.useEffect = function(effect, deps) {
            if (firstEffect && (!deps || deps.length === 0)) {
                firstEffect = false;
                const wrappedEffect = function() {
                    forceNextGenLoad();
                    return effect.apply(this, arguments);
                };
                return originalUseEffect.call(this, wrappedEffect, deps);
            }
            return originalUseEffect.call(this, effect, deps);
        };
    }
};

// PART 3: Persistent auto-load script
const createPersistentAutoload = () => {
    const script = document.createElement('script');
    script.id = 'nextgen-autoload';
    script.textContent = `
    // NextGen Auto-Load on Every Page Load
    (function() {
        const autoLoadNextGen = () => {
            // Find and select NextGen immediately
            const selects = document.querySelectorAll('select');
            for (const select of selects) {
                for (const option of select.options) {
                    if (option.text.includes('NextGen')) {
                        select.value = option.value;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        // Auto-submit if there's a form
                        const form = select.closest('form');
                        if (form) {
                            setTimeout(() => form.submit(), 100);
                        }
                        
                        console.log('✅ NextGen auto-loaded');
                        return true;
                    }
                }
            }
            return false;
        };
        
        // Try multiple times to ensure it loads
        const attempts = [0, 100, 300, 500, 1000];
        attempts.forEach(delay => {
            setTimeout(autoLoadNextGen, delay);
        });
        
        // Also set as default in storage
        localStorage.setItem('defaultApp', 'PMS NextGen');
        localStorage.setItem('autoLoadApp', 'true');
        sessionStorage.setItem('currentApp', 'PMS NextGen');
    })();
    `;
    
    // Remove old and add new
    const existing = document.getElementById('nextgen-autoload');
    if (existing) existing.remove();
    document.head.appendChild(script);
};

// PART 4: Monitor for app switching
const preventAppSwitch = () => {
    // Monitor select changes to keep NextGen selected
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
                const element = mutation.target;
                if (element.tagName === 'SELECT') {
                    const selectedText = element.options[element.selectedIndex]?.text || '';
                    if (!selectedText.includes('NextGen')) {
                        // Switch back to NextGen
                        for (let i = 0; i < element.options.length; i++) {
                            if (element.options[i].text.includes('NextGen')) {
                                element.value = element.options[i].value;
                                console.log("🔄 Switched back to NextGen");
                                break;
                            }
                        }
                    }
                }
            }
        });
    });
    
    // Observe all selects
    document.querySelectorAll('select').forEach(select => {
        observer.observe(select, { attributes: true });
    });
};

// PART 5: Execute everything
console.log("🎯 Implementing NextGen auto-load...\n");

// Apply overrides first
overrideInit();

// Force load immediately
forceNextGenLoad();

// Create persistent script
createPersistentAutoload();

// Set up monitoring
setTimeout(preventAppSwitch, 1000);

// Try again at intervals
[500, 1000, 2000].forEach(delay => {
    setTimeout(forceNextGenLoad, delay);
});

// Also intercept any AJAX/fetch that might load app data
const originalFetch = window.fetch;
window.fetch = function(...args) {
    // If fetching app data, ensure NextGen is selected
    if (args[0] && args[0].toString().includes('app')) {
        forceNextGenLoad();
    }
    return originalFetch.apply(this, args);
};

console.log("✅ NextGen will now load FIRST automatically!");
console.log("💡 The page will always start with NextGen selected");
console.log("💡 No need to manually select it from the dropdown");