from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import os
import ssl
import threading
import shutil
from datetime import datetime, timedelta
import uuid
import io
import base64
from werkzeug.utils import secure_filename

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

# Supabase imports for real-time database
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
    print("🚀 Supabase client available - enabling real-time database!")
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None  # Define Client as None if not available
    create_client = None  # Define create_client as None if not available
    print("📦 Supabase not available - using local storage fallback")

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not available - using system environment variables")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'green-heaven-secret-key-2024')

# Initialize Flask-SocketIO with flexible async mode and protocol compatibility
# Try gevent first (for production), fallback to threading (for development)
try:
    import gevent
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode='gevent',
        logger=False,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    print("🌟 Using gevent async mode for optimal performance")
except ImportError:
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        async_mode='threading',
        logger=False,
        engineio_logger=False,
        ping_timeout=60,
        ping_interval=25
    )
    print("🔧 Using threading async mode for development")

# Initialize Supabase client for real-time database
supabase = None
if SUPABASE_AVAILABLE and create_client:
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        try:
            # Create Supabase client - try simple connection first
            try:
                supabase = create_client(supabase_url, supabase_key)
                print(f"✅ Supabase connected: {supabase_url}")
                print("🔄 Real-time database active - lightning fast performance!")
                
            except Exception as ssl_error:
                print(f"⚠️ Initial connection failed, trying compatibility mode: {ssl_error}")
                
                # For compatibility issues, try with basic retry
                try:
                    import time
                    time.sleep(1)  # Brief pause before retry
                    supabase = create_client(supabase_url, supabase_key)
                    print(f"✅ Supabase connected (retry successful): {supabase_url}")
                    print("🔄 Real-time database active with retry!")
                    
                except Exception as retry_error:
                    print(f"❌ Connection failed after retry: {retry_error}")
                    print("📁 Continuing with local storage only")
                    supabase = None
            
            # Test connection if supabase client was created successfully
            if supabase:
                try:
                    test_result = supabase.table('menu_items').select('id').limit(1).execute()
                    print(f"💾 Real-time database fully operational with {len(test_result.data)} test items")
                except Exception as test_error:
                    error_msg = str(test_error)
                    if "SSLSocket" in error_msg or "SSL" in error_msg:
                        print(f"🔐 SSL compatibility issue detected: {error_msg}")
                        print("📁 Database will fall back to local storage for operations")
                        # Don't set supabase to None here - let individual operations handle the fallback
                    else:
                        print(f"⚠️ Database test warning: {test_error}")
                        print("🔄 Connection might still work for individual operations")
                
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            print("📁 Falling back to local storage")
            supabase = None
    else:
        print("⚠️ Supabase credentials not found - using local storage")
        print("💡 Add SUPABASE_URL and SUPABASE_ANON_KEY to environment variables")

# Supabase Storage Functions for Images
def upload_image_to_supabase(file_data, filename, content_type='image/jpeg'):
    """Upload image to Supabase Storage"""
    if not supabase:
        return None
    
    try:
        # Upload to the menu-images bucket
        result = supabase.storage.from_('menu-images').upload(
            path=filename,
            file=file_data,
            file_options={'content-type': content_type}
        )
        
        if result:
            # Get public URL
            public_url = supabase.storage.from_('menu-images').get_public_url(filename)
            return public_url
        
    except Exception as e:
        print(f"❌ Error uploading image to Supabase: {e}")
        return None

def delete_image_from_supabase(filename):
    """Delete image from Supabase Storage"""
    if not supabase:
        return False
    
    try:
        result = supabase.storage.from_('menu-images').remove([filename])
        return True
    except Exception as e:
        print(f"❌ Error deleting image from Supabase: {e}")
        return False

def get_menu_items_from_supabase():
    """Load menu items from Supabase database"""
    if not supabase:
        return None
    
    try:
        result = supabase.table('menu_items').select('*').execute()
        return result.data
    except Exception as e:
        error_message = str(e)
        if "SSLSocket" in error_message or "SSL" in error_message:
            print(f"🔐 SSL issue loading menu items from Supabase: {error_message}")
        else:
            print(f"❌ Error loading menu items from Supabase: {e}")
        return None

