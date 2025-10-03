// Customer page functionality with improved error handling

// DOM elements
const callStaffBtn = document.getElementById('call-staff-btn');
const cartBtn = document.getElementById('cart-btn');
const cartModal = document.getElementById('cart-modal');
const confirmationModal = document.getElementById('confirmation-modal');
const callSuccessModal = document.getElementById('call-success-modal');
const menuGrid = document.getElementById('menu-grid');
const categoryBtns = document.querySelectorAll('.category-btn');

// Global variables
let cart = {};
let orderStatus = null;
let customerOrders = [];
let menuItems = []; // Will be populated from the template or API

// Initialize socket connection with proper error handling
let socket;
let connectionRetries = 0;
const maxRetries = 3;

function initializeSocket() {
    // Check if Socket.IO is available
    if (typeof io === 'undefined') {
        console.warn('⚠️ Socket.IO not available, some features may not work');
        return;
    }
    
    try {
        // Show a subtle loading indicator for socket connection
        console.log('🔄 Connecting to real-time updates...');
        
        socket = io({
            transports: ['polling', 'websocket'],
            timeout: 20000,
            reconnection: true,
            reconnectionAttempts: maxRetries,
            reconnectionDelay: 1000,
            forceNew: false, // Reuse existing connection if available
            upgrade: true,
            rememberUpgrade: false
        });

        socket.on('connect', function() {
            console.log('✅ Customer socket connected');
            socket.emit('join_customer_room', { table_number: tableNumber });
            connectionRetries = 0;
            showCustomerNotification('Real-time updates connected! 📡', 'success', 1500);
        });

        socket.on('disconnect', function() {
            console.log('❌ Customer socket disconnected');
        });

        socket.on('connect_error', function(error) {
            connectionRetries++;
            console.error('Socket connection error:', error);
            
            if (connectionRetries >= maxRetries) {
                console.warn('Max connection retries reached. Some features may not work.');
                showCustomerNotification('Real-time updates unavailable. Basic features still work!', 'warning', 3000);
            }
        });

        socket.on('joined_customer_room', function() {
            console.log('✅ Successfully joined customer room');
        });

        // Listen for order status updates
        socket.on('order_status_updated', function(data) {
            // Update the order in our local list
            const orderIndex = customerOrders.findIndex(order => order.order_id === data.order_id);
            if (orderIndex !== -1) {
                customerOrders[orderIndex].status = data.status;
            }
            
            // Update the UI
            updateOrderStatusDisplay();
            playNotificationSound();
            
            // Show notification for important status changes
            if (data.status === 'ready') {
                showCustomerNotification('Your order is ready for pickup!', 'success');
            } else if (data.status === 'preparing') {
                showCustomerNotification('Your order is being prepared', 'info');
            }
        });

        socket.on('menu_updated', function(newItem) {
            // Refresh page to show new menu item
            location.reload();
        });

    } catch (error) {
        console.error('Failed to initialize socket:', error);
    }
}

// Initialize socket
initializeSocket();

// Cart functionality
function updateQuantity(itemId, change) {
    const quantityEl = document.getElementById(`qty-${itemId}`);
    if (!quantityEl) {
        console.error('Quantity element not found for item:', itemId);
        return;
    }
    
    const currentQty = parseInt(quantityEl.textContent) || 0;
    const newQty = Math.max(0, currentQty + change);
    
    quantityEl.textContent = newQty;
    
    // Find the item - check both menuItems and window.menuItemsData
    let item = null;
    if (menuItems && menuItems.length > 0) {
        item = menuItems.find(item => item.id === itemId);
    } else if (window.menuItemsData && window.menuItemsData.length > 0) {
        item = window.menuItemsData.find(item => item.id === itemId);
        // Update menuItems array if it wasn't initialized
        if (!menuItems || menuItems.length === 0) {
            menuItems = window.menuItemsData;
        }
    }
    
    if (!item) {
        console.error('Menu item not found:', itemId);
        // Try to get item data from the DOM as fallback
        const itemElement = document.querySelector(`[data-item-id="${itemId}"]`);
        if (itemElement) {
            const nameEl = itemElement.querySelector('.item-name');
            const priceEl = itemElement.querySelector('.item-price');
            if (nameEl && priceEl) {
                const priceText = priceEl.textContent.replace('LKR', '').trim();
                const price = parseFloat(priceText);
                if (!isNaN(price)) {
                    item = {
                        id: itemId,
                        name: nameEl.textContent.trim(),
                        price: price,
                        description: itemElement.querySelector('.item-description')?.textContent?.trim() || '',
                        category: itemElement.dataset.category || 'Unknown'
                    };
                }
            }
        }
    }
    
    if (!item) {
        console.error('Could not find or create item data for:', itemId);
        return;
    }
    
    // Update cart
    if (newQty === 0) {
        delete cart[itemId];
    } else {
        cart[itemId] = {
            ...item,
            quantity: newQty
        };
    }
    
    updateCartDisplay();
}

