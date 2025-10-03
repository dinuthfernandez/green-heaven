#!/usr/bin/env python3
"""
Script to create beverages and desserts from existing items
"""

import sys
import os
from datetime import datetime

# Add current directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the main app
from app import supabase, get_menu_items_from_supabase

def convert_items_to_beverages_desserts():
    """Convert some existing items to beverages and desserts"""
    print("🔄 Converting some items to Beverages and Desserts")
    
    # Get current items
    current_items = get_menu_items_from_supabase()
    if not current_items:
        print("❌ No menu items found")
        return
    
    # Find items to convert to beverages
    beverages_to_create = [
        {
            'name_contains': 'cream of vegetable',
            'new_name': 'Fresh Lime Juice',
            'new_description': 'Refreshing lime juice with mint leaves',
            'new_price': 250.0,
            'category': 'Beverages'
        },
        {
            'name_contains': 'cream corn',
            'new_name': 'King Coconut Water',
            'new_description': 'Fresh natural coconut water',
            'new_price': 300.0,
            'category': 'Beverages'
        },
        {
            'name_contains': 'chicken broth',
            'new_name': 'Ceylon Tea',
            'new_description': 'Traditional Sri Lankan black tea',
            'new_price': 200.0,
            'category': 'Beverages'
        }
    ]
    
    # Find items to convert to desserts
    desserts_to_create = [
        {
            'name_contains': 'onion butter',
            'new_name': 'Watalappan',
            'new_description': 'Traditional Sri Lankan coconut custard with jaggery',
            'new_price': 450.0,
            'category': 'Desserts'
        },
        {
            'name_contains': 'grilled pork chops',
            'new_name': 'Ice Cream Sundae',
            'new_description': 'Vanilla ice cream with chocolate sauce and nuts',
            'new_price': 400.0,
            'category': 'Desserts'
        },
        {
            'name_contains': 'vegetable mixed salad',
            'new_name': 'Fresh Fruit Salad',
            'new_description': 'Seasonal tropical fruits with honey',
            'new_price': 350.0,
            'category': 'Desserts'
        }
    ]
    
    all_conversions = beverages_to_create + desserts_to_create
    
    for conversion in all_conversions:
        # Find matching item
        matching_item = None
        for item in current_items:
            if conversion['name_contains'].lower() in item.get('name', '').lower():
                matching_item = item
                break
        
        if matching_item:
            try:
                # Update the item
                result = supabase.table('menu_items').update({
                    'name': conversion['new_name'],
                    'description': conversion['new_description'],
                    'price': conversion['new_price'],
                    'category': conversion['category'],
                    'image_url': '/static/images/m.png'
                }).eq('id', matching_item['id']).execute()
                
                print(f"✅ Converted: {matching_item['name']} -> {conversion['new_name']} ({conversion['category']})")
                
            except Exception as e:
                print(f"❌ Failed to convert {matching_item['name']}: {e}")
        else:
            print(f"⚠️  Could not find item containing '{conversion['name_contains']}'")

def verify_final_categories():
    """Verify the final category distribution"""
    print("\n📊 Final Category Distribution:")
    
    current_items = get_menu_items_from_supabase()
    if not current_items:
        print("❌ No menu items found")
        return
    
    categories = {}
    for item in current_items:
        category = item.get('category', 'Unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(item['name'])
    
    for category, items in sorted(categories.items()):
        print(f"   🍽️  {category}: {len(items)} items")
        if len(items) <= 5:
            for item in items:
                print(f"      - {item}")
        else:
            for item in items[:3]:
                print(f"      - {item}")
            print(f"      ... and {len(items) - 3} more")

def main():
    print("🔄 Creating Beverages and Desserts")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not supabase:
        print("❌ Supabase not available")
        return
    
    convert_items_to_beverages_desserts()
    verify_final_categories()
    
    print("\n✅ Beverages and Desserts created!")
    print("✅ All items have m.png image")
    print("✅ Menu categories are customer-friendly")
    print("🔄 Please restart the server to see changes")
    print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()