def save_menu_item_to_supabase(menu_item):
    """Save or update menu item in Supabase"""
    if not supabase:
        return False
    
    try:
        result = supabase.table('menu_items').upsert(menu_item).execute()
        return True
    except Exception as e:
        print(f"❌ Error saving menu item to Supabase: {e}")
        return False

# Fallback to file-based storage if Supabase not available
if not supabase:
    print("📂 Using lightweight file-based storage")
    # Simple file-based storage - perfect for lightweight restaurant data
    import threading
    import time
    from pathlib import Path

    # Thread lock for safe file operations
    storage_lock = threading.Lock()

    # Data storage configuration
    DATA_DIR = 'data'
    ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
    MANUAL_ORDERS_FILE = os.path.join(DATA_DIR, 'manual_orders.json')
    DAILY_TOTALS_FILE = os.path.join(DATA_DIR, 'daily_totals.json')
    BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

    # Create data directories
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    print("📁 Local storage initialized with automatic backups")

# Simple file-based storage - perfect for lightweight restaurant data
import threading
import time
from pathlib import Path

# Thread lock for safe file operations
storage_lock = threading.Lock()

# Data storage configuration
DATA_DIR = 'data'
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
MANUAL_ORDERS_FILE = os.path.join(DATA_DIR, 'manual_orders.json')
DAILY_TOTALS_FILE = os.path.join(DATA_DIR, 'daily_totals.json')
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

# Create data directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

print("📂 Using lightweight file-based storage - perfect for restaurant data!")
print("� Data will be stored locally with automatic backups")

# Data storage configuration
DATA_DIR = 'data'
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
MANUAL_ORDERS_FILE = os.path.join(DATA_DIR, 'manual_orders.json')
DAILY_TOTALS_FILE = os.path.join(DATA_DIR, 'daily_totals.json')

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Data storage functions - Supabase (real-time) or File-based (fallback)
def load_data(collection_name):
    """Load data from Supabase or local storage"""
    if supabase:
        try:
            # Use Supabase for real-time data
            table_mapping = {
                'orders': 'orders',
                'manual_orders': 'manual_orders', 
                'daily_totals': 'daily_totals',
                'staff_calls': 'staff_calls'
            }
            
            table_name = table_mapping.get(collection_name)
            if not table_name:
                print(f"Warning: Unknown collection: {collection_name}")
                return []
            
            # Use appropriate timestamp column for ordering
            timestamp_col = 'updated_at' if collection_name == 'daily_totals' else 'created_at'
            response = supabase.table(table_name).select("*").order(timestamp_col, desc=True).execute()
            data = response.data if response.data else []
            
            # Transform data for local format compatibility if needed
            if collection_name == 'orders' and data:
                import json
                for item in data:
                    # Map 'total_amount' back to 'total' for local compatibility
                    if 'total_amount' in item:
                        item['total'] = item['total_amount']
                    
                    # Convert items JSON string back to list for local compatibility
                    if 'items' in item and isinstance(item['items'], str):
                        try:
                            item['items'] = json.loads(item['items'])
                        except (json.JSONDecodeError, TypeError):
                            item['items'] = []
                    
                    # Add timestamp from created_at for compatibility
                    if 'created_at' in item and 'timestamp' not in item:
                        from datetime import datetime
                        try:
                            dt = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))
                            item['timestamp'] = dt.strftime('%H:%M:%S')
                            item['date'] = dt.strftime('%Y-%m-%d')
                        except:
                            pass
            
            print(f"📊 Loaded {len(data)} items from Supabase {table_name}")
            return data
            
        except Exception as e:
            error_message = str(e)
            # Check for specific SSL-related errors
            if "SSLSocket" in error_message or "SSL" in error_message:
                print(f"🔐 SSL connection issue for {collection_name}: {error_message}")
                print("📁 Using local storage instead of Supabase")
            else:
                print(f"❌ Supabase error for {collection_name}: {e}")
                print("📁 Falling back to local storage")
            return load_data_local(collection_name)
    else:
        # Use local file storage
        return load_data_local(collection_name)

def load_data_local(collection_name):
    """Load data from local JSON file with thread safety"""
    try:
        with storage_lock:
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
        # Try to recover from backup
        backup_data = load_backup_data(collection_name)
        if backup_data:
            print(f"📦 Recovered {len(backup_data)} items from backup")
            return backup_data
        return []
    except Exception as e:
        print(f"Error loading {collection_name}: {e}")
        return []

