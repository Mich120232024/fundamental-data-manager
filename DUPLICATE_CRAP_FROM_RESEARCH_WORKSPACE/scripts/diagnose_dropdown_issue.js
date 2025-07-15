// PROPER DIAGNOSIS - Let's understand what's actually happening
console.log("🔍 DIAGNOSING DROPDOWN ISSUE - Not assuming, CHECKING");

// 1. Identify the problematic dropdown
console.log("\n1️⃣ FINDING THE PROBLEMATIC DROPDOWN:");
document.addEventListener('mousedown', function diagnoseClick(e) {
    if (e.target.tagName === 'SELECT' || e.target.classList.contains('dropdown')) {
        console.log("🎯 Clicked element:", {
            element: e.target,
            tagName: e.target.tagName,
            classes: e.target.className,
            id: e.target.id,
            computedPosition: getComputedStyle(e.target).position,
            parentPosition: getComputedStyle(e.target.parentElement).position,
            hasEventListeners: e.target.onclick || e.target.onmousedown
        });
        
        // Check what's listening to this element
        const listeners = getEventListeners ? getEventListeners(e.target) : 'Cannot detect (use Chrome DevTools)';
        console.log("📡 Event listeners:", listeners);
        
        // Track mouse position
        console.log("🖱️ Mouse position:", { x: e.clientX, y: e.clientY });
        
        // Check if element moves
        const originalPos = e.target.getBoundingClientRect();
        setTimeout(() => {
            const newPos = e.target.getBoundingClientRect();
            if (originalPos.left !== newPos.left || originalPos.top !== newPos.top) {
                console.error("❌ ELEMENT MOVED!", {
                    original: originalPos,
                    new: newPos,
                    delta: {
                        x: newPos.left - originalPos.left,
                        y: newPos.top - originalPos.top
                    }
                });
            }
        }, 100);
    }
}, true);

// 2. Monitor for drag behavior
let isDragging = false;
let dragElement = null;

document.addEventListener('mousedown', function(e) {
    if (e.target.tagName === 'SELECT' || e.target.classList.contains('dropdown')) {
        isDragging = true;
        dragElement = e.target;
        console.log("🚨 DRAG START DETECTED on:", dragElement);
    }
}, true);

document.addEventListener('mousemove', function(e) {
    if (isDragging && dragElement) {
        console.error("❌ DRAG BEHAVIOR DETECTED!", {
            element: dragElement,
            mousePos: { x: e.clientX, y: e.clientY },
            elementStyle: {
                position: dragElement.style.position,
                left: dragElement.style.left,
                top: dragElement.style.top,
                transform: dragElement.style.transform
            }
        });
        
        // Check parent containers
        let parent = dragElement.parentElement;
        while (parent && parent !== document.body) {
            if (parent.style.position || getComputedStyle(parent).position !== 'static') {
                console.warn("⚠️ Parent with positioning:", {
                    element: parent,
                    position: getComputedStyle(parent).position,
                    transform: getComputedStyle(parent).transform
                });
            }
            parent = parent.parentElement;
        }
    }
});

document.addEventListener('mouseup', function() {
    if (isDragging) {
        console.log("🛑 DRAG END");
        isDragging = false;
        dragElement = null;
    }
});

// 3. Check for CSS that might cause sticking
console.log("\n2️⃣ CHECKING CSS RULES:");
const selects = document.querySelectorAll('select, .dropdown');
selects.forEach((select, i) => {
    const computed = getComputedStyle(select);
    const problematicStyles = {
        position: computed.position,
        cursor: computed.cursor,
        userSelect: computed.userSelect,
        pointerEvents: computed.pointerEvents,
        transform: computed.transform,
        willChange: computed.willChange,
        zIndex: computed.zIndex
    };
    
    // Flag potential issues
    if (computed.position === 'absolute' || computed.position === 'fixed') {
        console.warn(`⚠️ Dropdown ${i} has position: ${computed.position}`);
    }
    if (computed.cursor !== 'pointer' && computed.cursor !== 'default') {
        console.warn(`⚠️ Dropdown ${i} has unusual cursor: ${computed.cursor}`);
    }
    if (computed.transform !== 'none') {
        console.warn(`⚠️ Dropdown ${i} has transform: ${computed.transform}`);
    }
    
    console.log(`Dropdown ${i} styles:`, problematicStyles);
});

// 4. Detect framework
console.log("\n3️⃣ DETECTING FRAMEWORK:");
const frameworkDetection = {
    React: !!(window.React || document.querySelector('[data-reactroot]')),
    Vue: !!(window.Vue || document.querySelector('#app').__vue__),
    Angular: !!(window.ng || document.querySelector('[ng-version]')),
    jQuery: !!(window.jQuery || window.$)
};
console.log("Frameworks detected:", frameworkDetection);

// 5. Test fix
window.testFix = function() {
    console.log("\n🔧 TESTING TARGETED FIX:");
    
    // Find the problematic dropdown
    const dropdowns = document.querySelectorAll('select, .dropdown');
    dropdowns.forEach(dropdown => {
        // Remove any transform
        dropdown.style.transform = 'none';
        
        // Ensure proper positioning
        if (getComputedStyle(dropdown).position === 'absolute') {
            dropdown.style.position = 'relative';
        }
        
        // Remove drag behavior
        dropdown.draggable = false;
        dropdown.style.userSelect = 'none';
        dropdown.style.cursor = 'pointer';
        
        // Clear any bad event listeners by cloning
        const newDropdown = dropdown.cloneNode(true);
        dropdown.parentNode.replaceChild(newDropdown, dropdown);
        
        console.log("✅ Applied fix to:", newDropdown);
    });
};

console.log("\n📋 INSTRUCTIONS:");
console.log("1. Click on the problematic dropdown");
console.log("2. Watch the console for diagnostic info");
console.log("3. Run testFix() to test a targeted solution");
console.log("4. Report back what you see!");