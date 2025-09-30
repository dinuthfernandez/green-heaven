#!/usr/bin/env python3
"""
Data Migration Script for Green Heaven
Migrates existing data from local JSON files to Supabase
"""

import json
import os
from datetime import datetime, date
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def init_supabase():
    """Initialize Supabase client"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Supabase credentials not found in environment variables")
        return None
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Connected to Supabase")
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None

def load_json_file(filename):
    """Load data from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  File {filename} not found")
        return None
    except json.JSONDecodeError:
        print(f"⚠️  Invalid JSON in {filename}")
        return None

def migrate_orders(supabase: Client):
    """Migrate orders from data/orders.json to Supabase"""
    print("\n📦 Migrating orders...")
    
    orders_data = load_json_file('data/orders.json')
    if not orders_data:
        print("No orders data to migrate")
        return
    
    migrated_count = 0
    
    for order in orders_data:
        try:
            # Convert to Supabase format
            supabase_order = {
                'customer_name': order.get('customerName', 'Unknown'),
                'table_number': str(order.get('tableNumber', '0')),
                'items': order.get('items', []),
                'total_amount': float(order.get('total', 0)),
                'status': 'delivered',  # Assume old orders are delivered
                'created_at': order.get('timestamp', datetime.now().isoformat())
            }
            
            result = supabase.table('manual_orders').insert(supabase_order).execute()
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to migrate order: {e}")
    
    print(f"✅ Migrated {migrated_count} orders")

def migrate_daily_totals(supabase: Client):
    """Migrate daily totals from data/daily_totals.json to Supabase"""
    print("\n📊 Migrating daily totals...")
    
    totals_data = load_json_file('data/daily_totals.json')
    if not totals_data:
        print("No daily totals data to migrate")
        return
    
    migrated_count = 0
    
    for date_str, data in totals_data.items():
        try:
            # Convert to Supabase format
            supabase_total = {
                'date': date_str,
                'digital_orders': data.get('digitalOrders', 0),
                'manual_orders': data.get('manualOrders', 0),
                'digital_revenue': float(data.get('digitalRevenue', 0)),
                'manual_revenue': float(data.get('manualRevenue', 0)),
                'total_orders': data.get('totalOrders', 0),
                'total_revenue': float(data.get('totalRevenue', 0))
            }
            
            # Use upsert to handle duplicates
            result = supabase.table('daily_totals').upsert(supabase_total).execute()
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to migrate daily total for {date_str}: {e}")
    
    print(f"✅ Migrated {migrated_count} daily totals")

def test_supabase_connection(supabase: Client):
    """Test Supabase connection and basic operations"""
    print("\n🧪 Testing Supabase connection...")
    
    try:
        # Test reading
        result = supabase.table('daily_totals').select('*').limit(1).execute()
        print("✅ Read test successful")
        
        # Test writing
        test_data = {
            'date': date.today().isoformat(),
            'digital_orders': 0,
            'manual_orders': 0,
            'digital_revenue': 0.0,
            'manual_revenue': 0.0,
            'total_orders': 0,
            'total_revenue': 0.0
        }
        
        result = supabase.table('daily_totals').upsert(test_data).execute()
        print("✅ Write test successful")
        
        print("🎉 Supabase is ready for production!")
        
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")

def main():
    """Main migration function"""
    print("🚀 Starting Green Heaven data migration to Supabase...")
    
    # Initialize Supabase
    supabase = init_supabase()
    if not supabase:
        print("❌ Migration aborted - could not connect to Supabase")
        return
    
    # Migrate data
    migrate_orders(supabase)
    migrate_daily_totals(supabase)
    
    # Test connection
    test_supabase_connection(supabase)
    
    print("\n✨ Migration completed!")
    print("🌿 Your Green Heaven system is now powered by Supabase!")

if __name__ == "__main__":
    main()