def save_data(collection_name, data):
    """Save data to Supabase or local storage"""
    if supabase:
        try:
            # Use Supabase for real-time updates
            table_mapping = {
                'orders': 'orders',
                'manual_orders': 'manual_orders',
                'daily_totals': 'daily_totals', 
                'staff_calls': 'staff_calls'
            }
            
            table_name = table_mapping.get(collection_name)
            if not table_name:
                print(f"Warning: Unknown collection: {collection_name}")
                return
            
            # For daily_totals, use upsert to handle updates
            if collection_name == 'daily_totals' and data:
                for item in data:
                    if 'id' in item:
                        # Update existing record
                        supabase.table(table_name).update(item).eq('id', item['id']).execute()
                    else:
                        # Insert new record
                        supabase.table(table_name).insert(item).execute()
            else:
                # For other collections, insert new records
                if data:
                    supabase.table(table_name).insert(data if isinstance(data, list) else [data]).execute()
            
            print(f"✅ Saved {len(data) if isinstance(data, list) else 1} items to Supabase {table_name}")
            
            # Also save locally as backup
            save_data_local(collection_name, data)
            
        except Exception as e:
            print(f"❌ Supabase save error for {collection_name}: {e}")
            print("📁 Falling back to local storage")
            save_data_local(collection_name, data)
    else:
        # Use local file storage
        save_data_local(collection_name, data)

def save_data_local(collection_name, data):
    """Save data to local JSON file with thread safety and backup"""
    try:
        with storage_lock:
            # Create backup before saving
            create_backup(collection_name)
            
            file_mapping = {
                'orders': ORDERS_FILE,
                'manual_orders': MANUAL_ORDERS_FILE,
                'daily_totals': DAILY_TOTALS_FILE
            }
            
            filename = file_mapping.get(collection_name)
            if not filename:
                print(f"Warning: Unknown collection name: {collection_name}")
                return
            
            # Atomic write using temporary file
            temp_filename = filename + '.tmp'
            
            with open(temp_filename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False, default=str)
            
            # Atomic move (replaces original file)
            os.replace(temp_filename, filename)
            
    except Exception as e:
        print(f"Error saving to local {collection_name}: {e}")
        # Clean up temp file if it exists
        try:
            file_mapping = {
                'orders': ORDERS_FILE,
                'manual_orders': MANUAL_ORDERS_FILE,
                'daily_totals': DAILY_TOTALS_FILE
            }
            filename = file_mapping.get(collection_name)
            if filename:
                temp_filename = filename + '.tmp'
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)
        except:
            pass

def create_backup(collection_name):
    """Create backup of data file"""
    try:
        file_mapping = {
            'orders': ORDERS_FILE,
            'manual_orders': MANUAL_ORDERS_FILE,
            'daily_totals': DAILY_TOTALS_FILE
        }
        
        filename = file_mapping.get(collection_name)
        if not filename or not os.path.exists(filename):
            return
            
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = os.path.join(BACKUP_DIR, f"{collection_name}_{timestamp}.json")
        
        # Keep only last 10 backups per collection
        cleanup_old_backups(collection_name)
        
        # Create backup
        import shutil
        shutil.copy2(filename, backup_filename)
        
    except Exception as e:
        print(f"Warning: Failed to create backup for {collection_name}: {e}")

def cleanup_old_backups(collection_name, keep=10):
    """Keep only the most recent backups"""
    try:
        backup_pattern = f"{collection_name}_*.json"
        backup_files = list(Path(BACKUP_DIR).glob(backup_pattern))
        
        if len(backup_files) > keep:
            # Sort by modification time, keep newest
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for old_backup in backup_files[keep:]:
                old_backup.unlink()
                
    except Exception as e:
        print(f"Warning: Failed to cleanup old backups: {e}")

def load_backup_data(collection_name):
    """Load data from most recent backup"""
    try:
        backup_pattern = f"{collection_name}_*.json"
        backup_files = list(Path(BACKUP_DIR).glob(backup_pattern))
        
        if not backup_files:
            return []
            
        # Get most recent backup
        latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
        
        with open(latest_backup, 'r', encoding='utf-8') as file:
            print(f"📦 Restored data from backup: {latest_backup.name}")
            return json.load(file)
            
    except Exception as e:
        print(f"Error loading backup for {collection_name}: {e}")
        return []

