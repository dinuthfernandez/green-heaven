from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
from datetime import datetime, timedelta
import uuid
import io

# PDF generation imports (optional)
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("PDF generation not available - reportlab not installed")

# Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Firebase not available - using local storage")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available - using system environment variables")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'green-heaven-secret-key-2024')
socketio = SocketIO(app, cors_allowed_origins="*")

# Firebase Configuration with improved error handling
db = None
if FIREBASE_AVAILABLE:
    try:
        # Ensure firebase_admin, credentials, and firestore are imported
        import firebase_admin
        from firebase_admin import credentials, firestore

        # Initialize Firebase (only if not already initialized)
        if not firebase_admin._apps:
            # First try service account file
            service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
            if service_account_path and os.path.exists(service_account_path):
                print("📝 Using Firebase service account file")
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            else:
                # Use environment variables for Render deployment
                firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
                firebase_private_key = os.getenv('FIREBASE_PRIVATE_KEY')
                firebase_client_email = os.getenv('FIREBASE_CLIENT_EMAIL')
                
                print(f"📝 Firebase Project ID: {firebase_project_id}")
                print(f"📝 Firebase Client Email: {firebase_client_email}")
                print(f"📝 Firebase Private Key: {'Present' if firebase_private_key else 'Missing'}")
                
                if firebase_project_id and firebase_private_key and firebase_client_email:
                    firebase_config = {
                        "type": "service_account",
                        "project_id": firebase_project_id,
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": firebase_private_key.replace('\\n', '\n'),
                        "client_email": firebase_client_email,
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{firebase_client_email}"
                    }
                    print("📝 Initializing Firebase with environment variables")
                    cred = credentials.Certificate(firebase_config)
                    firebase_admin.initialize_app(cred)
                else:
                    print("❌ Missing required Firebase environment variables")
                    print(f"   - FIREBASE_PROJECT_ID: {'✓' if firebase_project_id else '✗'}")
                    print(f"   - FIREBASE_PRIVATE_KEY: {'✓' if firebase_private_key else '✗'}")
                    print(f"   - FIREBASE_CLIENT_EMAIL: {'✓' if firebase_client_email else '✗'}")
                    raise Exception("Missing required Firebase environment variables")

        # Get Firestore client
        db = firestore.client()
        
        # Test connection
        try:
            test_collection = db.collection('connection_test')
            test_doc = test_collection.document('test')
            test_doc.set({'timestamp': datetime.now().isoformat(), 'status': 'connected'})
            print("✅ Firebase connected and tested successfully!")
        except Exception as test_error:
            print(f"⚠️ Firebase connected but test write failed: {test_error}")
            # Don't fail completely, just warn

    except Exception as e:
        print(f"❌ Firebase connection failed: {e}")
        print(f"📝 Error details: {type(e).__name__}: {str(e)}")
        print("📝 Falling back to local JSON storage")
        db = None
else:
    print("📝 Firebase not available - using local JSON storage")

# Data storage configuration
DATA_DIR = 'data'
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
MANUAL_ORDERS_FILE = os.path.join(DATA_DIR, 'manual_orders.json')
DAILY_TOTALS_FILE = os.path.join(DATA_DIR, 'daily_totals.json')

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Data storage functions with improved performance and error handling
def load_data(collection_name):
    """Load data from Firebase or local JSON file with caching"""
    try:
        if db:
            # Firebase implementation with timeout
            docs = db.collection(collection_name).stream()
            data = [doc.to_dict() for doc in docs]
            return data
        else:
            # Local JSON file implementation
            file_mapping = {
                'orders': ORDERS_FILE,
                'manual_orders': MANUAL_ORDERS_FILE,
                'daily_totals': DAILY_TOTALS_FILE
            }
            
            filename = file_mapping.get(collection_name)
            if not filename:
                print(f"Warning: Unknown collection name: {collection_name}")
                return []
                
            if not os.path.exists(filename):
                print(f"Info: File {filename} doesn't exist, returning empty list")
                return []
                
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    return []
                return json.loads(content)
                
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {collection_name}: {e}")
        return []
    except Exception as e:
        print(f"Error loading from {collection_name}: {e}")
        return []