// Make updateQuantity available globally for inline onclick handlers
window.updateQuantity = updateQuantity;

function updateCartDisplay() {
    const cartCount = Object.values(cart).reduce((sum, item) => sum + item.quantity, 0);
    const cartTotal = Object.values(cart).reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    document.getElementById('cart-count').textContent = cartCount;
    document.getElementById('cart-total').textContent = cartTotal.toFixed(2);
    
    // Update cart button state
    cartBtn.style.opacity = cartCount > 0 ? '1' : '0.6';
}

// Category filtering
function filterMenuItems(category) {
    const menuItems = document.querySelectorAll('.menu-item');
    
    menuItems.forEach(item => {
        const itemCategory = item.dataset.category;
        if (category === 'all' || itemCategory === category) {
            item.classList.remove('hidden');
        } else {
            item.classList.add('hidden');
        }
    });
}

// Call staff functionality with improved reliability
function callStaff() {
    // Prevent multiple calls
    if (callStaffBtn.disabled) return;
    
    const data = {
        customer_name: customerName,
        table_number: tableNumber
    };
    
    // Show loading state
    const originalText = callStaffBtn.innerHTML;
    callStaffBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calling...';
    callStaffBtn.disabled = true;
    
    // Set timeout for the request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
    
    fetch('/api/call-staff', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            showModal(callSuccessModal);
            showCustomerNotification('Staff has been notified!', 'success');
        } else {
            throw new Error(data.message || 'Failed to call staff');
        }
    })
    .catch(error => {
        console.error('Error calling staff:', error);
        
        let errorMessage = 'Failed to call staff. Please try again.';
        if (error.name === 'AbortError') {
            errorMessage = 'Request timed out. Please check your connection and try again.';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showCustomerNotification(errorMessage, 'error');
    })
    .finally(() => {
        // Reset button state
        callStaffBtn.innerHTML = originalText;
        callStaffBtn.disabled = false;
    });
}

// Customer notification system
function showCustomerNotification(message, type = 'info') {
    // Remove any existing notifications
    const existingNotifications = document.querySelectorAll('.customer-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    const notification = document.createElement('div');
    notification.className = `customer-notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Styles
    notification.style.cssText = `
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 12px;
        max-width: 90vw;
        font-weight: 500;
        animation: slideInDown 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutUp 0.3s ease forwards';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 300);
    }, 4000);
}

// Add CSS animations for notifications
function addNotificationStyles() {
    if (document.getElementById('notification-styles')) return;
    
    const styles = document.createElement('style');
    styles.id = 'notification-styles';
    styles.textContent = `
        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateX(-50%) translateY(-100%);
            }
            to {
                opacity: 1;
                transform: translateX(-50%) translateY(0);
            }
        }
        
        @keyframes slideOutUp {
            to {
                opacity: 0;
                transform: translateX(-50%) translateY(-100%);
            }
        }
        
        .customer-notification .notification-content {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 14px;
        }
        
        .customer-notification i {
            font-size: 16px;
        }
    `;
    
    document.head.appendChild(styles);
}

// Order placement with improved error handling and validation
function placeOrder() {
    // Prevent multiple submissions
    const placeOrderBtn = document.getElementById('place-order-btn');
    if (placeOrderBtn.disabled) return;
    
    // Validate cart
    const cartItems = Object.values(cart);
    if (cartItems.length === 0) {
        showCustomerNotification('Your cart is empty', 'error');
        return;
    }
    
    const orderItems = cartItems.map(item => ({
        id: item.id,
        name: item.name,
        price: item.price,
        quantity: item.quantity
    }));
    
    const total = orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    // Validate total
    if (total <= 0) {
        showCustomerNotification('Invalid order total', 'error');
        return;
    }
    
    const orderData = {
        customer_name: customerName,
        table_number: tableNumber,
        items: orderItems,
        total: total
    };
    
    // Show loading state
    const originalText = placeOrderBtn.innerHTML;
    placeOrderBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Placing Order...';
    placeOrderBtn.disabled = true;
    
    // Set timeout for the request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout for orders
    
    fetch('/api/place-order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return response.json();
    })
    .then(data => {
        if (data.status === 'success') {
            // Add order to our local list
            const newOrder = {
                order_id: data.order_id,
                status: 'pending',
                items: Object.values(cart),
                timestamp: new Date().toLocaleTimeString()
            };
            customerOrders.push(newOrder);
            
            // Update display
            updateOrderStatusDisplay();
            
            // Clear cart
            cart = {};
            updateCartDisplay();
            
            // Reset all quantity displays
            document.querySelectorAll('.quantity').forEach(el => {
                el.textContent = '0';
            });
            
            // Hide cart modal and show confirmation
            hideModal(cartModal);
            showModal(confirmationModal);
            
            playNotificationSound();
            showCustomerNotification('Order placed successfully!', 'success');
            
            console.log('✅ Order placed successfully:', data.order_id);
        } else {
            throw new Error(data.message || 'Failed to place order');
        }
    })
    .catch(error => {
        console.error('Error placing order:', error);
        
        let errorMessage = 'Failed to place order. Please try again.';
        if (error.name === 'AbortError') {
            errorMessage = 'Order submission timed out. Please check your connection and try again.';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showCustomerNotification(errorMessage, 'error');
    })
    .finally(() => {
        // Reset button state
        placeOrderBtn.innerHTML = originalText;
        placeOrderBtn.disabled = false;
    });
}

