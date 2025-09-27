# Green Heaven Restaurant Management System

A modern, real-time restaurant management system built with Python Flask, HTML, CSS, and JavaScript. This system provides separate interfaces for restaurant staff and customers with real-time communication via WebSockets.

## 🆕 Latest Updates & Improvements

### ✅ **Enhanced Order Tracking**
- **Order Statistics Dashboard**: Real-time counters for pending, preparing, ready, and completed orders
- **Order Filtering**: Filter orders by status (All, Pending, Preparing, Ready, Completed)
- **Improved Order Management**: Better status tracking and workflow management
- **Order History**: Complete tracking from placement to completion

### ✅ **Mobile & Tablet Optimized**
- **Fully Responsive Design**: Works perfectly on smartphones, tablets, and desktops
- **Touch-Friendly Interface**: Optimized buttons and controls for touch devices
- **Mobile-First Approach**: Better typography and spacing for small screens
- **Tablet Layout**: Optimized layouts for medium-sized screens

### ✅ **Error Handling & Reliability**
- **Robust Error Handling**: Comprehensive error handling for all API endpoints
- **Better Data Validation**: Validation for all user inputs
- **Loading States**: Visual feedback during operations
- **Error Messages**: User-friendly error messages

### ✅ **Performance Improvements**
- **Dynamic Menu Loading**: Menu items load dynamically for better performance
- **Real-time Updates**: Instant updates without page refreshes
- **Auto-refresh**: Automatic data refreshing every 30 seconds

## Features

### Customer Features
- **Welcome Page**: Customers enter their name and table number
- **Dynamic Menu**: Browse menu items with photos, descriptions, and prices
- **Category Filtering**: Filter menu by categories (Appetizers, Main Course, Sri Lankan Specials, etc.)
- **Shopping Cart**: Add items to cart with quantity controls
- **Order Placement**: Place orders directly from the table
- **Call Staff**: Request staff assistance with table number notification
- **Real-time Updates**: Receive notifications when order status changes
- **Mobile Optimized**: Perfect mobile and tablet experience
- **Touch-Friendly**: Optimized for touch interactions

### Staff Features
- **Enhanced Dashboard**: Overview with order statistics and filtering
- **Order Statistics**: Real-time counters for all order statuses
- **Order Filtering**: Filter by pending, preparing, ready, completed orders
- **Alert Management**: Receive and manage customer staff calls with table numbers
- **Advanced Order Management**: Track orders through complete workflow
- **Menu Management**: Add new menu items with photos, descriptions, and prices
- **Real-time Notifications**: Instant alerts for new orders and staff calls
- **Audio Alerts**: Sound notifications for important events
- **Mobile Optimized**: Full functionality on mobile devices

### Technical Features
- **Real-time Communication**: WebSocket integration for instant updates
- **Fully Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Modern UI**: Clean, professional interface with Green Heaven branding
- **Sri Lankan Theme**: Designed for Sri Lankan restaurant in Katuneriya
- **Audio Notifications**: Sound alerts for staff and customers
- **Error Handling**: Comprehensive error handling and user feedback
- **Performance Optimized**: Fast loading and smooth interactions
- **Touch-Friendly**: Optimized for touch devices with proper touch targets
- **Mobile-First**: Designed with mobile users in mind

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Step 1: Install Dependencies
```bash
cd "/Users/dinuthfernando/Documents/projects/green heaven"
pip install -r requirements.txt
```

### Step 2: Run the Application
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
2. Monitor alerts and orders in real-time
3. Update order statuses as food is prepared
4. Add new menu items with photos and descriptions

## Project Structure

```
green heaven/
├── app.py                 # Flask application with routes and API endpoints
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── customer_entry.html    # Customer welcome/entry page
│   ├── customer_page.html     # Main customer interface
│   └── staff_page.html        # Staff dashboard
└── static/               # Static assets
    ├── css/              # Stylesheets
    │   ├── customer-entry.css # Entry page styles
    │   ├── customer.css       # Customer page styles
    │   └── staff.css          # Staff dashboard styles
    ├── js/               # JavaScript files
    │   ├── customer.js        # Customer functionality
    │   └── staff.js           # Staff functionality
    └── images/           # Image assets (for menu items)
```

## API Endpoints

### Customer Endpoints
- `GET /` - Customer entry page
- `GET /customer` - Main customer interface
- `POST /api/call-staff` - Request staff assistance
- `POST /api/place-order` - Place a new order

### Staff Endpoints  
- `GET /staff` - Staff dashboard
- `POST /api/add-menu-item` - Add new menu item
- `POST /api/update-order-status` - Update order status
- `POST /api/dismiss-alert` - Dismiss staff alert
- `GET /api/orders` - Get orders (with optional status filter)
- `GET /api/orders/stats` - Get order statistics
- `GET /api/alerts` - Get all active alerts

## Customization

### Adding Menu Items
Staff can add menu items through the dashboard with:
- Item name and description
- Category (Appetizers, Main Course, etc.)
- Price in LKR
- Photo URL
- Detailed description

### Styling
The application uses a green theme representing "Green Heaven":
- Primary colors: #2d5a27, #4a7c59
- Modern, clean design with gradients and shadows
- Fully responsive for all device sizes

### Restaurant Information
Update restaurant details in the templates:
- Restaurant name: "Green Heaven" 
- Location: "Katuneriya, Sri Lanka"
- Contact info and hours in customer_entry.html

## Technologies Used

- **Backend**: Python Flask, Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Real-time**: WebSockets via Socket.IO
- **Styling**: CSS Grid, Flexbox, CSS animations
- **Icons**: Font Awesome
- **Fonts**: Inter (Google Fonts)

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Production Deployment

For production deployment:

1. Set up a proper database (PostgreSQL/MySQL) instead of in-memory storage
2. Configure a production WSGI server (Gunicorn)
3. Set up SSL certificates for HTTPS
4. Use environment variables for configuration
5. Set up proper logging and monitoring
6. Configure file uploads for menu item images

## 🌐 Deployment on Render

### Prerequisites
- GitHub repository
- Render account (free tier available)
- Firebase/Supabase database setup

### Environment Variables for Render
Set these in your Render dashboard:
```
DATABASE_URL=your_database_connection_string
SECRET_KEY=your_secret_key_here
PORT=5001
PYTHON_VERSION=3.9.7
```

### Deployment Files
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification
- `render.yaml` - Render configuration

### Automatic Deployment
1. Connect your GitHub repository to Render
2. Render will automatically detect the Flask app
3. Set environment variables in Render dashboard
4. Deploy will trigger on every git push

## 📊 Database Integration

### Firebase Setup (Recommended)
1. Create Firebase project at https://console.firebase.google.com
2. Enable Firestore Database
3. Generate service account key
4. Add credentials to Render environment variables

### Database Collections
- `orders` - Digital orders
- `manual_orders` - Staff-added orders
- `daily_totals` - Revenue tracking
- `staff_alerts` - Customer assistance requests

## 🔄 Real-time Database Features
- **Live Order Tracking**: Orders sync across all devices
- **Staff Notifications**: Instant alerts for new orders/requests
- **Revenue Analytics**: Real-time business metrics
- **Multi-device Sync**: Works across multiple staff devices

## Contributing

This is a custom restaurant management system for Green Heaven restaurant. For modifications or improvements, please ensure all changes maintain the Sri Lankan theme and real-time functionality.

## License

Custom application for Green Heaven Restaurant, Katuneriya, Sri Lanka.