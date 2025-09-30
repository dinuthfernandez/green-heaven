// Green Heaven Staff Dashboard JavaScript

class StaffDashboard {
    constructor() {
        this.socket = null;
        this.currentPage = 'overview';
        this.sidebarOpen = window.innerWidth > 1024;
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
        console.log('🚀 Initializing Staff Dashboard...');
        this.bindEvents();
        this.initializeNavigationNew();
        this.loadInitialData();
        this.startAutoRefresh();
        console.log('✅ Staff Dashboard initialized successfully');
    }

    handleSocketConnection(socketInstance) {
        this.socket = socketInstance;
        console.log('🔗 Socket.IO connected to dashboard');
    }

    bindEvents() {
        // Navigation click handler
        document.addEventListener('click', (e) => {
            // Navigation links
            if (e.target.closest('.nav-link')) {
                e.preventDefault();
                const navLink = e.target.closest('.nav-link');
                const page = navLink.getAttribute('data-page');
                if (page) {
                    this.navigateToPageNew(page);
                }
                return;
            }

            // Menu toggle
            if (e.target.closest('.menu-toggle')) {
                this.toggleSidebar();
                return;
            }

            // Refresh button
            if (e.target.closest('.btn-refresh')) {
                this.refreshData();
                return;
            }

            // Filter buttons
            if (e.target.closest('.filter-btn')) {
                this.applyFilter(e.target.closest('.filter-btn'));
                return;
            }

            // Action buttons with proper delegation
            this.handleActionButtons(e);
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1':
                        e.preventDefault();
                        this.navigateToPageNew('overview');
                        break;
                    case '2':
                        e.preventDefault();
                        this.navigateToPageNew('tables');
                        break;
                    case '3':
                        e.preventDefault();
                        this.navigateToPageNew('orders');
                        break;
                    case '4':
                        e.preventDefault();
                        this.navigateToPageNew('alerts');
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

    handleActionButtons(e) {
        const button = e.target.closest('button');
        if (!button) return;

        // Table actions
        if (button.classList.contains('btn-clean-table')) {
            const tableId = button.getAttribute('data-table-id');
            this.cleanTable(tableId);
        }
        else if (button.classList.contains('btn-view-details')) {
            const tableId = button.getAttribute('data-table-id');
            this.viewTableDetails(tableId);
        }
        // Order actions
        else if (button.classList.contains('btn-mark-preparing')) {
            const orderId = button.getAttribute('data-order-id');
            this.updateOrderStatus(orderId, 'preparing');
        }
        else if (button.classList.contains('btn-mark-ready')) {
            const orderId = button.getAttribute('data-order-id');
            this.updateOrderStatus(orderId, 'ready');
        }
        else if (button.classList.contains('btn-complete-order')) {
            const orderId = button.getAttribute('data-order-id');
            this.updateOrderStatus(orderId, 'completed');
        }
        // Alert actions
        else if (button.classList.contains('btn-resolve-alert')) {
            const alertId = button.getAttribute('data-alert-id');
            this.resolveAlert(alertId);
        }
        else if (button.classList.contains('btn-respond-alert')) {
            const alertId = button.getAttribute('data-alert-id');
            this.respondToAlert(alertId);
        }
    }

    initializeNavigationNew() {
        // Set active page based on URL fragment or default to overview
        const hash = window.location.hash.slice(1);
        const initialPage = hash && this.isValidPage(hash) ? hash : 'overview';
        this.navigateToPageNew(initialPage, false);
    }

    isValidPage(pageName) {
        const validPages = ['overview', 'tables', 'orders', 'alerts', 'menu', 'analytics', 'settings'];
        return validPages.includes(pageName);
    }

    navigateToPageNew(pageName, updateUrl = true) {
        if (!this.isValidPage(pageName)) {
            console.warn(`Invalid page: ${pageName}`);
            return;
        }

        console.log(`📄 Navigating to: ${pageName}`);

        // Remove active class from all nav items and page content
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelectorAll('.page-content').forEach(page => {
            page.classList.remove('active');
        });

        // Add active class to current nav item and page
        const navItem = document.querySelector(`[data-page="${pageName}"]`);
        const pageContent = document.getElementById(`${pageName}-page`);

        if (navItem && pageContent) {
            navItem.classList.add('active');
            pageContent.classList.add('active');
            this.currentPage = pageName;

            // Update page title
            const pageTitle = document.getElementById('page-title');
            if (pageTitle) {
                const titles = {
                    overview: 'Restaurant Overview',
                    tables: 'Table Management',
                    orders: 'Order Management',
                    alerts: 'Customer Calls & Alerts',
                    menu: 'Menu Management',
                    analytics: 'Analytics & Reports',
                    settings: 'Restaurant Settings'
                };
                pageTitle.textContent = titles[pageName] || 'Dashboard';
            }

            // Update URL
            if (updateUrl) {
                window.history.pushState(null, '', `#${pageName}`);
            }

            // Load page-specific data
            this.loadPageData(pageName);

            // Close sidebar on mobile after navigation
            if (window.innerWidth <= 1024) {
                this.closeSidebar();
            }
        } else {
            console.error(`Navigation elements not found for page: ${pageName}`);
        }
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.toggle('open');
            this.sidebarOpen = sidebar.classList.contains('open');
        }
    }

    closeSidebar() {
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
            sidebar.classList.remove('open');
            this.sidebarOpen = false;
        }
    }

    handleResize() {
        if (window.innerWidth > 1024) {
            // Desktop - ensure sidebar is properly shown
            const sidebar = document.querySelector('.sidebar');
            if (sidebar) {
                sidebar.classList.remove('open');
                this.sidebarOpen = true;
            }
        } else {
            // Mobile - hide sidebar
            this.sidebarOpen = false;
        }
    }

    async loadInitialData() {
        console.log('📊 Loading initial data...');
        try {
            // Show loading states
            this.showLoadingStates();
            
            await Promise.all([
                this.loadTables(),
                this.loadOrders(),
                this.loadAlerts(),
                this.loadMenu(),
                this.loadAnalytics()
            ]);
            
            this.updateDashboard();
            console.log('✅ Initial data loaded successfully');
        } catch (error) {
            console.error('❌ Error loading initial data:', error);
            this.showNotification('Error loading data. Please refresh the page.', 'error');
        }
    }

    showLoadingStates() {
        // Show loading spinners in each section
        const loadingHTML = `
            <div class="loading-message">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading...</p>
            </div>
        `;
        
        const containers = [
            '#tables-grid',
            '#orders-list', 
            '#alerts-list',
            '.activity-feed'
        ];
        
        containers.forEach(selector => {
            const container = document.querySelector(selector);
            if (container) {
                container.innerHTML = loadingHTML;
            }
        });
    }

    async loadTables() {
        try {
            const response = await fetch('/api/tables');
            if (response.ok) {
                this.data.tables = await response.json();
            } else {
                // Fallback data
                this.data.tables = this.generateFallbackTables();
            }
        } catch (error) {
            console.warn('Using fallback table data:', error);
            this.data.tables = this.generateFallbackTables();
        }
    }

    async loadOrders() {
        try {
            const response = await fetch('/api/orders');
            if (response.ok) {
                this.data.orders = await response.json();
            } else {
                this.data.orders = [];
            }
        } catch (error) {
            console.warn('Orders data unavailable:', error);
            this.data.orders = [];
        }
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts');
            if (response.ok) {
                this.data.alerts = await response.json();
            } else {
                this.data.alerts = [];
            }
        } catch (error) {
            console.warn('Alerts data unavailable:', error);
            this.data.alerts = [];
        }
    }

