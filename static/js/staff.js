// Staff page functionality

// Initialize Socket.IO with error handling
let socket;
let connectionAttempts = 0;
const maxConnectionAttempts = 5;

function initializeSocket() {
    try {
        socket = io({
            transports: ['websocket', 'polling'],
            timeout: 5000,
            reconnection: true,
            reconnectionAttempts: maxConnectionAttempts,
            reconnectionDelay: 1000
        });

        // Join staff room for real-time updates
        socket.on('connect', function() {
            console.log('✅ Socket connected successfully');
            socket.emit('join_staff_room');
            connectionAttempts = 0;
            showNotification('Connected to live updates', 'success');
        });

        socket.on('disconnect', function() {
            console.log('❌ Socket disconnected');
            showNotification('Lost connection to live updates', 'error');
        });

        socket.on('connect_error', function(error) {
            connectionAttempts++;
            console.error('Socket connection error:', error);
            
            if (connectionAttempts >= maxConnectionAttempts) {
                showNotification('Unable to connect to live updates. Refresh page to retry.', 'error');
            }
        });

        socket.on('joined_staff_room', function() {
            console.log('✅ Successfully joined staff room');
        });

        // Socket event listeners for real-time updates
        socket.on('new_alert', function(alert) {
            console.log('📢 New alert received:', alert);
            addNewAlert(alert);
            loadTableData(); // Refresh table data to show alert
        });

        socket.on('new_order', function(order) {
            console.log('🔔 New order received:', order);
            addNewOrder(order);
            loadTableData(); // Refresh table data to show new order
        });

        socket.on('order_status_updated', function(data) {
            console.log('📝 Order status updated:', data);
            updateOrderInDOM(data.order_id, data.status);
            loadTableData(); // Refresh table data
        });

        socket.on('menu_updated', function(item) {
            console.log('🍽️ Menu updated:', item);
            loadMenu(); // Refresh menu display
        });

        socket.on('menu_item_deleted', function(data) {
            console.log('🗑️ Menu item deleted:', data);
            loadMenu(); // Refresh menu display
        });

    } catch (error) {
        console.error('Failed to initialize socket:', error);
        showNotification('Live updates unavailable. Some features may not work properly.', 'error');
    }
}

// Initialize socket connection
initializeSocket();

// DOM elements
const alertsContainer = document.getElementById('alerts-container');
const ordersContainer = document.getElementById('orders-container');
const menuGrid = document.getElementById('menu-grid');
const alertCount = document.getElementById('alert-count');
const addMenuForm = document.getElementById('add-menu-form');
const alertSound = document.getElementById('alert-sound');
const filterBtns = document.querySelectorAll('.filter-btn');

// Current filter
let currentFilter = 'all';

// Load initial data
loadOrders();
loadMenu();

// Order management functions
function loadOrders() {
    fetch('/api/orders')
        .then(response => response.json())
        .then(orders => {
            displayOrders(orders);
            updateOrderStats();
        })
        .catch(error => {
            console.error('Error loading orders:', error);
            showNotification('Failed to load orders', 'error');
        });
}

function loadMenu() {
    fetch('/api/menu')
        .then(response => response.json())
        .then(menuItems => {
            displayMenuItems(menuItems);
        })
        .catch(error => {
            console.error('Error loading menu:', error);
            showNotification('Failed to load menu', 'error');
        });
}

function displayMenuItems(menuItems) {
    const menuGrid = document.getElementById('menu-grid');
    if (!menuGrid) return;
    
    menuGrid.innerHTML = menuItems.map(item => `
        <div class="menu-item-card" data-item-id="${item.id}">
            ${item.image ? 
                `<img src="${item.image}" alt="${item.name}" class="menu-item-image">` :
                `<div class="menu-item-placeholder">
                    <i class="fas fa-image"></i>
                </div>`
            }
            <div class="menu-item-info">
                <h4>${item.name}</h4>
                <p class="menu-item-category">${item.category}</p>
                <p class="menu-item-description">${item.description}</p>
                <span class="menu-item-price">LKR ${item.price.toFixed(2)}</span>
            </div>
            <div class="menu-item-actions">
                <button class="btn-toggle-availability" 
                        onclick="toggleItemAvailability('${item.id}', ${item.available !== false})"
                        title="${item.available !== false ? 'Mark as unavailable' : 'Mark as available'}">
                    <i class="fas fa-${item.available !== false ? 'eye-slash' : 'eye'}"></i>
                </button>
                <button class="btn-delete-item" 
                        onclick="deleteMenuItem('${item.id}')"
                        title="Delete item">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `).join('');
}