// Modal functions
function showModal(modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function hideModal(modal) {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function populateCartModal() {
    const cartItemsContainer = document.getElementById('cart-items');
    const cartItems = Object.values(cart);
    
    if (cartItems.length === 0) {
        cartItemsContainer.innerHTML = '<p style="text-align: center; color: #64748b; padding: 40px;">Your cart is empty</p>';
        document.getElementById('place-order-btn').disabled = true;
        return;
    }
    
    document.getElementById('place-order-btn').disabled = false;
    
    cartItemsContainer.innerHTML = cartItems.map(item => `
        <div class="cart-item">
            <div class="cart-item-info">
                <h4>${item.name}</h4>
                <div class="cart-item-details">${item.quantity} × LKR ${item.price.toFixed(2)}</div>
            </div>
            <div class="cart-item-price">LKR ${(item.price * item.quantity).toFixed(2)}</div>
        </div>
    `).join('');
    
    const total = cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    document.getElementById('final-total').textContent = total.toFixed(2);
}

function updateOrderStatusDisplay() {
    const orderStatusSection = document.getElementById('order-status-section');
    const currentOrdersDiv = document.getElementById('current-orders');
    
    if (customerOrders.length === 0) {
        orderStatusSection.style.display = 'none';
        return;
    }
    
    orderStatusSection.style.display = 'block';
    
    // Update progress steps based on most advanced order
    const mostAdvancedStatus = getMostAdvancedStatus();
    updateProgressSteps(mostAdvancedStatus);
    
    // Display all current orders
    currentOrdersDiv.innerHTML = customerOrders.map(order => {
        const statusText = getStatusText(order.status);
        const statusClass = getStatusClass(order.status);
        const itemCount = order.items.reduce((sum, item) => sum + item.quantity, 0);
        
        return `
            <div class="order-item ${statusClass}">
                <div class="order-header">
                    <span class="order-id">Order #${order.order_id}</span>
                    <span class="order-time">${order.timestamp}</span>
                </div>
                <div class="order-details">
                    <span class="item-count">${itemCount} items</span>
                    <span class="order-status">${statusText}</span>
                </div>
            </div>
        `;
    }).join('');
}

function getMostAdvancedStatus() {
    const statusOrder = ['pending', 'preparing', 'ready', 'completed'];
    let mostAdvanced = 'pending';
    
    customerOrders.forEach(order => {
        if (statusOrder.indexOf(order.status) > statusOrder.indexOf(mostAdvanced)) {
            mostAdvanced = order.status;
        }
    });
    
    return mostAdvanced;
}

function updateProgressSteps(currentStatus) {
    const steps = document.querySelectorAll('.progress-step');
    const statusOrder = ['pending', 'preparing', 'ready'];
    const currentIndex = statusOrder.indexOf(currentStatus);
    
    steps.forEach((step, index) => {
        step.classList.remove('active', 'completed');
        if (index < currentIndex) {
            step.classList.add('completed');
        } else if (index === currentIndex) {
            step.classList.add('active');
        }
    });
}

function getStatusText(status) {
    const statusMessages = {
        'pending': 'Order Received',
        'preparing': 'Being Prepared',
        'ready': 'Ready for Pickup',
        'completed': 'Completed'
    };
    return statusMessages[status] || status;
}

function getStatusClass(status) {
    return `status-${status}`;
}

function playNotificationSound() {
    const audio = document.getElementById('notification-sound');
    if (audio) {
        audio.play().catch(e => console.log('Audio play failed:', e));
    }
}

// Event listeners
callStaffBtn.addEventListener('click', callStaff);

cartBtn.addEventListener('click', () => {
    populateCartModal();
    showModal(cartModal);
});

// Category buttons
categoryBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active class from all buttons
        categoryBtns.forEach(b => b.classList.remove('active'));
        // Add active class to clicked button
        btn.classList.add('active');
        // Filter menu items
        filterMenuItems(btn.dataset.category);
    });
});