def add_document(collection_name, document_data):
    """Add a single document to Supabase or local storage"""
    if supabase:
        try:
            # Use Supabase for real-time database
            table_mapping = {
                'orders': 'orders',
                'manual_orders': 'manual_orders',
                'daily_totals': 'daily_totals',
                'staff_calls': 'staff_calls'
            }
            
            table_name = table_mapping.get(collection_name)
            if not table_name:
                print(f"Warning: Unknown collection: {collection_name}")
                return
            
            # Create a copy to avoid modifying the original data
            supabase_data = document_data.copy()
            
            # Transform data for Supabase schema if needed
            if collection_name == 'orders':
                # Map 'total' to 'total_amount' for Supabase
                if 'total' in supabase_data:
                    supabase_data['total_amount'] = supabase_data['total']
                    del supabase_data['total']
                
                # Convert items list to JSON string for Supabase
                if 'items' in supabase_data and isinstance(supabase_data['items'], list):
                    import json
                    supabase_data['items'] = json.dumps(supabase_data['items'])
                
                # Remove fields that don't exist in Supabase schema
                fields_to_remove = ['date', 'timestamp']
                for field in fields_to_remove:
                    if field in supabase_data:
                        del supabase_data[field]
            
            # Ensure document has required fields
            if 'id' not in supabase_data:
                supabase_data['id'] = str(uuid.uuid4())
            
            if 'created_at' not in supabase_data:
                supabase_data['created_at'] = datetime.now().isoformat()
            
            # Insert into Supabase
            response = supabase.table(table_name).insert(supabase_data).execute()
            print(f"✅ Added document to Supabase {table_name}: {supabase_data.get('id', 'no-id')}")
            
            # Emit real-time update to all connected clients
            socketio.emit('database_updated', {
                'table': table_name,
                'action': 'insert',
                'data': document_data
            })
            
        except Exception as e:
            error_message = str(e)
            if "SSLSocket" in error_message or "SSL" in error_message:
                print(f"🔐 SSL issue adding to {collection_name}: {error_message}")
            else:
                print(f"❌ Supabase add error for {collection_name}: {e}")
            print("📁 Falling back to local storage")
            add_document_local(collection_name, document_data)
    else:
        add_document_local(collection_name, document_data)

def add_document_local(collection_name, document_data):
    """Add a single document to local storage"""
    try:
        # Local storage - append to existing data
        current_data = load_data_local(collection_name)
        current_data.append(document_data)
        save_data_local(collection_name, current_data)
        print(f"✅ Added document to local {collection_name}: {document_data.get('id', 'no-id')}")
    except Exception as e:
        print(f"Error adding document to local {collection_name}: {e}")

def update_document(collection_name, document_id, update_data):
    """Update a document in Supabase or local storage"""
    if supabase:
        try:
            # Use Supabase for real-time updates
            table_mapping = {
                'orders': 'orders',
                'manual_orders': 'manual_orders',
                'daily_totals': 'daily_totals',
                'staff_calls': 'staff_calls'
            }
            
            table_name = table_mapping.get(collection_name)
            if not table_name:
                print(f"Warning: Unknown collection: {collection_name}")
                return
                
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.now().isoformat()
            
            # Update in Supabase
            response = supabase.table(table_name).update(update_data).eq('id', document_id).execute()
            print(f"✅ Updated document in Supabase {table_name}: {document_id}")
            
            # Emit real-time update to all connected clients
            socketio.emit('database_updated', {
                'table': table_name,
                'action': 'update', 
                'id': document_id,
                'data': update_data
            })
            
        except Exception as e:
            print(f"❌ Supabase update error for {collection_name}: {e}")
            print("📁 Falling back to local storage")
            update_document_local(collection_name, document_id, update_data)
    else:
        update_document_local(collection_name, document_id, update_data)

