#!/usr/bin/env python3
"""
Comprehensive menu fix script to:
1. Update all menu items with proper m.png image paths
2. Ensure categories are properly set
3. Verify changes persist in database
4. Test that the API returns correct data
"""

import os
import sys
import requests
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append('/Users/dinuthfernando/Documents/projects/green heaven')

try:
    from app import supabase, get_menu_items_from_supabase
    print("✅ Successfully imported Supabase client")
except Exception as e:
    print(f"❌ Error importing: {e}")
    sys.exit(1)

def update_menu_images():
    """Update all menu items with m.png image and fix categories"""
    print("🔄 Starting comprehensive menu update...")
    
    try:
        # Get current menu items
        print("📊 Fetching current menu items...")
        result = supabase.table('menu_items').select('*').execute()
        
        if not result.data:
            print("❌ No menu items found in database")
            return False
            
        items = result.data
        print(f"📋 Found {len(items)} menu items to update")
        
        # Define category mappings for proper organization
        category_mappings = {
            'Appetizer': 'Appetizers',
            'appetizer': 'Appetizers', 
            'appetizers': 'Appetizers',
            'Main Course': 'Main Course',
            'main': 'Main Course',
            'main course': 'Main Course',
            'main_course': 'Main Course',
            'Dessert': 'Desserts',
            'dessert': 'Desserts',
            'desserts': 'Desserts',
            'Beverage': 'Beverages',
            'beverage': 'Beverages',
            'beverages': 'Beverages',
            'drink': 'Beverages',
            'drinks': 'Beverages'
        }
        
        updated_count = 0
        failed_count = 0
        
        for item in items:
            try:
                item_id = item['id']
                current_image = item.get('image_url', '')
                current_category = item.get('category', '')
                
                # Normalize category
                normalized_category = category_mappings.get(current_category, current_category)
                if not normalized_category or normalized_category not in ['Appetizers', 'Main Course', 'Desserts', 'Beverages']:
                    normalized_category = 'Main Course'  # Default category
                
                # Set image URL
                new_image_url = '/static/images/m.png'
                
                # Update the item
                update_data = {
                    'image_url': new_image_url,
                    'category': normalized_category
                }
                
                result = supabase.table('menu_items').update(update_data).eq('id', item_id).execute()
                
                if result.data:
                    updated_count += 1
                    print(f"✅ Updated {item['name']}: {normalized_category} - {new_image_url}")
                else:
                    failed_count += 1
                    print(f"❌ Failed to update {item['name']}")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Error updating {item.get('name', 'unknown')}: {e}")
                
        print(f"\n📊 Update Summary:")
        print(f"   ✅ Successfully updated: {updated_count}")
        print(f"   ❌ Failed updates: {failed_count}")
        
        return updated_count > 0
        
    except Exception as e:
        print(f"❌ Error in update_menu_images: {e}")
        return False

def verify_updates():
    """Verify that the updates were successful"""
    print("\n🔍 Verifying updates...")
    
    try:
        # Wait a moment for database to propagate changes
        time.sleep(2)
        
        # Get updated items directly from database
        result = supabase.table('menu_items').select('*').execute()
        
        if not result.data:
            print("❌ No items found during verification")
            return False
            
        items = result.data
        correct_images = 0
        category_counts = {}
        
        print(f"📋 Verifying {len(items)} items...")
        
        for item in items:
            image_url = item.get('image_url', '')
            category = item.get('category', '')
            
            if 'm.png' in image_url:
                correct_images += 1
                
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print(f"\n📸 Images with m.png: {correct_images}/{len(items)}")
        print(f"📊 Category distribution: {category_counts}")
        
        # Test the API endpoint
        print("\n🌐 Testing API endpoint...")
        try:
            response = requests.get('http://localhost:5001/api/menu', timeout=10)
            if response.status_code == 200:
                api_items = response.json()
                print(f"✅ API returning {len(api_items)} items")
                
                api_correct_images = 0
                for item in api_items:
                    if 'm.png' in item.get('image', ''):
                        api_correct_images += 1
                        
                print(f"📸 API items with m.png: {api_correct_images}/{len(api_items)}")
                
                # Show sample items
                print("\n📋 Sample API items:")
                for item in api_items[:3]:
                    print(f"   {item['name']}: {item.get('category', 'No category')} - {item.get('image', 'No image')}")
                    
            else:
                print(f"❌ API test failed: Status {response.status_code}")
                
        except Exception as e:
            print(f"❌ API test error: {e}")
            
        return correct_images == len(items)
        
    except Exception as e:
        print(f"❌ Error in verify_updates: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Green Heaven Menu Comprehensive Fix")
    print("=" * 50)
    
    # Check if server is running
    print("🔌 Checking if server is running...")
    try:
        response = requests.get('http://localhost:5001/api/menu', timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
    except:
        print("⚠️ Server may not be running - continuing with database updates")
    
    # Update menu images
    if update_menu_images():
        print("\n✅ Menu update completed successfully")
        
        # Verify updates
        if verify_updates():
            print("\n🎉 All menu items successfully updated with m.png!")
            print("💡 Changes should now be visible in the application")
        else:
            print("\n⚠️ Some verification checks failed - please check manually")
    else:
        print("\n❌ Menu update failed")
        
    print("\n" + "=" * 50)
    print("🏁 Fix complete!")

if __name__ == "__main__":
    main()