def save_data(collection_name, data):
    """Save data to Firebase or local JSON file with better error handling"""
    try:
        if db:
            # Firebase implementation with batch operations for better performance
            if isinstance(data, list):
                # Use batch operations for better performance
                batch = db.batch()
                
                # Clear existing data first
                existing_docs = db.collection(collection_name).limit(500).stream()
                for doc in existing_docs:
                    batch.delete(doc.reference)
                
                # Add new data
                for item in data:
                    doc_id = item.get('id', str(uuid.uuid4()))
                    doc_ref = db.collection(collection_name).document(doc_id)
                    batch.set(doc_ref, item)
                
                # Commit batch
                batch.commit()
            else:
                # Single document
                doc_id = data.get('id', str(uuid.uuid4()))
                db.collection(collection_name).document(doc_id).set(data)
                
        else:
            # Local JSON file implementation with atomic writes
            save_data_local(collection_name, data)
            
    except Exception as e:
        print(f"Error saving to Firebase {collection_name}: {e}")
        # Always fall back to local storage
        save_data_local(collection_name, data)

def save_data_local(collection_name, data):
    """Save data to local JSON file with atomic writes"""
    file_mapping = {
        'orders': ORDERS_FILE,
        'manual_orders': MANUAL_ORDERS_FILE,
        'daily_totals': DAILY_TOTALS_FILE
    }
    
    filename = file_mapping.get(collection_name)
    if not filename:
        print(f"Warning: Unknown collection name: {collection_name}")
        return
        
    temp_filename = filename + '.tmp'
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Write to temporary file first, then rename (atomic operation)
        with open(temp_filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, default=str, ensure_ascii=False)
        
        # Atomic rename
        os.rename(temp_filename, filename)
        
    except Exception as e:
        print(f"Error saving to local file {filename}: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

def add_document(collection_name, document_data):
    """Add a single document to Firebase or local storage"""
    if db:
        try:
            doc_id = document_data.get('id', str(uuid.uuid4()))
            db.collection(collection_name).document(doc_id).set(document_data)
        except Exception as e:
            print(f"Error adding document to Firebase {collection_name}: {e}")
            # Fall back to local storage
            current_data = load_data(collection_name)
            current_data.append(document_data)
            save_data_local(collection_name, current_data)
    else:
        # Local storage - append to existing data
        current_data = load_data(collection_name)
        current_data.append(document_data)
        save_data_local(collection_name, current_data)

def update_document(collection_name, document_id, update_data):
    """Update a document in Firebase or local storage"""
    if db:
        try:
            db.collection(collection_name).document(document_id).update(update_data)
        except Exception as e:
            print(f"Error updating document in Firebase {collection_name}: {e}")
            # Fall back to local storage
            current_data = load_data(collection_name)
            for item in current_data:
                if item.get('id') == document_id:
                    item.update(update_data)
                    break
            save_data_local(collection_name, current_data)
    else:
        # Local storage - update in memory and save
        current_data = load_data(collection_name)
        for item in current_data:
            if item.get('id') == document_id:
                item.update(update_data)
                break
        save_data_local(collection_name, current_data)

def get_today_date():
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')

def get_daily_totals():
    """Get daily totals for today"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if db:
        # Firebase implementation
        try:
            doc_ref = db.collection('daily_totals').document(today)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                # Create default totals
                default_totals = {
                    'date': today,
                    'digital_orders': 0,
                    'manual_orders': 0,
                    'digital_revenue': 0.0,
                    'manual_revenue': 0.0,
                    'total_orders': 0,
                    'total_revenue': 0.0
                }
                doc_ref.set(default_totals)
                return default_totals
        except Exception as e:
            print(f"Error getting daily totals from Firebase: {e}")
            # Fall back to local storage
            pass
    
    # Local storage implementation
    daily_totals = load_data('daily_totals')
    
    # Find today's totals
    for totals in daily_totals:
        if totals.get('date') == today:
            return totals
    
    # Create default if not found
    default_totals = {
        'date': today,
        'digital_orders': 0,
        'manual_orders': 0,
        'digital_revenue': 0.0,
        'manual_revenue': 0.0,
        'total_orders': 0,
        'total_revenue': 0.0
    }
    daily_totals.append(default_totals)
    save_data('daily_totals', daily_totals)
    return default_totals

def update_daily_totals(amount, order_type):
    """Update daily totals with new order"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    if db:
        # Firebase implementation
        try:
            doc_ref = db.collection('daily_totals').document(today)
            doc = doc_ref.get()
            
            if doc.exists:
                totals = doc.to_dict()
            else:
                totals = {
                    'date': today,
                    'digital_orders': 0,
                    'manual_orders': 0,
                    'digital_revenue': 0.0,
                    'manual_revenue': 0.0,
                    'total_orders': 0,
                    'total_revenue': 0.0
                }
            
            # Ensure totals is not None and has all required keys
            if totals is None:
                totals = {
                    'date': today,
                    'digital_orders': 0,
                    'manual_orders': 0,
                    'digital_revenue': 0.0,
                    'manual_revenue': 0.0,
                    'total_orders': 0,
                    'total_revenue': 0.0
                }
            
            # Update based on order type
            if order_type == 'digital':
                totals['digital_orders'] = totals.get('digital_orders', 0) + 1
                totals['digital_revenue'] = totals.get('digital_revenue', 0.0) + float(amount)
            elif order_type == 'manual':
                totals['manual_orders'] = totals.get('manual_orders', 0) + 1
                totals['manual_revenue'] = totals.get('manual_revenue', 0.0) + float(amount)
            
            # Update totals
            totals['total_orders'] = totals.get('digital_orders', 0) + totals.get('manual_orders', 0)
            totals['total_revenue'] = totals.get('digital_revenue', 0.0) + totals.get('manual_revenue', 0.0)
            
            # Save to Firebase
            doc_ref.set(totals)
            return
            
        except Exception as e:
            print(f"Error updating daily totals in Firebase: {e}")
            # Fall back to local storage
            pass
    
    # Local storage implementation
    daily_totals = load_data('daily_totals')
    
    # Find or create today's totals
    today_totals = None
    for totals in daily_totals:
        if totals.get('date') == today:
            today_totals = totals
            break
    
    if not today_totals:
        today_totals = {
            'date': today,
            'digital_orders': 0,
            'manual_orders': 0,
            'digital_revenue': 0.0,
            'manual_revenue': 0.0,
            'total_orders': 0,
            'total_revenue': 0.0
        }
        daily_totals.append(today_totals)
    
    # Update based on order type
    if order_type == 'digital':
        today_totals['digital_orders'] += 1
        today_totals['digital_revenue'] += float(amount)
    elif order_type == 'manual':
        today_totals['manual_orders'] += 1
        today_totals['manual_revenue'] += float(amount)
    
    # Update totals
    today_totals['total_orders'] = today_totals['digital_orders'] + today_totals['manual_orders']
    today_totals['total_revenue'] = today_totals['digital_revenue'] + today_totals['manual_revenue']
    
    save_data('daily_totals', daily_totals)

# Load persistent data (initialize empty if using database)
if not db:
    all_orders = load_data('orders')
    manual_orders = load_data('manual_orders')

# In-memory storage (in production, use a database)
menu_items = [
    {
        'id': 'sri-curry',
        'name': 'Traditional Sri Lankan Curry',
        'description': 'Authentic curry with coconut milk, served with rice and papadum',
        'price': 1250.00,
        'image': 'https://images.unsplash.com/photo-1585937421612-70a008356fbe?w=400',
        'category': 'Sri Lankan Specials'
    },
    {
        'id': 'kottu-roti',
        'name': 'Chicken Kottu Roti',
        'description': 'Chopped flatbread stir-fried with chicken, vegetables and spices',
        'price': 950.00,
        'image': 'https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=400',
        'category': 'Sri Lankan Specials'
    },
    {
        'id': 'hoppers',
        'name': 'Egg Hoppers (2 pieces)',
        'description': 'Traditional bowl-shaped pancakes with egg, served with sambol',
        'price': 450.00,
        'image': 'https://images.unsplash.com/photo-1596797038530-2c107229654b?w=400',
        'category': 'Appetizers'
    },
    {
        'id': 'fish-curry',
        'name': 'Fish Curry',
        'description': 'Fresh fish cooked in coconut curry with Sri Lankan spices',
        'price': 1450.00,
        'image': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=400',
        'category': 'Main Course'
    },
    {
        'id': 'mango-lassi',
        'name': 'Fresh Mango Lassi',
        'description': 'Creamy yogurt drink blended with fresh mango',
        'price': 350.00,
        'image': 'https://images.unsplash.com/photo-1553909489-cd47e0ef937f?w=400',
        'category': 'Beverages'
    },
    {
        'id': 'coconut-cake',
        'name': 'Coconut Cake',
        'description': 'Traditional Sri Lankan coconut cake with jaggery',
        'price': 550.00,
        'image': 'https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400',
        'category': 'Desserts'
    }
]
# Initialize empty data (orders now use persistent storage)
staff_alerts = []

# Routes for customer pages
@app.route('/')
def customer_entry():
    """Customer entry page - name and table number"""
    return render_template('customer_entry.html')

@app.route('/customer')
def customer_page():
    """Main customer page - menu and ordering"""
    customer_name = request.args.get('name', '')
    table_number = request.args.get('table', '')
    
    if not customer_name or not table_number:
        return redirect(url_for('customer_entry'))
    
    return render_template('customer_page.html', 
                         customer_name=customer_name, 
                         table_number=table_number,
                         menu_items=menu_items)

# Routes for restaurant staff
@app.route('/staff')
def staff_page():
    """Restaurant staff page - orders, alerts, table management"""
    # Get table status information
    orders = load_data('orders')
    if not orders:
        orders = []
    tables = get_table_status()
    return render_template('staff_page.html', 
                         menu_items=menu_items,
                         orders=orders,
                         alerts=staff_alerts,
                         tables=tables)

@app.route('/menu-management')
def menu_management():
    """Menu management page"""
    return render_template('menu_management.html', menu_items=menu_items)

@app.route('/system-status')
def system_status():
    """System status and diagnostics page"""
    return render_template('system_status.html')

def get_table_status():
    """Get status of all tables"""
    tables = {}
    # Initialize all tables (assuming 12 regular tables + 2 VIP)
    table_numbers = [str(i) for i in range(1, 13)] + ['VIP1', 'VIP2']
    
    for table_num in table_numbers:
        tables[table_num] = {
            'number': table_num,
            'status': 'empty',  # empty, occupied, needs_attention
            'customer_name': None,
            'orders': [],
            'alerts': [],
            'total_amount': 0,
            'last_activity': None
        }
    
    # Update with current orders
    orders = load_data('orders')
    if not orders:
        orders = []
        
    for order in orders:
        table_num = order['table_number']
        if table_num in tables:
            tables[table_num]['status'] = 'occupied'
            tables[table_num]['customer_name'] = order['customer_name']
            tables[table_num]['orders'].append(order)
            tables[table_num]['total_amount'] += order['total']
            tables[table_num]['last_activity'] = order['timestamp']
    
    # Update with current alerts
    for alert in staff_alerts:
        table_num = alert['table_number']
        if table_num in tables:
            tables[table_num]['status'] = 'needs_attention'
            tables[table_num]['alerts'].append(alert)
            if not tables[table_num]['customer_name']:
                tables[table_num]['customer_name'] = alert['customer_name']
    
    return list(tables.values())

# API endpoints
@app.route('/api/call-staff', methods=['POST'])
def call_staff():
    """Handle customer call for staff with improved error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        table_number = data.get('table_number', '').strip()
        customer_name = data.get('customer_name', '').strip()
        
        if not table_number or not customer_name:
            return jsonify({'status': 'error', 'message': 'Table number and customer name are required'}), 400
        
        # Validate table number format
        if not (table_number.isdigit() or table_number.startswith('VIP')):
            return jsonify({'status': 'error', 'message': 'Invalid table number format'}), 400
        
        alert = {
            'id': str(uuid.uuid4()),
            'table_number': table_number,
            'customer_name': customer_name,
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'type': 'call_staff'
        }
        
        # Add to in-memory alerts
        staff_alerts.append(alert)
        
        # Emit to staff room with error handling
        try:
            socketio.emit('new_alert', alert, to='staff')
            print(f"✅ Alert emitted to staff: Table {table_number} - {customer_name}")
        except Exception as socket_error:
            print(f"Warning: Failed to emit alert via socket: {socket_error}")
            # Don't fail the request if socket fails
        
        return jsonify({'status': 'success', 'message': 'Staff has been notified!'})
        
    except Exception as e:
        print(f"Error in call_staff: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/place-order', methods=['POST'])
def place_order():
    """Handle customer order placement with improved validation and error handling"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        customer_name = data.get('customer_name', '').strip()
        table_number = data.get('table_number', '').strip()
        items = data.get('items', [])
        total = data.get('total')
        
        # Comprehensive validation
        if not customer_name:
            return jsonify({'status': 'error', 'message': 'Customer name is required'}), 400
        
        if not table_number:
            return jsonify({'status': 'error', 'message': 'Table number is required'}), 400
        
        if not items or not isinstance(items, list):
            return jsonify({'status': 'error', 'message': 'Order items are required'}), 400
        
        if not total or not isinstance(total, (int, float)) or total <= 0:
            return jsonify({'status': 'error', 'message': 'Valid total amount is required'}), 400
        
        # Validate items structure
        for item in items:
            if not isinstance(item, dict) or not all(key in item for key in ['id', 'name', 'price', 'quantity']):
                return jsonify({'status': 'error', 'message': 'Invalid item structure'}), 400
            
            if item['quantity'] <= 0 or item['price'] <= 0:
                return jsonify({'status': 'error', 'message': 'Invalid item quantity or price'}), 400
        
        # Verify calculated total
        calculated_total = sum(item['price'] * item['quantity'] for item in items)
        if abs(calculated_total - total) > 0.01:  # Allow for small floating point differences
            return jsonify({'status': 'error', 'message': 'Order total mismatch'}), 400
        
        order = {
            'id': str(uuid.uuid4()),
            'customer_name': customer_name,
            'table_number': table_number,
            'items': items,
            'total': float(total),
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'status': 'pending'
        }
        
        # Save to persistent storage
        try:
            add_document('orders', order)
        except Exception as save_error:
            print(f"Error saving order: {save_error}")
            return jsonify({'status': 'error', 'message': 'Failed to save order'}), 500
        
        # Update daily totals
        try:
            update_daily_totals(total, 'digital')
        except Exception as totals_error:
            print(f"Warning: Failed to update daily totals: {totals_error}")
            # Don't fail the request if totals update fails
        
        # Emit to staff room
        try:
            socketio.emit('new_order', order, to='staff')
            print(f"✅ Order emitted to staff: {order['id']} - Table {table_number}")
        except Exception as socket_error:
            print(f"Warning: Failed to emit order via socket: {socket_error}")
            # Don't fail the request if socket fails
        
        return jsonify({
            'status': 'success', 
            'message': 'Order placed successfully!', 
            'order_id': order['id']
        })
        
    except Exception as e:
        print(f"Error in place_order: {e}")
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/add-menu-item', methods=['POST'])
def add_menu_item():
    """Add new menu item (staff only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        name = data.get('name')
        price = data.get('price')
        
        if not name or not price:
            return jsonify({'status': 'error', 'message': 'Name and price are required'}), 400
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            return jsonify({'status': 'error', 'message': 'Invalid price format'}), 400
        
        menu_item = {
            'id': str(uuid.uuid4()),
            'name': name,
            'description': data.get('description', ''),
            'price': price,
            'image': data.get('image', ''),
            'category': data.get('category', 'Main Course')
        }
        menu_items.append(menu_item)
        
        # Emit to all customers
        socketio.emit('menu_updated', menu_item)
        
        return jsonify({'status': 'success', 'menu_item': menu_item})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/update-order-status', methods=['POST'])
def update_order_status():
    """Update order status (staff only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        order_id = data.get('order_id')
        new_status = data.get('status')
        
        if not order_id or not new_status:
            return jsonify({'status': 'error', 'message': 'Order ID and status are required'}), 400
        
        order_found = False
        orders = load_data('orders')
        if not orders:
            orders = []
            
        for order in orders:
            if order['id'] == order_id:
                order['status'] = new_status
                order_found = True
                # Update in database
                update_document('orders', order_id, {'status': new_status})
                break
        
        if not order_found:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        
        # Emit to customers and staff
        socketio.emit('order_status_updated', {
            'order_id': order_id, 
            'status': new_status
        })
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/dismiss-alert', methods=['POST'])
def dismiss_alert():
    """Dismiss staff alert"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        alert_id = data.get('alert_id')
        if not alert_id:
            return jsonify({'status': 'error', 'message': 'Alert ID is required'}), 400
        
        global staff_alerts
        staff_alerts = [alert for alert in staff_alerts if alert['id'] != alert_id]
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/menu')
def get_menu():
    """Get all menu items"""
    return jsonify(menu_items)

@app.route('/api/orders')
def get_orders():
    """Get orders with optional status filter"""
    orders = load_data('orders')
    if not orders:
        orders = []
        
    status_filter = request.args.get('status')
    if status_filter:
        filtered_orders = [order for order in orders if order['status'] == status_filter]
        return jsonify(filtered_orders)
    return jsonify(orders)

@app.route('/api/orders/stats')
def get_order_stats():
    """Get order statistics"""
    orders = load_data('orders')
    if not orders:
        orders = []
        
    stats = {
        'total': len(orders),
        'pending': len([o for o in orders if o['status'] == 'pending']),
        'preparing': len([o for o in orders if o['status'] == 'preparing']),
        'ready': len([o for o in orders if o['status'] == 'ready']),
        'completed': len([o for o in orders if o['status'] == 'completed'])
    }
    return jsonify(stats)

# Manual Order Management
@app.route('/api/manual-order', methods=['POST'])
def add_manual_order():
    """Add a manual order (staff only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        customer_name = data.get('customer_name', 'Walk-in Customer')
        table_number = data.get('table_number', 'Takeout')
        items_description = data.get('items_description', '')
        total = float(data.get('total', 0))
        notes = data.get('notes', '')
        
        if not items_description or total <= 0:
            return jsonify({'status': 'error', 'message': 'Items description and total amount are required'}), 400
        
        # Create manual order
        manual_order = {
            'id': str(uuid.uuid4()),
            'customer_name': customer_name,
            'table_number': table_number,
            'items_description': items_description,
            'total': total,
            'notes': notes,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'type': 'manual'
        }
        
        # Save to persistent storage
        add_document('manual_orders', manual_order)
        
        # Update daily totals
        update_daily_totals(total, 'manual')
        
        return jsonify({'status': 'success', 'message': 'Manual order added successfully!', 'order_id': manual_order['id']})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/manual-orders')
def get_manual_orders():
    """Get all manual orders with optional date filter"""
    date_filter = request.args.get('date')
    manual_orders = load_data('manual_orders')
    if not manual_orders:
        manual_orders = []
    
    if date_filter:
        filtered_orders = [order for order in manual_orders if order.get('date') == date_filter]
        return jsonify(filtered_orders)
    return jsonify(manual_orders)

@app.route('/api/daily-totals')
def get_daily_totals_api():
    """Get daily totals for a specific date"""
    totals = get_daily_totals()
    return jsonify(totals)

# PDF Report Generation
@app.route('/api/generate-report', methods=['POST'])
def generate_pdf_report():
    """Generate PDF report for specified date range"""
    
    # Check if PDF generation is available
    if not PDF_AVAILABLE:
        return jsonify({
            'error': 'PDF generation not available. reportlab package not installed.',
            'message': 'Please install reportlab package to generate PDF reports'
        }), 503
    
    try:
        data = request.get_json()
        start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        end_date = data.get('end_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Collect data for the period
        digital_orders = load_data('orders') or []
        manual_orders = load_data('manual_orders') or []
        
        # Filter orders by date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered_digital = []
        filtered_manual = []
        
        for order in digital_orders:
            order_date = datetime.strptime(order.get('timestamp', '').split()[0], '%H:%M:%S')
            # For digital orders, we need to use today's date since they only have time
            order_date = datetime.now().replace(hour=order_date.hour, minute=order_date.minute, second=order_date.second)
            if start_dt.date() <= order_date.date() <= end_dt.date():
                filtered_digital.append(order)
        
        for order in manual_orders:
            if 'date' in order:
                order_date = datetime.strptime(order['date'], '%Y-%m-%d')
                if start_dt.date() <= order_date.date() <= end_dt.date():
                    filtered_manual.append(order)
        
        # Generate PDF with all the imports inside the function
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#27AE60'),
            alignment=1  # Center
        )
        story.append(Paragraph("Green Heaven Restaurant", title_style))
        story.append(Paragraph("Business Report", styles['Heading2']))
        story.append(Paragraph(f"Period: {start_date} to {end_date}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary Statistics
        total_digital_revenue = sum(order.get('total', 0) for order in filtered_digital)
        total_manual_revenue = sum(order.get('total', 0) for order in filtered_manual)
        total_revenue = total_digital_revenue + total_manual_revenue
        
        summary_data = [
            ['Metric', 'Digital Orders', 'Manual Orders', 'Total'],
            ['Number of Orders', len(filtered_digital), len(filtered_manual), len(filtered_digital) + len(filtered_manual)],
            ['Revenue (LKR)', f"{total_digital_revenue:.2f}", f"{total_manual_revenue:.2f}", f"{total_revenue:.2f}"],
            ['Average Order Value', 
             f"{total_digital_revenue/len(filtered_digital):.2f}" if filtered_digital else "0.00",
             f"{total_manual_revenue/len(filtered_manual):.2f}" if filtered_manual else "0.00",
             f"{total_revenue/(len(filtered_digital) + len(filtered_manual)):.2f}" if (filtered_digital or filtered_manual) else "0.00"
            ]
        ]
        
        story.append(Paragraph("Summary", styles['Heading3']))
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Digital Orders Details
        if filtered_digital:
            story.append(Paragraph("Digital Orders", styles['Heading3']))
            digital_data = [['Order ID', 'Customer', 'Table', 'Items', 'Total (LKR)', 'Status', 'Time']]
            for order in filtered_digital:
                items_text = ', '.join([f"{item['name']} x{item['quantity']}" for item in order.get('items', [])])
                digital_data.append([
                    order.get('id', '')[:8] + '...',
                    order.get('customer_name', ''),
                    order.get('table_number', ''),
                    items_text[:30] + '...' if len(items_text) > 30 else items_text,
                    f"{order.get('total', 0):.2f}",
                    order.get('status', ''),
                    order.get('timestamp', '')
                ])
            
            digital_table = Table(digital_data)
            digital_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5DADE2')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(digital_table)
            story.append(Spacer(1, 20))
        
        # Manual Orders Details
        if filtered_manual:
            story.append(Paragraph("Manual Orders", styles['Heading3']))
            manual_data = [['Order ID', 'Customer', 'Table', 'Description', 'Total (LKR)', 'Date', 'Notes']]
            for order in filtered_manual:
                manual_data.append([
                    order.get('id', '')[:8] + '...',
                    order.get('customer_name', ''),
                    order.get('table_number', ''),
                    order.get('items_description', '')[:30] + '...' if len(order.get('items_description', '')) > 30 else order.get('items_description', ''),
                    f"{order.get('total', 0):.2f}",
                    order.get('date', ''),
                    order.get('notes', '')[:20] + '...' if len(order.get('notes', '')) > 20 else order.get('notes', '')
                ])
            
            manual_table = Table(manual_data)
            manual_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F4D03F')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(manual_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        # Generate filename
        filename = f"Green_Heaven_Report_{start_date}_to_{end_date}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts')
def get_alerts():
    """Get all active alerts"""
    return jsonify(staff_alerts)

@app.route('/api/tables')
def get_tables_api():
    """API endpoint to get table status data"""
    tables = get_table_status()
    return jsonify(tables)

@app.route('/api/system-status')
def get_system_status():
    """Get system status and diagnostics"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'firebase_available': FIREBASE_AVAILABLE,
            'firebase_connected': db is not None,
            'pdf_generation': PDF_AVAILABLE,
            'environment': 'production' if os.getenv('PORT') else 'development',
            'data_storage': 'firebase' if db else 'local'
        }
        
        # Test Firebase connection if available
        if db:
            try:
                # Try a simple read operation
                test_doc = db.collection('test').limit(1).stream()
                list(test_doc)  # Execute the query
                status['firebase_read_test'] = 'success'
            except Exception as e:
                status['firebase_read_test'] = f'failed: {str(e)}'
                status['firebase_error'] = str(e)
        
        # Get environment variables status (without exposing values)
        env_vars = {
            'FIREBASE_PROJECT_ID': bool(os.getenv('FIREBASE_PROJECT_ID')),
            'FIREBASE_PRIVATE_KEY': bool(os.getenv('FIREBASE_PRIVATE_KEY')),
            'FIREBASE_CLIENT_EMAIL': bool(os.getenv('FIREBASE_CLIENT_EMAIL')),
            'SECRET_KEY': bool(os.getenv('SECRET_KEY')),
            'PORT': os.getenv('PORT', 'not_set')
        }
        status['environment_variables'] = env_vars
        
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/tables/<table_number>/clear-alerts', methods=['POST'])
def clear_table_alerts(table_number):
    """Clear alerts for a specific table"""
    global staff_alerts
    # Remove alerts for the specific table
    staff_alerts = [alert for alert in staff_alerts if not (alert.get('table') == table_number)]
    return jsonify({'success': True})

@app.route('/api/tables/clear-all-alerts', methods=['POST'])
def clear_all_table_alerts():
    """Clear all table alerts"""
    global staff_alerts
    staff_alerts = []
    return jsonify({'success': True})

@app.route('/api/menu/stats')
def get_menu_stats():
    """Get menu statistics"""
    total = len(menu_items)
    available = len([item for item in menu_items if item.get('available', True)])
    stats = {
        'total': total,
        'available': available,
        'unavailable': total - available
    }
    return jsonify(stats)

@app.route('/api/menu-item/<item_id>/availability', methods=['PATCH'])
def update_item_availability(item_id):
    """Update menu item availability"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        available = data.get('available')
        if available is None:
            return jsonify({'status': 'error', 'message': 'Available status is required'}), 400
        
        # Find and update the item
        for item in menu_items:
            if item['id'] == item_id:
                item['available'] = available
                socketio.emit('menu_updated', item)
                return jsonify({'status': 'success'})
        
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/menu-item/<item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    """Delete a menu item"""
    try:
        global menu_items
        original_length = len(menu_items)
        menu_items = [item for item in menu_items if item['id'] != item_id]
        
        if len(menu_items) < original_length:
            socketio.emit('menu_item_deleted', {'item_id': item_id})
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/tables')
def get_tables():
    """Get table status information"""
    tables = get_table_status()
    return jsonify(tables)

# Socket events
@socketio.on('join_staff_room')
def on_join_staff():
    join_room('staff')
    emit('joined_staff_room')

@socketio.on('join_customer_room')
def on_join_customer(data):
    table_number = data.get('table_number')
    join_room(f'table_{table_number}')
    emit('joined_customer_room')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)