def update_document_local(collection_name, document_id, update_data):
    """Update a document in local storage"""
    try:
        # Local storage - update in memory and save
        current_data = load_data_local(collection_name)
        updated = False
        
        for item in current_data:
            if item.get('id') == document_id:
                item.update(update_data)
                updated = True
                break
                
        if updated:
            save_data_local(collection_name, current_data)
            print(f"✅ Updated document in local {collection_name}: {document_id}")
        else:
            print(f"Warning: Document not found for update: {document_id}")
            
    except Exception as e:
        print(f"Error updating document in local {collection_name}: {e}")

def get_today_date():
    """Get today's date in YYYY-MM-DD format"""
    return datetime.now().strftime('%Y-%m-%d')

def get_daily_totals():
    """Get daily totals for today"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Local storage implementation only
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
    
    # Local storage implementation only
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

# Load persistent data
all_orders = load_data('orders')
manual_orders = load_data('manual_orders')

# Load menu items from Supabase or use fallback
def load_menu_items():
    """Load menu items with Supabase integration"""
    # Try to load from Supabase first
    supabase_menu = get_menu_items_from_supabase()
    
    if supabase_menu:
        print(f"📊 Loaded {len(supabase_menu)} menu items from Supabase")
        # Convert Supabase format to app format
        formatted_items = []
        for item in supabase_menu:
            formatted_item = {
                'id': item.get('id'),
                'name': item.get('name'),
                'description': item.get('description', ''),
                'price': float(item.get('price', 0)),
                'image': '/static/images/m.png',
                'category': item.get('category', 'Main Course'),
                'available': item.get('available', True)
            }
            formatted_items.append(formatted_item)
        return formatted_items
    
    # Fallback to default menu items
    print("📂 Using fallback menu items")
    return [
        {
            'id': 'sri-curry',
            'name': 'Traditional Sri Lankan Curry',
            'description': 'Authentic curry with coconut milk, served with rice and papadum',
            'price': 1250.00,
            'image': '/static/images/m.png',
            'category': 'Sri Lankan Specials',
            'available': True
        },
        {
            'id': 'kottu-roti',
            'name': 'Chicken Kottu Roti',
            'description': 'Chopped flatbread stir-fried with chicken, vegetables and spices',
            'price': 950.00,
            'image': '/static/images/m.png',
            'category': 'Sri Lankan Specials',
            'available': True
        },
        {
            'id': 'hoppers',
            'name': 'Egg Hoppers (2 pieces)',
            'description': 'Traditional bowl-shaped pancakes with egg, served with sambol',
            'price': 450.00,
            'image': '/static/images/m.png',
            'category': 'Appetizers',
            'available': True
        },
        {
            'id': 'fish-curry',
            'name': 'Fish Curry',
            'description': 'Fresh fish in aromatic spices with coconut gravy',
            'price': 1350.00,
            'image': '/static/images/m.png',
            'category': 'Sri Lankan Specials',
            'available': True
        },
        {
            'id': 'pol-sambol',
            'name': 'Pol Sambol',
            'description': 'Traditional coconut relish with chili and lime',
            'price': 250.00,
            'image': '/static/images/m.png',
            'category': 'Sides',
            'available': True
        },
        {
            'id': 'papadum',
            'name': 'Papadum (4 pieces)',
            'description': 'Crispy lentil wafers',
            'price': 200.00,
            'image': '/static/images/m.png',
            'category': 'Sides',
            'available': True
        },
        {
            'id': 'mango-lassi',
            'name': 'Mango Lassi',
            'description': 'Fresh mango yogurt drink',
            'price': 350.00,
            'image': '/static/images/m.png',
            'category': 'Beverages',
            'available': True
        },
        {
            'id': 'thai-curry',
            'name': 'Thai Green Curry',
            'description': 'Spicy green curry with vegetables or chicken',
            'price': 1150.00,
            'image': '/static/images/m.png',
            'category': 'International',
            'available': True
        },
        {
            'id': 'fried-rice',
            'name': 'Special Fried Rice',
            'description': 'Wok-fried rice with egg and vegetables',
            'price': 850.00,
            'image': '/static/images/m.png',
            'category': 'Rice & Noodles',
            'available': True
        },
        {
            'id': 'garlic-naan',
            'name': 'Garlic Naan',
            'description': 'Fresh baked bread with garlic and herbs',
            'price': 350.00,
            'image': '/static/images/m.png',
            'category': 'Breads',
            'available': True
        }
    ]

# Initialize menu items
menu_items = load_menu_items()

# Initialize empty data (orders now use persistent storage)
staff_alerts = []

@app.route('/debug')
def debug_page():
    """Debug page for testing menu functionality"""
    return send_from_directory('.', 'debug_menu.html')

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
    
    # Load fresh menu items from Supabase each time
    fresh_menu_items = load_menu_items()
    
    # Pass Supabase config for real-time subscriptions
    supabase_url = os.getenv('SUPABASE_URL', '') if supabase else ''
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY', '') if supabase else ''
    
    return render_template('customer_page.html', 
                         customer_name=customer_name, 
                         table_number=table_number,
                         menu_items=fresh_menu_items,
                         supabase_url=supabase_url,
                         supabase_anon_key=supabase_anon_key)

# Routes for restaurant staff
@app.route('/staff')
def staff_page():
    """Modern staff dashboard with organized navigation"""
    return render_template('staff_dashboard.html')

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
        
        # Save to Supabase if available
        if supabase:
            supabase_item = {
                'id': menu_item['id'],
                'name': menu_item['name'],
                'description': menu_item['description'],
                'price': menu_item['price'],
                'image_url': menu_item['image'],
                'category': menu_item['category'],
                'available': True
            }
            save_menu_item_to_supabase(supabase_item)
        
        # Emit to all customers
        socketio.emit('menu_updated', menu_item)
        
        return jsonify({'status': 'success', 'menu_item': menu_item})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/upload-menu-image', methods=['POST'])
def upload_menu_image():
    """Upload image for menu item"""
    try:
        if 'image' not in request.files:
            return jsonify({'status': 'error', 'message': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        filename = file.filename or 'unknown'
        file_ext = os.path.splitext(secure_filename(filename))[1].lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({'status': 'error', 'message': 'Invalid file type. Only JPG, PNG, GIF, and WebP are allowed'}), 400
        
        # Generate unique filename
        unique_filename = f"menu-{uuid.uuid4()}{file_ext}"
        
        # Read file data
        file_data = file.read()
        
        # Upload to Supabase Storage
        if supabase:
            content_type = file.content_type or 'image/jpeg'
            image_url = upload_image_to_supabase(
                file_data, 
                unique_filename, 
                content_type=content_type
            )
            
            if image_url:
                return jsonify({
                    'status': 'success', 
                    'image_url': image_url,
                    'filename': unique_filename
                })
            else:
                return jsonify({'status': 'error', 'message': 'Failed to upload image to storage'}), 500
        else:
            # Fallback: save to local static folder
            upload_folder = os.path.join('static', 'images', 'menu')
            os.makedirs(upload_folder, exist_ok=True)
            
            file_path = os.path.join(upload_folder, unique_filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            local_url = f"/static/images/menu/{unique_filename}"
            return jsonify({
                'status': 'success',
                'image_url': local_url,
                'filename': unique_filename
            })
            
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
    """Get all menu items with fresh data from Supabase"""
    fresh_menu_items = load_menu_items()
    return jsonify(fresh_menu_items)

@app.route('/api/menu-item/<item_id>')
def get_menu_item(item_id):
    """Get a single menu item by ID"""
    try:
        # Load fresh menu items
        fresh_menu_items = load_menu_items()
        
        # Find the specific item
        for item in fresh_menu_items:
            if item['id'] == item_id:
                return jsonify({'status': 'success', 'item': item})
        
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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

@app.route('/api/orders/clear-all', methods=['DELETE'])
def clear_all_orders():
    """Clear all orders from the system"""
    try:
        # Clear from Supabase if available
        if supabase:
            try:
                # Get all order IDs first
                result = supabase.table('orders').select('id').execute()
                if result.data:
                    for order in result.data:
                        supabase.table('orders').delete().eq('id', order['id']).execute()
                    print(f"✅ Cleared {len(result.data)} orders from Supabase")
            except Exception as e:
                print(f"⚠️ Error clearing Supabase orders: {e}")
        
        # Clear local storage
        save_data('orders', [])
        
        # Reset daily totals for today
        daily_totals = load_data('daily_totals')
        today = datetime.now().strftime('%Y-%m-%d')
        for totals in daily_totals:
            if totals.get('date') == today:
                totals.update({
                    'digital_orders': 0,
                    'manual_orders': 0,
                    'digital_revenue': 0.0,
                    'manual_revenue': 0.0,
                    'total_orders': 0,
                    'total_revenue': 0.0
                })
                break
        save_data('daily_totals', daily_totals)
        
        return jsonify({'status': 'success', 'message': 'All orders cleared successfully'})
        
    except Exception as e:
        print(f"Error clearing all orders: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
            'firebase_available': False,
            'firebase_connected': False,
            'pdf_generation': PDF_AVAILABLE,
            'environment': 'production' if os.getenv('PORT') else 'development',
            'data_storage': 'local'
        }
        
        # Local storage status
        status['storage_status'] = 'file-based JSON storage with backup'
        status['data_files'] = {
            'orders': os.path.exists('data/orders.json'),
            'manual_orders': os.path.exists('data/manual_orders.json'),
            'daily_totals': os.path.exists('data/daily_totals.json')
        }
        
        # Get environment variables status (without exposing values)
        env_vars = {
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

@app.route('/api/menu-item/<item_id>', methods=['PUT'])
def update_menu_item(item_id):
    """Update a menu item (name, price, image)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Find the item to update
        for item in menu_items:
            if item['id'] == item_id:
                # Update fields if provided
                if 'name' in data:
                    item['name'] = data['name'].strip()
                if 'price' in data:
                    try:
                        item['price'] = float(data['price'])
                    except (ValueError, TypeError):
                        return jsonify({'status': 'error', 'message': 'Invalid price format'}), 400
                if 'description' in data:
                    item['description'] = data['description'].strip()
                if 'category' in data:
                    item['category'] = data['category'].strip()
                if 'image_url' in data:
                    item['image_url'] = data['image_url'].strip()
                
                # Update in Supabase
                try:
                    if supabase:
                        supabase_item = item.copy()
                        result = supabase.table('menu_items').update(supabase_item).eq('id', item_id).execute()
                        print(f"✅ Updated menu item in Supabase: {item['name']}")
                except Exception as e:
                    print(f"⚠️ Failed to update in Supabase: {e}")
                    # Continue with local update even if Supabase fails
                
                # Emit update via socket
                socketio.emit('menu_item_updated', item)
                
                return jsonify({
                    'status': 'success', 
                    'message': 'Menu item updated successfully',
                    'item': item
                })
        
        # If not found, always return a response
        return jsonify({'status': 'error', 'message': 'Item not found'}), 404
            
    except Exception as e:
        print(f"Error updating menu item: {e}")
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

