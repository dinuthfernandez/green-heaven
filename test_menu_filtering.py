#!/usr/bin/env python3
"""
Test menu filtering functionality
"""

import requests
import json

def test_menu_api():
    """Test the menu API and check categories"""
    try:
        response = requests.get('http://localhost:5001/api/menu')
        if response.status_code == 200:
            menu_items = response.json()
            print(f"✅ Menu API working - {len(menu_items)} items loaded")
            
            # Get unique categories
            categories = set()
            for item in menu_items:
                categories.add(item.get('category', 'Unknown'))
            
            print(f"📋 Categories found in database:")
            for cat in sorted(categories):
                count = len([item for item in menu_items if item.get('category') == cat])
                print(f"  - {cat}: {count} items")
            
            print(f"\n🔍 Category buttons should have these data-category values:")
            for cat in sorted(categories):
                print(f'  <button data-category="{cat}">{cat}</button>')
                
            return True
        else:
            print(f"❌ Menu API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing menu API: {e}")
        return False

def test_customer_page():
    """Test if the customer page loads"""
    try:
        response = requests.get('http://localhost:5001/customer?name=Test&table=1')
        if response.status_code == 200:
            print("✅ Customer page loads successfully")
            
            # Check if category buttons are in the HTML
            html = response.text
            categories_to_check = ['Starters', 'Soup', 'Sandwiches', 'Salads', 'Main Dishes', 'Rice', 'Noodles', 'Pasta', 'Grill Recipes', 'Side Dishes']
            
            for category in categories_to_check:
                if f'data-category="{category}"' in html:
                    print(f"  ✅ Found button for: {category}")
                else:
                    print(f"  ❌ Missing button for: {category}")
                    
            return True
        else:
            print(f"❌ Customer page failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing customer page: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Green Heaven Menu Filtering")
    print("=" * 50)
    
    if test_menu_api():
        print("\n" + "=" * 50)
        test_customer_page()
    
    print("\n🏁 Test complete!")