// Modal close buttons
document.querySelectorAll('.close-modal, #close-cart-modal-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        hideModal(cartModal);
    });
});

document.getElementById('close-confirmation-btn').addEventListener('click', () => {
    hideModal(confirmationModal);
});

document.getElementById('close-call-success-btn').addEventListener('click', () => {
    hideModal(callSuccessModal);
});

document.getElementById('place-order-btn').addEventListener('click', placeOrder);

// Close modals when clicking outside
document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            hideModal(modal);
        }
    });
});

// Initialize with proper error handling
document.addEventListener('DOMContentLoaded', () => {
    try {
        // Initialize menu items from global data
        if (window.menuItemsData && Array.isArray(window.menuItemsData)) {
            menuItems = window.menuItemsData;
            console.log('✅ Menu pre-loaded with', menuItems.length, 'items');
            console.log('📋 Menu items:', menuItems.map(item => ({ id: item.id, name: item.name })));
        } else {
            console.log('⚠️ No menu data found in window.menuItemsData, will load from API');
            menuItems = []; // Initialize as empty array
            loadMenuItems();
        }
        
        // Add notification styles
        addNotificationStyles();
        
        // Update cart display
        updateCartDisplay();
        
        // Show welcome animation immediately
        setTimeout(() => {
            const header = document.querySelector('.header');
            if (header) {
                header.style.transform = 'translateY(0)';
                header.style.opacity = '1';
            }
        }, 100);
        
        // Initialize order status section
        initializeOrderStatus();
        
        // Initialize socket connection after page is ready (non-blocking)
        setTimeout(() => {
            initializeSocket();
        }, 300);
        
        console.log('✅ Customer page initialized successfully');
        
        // Show quick loading complete notification
        showCustomerNotification('Welcome to Green Heaven! 🌿', 'success', 2000);
        
    } catch (error) {
        console.error('❌ Error initializing customer page:', error);
        showCustomerNotification('Some features may not work properly. Please refresh the page.', 'error');
    }
});

// Load menu items for real-time updates
function loadMenuItems() {
    // Don't block the UI while loading
    fetch('/api/menu', {
        method: 'GET',
        headers: {
            'Cache-Control': 'max-age=300' // Cache for 5 minutes
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            menuItems = data;
            console.log('✅ Menu items loaded successfully');
            
            // Update any menu displays if needed
            if (typeof updateMenuDisplay === 'function') {
                updateMenuDisplay();
            }
        })
        .catch(error => {
            console.error('Error loading menu items:', error);
            // Gracefully handle menu loading errors
            showCustomerNotification('Using offline menu. Some items may not be available.', 'warning', 3000);
        });
}

// Handle page visibility change for better performance
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible, refresh menu if needed
        loadMenuItems();
        
        // Check order status if we have an active order
        if (orderStatus) {
            console.log('Page visible, order status:', orderStatus.status);
        }
    }
});

// Improved error handling for fetch requests
function fetchWithRetry(url, options = {}, retries = 2) {
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response;
        })
        .catch(error => {
            if (retries > 0 && error.name !== 'AbortError') {
                console.warn(`Retrying request to ${url}. Retries left: ${retries}`);
                return new Promise(resolve => {
                    setTimeout(() => {
                        resolve(fetchWithRetry(url, options, retries - 1));
                    }, 1000);
                });
            }
            throw error;
        });
}

// Initialize order status functionality
function initializeOrderStatus() {
    const toggleBtn = document.getElementById('toggle-status-btn');
    const statusContent = document.getElementById('status-content');
    
    if (toggleBtn && statusContent) {
        toggleBtn.addEventListener('click', () => {
            const isExpanded = statusContent.style.display !== 'none';
            statusContent.style.display = isExpanded ? 'none' : 'block';
            toggleBtn.innerHTML = isExpanded ? '<i class="fas fa-chevron-down"></i>' : '<i class="fas fa-chevron-up"></i>';
        });
    }
    
    // Load existing orders for this table
    loadCustomerOrders();
}

// Load existing orders for this customer/table
function loadCustomerOrders() {
    // This would be called to load any existing orders for this table
    // For now, we'll just initialize the display
    updateOrderStatusDisplay();
}