# Green Heaven Restaurant Management System

A modern, real-time restaurant management system built with Python Flask and featuring a comprehensive staff dashboard. This system provides organized interfaces for restaurant staff and customers with real-time communication via WebSockets.

## 🆕 Latest Updates & Major Improvements

### ✅ **Complete Staff Dashboard Redesign**
- **Modern Dashboard Layout**: Professional sidebar navigation with organized sections
- **Separated Functional Areas**: Overview, Table Management, Orders, Alerts, Menu, Analytics, Settings
- **Real-time Navigation**: Smooth page transitions with keyboard shortcuts (Ctrl+1-7)
- **Live Notifications**: Real-time badges and notification counts
- **Mobile-Responsive**: Collapsible sidebar and optimized mobile experience

### ✅ **Enhanced Staff Workflow**
- **Overview Dashboard**: Quick stats, recent activity feed, and action buttons
- **Table Management**: Visual table status with customer information and alerts
- **Order Processing**: Complete workflow from pending to completion
- **Alert System**: Customer call management with response capabilities
- **Menu Preview**: Quick access to menu items and management
- **Analytics**: Performance metrics and reporting
- **Settings Panel**: System configuration and preferences

### ✅ **Real-time Performance Optimization**
- **Supabase Integration**: Enterprise-level real-time database with local fallback
- **Socket.IO Communication**: Instant updates across all connected devices
- **Auto-refresh**: Automatic data synchronization every 30 seconds
- **Template Optimization**: Removed JSON template injection for better performance
- **API-based Loading**: Dynamic content loading via REST APIs

### ✅ **Mobile & Responsive Design**
- **Mobile-First Approach**: Optimized for smartphones and tablets
- **Touch-Friendly Interface**: Large buttons and intuitive navigation
- **Responsive Sidebar**: Collapsible navigation for mobile devices
- **Adaptive Layouts**: Grid systems that work across all screen sizes

## Features

### Customer Features
- **Welcome Page**: Enter name and table number (Operating Hours: 11:00 AM - 11:00 PM)
- **Dynamic Menu**: Browse items with photos, descriptions, and prices
- **Category Filtering**: Filter by Appetizers, Main Course, Sri Lankan Specials, etc.
- **Shopping Cart**: Add items with quantity controls
- **Order Placement**: Place orders directly from the table
- **Call Staff**: Request assistance with real-time notifications
- **Order Tracking**: Real-time updates on order status

### Staff Features - Modern Dashboard
#### Overview Section
- **Quick Statistics**: Tables occupied/available, pending orders, active alerts
- **Recent Activity**: Live feed of orders, alerts, and customer interactions
- **Quick Actions**: Direct access to common tasks

#### Table Management
- **Visual Table Status**: Color-coded table cards with real-time status
- **Customer Information**: Names, seating duration, order totals
- **Alert Indicators**: Visual and audio alerts for customer requests
- **Action Buttons**: Table cleaning, details view, status updates

#### Order Management
- **Complete Order Workflow**: Pending → Preparing → Ready → Completed
- **Order Filtering**: Filter by status with active indicators
- **Order Details**: Customer info, items, quantities, totals
- **Status Updates**: One-click status changes with real-time sync

#### Alert System
- **Customer Call Management**: Organized list of customer requests
- **Response System**: Send responses directly to customer tables
- **Auto-Resolution**: Mark alerts as resolved with staff actions
- **Priority Indicators**: Visual cues for urgent requests

#### Analytics & Reporting
- **Daily Revenue**: Real-time revenue tracking
- **Order Statistics**: Counts by status and time periods
- **Table Utilization**: Occupancy rates and turnover metrics
- **Popular Items**: Most ordered menu items analysis

### Technical Features
- **Real-time Communication**: WebSocket integration for instant updates
- **Modern Dashboard**: Professional interface with organized navigation
- **Supabase Database**: Real-time database with local fallback
- **API Architecture**: RESTful endpoints for all operations
- **Error Handling**: Comprehensive error management
- **Performance Optimized**: Fast loading and smooth interactions
- **Keyboard Shortcuts**: Quick navigation for power users

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
cd "/Users/dinuthfernando/Documents/projects/green heaven"
pip install -r requirements.txt
```

### Step 2: Environment Configuration
Create a `.env` file with your Supabase credentials (optional):
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SECRET_KEY=your_secret_key
```

