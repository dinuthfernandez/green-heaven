// Debug script to test cart functionality
function debugCartFunctionality() {
    console.log('🔍 DEBUG: Testing cart functionality step by step...');
    
    // 1. Check if menu items are loaded
    console.log('1. Menu items check:');
    console.log('   window.menuItemsData exists:', typeof window.menuItemsData !== 'undefined');
    console.log('   menuItems exists:', typeof menuItems !== 'undefined');
    if (typeof menuItems !== 'undefined') {
        console.log('   menuItems length:', menuItems.length);
        console.log('   First item:', menuItems[0]);
    }
    
    // 2. Check if DOM elements exist
    console.log('2. DOM elements check:');
    const testItemId = 'tom-yum'; // Known item ID
    const qtyElement = document.getElementById(`qty-${testItemId}`);
    console.log('   Quantity element exists:', qtyElement !== null);
    
    const plusBtn = document.querySelector(`[onclick="updateQuantity('${testItemId}', 1)"]`);
    console.log('   Plus button exists:', plusBtn !== null);
    
    const cartBtn = document.getElementById('cart-btn');
    console.log('   Cart button exists:', cartBtn !== null);
    
    // 3. Check if functions are defined
    console.log('3. Function definitions:');
    console.log('   updateQuantity function:', typeof updateQuantity);
    console.log('   updateCartDisplay function:', typeof updateCartDisplay);
    console.log('   placeOrder function:', typeof placeOrder);
    console.log('   callStaff function:', typeof callStaff);
    
    // 4. Test updateQuantity function manually
    if (typeof updateQuantity === 'function' && menuItems && menuItems.length > 0) {
        console.log('4. Testing updateQuantity function...');
        const testItem = menuItems[0];
        console.log('   Testing with item:', testItem.name, '(ID:', testItem.id, ')');
        
        try {
            updateQuantity(testItem.id, 1);
            console.log('   ✅ updateQuantity called successfully');
            console.log('   Cart after update:', cart);
        } catch (error) {
            console.log('   ❌ updateQuantity failed:', error);
        }
    }
    
    // 5. Check cart state
    console.log('5. Cart state:');
    console.log('   cart object:', cart);
    console.log('   cart keys:', Object.keys(cart));
    
    return {
        menuItemsLoaded: typeof menuItems !== 'undefined' && menuItems.length > 0,
        functionsLoaded: typeof updateQuantity === 'function',
        domElementsExist: qtyElement !== null && plusBtn !== null,
        cartState: cart
    };
}

// Run debug when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', debugCartFunctionality);
} else {
    debugCartFunctionality();
}