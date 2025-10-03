#!/usr/bin/env python3
"""
Debug script to identify the specific issue with Supabase updates
"""

import os
import sys
import time

# Add the current directory to Python path
sys.path.append('/Users/dinuthfernando/Documents/projects/green heaven')

try:
    from app import supabase
    print("✅ Successfully imported Supabase client")
except Exception as e:
    print(f"❌ Error importing: {e}")
    sys.exit(1)

def debug_single_update():
    """Try to update a single item to see the exact error"""
    print("🔍 Debugging single item update...")
    
    try:
        # Get first menu item
        result = supabase.table('menu_items').select('*').limit(1).execute()
        
        if not result.data:
            print("❌ No menu items found")
            return
            
        item = result.data[0]
        print(f"📋 Testing update for item: {item['name']} (ID: {item['id']})")
        print(f"    Current image: {item.get('image_url', 'None')}")
        print(f"    Current category: {item.get('category', 'None')}")
        
        # Try to update
        update_data = {
            'image_url': '/static/images/m.png',
            'category': 'Appetizers'
        }
        
        print(f"🔄 Attempting update with data: {update_data}")
        
        result = supabase.table('menu_items').update(update_data).eq('id', item['id']).execute()
        
        print(f"📊 Update result: {result}")
        
        if hasattr(result, 'data') and result.data:
            print("✅ Update successful!")
            print(f"📋 Updated item: {result.data[0]}")
        else:
            print("❌ Update failed - no data returned")
            
        # Check for errors
        if hasattr(result, 'error') and result.error:
            print(f"❌ Error details: {result.error}")
            
    except Exception as e:
        print(f"❌ Exception during update: {e}")
        import traceback
        traceback.print_exc()

def check_permissions():
    """Check what operations we can perform"""
    print("\n🔐 Checking permissions...")
    
    try:
        # Test SELECT
        result = supabase.table('menu_items').select('id, name').limit(1).execute()
        if result.data:
            print("✅ SELECT permission: OK")
        else:
            print("❌ SELECT permission: Failed")
            
        # Test INSERT (create a test item)
        test_item = {
            'name': 'Test Item',
            'price': 1.00,
            'category': 'Test',
            'image_url': '/static/images/m.png',
            'description': 'Test description'
        }
        
        result = supabase.table('menu_items').insert(test_item).execute()
        if result.data:
            print("✅ INSERT permission: OK")
            # Clean up test item
            test_id = result.data[0]['id']
            supabase.table('menu_items').delete().eq('id', test_id).execute()
            print("🧹 Cleaned up test item")
        else:
            print("❌ INSERT permission: Failed")
            
    except Exception as e:
        print(f"❌ Permission check error: {e}")

def main():
    print("🐛 Supabase Update Debug Tool")
    print("=" * 40)
    
    debug_single_update()
    check_permissions()
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    main()