function toggleItemAvailability(itemId, currentlyAvailable) {
    fetch(`/api/menu-item/${itemId}/availability`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ available: !currentlyAvailable })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadMenu(); // Refresh menu display
            showNotification(`Item ${!currentlyAvailable ? 'enabled' : 'disabled'} successfully`, 'success');
        } else {
            showNotification('Failed to update item availability', 'error');
        }
    })
    .catch(error => {
        console.error('Error updating item availability:', error);
        showNotification('Failed to update item availability', 'error');
    });
}

function deleteMenuItem(itemId) {
    if (!confirm('Are you sure you want to delete this menu item?')) return;
    
    fetch(`/api/menu-item/${itemId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadMenu(); // Refresh menu display
            showNotification('Menu item deleted successfully', 'success');
        } else {
            showNotification('Failed to delete menu item', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting menu item:', error);
        showNotification('Failed to delete menu item', 'error');
    });
}

// Table Management Functions
let tableData = [];

function loadTableData() {
    fetch('/api/tables')
        .then(response => response.json())
        .then(data => {
            tableData = data;
            updateTableCards();
            updateStats();
        })
        .catch(error => console.error('Error loading table data:', error));
}

function updateTableCards() {
    const tablesGrid = document.getElementById('tables-grid');
    if (!tablesGrid) return;
    
    tablesGrid.innerHTML = '';
    
    tableData.forEach(table => {
        const tableCard = createTableCard(table);
        tablesGrid.appendChild(tableCard);
    });
}

function createTableCard(table) {
    const card = document.createElement('div');
    card.className = `table-card table-${table.status}`;
    card.setAttribute('data-table', table.number);
    
    const statusIcon = table.number.includes('VIP') ? 'crown' : 'table';
    
    card.innerHTML = `
        <div class="table-header">
            <div class="table-number">
                <i class="fas fa-${statusIcon}"></i>
                <span>${table.number}</span>
            </div>
            <div class="table-status-indicator"></div>
        </div>
        
        <div class="table-content">
            ${table.customer_name ? `
                <div class="customer-info">
                    <strong>${table.customer_name}</strong>
                    ${table.last_activity ? `<small>Active: ${table.last_activity}</small>` : ''}
                </div>
                
                ${table.orders && table.orders.length ? `
                    <div class="table-orders">
                        <div class="orders-summary">
                            <span>${table.orders.length} order${table.orders.length !== 1 ? 's' : ''}</span>
                            <span class="total-amount">LKR ${table.total_amount.toFixed(2)}</span>
                        </div>
                        <div class="order-statuses">
                            ${table.orders.map(order => 
                                `<span class="order-status-badge status-${order.status}">${order.status.charAt(0).toUpperCase() + order.status.slice(1)}</span>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}
                
                ${table.alerts && table.alerts.length ? `
                    <div class="table-alerts">
                        <i class="fas fa-bell"></i>
                        <span>${table.alerts.length} alert${table.alerts.length !== 1 ? 's' : ''}</span>
                    </div>
                ` : ''}
            ` : `
                <div class="empty-table">
                    <i class="fas fa-chair"></i>
                    <span>Available</span>
                </div>
            `}
        </div>
        
        ${table.status !== 'empty' ? `
            <div class="table-actions">
                ${table.alerts && table.alerts.length ? `
                    <button class="btn-clear-alerts" onclick="clearTableAlerts('${table.number}')">
                        <i class="fas fa-bell-slash"></i>
                    </button>
                ` : ''}
                <button class="btn-view-details" onclick="viewTableDetails('${table.number}')">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
        ` : ''}
    `;
    
    return card;
}

function clearTableAlerts(tableNumber) {
    fetch(`/api/tables/${tableNumber}/clear-alerts`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadTableData(); // Refresh table data
            showNotification('Alerts cleared successfully', 'success');
        }
    })
    .catch(error => console.error('Error clearing alerts:', error));
}

function viewTableDetails(tableNumber) {
    const table = tableData.find(t => t.number === tableNumber);
    if (!table) return;
    
    // Create modal or expand card to show detailed information
    alert(`Table ${tableNumber}\nCustomer: ${table.customer_name || 'None'}\nOrders: ${table.orders ? table.orders.length : 0}\nTotal: LKR ${table.total_amount || 0}`);
}

function clearAllAlerts() {
    fetch('/api/tables/clear-all-alerts', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadTableData();
            showNotification('All alerts cleared', 'success');
        }
    })
    .catch(error => console.error('Error clearing all alerts:', error));
}

function updateStats() {
    const occupiedTables = tableData.filter(t => t.status === 'occupied' || t.status === 'needs_attention').length;
    const availableTables = tableData.filter(t => t.status === 'empty').length;
    const alertTables = tableData.filter(t => t.status === 'needs_attention').length;
    const totalRevenue = tableData.reduce((sum, t) => sum + (t.total_amount || 0), 0);
    
    // Update stat displays
    const occupiedElement = document.getElementById('occupied-tables');
    const availableElement = document.getElementById('available-tables');
    const alertsElement = document.getElementById('tables-with-alerts');
    const revenueElement = document.getElementById('daily-revenue');
    
    if (occupiedElement) occupiedElement.textContent = occupiedTables;
    if (availableElement) availableElement.textContent = availableTables;
    if (alertsElement) alertsElement.textContent = alertTables;
    if (revenueElement) revenueElement.textContent = `LKR ${totalRevenue.toFixed(0)}`;
}

function refreshData() {
    loadTableData();
    loadOrders();
    showNotification('Data refreshed', 'success');
}

function showNotification(message, type = 'info') {
    // Simple notification system - you can enhance this later
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 16px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    if (type === 'success') {
        notification.style.background = '#22c55e';
    } else if (type === 'error') {
        notification.style.background = '#ef4444';
    } else {
        notification.style.background = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => notification.style.opacity = '1', 10);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

// Load table data on page load
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('tables-grid')) {
        loadTableData();
        // Refresh table data every 30 seconds
        setInterval(loadTableData, 30000);
    }
});

function updateOrderInDOM(orderId, newStatus) {
    const orderElement = document.querySelector(`[data-order-id="${orderId}"]`);
    if (orderElement) {
        const statusElement = orderElement.querySelector('.order-status');
        if (statusElement) {
            statusElement.textContent = newStatus.charAt(0).toUpperCase() + newStatus.slice(1);
            statusElement.className = `order-status status-${newStatus}`;
        }
        
        // Update action buttons
        updateOrderActionButtons(orderElement, newStatus);
        
        // If current filter doesn't match, hide the order
        if (currentFilter !== 'all' && currentFilter !== newStatus) {
            orderElement.style.display = 'none';
        } else {
            orderElement.style.display = 'block';
        }
    }
    
    // Update order statistics
    updateOrderStats();
}

// Display orders
function displayOrders(orders) {
    if (!ordersContainer) {
        console.error('Orders container not found');
        return;
    }
    
    const filteredOrders = currentFilter === 'all' ? orders : orders.filter(order => order.status === currentFilter);
    
    if (filteredOrders.length === 0) {
        ordersContainer.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-clipboard-list"></i>
                <h3>No ${currentFilter === 'all' ? '' : currentFilter} orders</h3>
                <p>Orders will appear here when customers place them</p>
            </div>
        `;
        return;
    }
    
    ordersContainer.innerHTML = filteredOrders.map(order => createOrderHTML(order)).join('');
}

// Create order HTML
function createOrderHTML(order) {
    const actionButtons = getOrderActionButtons(order);
    
    return `
        <div class="order-item" data-order-id="${order.id}">
            <div class="order-header">
                <h4>Table ${order.table_number} - ${order.customer_name}</h4>
                <span class="order-status status-${order.status}">${order.status.charAt(0).toUpperCase() + order.status.slice(1)}</span>
            </div>
            <div class="order-items">
                ${order.items.map(item => `
                    <div class="order-item-detail">
                        <span>${item.quantity}x ${item.name}</span>
                        <span>LKR ${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                `).join('')}
            </div>
            <div class="order-footer">
                <span class="order-total">Total: LKR ${order.total.toFixed(2)}</span>
                <span class="order-time">${order.timestamp}</span>
            </div>
            <div class="order-actions">
                ${actionButtons}
            </div>
        </div>
    `;
}

// Get order action buttons based on status
function getOrderActionButtons(order) {
    switch(order.status) {
        case 'pending':
            return `<button onclick="updateOrderStatus('${order.id}', 'preparing')" class="btn-preparing">
                        <i class="fas fa-play"></i> Start Preparing
                    </button>`;
        case 'preparing':
            return `<button onclick="updateOrderStatus('${order.id}', 'ready')" class="btn-ready">
                        <i class="fas fa-check"></i> Ready to Serve
                    </button>`;
        case 'ready':
            return `<button onclick="updateOrderStatus('${order.id}', 'completed')" class="btn-completed">
                        <i class="fas fa-check-double"></i> Mark as Served
                    </button>`;
        case 'completed':
            return '<span style="color: #6b7280; font-size: 14px;">Order Completed</span>';
        default:
            return '';
    }
}

// Filter orders
function filterOrders(status) {
    currentFilter = status;
    
    // Update filter buttons
    filterBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.status === status);
    });
    
    // Reload orders with filter
    loadOrders();
}

