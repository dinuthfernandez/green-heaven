#!/usr/bin/env python3
"""
Full System Test Script for Green Heaven Restaurant
Tests all major functionality and displays results
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001"
TEST_TABLE = "1"
TEST_CUSTOMER = "Test Customer"

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_customer_entry():
    """Test customer entry functionality"""
    print_section("Testing Customer Entry")
    
    url = f"{BASE_URL}/api/customer-entry"
    data = {
        "name": TEST_CUSTOMER,
        "table_number": TEST_TABLE
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("✅ Customer entry successful")
            return response.json()
        else:
            print(f"❌ Customer entry failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Customer entry error: {e}")
        return None

def test_place_order():
    """Test placing an order"""
    print_section("Testing Order Placement")
    
    # First get menu items
    try:
        menu_response = requests.get(f"{BASE_URL}/api/menu")
        if menu_response.status_code != 200:
            print("❌ Failed to get menu items")
            return None
        
        menu_items = menu_response.json()
        if not menu_items:
            print("❌ No menu items found")
            return None
        
        # Use first available item for test order
        test_item = menu_items[0]
        print(f"📝 Using test item: {test_item['name']} - LKR {test_item['price']}")
        
        # Place order
        url = f"{BASE_URL}/api/place-order"
        order_data = {
            "customer_name": TEST_CUSTOMER,
            "table_number": TEST_TABLE,
            "items": [
                {
                    "id": test_item["id"],
                    "name": test_item["name"],
                    "price": test_item["price"],
                    "quantity": 2
                }
            ]
        }
        
        response = requests.post(url, json=order_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Order placed successfully - Order ID: {result.get('order_id')}")
            return result
        else:
            print(f"❌ Order placement failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Order placement error: {e}")
        return None

def test_order_status_updates(order_id):
    """Test order status progression"""
    print_section("Testing Order Status Updates")
    
    statuses = ['preparing', 'ready', 'completed']
    
    for status in statuses:
        try:
            url = f"{BASE_URL}/api/orders/{order_id}"
            data = {"status": status}
            
            response = requests.put(url, json=data)
            if response.status_code == 200:
                print(f"✅ Order status updated to: {status}")
                time.sleep(1)  # Brief pause between updates
            else:
                print(f"❌ Failed to update status to {status}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Status update error for {status}: {e}")

def test_call_staff():
    """Test call staff functionality"""
    print_section("Testing Call Staff Feature")
    
    url = f"{BASE_URL}/api/call-staff"
    data = {
        "customer_name": TEST_CUSTOMER,
        "table_number": TEST_TABLE
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("✅ Staff call successful")
            return True
        else:
            print(f"❌ Staff call failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Staff call error: {e}")
        return False

def display_current_data():
    """Display current system data"""
    print_section("Current System Data")
    
    try:
        # Check orders
        with open('data/orders.json', 'r') as f:
            orders = json.load(f)
        print(f"📊 Orders in system: {len(orders)}")
        
        for order in orders[-3:]:  # Show last 3 orders
            print(f"   Order {order['order_id']}: {order['status']} - {order['customer_name']} (Table {order['table_number']})")
        
        # Check daily totals
        try:
            with open('data/daily_totals.json', 'r') as f:
                totals = json.load(f)
            
            today = datetime.now().strftime('%Y-%m-%d')
            if today in totals:
                today_data = totals[today]
                print(f"📈 Today's totals: {today_data['total_orders']} orders, LKR {today_data['total_revenue']:.2f}")
            else:
                print("📈 No sales data for today yet")
                
        except FileNotFoundError:
            print("📈 No daily totals file found")
        
    except FileNotFoundError:
        print("📊 No orders file found")

def run_full_test():
    """Run complete system test"""
    print("🧪 Starting Full System Test")
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test customer entry
    customer_result = test_customer_entry()
    
    # Test order placement
    order_result = test_place_order()
    if order_result and 'order_id' in order_result:
        order_id = order_result['order_id']
        
        # Test status updates
        test_order_status_updates(order_id)
    
    # Test call staff
    test_call_staff()
    
    # Display current data
    display_current_data()
    
    print_section("Test Summary")
    print("✅ All major functionality tested")
    print("🎯 Check the web interface to see real-time updates")
    print("📱 Customer page: http://localhost:5001/customer-entry")
    print("👥 Staff dashboard: http://localhost:5001/staff")
    print(f"🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_full_test()