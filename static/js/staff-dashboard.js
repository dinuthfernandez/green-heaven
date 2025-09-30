// Green Heaven Staff Dashboard JavaScript

class StaffDashboard {
    constructor() {
        this.socket = io();
        this.currentPage = 'overview';
        this.sidebarOpen = true;
        this.refreshInterval = null;
        this.data = {
            tables: [],
            orders: [],
            alerts: [],
            menu: [],
            analytics: {}
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.setupSocket();
        this.initializeNavigigation();
        this.loadInitialData();
        this.startAutoRefresh();
    }

    bindEvents() {
        // Navigation
        document.addEventListener('click', (e) => {
            if (e.target.matches('.nav-link')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                this.navigateToPage(page);
            }

            if (e.target.matches('.menu-toggle')) {
                this.toggleSidebar();
            }

            if (e.target.matches('.btn-refresh')) {
                this.refreshData();
            }

            if (e.target.matches('.filter-btn')) {
                this.applyFilter(e.target);
            }

            // Table actions
            if (e.target.matches('.btn-clean-table')) {
                const tableId = e.target.dataset.tableId;
                this.cleanTable(tableId);
            }

            if (e.target.matches('.btn-view-details')) {
                const tableId = e.target.dataset.tableId;
                this.viewTableDetails(tableId);
            }

            // Order actions
            if (e.target.matches('.btn-mark-preparing')) {
                const orderId = e.target.dataset.orderId;
                this.updateOrderStatus(orderId, 'preparing');
            }

            if (e.target.matches('.btn-mark-ready')) {
                const orderId = e.target.dataset.orderId;
                this.updateOrderStatus(orderId, 'ready');
            }

            if (e.target.matches('.btn-complete-order')) {
                const orderId = e.target.dataset.orderId;
                this.updateOrderStatus(orderId, 'completed');
            }

            // Alert actions
            if (e.target.matches('.btn-resolve-alert')) {
                const alertId = e.target.dataset.alertId;
                this.resolveAlert(alertId);
            }

            if (e.target.matches('.btn-respond-alert')) {
                const alertId = e.target.dataset.alertId;
                this.respondToAlert(alertId);
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateToPage('overview');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateToPage('tables');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateToPage('orders');
                        break;
                    case 'r':
                        e.preventDefault();
                        this.refreshData();
                        break;
                }
            }
        });

        // Window resize
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }

    setupSocket() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.updateConnectionStatus(false);
        });

        this.socket.on('table_update', (data) => {
            this.handleTableUpdate(data);
        });

        this.socket.on('new_order', (data) => {
            this.handleNewOrder(data);
        });

        this.socket.on('order_update', (data) => {
            this.handleOrderUpdate(data);
        });

        this.socket.on('customer_call', (data) => {
            this.handleCustomerCall(data);
        });

        this.socket.on('data_updated', (data) => {
            this.handleDataUpdate(data);
        });
    }

    initializeNavigigation() {
        // Set active page based on URL fragment or default to overview
        const hash = window.location.hash.slice(1);
        const initialPage = hash || 'overview';
        this.navigateToPage(initialPage, false);
    }

    navigateToPage(pageName, updateUrl = true) {
        // Remove active class from all nav items and page content
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });

        // Add active class to current nav item and page
        const navItem = document.querySelector(`.nav-link[data-page="${pageName}"]`)?.parentElement;
        const pageContent = document.getElementById(`${pageName}-page`);

        if (navItem && pageContent) {
            navItem.classList.add('active');
            pageContent.classList.add('active');
            this.currentPage = pageName;

            // Update page title
            const pageTitle = document.getElementById('page-title');
            const titles = {
                overview: 'Dashboard Overview',
                tables: 'Table Management',
                orders: 'Order Management',
                alerts: 'Customer Calls & Alerts',
                menu: 'Menu Management',
                analytics: 'Analytics & Reports',
                settings: 'Settings'
            };
            pageTitle.textContent = titles[pageName] || 'Dashboard';

            // Update URL
            if (updateUrl) {
                window.history.pushState(null, '', `#${pageName}`);
            }

            // Load page-specific data
            this.loadPageData(pageName);
        }
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        sidebar.classList.toggle('open');
        this.sidebarOpen = !this.sidebarOpen;
    }

    handleResize() {
        if (window.innerWidth > 1024 && !this.sidebarOpen) {
            this.sidebarOpen = true;
            document.querySelector('.sidebar').classList.remove('open');
        }
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadTables(),
                this.loadOrders(),
                this.loadAlerts(),
                this.loadMenu(),
                this.loadAnalytics()
            ]);
            this.updateDashboard();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showNotification('Error loading data', 'error');
        }
    }

    async loadTables() {
        try {
            const response = await fetch('/api/tables');
            this.data.tables = await response.json();
        } catch (error) {
            console.error('Error loading tables:', error);
        }
    }

    async loadOrders() {
        try {
            const response = await fetch('/api/orders');
            this.data.orders = await response.json();
        } catch (error) {
            console.error('Error loading orders:', error);
        }
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts');
            this.data.alerts = await response.json();
        } catch (error) {
            console.error('Error loading alerts:', error);
        }
    }

    async loadMenu() {
        try {
            const response = await fetch('/api/menu');
            this.data.menu = await response.json();
        } catch (error) {
            console.error('Error loading menu:', error);
        }
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            this.data.analytics = await response.json();
        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    loadPageData(pageName) {
        switch(pageName) {
            case 'overview':
                this.renderOverview();
                break;
            case 'tables':
                this.renderTables();
                break;
            case 'orders':
                this.renderOrders();
                break;
            case 'alerts':
                this.renderAlerts();
                break;
            case 'menu':
                this.renderMenu();
                break;
            case 'analytics':
                this.renderAnalytics();
                break;
            case 'settings':
                this.renderSettings();
                break;
        }
    }

    updateDashboard() {
        this.updateStats();
        this.updateBadges();
        this.updateNotificationCount();
        this.renderCurrentPage();
    }

    updateStats() {
        const occupiedTables = this.data.tables.filter(table => table.status === 'occupied').length;
        const availableTables = this.data.tables.filter(table => table.status === 'empty').length;
        const pendingOrders = this.data.orders.filter(order => order.status === 'pending').length;
        const activeAlerts = this.data.alerts.filter(alert => !alert.resolved).length;

        // Update stat cards
        this.updateStatCard('occupied-tables', occupiedTables);
        this.updateStatCard('available-tables', availableTables);
        this.updateStatCard('pending-orders', pendingOrders);
        this.updateStatCard('active-alerts', activeAlerts);
    }

    updateStatCard(statId, value) {
        const element = document.querySelector(`[data-stat="${statId}"] .stat-number`);
        if (element) {
            element.textContent = value;
        }
    }

    updateBadges() {
        const pendingOrders = this.data.orders.filter(order => order.status === 'pending').length;
        const activeAlerts = this.data.alerts.filter(alert => !alert.resolved).length;

        // Update navigation badges
        const ordersBadge = document.querySelector('.nav-link[data-page="orders"] .badge');
        const alertsBadge = document.querySelector('.nav-link[data-page="alerts"] .badge');

        if (ordersBadge) {
            ordersBadge.textContent = pendingOrders;
            ordersBadge.style.display = pendingOrders > 0 ? 'block' : 'none';
        }

        if (alertsBadge) {
            alertsBadge.textContent = activeAlerts;
            alertsBadge.style.display = activeAlerts > 0 ? 'block' : 'none';
            alertsBadge.classList.toggle('alert-badge', activeAlerts > 0);
        }
    }

    updateNotificationCount() {
        const totalNotifications = this.data.alerts.filter(alert => !alert.resolved).length;
        const notificationCount = document.querySelector('.notification-count');
        
        if (notificationCount) {
            notificationCount.textContent = totalNotifications;
            notificationCount.style.display = totalNotifications > 0 ? 'block' : 'none';
        }
    }

    renderCurrentPage() {
        this.loadPageData(this.currentPage);
    }

    renderOverview() {
        this.renderRecentActivity();
    }

    renderRecentActivity() {
        const activityContainer = document.querySelector('.activity-feed');
        if (!activityContainer) return;

        const recentActivity = [
            ...this.data.orders.slice(-5).map(order => ({
                type: 'order',
                message: `New order from Table ${order.table_number}`,
                time: order.timestamp,
                icon: 'fas fa-shopping-cart'
            })),
            ...this.data.alerts.slice(-5).map(alert => ({
                type: 'alert',
                message: `Customer call from Table ${alert.table_number}`,
                time: alert.timestamp,
                icon: 'fas fa-bell'
            }))
        ].sort((a, b) => new Date(b.time) - new Date(a.time)).slice(0, 10);

        const activityHTML = recentActivity.map(activity => `
            <div class="activity-item">
                <div class="activity-icon ${activity.type}">
                    <i class="${activity.icon}"></i>
                </div>
                <div class="activity-content">
                    <p>${activity.message}</p>
                    <span class="activity-time">${this.formatTime(activity.time)}</span>
                </div>
            </div>
        `).join('');

        activityContainer.innerHTML = activityHTML;
    }

    renderTables() {
        const tablesContainer = document.querySelector('.tables-grid');
        if (!tablesContainer) return;

        const tablesHTML = this.data.tables.map(table => {
            const statusClass = `table-${table.status}`;
            const statusText = {
                empty: 'Available',
                occupied: 'Occupied',
                needs_attention: 'Needs Attention'
            };

            return `
                <div class="table-card ${statusClass}">
                    <div class="table-header">
                        <div class="table-number">
                            <div class="table-status-indicator"></div>
                            Table ${table.number}
                        </div>
                        <span class="table-status">${statusText[table.status]}</span>
                    </div>
                    
                    ${table.status === 'empty' ? `
                        <div class="empty-table">
                            <i class="fas fa-chair"></i>
                            <p>Available for seating</p>
                        </div>
                    ` : `
                        <div class="customer-info">
                            <p><strong>Customer:</strong> ${table.customer_name || 'N/A'}</p>
                            <p><strong>Duration:</strong> ${this.calculateDuration(table.seated_time)}</p>
                            ${table.order_total ? `<p><strong>Order Total:</strong> $${table.order_total.toFixed(2)}</p>` : ''}
                        </div>
                        
                        ${table.alerts && table.alerts.length > 0 ? `
                            <div class="table-alerts">
                                ${table.alerts.map(alert => `
                                    <div class="alert-item">
                                        <i class="fas fa-exclamation-triangle"></i>
                                        <span>${alert.message}</span>
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    `}
                    
                    <div class="table-actions">
                        ${table.status !== 'empty' ? `
                            <button class="btn-small btn-info btn-view-details" data-table-id="${table.id}">
                                <i class="fas fa-eye"></i> Details
                            </button>
                            <button class="btn-small btn-success btn-clean-table" data-table-id="${table.id}">
                                <i class="fas fa-broom"></i> Clean
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');

        tablesContainer.innerHTML = tablesHTML;
    }

    renderOrders() {
        const ordersContainer = document.querySelector('.orders-list');
        if (!ordersContainer) return;

        const ordersHTML = this.data.orders.map(order => `
            <div class="order-card">
                <div class="order-header">
                    <div class="order-info">
                        <span class="order-id">#${order.id}</span>
                        <span class="table-number">Table ${order.table_number}</span>
                        <span class="customer-name">${order.customer_name}</span>
                    </div>
                    <div class="order-status">
                        <span class="status-badge status-${order.status}">${order.status}</span>
                        <span class="order-time">${this.formatTime(order.timestamp)}</span>
                    </div>
                </div>
                
                <div class="order-items">
                    ${order.items.map(item => `
                        <div class="order-item">
                            <div>
                                <span class="item-name">${item.name}</span>
                                <span class="item-quantity">x${item.quantity}</span>
                            </div>
                            <span class="item-price">$${(item.price * item.quantity).toFixed(2)}</span>
                        </div>
                    `).join('')}
                </div>
                
                <div class="order-actions">
                    <span class="order-total">Total: $${order.total.toFixed(2)}</span>
                    <div>
                        ${order.status === 'pending' ? `
                            <button class="btn-small btn-info btn-mark-preparing" data-order-id="${order.id}">
                                <i class="fas fa-clock"></i> Mark Preparing
                            </button>
                        ` : ''}
                        ${order.status === 'preparing' ? `
                            <button class="btn-small btn-success btn-mark-ready" data-order-id="${order.id}">
                                <i class="fas fa-check"></i> Mark Ready
                            </button>
                        ` : ''}
                        ${order.status === 'ready' ? `
                            <button class="btn-small btn-primary btn-complete-order" data-order-id="${order.id}">
                                <i class="fas fa-check-double"></i> Complete
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `).join('');

        ordersContainer.innerHTML = ordersHTML;
    }

    renderAlerts() {
        const alertsContainer = document.querySelector('.alerts-list');
        if (!alertsContainer) return;

        const activeAlerts = this.data.alerts.filter(alert => !alert.resolved);
        
        const alertsHTML = activeAlerts.map(alert => `
            <div class="alert-card">
                <div class="alert-header">
                    <div class="alert-customer">
                        <i class="fas fa-user"></i>
                        <strong>${alert.customer_name}</strong>
                    </div>
                    <div class="alert-table">
                        <i class="fas fa-chair"></i>
                        Table ${alert.table_number}
                    </div>
                    <div class="alert-time">
                        <i class="fas fa-clock"></i>
                        ${this.formatTime(alert.timestamp)}
                    </div>
                </div>
                
                <div class="alert-message">
                    <p><strong>Request:</strong> ${alert.message}</p>
                </div>
                
                <div class="alert-actions">
                    <button class="btn-small btn-success btn-resolve-alert" data-alert-id="${alert.id}">
                        <i class="fas fa-check"></i> Resolve
                    </button>
                    <button class="btn-small btn-info btn-respond-alert" data-alert-id="${alert.id}">
                        <i class="fas fa-reply"></i> Respond
                    </button>
                </div>
            </div>
        `).join('');

        alertsContainer.innerHTML = alertsHTML || '<p class="text-center">No active alerts</p>';
    }

    renderMenu() {
        const menuContainer = document.querySelector('.menu-preview');
        if (!menuContainer) return;

        const menuHTML = this.data.menu.map(item => `
            <div class="menu-item-card">
                <h4>${item.name}</h4>
                <p>${item.description}</p>
                <p class="price">$${item.price.toFixed(2)}</p>
                <p class="category">${item.category}</p>
            </div>
        `).join('');

        menuContainer.innerHTML = menuHTML;
    }

    renderAnalytics() {
        // Implement analytics rendering
        console.log('Rendering analytics:', this.data.analytics);
    }

    renderSettings() {
        // Implement settings rendering
        console.log('Rendering settings');
    }

    // Action Methods
    async cleanTable(tableId) {
        try {
            const response = await fetch(`/api/tables/${tableId}/clean`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('Table cleaned successfully', 'success');
                this.loadTables();
            }
        } catch (error) {
            console.error('Error cleaning table:', error);
            this.showNotification('Error cleaning table', 'error');
        }
    }

    async updateOrderStatus(orderId, status) {
        try {
            const response = await fetch(`/api/orders/${orderId}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ status })
            });
            
            if (response.ok) {
                this.showNotification(`Order marked as ${status}`, 'success');
                this.loadOrders();
            }
        } catch (error) {
            console.error('Error updating order status:', error);
            this.showNotification('Error updating order status', 'error');
        }
    }

    async resolveAlert(alertId) {
        try {
            const response = await fetch(`/api/alerts/${alertId}/resolve`, {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('Alert resolved', 'success');
                this.loadAlerts();
            }
        } catch (error) {
            console.error('Error resolving alert:', error);
            this.showNotification('Error resolving alert', 'error');
        }
    }

    async respondToAlert(alertId) {
        const response = prompt('Enter your response:');
        if (!response) return;

        try {
            const apiResponse = await fetch(`/api/alerts/${alertId}/respond`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ response })
            });
            
            if (apiResponse.ok) {
                this.showNotification('Response sent', 'success');
            }
        } catch (error) {
            console.error('Error sending response:', error);
            this.showNotification('Error sending response', 'error');
        }
    }

    async refreshData() {
        const refreshBtn = document.querySelector('.btn-refresh');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
        }

        try {
            await this.loadInitialData();
            this.showNotification('Data refreshed', 'success');
        } catch (error) {
            this.showNotification('Error refreshing data', 'error');
        } finally {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
            }
        }
    }

    applyFilter(filterBtn) {
        // Remove active class from all filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Add active class to clicked button
        filterBtn.classList.add('active');
        
        // Apply filter logic based on button data
        const filter = filterBtn.dataset.filter;
        this.applyOrderFilter(filter);
    }

    applyOrderFilter(filter) {
        const orderCards = document.querySelectorAll('.order-card');
        
        orderCards.forEach(card => {
            const statusBadge = card.querySelector('.status-badge');
            const status = statusBadge ? statusBadge.textContent.toLowerCase() : '';
            
            if (filter === 'all' || status === filter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    // Socket Event Handlers
    handleTableUpdate(data) {
        console.log('Table update received:', data);
        this.loadTables();
        this.updateStats();
    }

    handleNewOrder(data) {
        console.log('New order received:', data);
        this.loadOrders();
        this.updateStats();
        this.showNotification(`New order from Table ${data.table_number}`, 'info');
    }

    handleOrderUpdate(data) {
        console.log('Order update received:', data);
        this.loadOrders();
        this.updateStats();
    }

    handleCustomerCall(data) {
        console.log('Customer call received:', data);
        this.data.alerts.push(data);
        this.updateBadges();
        this.updateNotificationCount();
        this.showNotification(`Customer call from Table ${data.table_number}`, 'warning');
        
        if (this.currentPage === 'alerts') {
            this.renderAlerts();
        }
    }

    handleDataUpdate(data) {
        console.log('Data update received:', data);
        this.loadInitialData();
    }

    updateConnectionStatus(connected) {
        const statusIndicator = document.querySelector('.connection-status');
        if (statusIndicator) {
            statusIndicator.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
            statusIndicator.title = connected ? 'Connected' : 'Disconnected';
        }
    }

    // Auto-refresh
    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadInitialData();
        }, 30000); // Refresh every 30 seconds
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Utility Methods
    formatTime(timestamp) {
        if (!timestamp) return 'N/A';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            const minutes = Math.floor(diff / 60000);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diff < 86400000) { // Less than 1 day
            const hours = Math.floor(diff / 3600000);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString();
        }
    }

    calculateDuration(startTime) {
        if (!startTime) return 'N/A';
        
        const start = new Date(startTime);
        const now = new Date();
        const diff = now - start;
        
        const hours = Math.floor(diff / 3600000);
        const minutes = Math.floor((diff % 3600000) / 60000);
        
        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else {
            return `${minutes}m`;
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add to DOM
        const container = document.getElementById('notifications-container') || this.createNotificationsContainer();
        container.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);

        // Close button handler
        notification.querySelector('.notification-close').addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    createNotificationsContainer() {
        const container = document.createElement('div');
        container.id = 'notifications-container';
        container.className = 'notifications-container';
        document.body.appendChild(container);
        return container;
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    // Cleanup
    destroy() {
        this.stopAutoRefresh();
        if (this.socket) {
            this.socket.disconnect();
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new StaffDashboard();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (window.dashboard) {
        window.dashboard.destroy();
    }
});