### Step 3: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5001`

## Usage

### For Customers
1. Visit `http://localhost:5001` 
2. Enter your name and table number
3. Browse the menu and add items to cart
4. Place orders or call staff as needed

### For Staff
1. Visit `http://localhost:5001/staff`
2. Navigate through the organized dashboard sections
3. Monitor real-time alerts and orders
4. Process orders through the complete workflow
5. Manage customer requests and responses

## Project Structure

```
green heaven/
├── app.py                     # Flask application with API endpoints
├── requirements.txt           # Python dependencies
├── templates/                 # HTML templates
│   ├── customer_entry.html        # Customer welcome page
│   ├── customer_page.html         # Customer interface
│   └── staff_dashboard.html       # Modern staff dashboard
└── static/                    # Static assets
    ├── css/                   # Stylesheets
    │   ├── customer-entry.css     # Entry page styles
    │   ├── customer.css           # Customer interface styles
    │   ├── menu-management.css    # Menu management styles
    │   └── staff-dashboard.css    # Modern dashboard styles
    ├── js/                    # JavaScript files
    │   ├── customer.js            # Customer functionality
    │   ├── menu-management.js     # Menu management
    │   └── staff-dashboard.js     # Dashboard functionality
    └── images/                # Image assets
```

## API Endpoints

### Customer Endpoints
- `GET /` - Customer entry page
- `GET /customer` - Main customer interface
- `POST /api/call-staff` - Request staff assistance
- `POST /api/place-order` - Place new order
- `GET /api/menu` - Get menu items

### Staff Dashboard Endpoints
- `GET /staff` - Modern staff dashboard
- `GET /api/tables` - Get table status
- `GET /api/orders` - Get orders with filtering
- `GET /api/alerts` - Get active alerts
- `GET /api/analytics` - Get performance metrics
- `POST /api/tables/<id>/clean` - Clean/reset table
- `PUT /api/orders/<id>/status` - Update order status
- `POST /api/alerts/<id>/resolve` - Resolve alert
- `POST /api/alerts/<id>/respond` - Send response to customer

### Legacy Endpoints
- `POST /api/add-menu-item` - Add menu item
- `POST /api/update-order-status` - Update order status
- `GET /api/orders/stats` - Get order statistics

## Dashboard Navigation

### Keyboard Shortcuts
- `Ctrl+1` - Overview
- `Ctrl+2` - Table Management  
- `Ctrl+3` - Order Management
- `Ctrl+R` - Refresh Data

### Navigation Sections
1. **Overview** - Dashboard home with quick stats and activity
2. **Tables** - Visual table management with status indicators
3. **Orders** - Complete order processing workflow
4. **Alerts** - Customer call and request management
5. **Menu** - Menu preview and management access
6. **Analytics** - Performance metrics and reports
7. **Settings** - System configuration

## Customization

### Restaurant Information
Update in templates:
- Restaurant name: "Green Heaven"
- Location: "Katuneriya, Sri Lanka"  
- Operating Hours: "11:00 AM - 11:00 PM"

### Styling
Modern green theme with:
- Primary colors: #2d5a27, #4a7c59
- Professional dashboard design
- Responsive grid layouts
- Smooth animations and transitions

## Technologies Used

- **Backend**: Python Flask, Flask-SocketIO
- **Database**: Supabase (with local JSON fallback)
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Real-time**: WebSockets via Socket.IO
- **Styling**: CSS Grid, Flexbox, modern animations
- **Icons**: Font Awesome
- **Fonts**: Inter (Google Fonts)

## Production Deployment

### Render.com Deployment
1. Connect GitHub repository
2. Set environment variables in Render dashboard
3. Auto-deployment on git push

### Environment Variables
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SECRET_KEY=your_flask_secret_key
PORT=5001
```

## Contributing

This is a custom restaurant management system for Green Heaven restaurant. The modern dashboard architecture provides a scalable foundation for additional features and customizations.

## License

Custom application for Green Heaven Restaurant, Katuneriya, Sri Lanka.