// Update order statistics
function updateOrderStats() {
    fetch('/api/orders/stats')
        .then(response => response.json())
        .then(stats => {
            document.getElementById('total-orders').textContent = stats.total;
            document.getElementById('pending-orders').textContent = stats.pending;
            document.getElementById('preparing-orders').textContent = stats.preparing;
            document.getElementById('ready-orders').textContent = stats.ready;
            document.getElementById('completed-orders').textContent = stats.completed;
        })
        .catch(error => console.error('Error updating stats:', error));
}

// Staff functions
function dismissAlert(alertId) {
    fetch('/api/dismiss-alert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ alert_id: alertId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Remove alert from DOM
            const alertElement = document.querySelector(`[data-alert-id="${alertId}"]`);
            if (alertElement) {
                alertElement.style.animation = 'alertSlideOut 0.3s ease forwards';
                setTimeout(() => {
                    alertElement.remove();
                    updateAlertCount();
                }, 300);
            }
        }
    })
    .catch(error => {
        console.error('Error dismissing alert:', error);
    });
}

function updateOrderStatus(orderId, status) {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
    button.disabled = true;
    
    fetch('/api/update-order-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            order_id: orderId, 
            status: status 
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Update the order status in the DOM
            const orderElement = document.querySelector(`[data-order-id="${orderId}"]`);
            if (orderElement) {
                const statusElement = orderElement.querySelector('.order-status');
                statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
                statusElement.className = `order-status status-${status}`;
                
                // Update action buttons
                updateOrderActionButtons(orderElement, status);
            }
        }
    })
    .catch(error => {
        console.error('Error updating order status:', error);
        alert('Failed to update order status. Please try again.');
    })
    .finally(() => {
        button.innerHTML = originalText;
        button.disabled = false;
    });
}

