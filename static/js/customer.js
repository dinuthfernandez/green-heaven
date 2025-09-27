// Customer page functionality

// DOM elements
const callStaffBtn = document.getElementById('call-staff-btn');
const cartBtn = document.getElementById('cart-btn');
const cartModal = document.getElementById('cart-modal');
const confirmationModal = document.getElementById('confirmation-modal');
const callSuccessModal = document.getElementById('call-success-modal');
const menuGrid = document.getElementById('menu-grid');
const categoryBtns = document.querySelectorAll('.category-btn');

// Cart functionality
function updateQuantity(itemId, change) {
    const quantityEl = document.getElementById(`qty-${itemId}`);
    const currentQty = parseInt(quantityEl.textContent);
    const newQty = Math.max(0, currentQty + change);
    
    quantityEl.textContent = newQty;
    
    // Find the item
    const item = menuItems.find(item => item.id === itemId);
    if (!item) return;
    
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

// Call staff functionality
function callStaff() {
    const data = {
        customer_name: customerName,
        table_number: tableNumber
    };
    
    callStaffBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calling...';
    callStaffBtn.disabled = true;
    
    fetch('/api/call-staff', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showModal(callSuccessModal);
        } else {
            alert(data.message || 'Failed to call staff. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error calling staff:', error);
        alert('Failed to call staff. Please try again.');
    })
    .finally(() => {
        callStaffBtn.innerHTML = '<i class="fas fa-bell"></i><span>Call Staff</span>';
        callStaffBtn.disabled = false;
    });
}

// Order placement
function placeOrder() {
    const orderItems = Object.values(cart).map(item => ({
        id: item.id,
        name: item.name,
        price: item.price,
        quantity: item.quantity
    }));
    
    const total = orderItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    
    const orderData = {
        customer_name: customerName,
        table_number: tableNumber,
        items: orderItems,
        total: total
    };
    
    // Show loading state
    document.getElementById('place-order-btn').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Placing Order...';
    document.getElementById('place-order-btn').disabled = true;
    
    fetch('/api/place-order', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            orderStatus = {
                order_id: data.order_id,
                status: 'pending'
            };
            
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
        } else {
            alert(data.message || 'Failed to place order. Please try again.');
        }
    })
    .catch(error => {
        console.error('Error placing order:', error);
        alert('Failed to place order. Please try again.');
    })
    .finally(() => {
        document.getElementById('place-order-btn').innerHTML = 'Place Order';
        document.getElementById('place-order-btn').disabled = false;
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

function updateOrderStatus(status) {
    const statusText = document.getElementById('order-status-text');
    const statusMessages = {
        'pending': 'Order Received',
        'preparing': 'Preparing Your Order',
        'ready': 'Order Ready for Pickup',
        'completed': 'Order Completed'
    };
    
    if (statusText) {
        statusText.textContent = statusMessages[status] || status;
        
        // Show status update notification
        if (status === 'ready') {
            // You could show a notification here
            console.log('Order is ready!');
        }
    }
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

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateCartDisplay();
    
    // Show welcome animation
    setTimeout(() => {
        const header = document.querySelector('.header');
        if (header) {
            header.style.transform = 'translateY(0)';
            header.style.opacity = '1';
        }
    }, 100);
});

// Socket event listeners
socket.on('menu_updated', function(newItem) {
    // Refresh page to show new menu item
    location.reload();
});

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && orderStatus) {
        // Page became visible, could check for order updates
        console.log('Page visible, order status:', orderStatus.status);
    }
});