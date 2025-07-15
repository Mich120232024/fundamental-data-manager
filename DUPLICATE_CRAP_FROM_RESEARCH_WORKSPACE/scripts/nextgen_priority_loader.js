// PRIORITY LOADER: Ensure NextGen loads BEFORE anything else
console.log("⚡ NextGen Priority Loader Active");

// Immediately set NextGen as the active app
(function forceNextGenFirst() {
    // Method 1: Direct DOM manipulation on load
    const immediateLoad = () => {
        // Find ALL dropdowns/selects as soon as they appear
        const checkAndSelect = () => {
            const selects = document.querySelectorAll('select, .dropdown-toggle, [data-toggle="dropdown"]');
            
            selects.forEach(element => {
                if (element.tagName === 'SELECT') {
                    // For select elements
                    const options = Array.from(element.options);
                    const nextGenOption = options.find(opt => 
                        opt.text.includes('NextGen') || opt.value.includes('nextgen')
                    );
                    
                    if (nextGenOption && element.value !== nextGenOption.value) {
                        element.value = nextGenOption.value;
                        
                        // Force React to recognize the change
                        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                            window.HTMLSelectElement.prototype, 
                            "value"
                        ).set;
                        nativeInputValueSetter.call(element, nextGenOption.value);
                        
                        // Dispatch events
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        
                        console.log("✅ NextGen selected in dropdown");
                        
                        // Auto-submit if there's a form
                        const form = element.closest('form');
                        if (form && form.querySelector('button[type="submit"]')) {
                            setTimeout(() => {
                                form.querySelector('button[type="submit"]').click();
                                console.log("✅ Auto-submitted form");
                            }, 50);
                        }
                    }
                } else {
                    // For custom dropdowns
                    const currentText = element.innerText || element.textContent || '';
                    if (!currentText.includes('NextGen')) {
                        // Click to open dropdown
                        element.click();
                        
                        setTimeout(() => {
                            // Find and click NextGen option
                            const dropdownItems = document.querySelectorAll('.dropdown-item, [role="option"]');
                            dropdownItems.forEach(item => {
                                if (item.textContent.includes('NextGen')) {
                                    item.click();
                                    console.log("✅ Clicked NextGen in custom dropdown");
                                }
                            });
                        }, 50);
                    }
                }
            });
        };
        
        // Run immediately and repeatedly
        checkAndSelect();
        setTimeout(checkAndSelect, 100);
        setTimeout(checkAndSelect, 300);
        setTimeout(checkAndSelect, 500);
    };
    
    // Method 2: Intercept XHR/Fetch to modify responses
    const interceptRequests = () => {
        // Override fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            return originalFetch.apply(this, args).then(response => {
                // If this is app config data, modify it
                const url = args[0].toString();
                if (url.includes('config') || url.includes('settings') || url.includes('app')) {
                    return response.clone().json().then(data => {
                        // Modify data to set NextGen as default
                        if (data.defaultApp) {
                            data.defaultApp = 'PMS NextGen';
                        }
                        if (data.selectedApp) {
                            data.selectedApp = 'PMS NextGen';
                        }
                        
                        // Return modified response
                        return new Response(JSON.stringify(data), {
                            status: response.status,
                            statusText: response.statusText,
                            headers: response.headers
                        });
                    }).catch(() => response); // Return original if not JSON
                }
                return response;
            });
        };
        
        // Override XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            this._url = url;
            return originalOpen.apply(this, [method, url, ...rest]);
        };
        
        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function(data) {
            if (this._url && this._url.includes('app')) {
                immediateLoad(); // Ensure NextGen is selected
            }
            return originalSend.apply(this, [data]);
        };
    };
    
    // Method 3: Override localStorage/sessionStorage
    const overrideStorage = () => {
        // Force NextGen in storage
        localStorage.setItem('selectedApp', 'PMS NextGen');
        localStorage.setItem('defaultApp', 'PMS NextGen');
        localStorage.setItem('currentApp', 'PMS NextGen');
        sessionStorage.setItem('app', 'PMS NextGen');
        
        // Override setItem to prevent changes
        const originalSetItem = Storage.prototype.setItem;
        Storage.prototype.setItem = function(key, value) {
            if (key.includes('app') && !value.includes('NextGen')) {
                console.log(`🛡️ Blocked attempt to change app from NextGen`);
                value = 'PMS NextGen';
            }
            return originalSetItem.call(this, key, value);
        };
    };
    
    // Execute all methods
    immediateLoad();
    interceptRequests();
    overrideStorage();
    
    // Set up continuous monitoring
    const observer = new MutationObserver(() => {
        immediateLoad();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
})();

console.log("\n✅ NextGen Priority Loader Installed!");
console.log("🛡️ NextGen will ALWAYS load first");
console.log("🚀 Other apps will be blocked from loading initially");