function updateOrderActionButtons(orderElement, status) {
    const actionsContainer = orderElement.querySelector('.order-actions');
    
    let buttonsHTML = '';
    const orderId = orderElement.dataset.orderId;
    
    switch(status) {
        case 'pending':
            buttonsHTML = `
                <button onclick="updateOrderStatus('${orderId}', 'preparing')" class="btn-preparing">
                    <i class="fas fa-play"></i> Start Preparing
                </button>
            `;
            break;
        case 'preparing':
            buttonsHTML = `
                <button onclick="updateOrderStatus('${orderId}', 'ready')" class="btn-ready">
                    <i class="fas fa-check"></i> Ready to Serve
                </button>
            `;
            break;
        case 'ready':
            buttonsHTML = `
                <button onclick="updateOrderStatus('${orderId}', 'completed')" class="btn-completed">
                    <i class="fas fa-check-double"></i> Mark as Served
                </button>
            `;
            break;
        case 'completed':
            buttonsHTML = '<span style="color: #6b7280; font-size: 14px;">Order Completed</span>';
            break;
    }
    
    actionsContainer.innerHTML = buttonsHTML;
}

function addMenuItem() {
    const formData = {
        name: document.getElementById('item-name').value.trim(),
        category: document.getElementById('item-category').value,
        price: parseFloat(document.getElementById('item-price').value),
        image: document.getElementById('item-image').value.trim(),
        description: document.getElementById('item-description').value.trim()
    };
    
    // Validation
    if (!formData.name || !formData.price || isNaN(formData.price) || formData.price <= 0) {
        alert('Please enter a valid item name and price.');
        return;
    }
    
    const submitBtn = document.querySelector('.btn-add');
    const originalText = submitBtn.innerHTML;
    
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Item...';
    submitBtn.disabled = true;
    
    fetch('/api/add-menu-item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Add new item to the menu grid
            addMenuItemToGrid(data.menu_item);
            
            // Reset form
            addMenuForm.reset();
            
            // Show success message
            showNotification('Menu item added successfully!', 'success');
        }
    })
    .catch(error => {
        console.error('Error adding menu item:', error);
        showNotification('Failed to add menu item. Please try again.', 'error');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function addMenuItemToGrid(item) {
    const menuGrid = document.getElementById('menu-grid');
    const menuItemHTML = `
        <div class="menu-item-card">
            ${item.image ? 
                `<img src="${item.image}" alt="${item.name}" class="menu-item-image">` :
                `<div class="menu-item-placeholder">
                    <i class="fas fa-image"></i>
                </div>`
            }
            <div class="menu-item-info">
                <h4>${item.name}</h4>
                <p class="menu-item-category">${item.category}</p>
                <p class="menu-item-description">${item.description}</p>
                <span class="menu-item-price">LKR ${item.price.toFixed(2)}</span>
            </div>
        </div>
    `;
    
    menuGrid.insertAdjacentHTML('beforeend', menuItemHTML);
}

function addNewAlert(alert) {
    const alertHTML = `
        <div class="alert-item" data-alert-id="${alert.id}">
            <div class="alert-content">
                <h4>Table ${alert.table_number} - ${alert.customer_name}</h4>
                <p>Requesting staff assistance</p>
                <span class="alert-time">${alert.timestamp}</span>
            </div>
            <button class="dismiss-btn" onclick="dismissAlert('${alert.id}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    alertsContainer.insertAdjacentHTML('afterbegin', alertHTML);
    updateAlertCount();
    playAlertSound();
}

function addNewOrder(order) {
    // Add to beginning of orders list
    const orderHTML = createOrderHTML(order);
    
    if (ordersContainer.querySelector('.empty-state')) {
        ordersContainer.innerHTML = '';
    }
    
    ordersContainer.insertAdjacentHTML('afterbegin', orderHTML);
    updateOrderStats();
    playAlertSound();
    
    // If current filter doesn't match new order status, don't show it
    if (currentFilter !== 'all' && currentFilter !== order.status) {
        const newOrderElement = ordersContainer.querySelector(`[data-order-id="${order.id}"]`);
        if (newOrderElement) {
            newOrderElement.style.display = 'none';
        }
    }
}

// Initialize page with proper error handling
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Initialize core functionality
        initializeSocket();
        loadInitialData();
        setupEventListeners();
        setupAutoRefresh();
        
        // Update alert count
        updateAlertCount();
        
        console.log('✅ Staff dashboard initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing staff dashboard:', error);
        showNotification('Failed to initialize dashboard. Please refresh the page.', 'error');
    }
});

function loadInitialData() {
    // Load all data in parallel for better performance
    Promise.all([
        loadOrders(),
        loadMenu(),
        loadTableData(),
        loadManualOrders(),
        loadDailyTotals()
    ]).catch(error => {
        console.error('Error loading initial data:', error);
        showNotification('Some data failed to load. Please refresh the page.', 'error');
    });
}

function setupEventListeners() {
    // Filter button event listeners
    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                filterOrders(btn.dataset.status);
            });
        });
    }
    
    // Form event listeners
    if (addMenuForm) {
        addMenuForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addMenuItem();
        });
    }
    
    if (manualOrderForm) {
        manualOrderForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            await handleManualOrderSubmission();
        });
    }
    
    if (generateReportForm) {
        setupReportGeneration();
    }
}

function setupAutoRefresh() {
    // Staggered refresh intervals to reduce server load
    
    // Fast refresh for critical data (orders, alerts)
    setInterval(() => {
        loadOrders();
        updateAlertCount();
    }, 10000); // Every 10 seconds
    
    // Medium refresh for table data
    setInterval(() => {
        if (document.getElementById('tables-grid')) {
            loadTableData();
        }
    }, 15000); // Every 15 seconds
    
    // Slow refresh for less critical data
    setInterval(() => {
        loadManualOrders();
        loadDailyTotals();
    }, 30000); // Every 30 seconds
    
    // Handle browser visibility change for immediate refresh when page becomes visible
    document.addEventListener('visibilitychange', () => {
        if (!document.hidden) {
            // Page became visible, refresh critical data immediately
            setTimeout(() => {
                loadOrders();
                if (document.getElementById('tables-grid')) {
                    loadTableData();
                }
                updateAlertCount();
            }, 500); // Small delay to ensure page is fully active
        }
    });
}

function updateAlertCount() {
    const alertElements = alertsContainer.querySelectorAll('.alert-item');
    alertCount.textContent = alertElements.length;
}

function playAlertSound() {
    if (alertSound) {
        alertSound.currentTime = 0;
        alertSound.play().catch(e => console.log('Audio play failed:', e));
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 1000;
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 400px;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Socket event listeners
socket.on('new_alert', function(alert) {
    addNewAlert(alert);
});

socket.on('new_order', function(order) {
    addNewOrder(order);
});

// Form event listener
addMenuForm.addEventListener('submit', function(e) {
    e.preventDefault();
    addMenuItem();
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    updateAlertCount();
    
    // Add animation styles to head
    const styles = `
        <style>
            @keyframes alertSlideOut {
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
            
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideOutRight {
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
            
            .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', styles);
    
    // Auto-refresh all data every 5 seconds
    setInterval(() => {
        refreshAllData();
    }, 5000);
    
    // Also refresh every 30 seconds as backup
    setInterval(updateAlertCount, 30000);
});

// Comprehensive refresh function
function refreshAllData() {
    try {
        // Refresh orders without showing loading state
        loadOrders();
        
        // Refresh table data if tables grid exists
        if (document.getElementById('tables-grid')) {
            loadTableData();
        }
        
        // Update alert count
        updateAlertCount();
        
        // Update order statistics
        updateOrderStats();
        
    } catch (error) {
        console.error('Error during auto-refresh:', error);
    }
}

// Handle browser visibility change
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        // Page became visible, refresh data immediately
        refreshAllData();
    }
});