    async loadMenu() {
        try {
            const response = await fetch('/api/menu');
            if (response.ok) {
                this.data.menu = await response.json();
            } else {
                this.data.menu = [];
            }
        } catch (error) {
            console.warn('Menu data unavailable:', error);
            this.data.menu = [];
        }
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/analytics');
            if (response.ok) {
                this.data.analytics = await response.json();
            } else {
                this.data.analytics = {};
            }
        } catch (error) {
            console.warn('Analytics data unavailable:', error);
            this.data.analytics = {};
        }
    }

    generateFallbackTables() {
        // Generate sample table data when API is not available
        const tables = [];
        for (let i = 1; i <= 12; i++) {
            tables.push({
                id: i,
                number: i <= 2 ? `VIP-${i}` : `T-${i}`,
                status: i <= 3 ? 'occupied' : (i <= 5 ? 'needs_attention' : 'empty'),
                customer_name: i <= 5 ? `Customer ${i}` : null,
                seated_time: i <= 5 ? new Date(Date.now() - (i * 30 * 60000)).toISOString() : null,
                order_total: i <= 5 ? (25 + i * 10) : null,
                alerts: i === 2 || i === 4 ? [{ message: 'Needs assistance' }] : []
            });
        }
        return tables;
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

    async clearAllAlerts() {
        if (!confirm('Are you sure you want to clear all customer alerts?')) {
            return;
        }

        try {
            const response = await fetch('/api/alerts/clear-all', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.showNotification('All alerts cleared successfully', 'success');
                this.loadAlerts();
                this.updateBadges();
            } else {
                this.showNotification('Error clearing alerts', 'error');
            }
        } catch (error) {
            console.error('Error clearing all alerts:', error);
            this.showNotification('Error clearing alerts', 'error');
        }
    }

    async viewTableDetails(tableId) {
        // For now, just show an alert with table info
        const table = this.data.tables.find(t => t.id == tableId);
        if (table) {
            alert(`Table Details:\nNumber: ${table.number}\nStatus: ${table.status}\nCustomer: ${table.customer_name || 'None'}`);
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