# Dashboard API Routes
@app.route('/api/tables/<table_id>/clean', methods=['POST'])
def clean_table(table_id):
    """Clean/reset a table"""
    try:
        orders = load_data('orders')
        # Remove orders for this table
        if orders:
            orders = [order for order in orders if order.get('table_number') != table_id]
            save_data('orders', orders)
        
        # Clear alerts for this table
        global staff_alerts
        staff_alerts = [alert for alert in staff_alerts if alert.get('table') != table_id]
        
        # Emit update
        socketio.emit('table_update', {'table_id': table_id, 'status': 'cleaned'}, to='staff')
        
        return jsonify({'status': 'success', 'message': f'Table {table_id} cleaned'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status_new(order_id):
    """Update order status for dashboard"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'status': 'error', 'message': 'Status is required'}), 400
        
        orders = load_data('orders')
        if not orders:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
        
        # Find and update the order
        order_updated = False
        for order in orders:
            if order.get('id') == order_id:
                order['status'] = new_status
                order['updated_at'] = datetime.now().isoformat()
                order_updated = True
                # Update in Supabase database
                try:
                    update_document('orders', order_id, {'status': new_status})
                except Exception as e:
                    print(f"Warning: Failed to update order in Supabase: {e}")
                break
        
        if order_updated:
            save_data('orders', orders)
            socketio.emit('order_update', {
                'order_id': order_id, 
                'status': new_status
            }, to='staff')
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Order not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    """Resolve a customer alert"""
    try:
        global staff_alerts
        # Find and remove the alert
        alert_found = False
        for i, alert in enumerate(staff_alerts):
            if alert.get('id') == alert_id:
                staff_alerts.pop(i)
                alert_found = True
                break
        
        if alert_found:
            socketio.emit('alert_resolved', {'alert_id': alert_id}, to='staff')
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Alert not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts/<alert_id>/respond', methods=['POST'])
def respond_to_alert(alert_id):
    """Send response to customer alert"""
    try:
        data = request.get_json()
        response_text = data.get('response')
        
        if not response_text:
            return jsonify({'status': 'error', 'message': 'Response text is required'}), 400
        
        # Find the alert
        alert = None
        for a in staff_alerts:
            if a.get('id') == alert_id:
                alert = a
                break
        
        if not alert:
            return jsonify({'status': 'error', 'message': 'Alert not found'}), 404
        
        # Send response to customer
        table_number = alert.get('table')
        socketio.emit('staff_response', {
            'message': response_text,
            'timestamp': datetime.now().isoformat()
        }, to=f'table_{table_number}')
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get analytics data for dashboard"""
    try:
        orders = load_data('orders') or []
        manual_orders = load_data('manual_orders') or []
        daily_totals = load_data('daily_totals') or {}
        
        # Calculate analytics
        today = datetime.now().strftime('%Y-%m-%d')
        today_orders = [order for order in orders if order.get('timestamp', '').startswith(today)]
        
        total_revenue = sum(order.get('total', 0) for order in today_orders)
        total_orders = len(today_orders)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Table utilization
        tables = get_table_status()
        occupied_tables = len([t for t in tables if t.get('status') == 'occupied'])
        total_tables = len(tables)
        table_utilization = (occupied_tables / total_tables * 100) if total_tables > 0 else 0
        
        analytics = {
            'daily_revenue': total_revenue,
            'daily_orders': total_orders,
            'avg_order_value': avg_order_value,
            'table_utilization': table_utilization,
            'peak_hours': '12:00 PM - 2:00 PM',  # Static for now
            'popular_items': get_popular_items(orders)
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_popular_items(orders):
    """Get most popular menu items"""
    item_counts = {}
    
    for order in orders:
        items = order.get('items', [])
        for item in items:
            name = item.get('name', 'Unknown')
            quantity = item.get('quantity', 1)
            item_counts[name] = item_counts.get(name, 0) + quantity
    
    # Sort by quantity and return top 5
    popular = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    return [{'name': name, 'quantity': qty} for name, qty in popular]

# Socket events with improved error handling and protocol compatibility
@socketio.on('join_staff_room')
def on_join_staff():
    try:
        join_room('staff')
        emit('joined_staff_room')
        print(f"✅ Staff joined room")
    except Exception as e:
        print(f"❌ Error joining staff room: {e}")
        emit('error', {'message': 'Failed to join staff room'})

@socketio.on('join_customer_room')
def on_join_customer(data):
    try:
        if not data or not isinstance(data, dict):
            emit('error', {'message': 'Invalid data format'})
            return
            
        table_number = data.get('table_number')
        if not table_number:
            emit('error', {'message': 'Table number is required'})
            return
            
        join_room(f'table_{table_number}')
        emit('joined_customer_room')
        print(f"✅ Customer joined table room: {table_number}")
    except Exception as e:
        print(f"❌ Error joining customer room: {e}")
        emit('error', {'message': 'Failed to join customer room'})

@socketio.on('connect')
def on_connect():
    try:
        print(f"✅ Socket.IO client connected")
    except Exception as e:
        print(f"❌ Error on connect: {e}")

@socketio.on('disconnect')
def on_disconnect(auth=None):
    try:
        print(f"🔌 Socket.IO client disconnected")
    except Exception as e:
        print(f"❌ Error on disconnect: {e}")

@socketio.on_error_default
def default_error_handler(e):
    print(f"❌ Socket.IO error: {e}")
    if hasattr(e, 'args') and len(e.args) > 0:
        print(f"Error details: {e.args[0]}")
    # Send generic error response to client
    emit('error', {'message': 'A socket error occurred'})

if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 5001))
        print(f"🚀 Starting Green Heaven Restaurant System on port {port}")
        print(f"🌐 Access at: http://localhost:{port}")
        socketio.run(app, debug=False, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Make sure the port is available and try again")