// Manual Order Management
const manualOrderForm = document.getElementById('add-manual-order-form');
const manualOrdersContainer = document.getElementById('manual-orders-container');

async function handleManualOrderSubmission() {
    const submitBtn = manualOrderForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    
    try {
        // Show loading state
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding Order...';
        submitBtn.disabled = true;
        
        const customerName = document.getElementById('manual-customer-name').value.trim();
        const tableNumber = document.getElementById('manual-table-number').value.trim();
        const itemsDescription = document.getElementById('manual-items-description').value.trim();
        const total = parseFloat(document.getElementById('manual-total').value);
        const notes = document.getElementById('manual-notes').value.trim();
        
        // Validation
        if (!itemsDescription || total <= 0) {
            showNotification('Please provide items description and total amount', 'error');
            return;
        }
        
        const response = await fetch('/api/manual-order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                customer_name: customerName,
                table_number: tableNumber,
                items_description: itemsDescription,
                total: total,
                notes: notes
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Manual order added successfully!', 'success');
            
            // Reset form with default values
            manualOrderForm.reset();
            document.getElementById('manual-customer-name').value = 'Walk-in Customer';
            document.getElementById('manual-table-number').value = 'Takeout';
            
            // Refresh related data
            loadManualOrders();
            loadDailyTotals();
            
            // Refresh table data if needed
            if (tableNumber !== 'Takeout') {
                loadTableData();
            }
        } else {
            showNotification('Error: ' + data.message, 'error');
        }
    } catch (error) {
        console.error('Error adding manual order:', error);
        showNotification('Error adding manual order', 'error');
    } finally {
        // Reset button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Load manual orders for today
async function loadManualOrders() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`/api/manual-orders?date=${today}`);
        const manualOrders = await response.json();
        
        if (manualOrdersContainer) {
            if (manualOrders.length === 0) {
                manualOrdersContainer.innerHTML = '<p style="text-align: center; color: #666;">No manual orders for today</p>';
            } else {
                manualOrdersContainer.innerHTML = manualOrders.map(order => `
                    <div class="manual-order-item">
                        <div class="manual-order-header">
                            <span class="manual-order-customer">${order.customer_name} - ${order.table_number}</span>
                            <span class="manual-order-total">LKR ${order.total.toFixed(2)}</span>
                        </div>
                        <div class="manual-order-details">
                            <p><strong>Items:</strong> ${order.items_description}</p>
                            ${order.notes ? `<p><strong>Notes:</strong> ${order.notes}</p>` : ''}
                            <p><strong>Time:</strong> ${order.timestamp}</p>
                        </div>
                    </div>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error loading manual orders:', error);
    }
}

// Daily Totals Management
const dailyTotalsContainer = document.getElementById('daily-totals');

async function loadDailyTotals() {
    try {
        const response = await fetch('/api/daily-totals');
        const totals = await response.json();
        
        if (dailyTotalsContainer) {
            dailyTotalsContainer.innerHTML = `
                <div class="total-item">
                    <div class="total-label">Digital Orders</div>
                    <div class="total-value">${totals.digital_orders}</div>
                    <div class="total-currency">orders</div>
                </div>
                <div class="total-item">
                    <div class="total-label">Manual Orders</div>
                    <div class="total-value">${totals.manual_orders}</div>
                    <div class="total-currency">orders</div>
                </div>
                <div class="total-item">
                    <div class="total-label">Digital Revenue</div>
                    <div class="total-value">LKR ${totals.digital_revenue.toFixed(2)}</div>
                </div>
                <div class="total-item">
                    <div class="total-label">Manual Revenue</div>
                    <div class="total-value">LKR ${totals.manual_revenue.toFixed(2)}</div>
                </div>
                <div class="total-item">
                    <div class="total-label">Total Revenue</div>
                    <div class="total-value">LKR ${totals.total_revenue.toFixed(2)}</div>
                </div>
                <div class="total-item">
                    <div class="total-label">Total Orders</div>
                    <div class="total-value">${totals.total_orders}</div>
                    <div class="total-currency">orders</div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading daily totals:', error);
    }
}

// PDF Report Generation
const generateReportForm = document.getElementById('generate-report-form');

if (generateReportForm) {
    // Set default dates (last 30 days)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(endDate.getDate() - 30);
    
    document.getElementById('report-end-date').value = endDate.toISOString().split('T')[0];
    document.getElementById('report-start-date').value = startDate.toISOString().split('T')[0];
    
    generateReportForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const startDate = document.getElementById('report-start-date').value;
        const endDate = document.getElementById('report-end-date').value;
        
        if (!startDate || !endDate) {
            alert('Please select both start and end dates');
            return;
        }
        
        if (new Date(startDate) > new Date(endDate)) {
            alert('Start date cannot be after end date');
            return;
        }
        
        try {
            const submitBtn = e.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
            submitBtn.disabled = true;
            
            const response = await fetch('/api/generate-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate
                })
            });
            
            if (response.ok) {
                // Create download link
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Green_Heaven_Report_${startDate}_to_${endDate}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                alert('Report generated successfully!');
            } else {
                const error = await response.json();
                alert('Error generating report: ' + error.message);
            }
            
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
            
        } catch (error) {
            console.error('Error generating report:', error);
            alert('Error generating report');
            
            const submitBtn = e.target.querySelector('button[type="submit"]');
            submitBtn.innerHTML = '<i class="fas fa-file-pdf"></i> Generate PDF Report';
            submitBtn.disabled = false;
        }
    });
}

// Update the auto-refresh to include new data
const originalRefreshAllData = refreshAllData;
refreshAllData = async function() {
    await originalRefreshAllData();
    loadManualOrders();
    loadDailyTotals();
};

// Load initial data for new sections
document.addEventListener('DOMContentLoaded', () => {
    loadManualOrders();
    loadDailyTotals();
});