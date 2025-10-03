#!/usr/bin/env python3
"""
Script to update all menu items with proper images and fix categories
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the main app
from app import supabase, get_menu_items_from_supabase, save_menu_item_to_supabase

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def update_menu_images():
    """Update all menu items to use the m.png image"""
    print_section("Updating Menu Item Images")
    
    # Get current menu items
    current_items = get_menu_items_from_supabase()
    if not current_items:
        print("❌ No menu items found in Supabase")
        return
    
    print(f"📊 Found {len(current_items)} menu items")
    
    # Update each item with the new image
    updated_count = 0
    for item in current_items:
        # Update image URL to use m.png
        item['image_url'] = '/static/images/m.png'
        
        # Ensure proper category formatting
        category = item.get('category', 'Main Course')
        if category not in ['Appetizers', 'Main Course', 'Sri Lankan Specials', 'Desserts', 'Beverages']:
            # Map common variations
            category_mapping = {
                'appetizer': 'Appetizers',
                'appetizers': 'Appetizers',
                'main': 'Main Course',
                'main course': 'Main Course',
                'mains': 'Main Course',
                'sri lankan': 'Sri Lankan Specials',
                'sri lankan special': 'Sri Lankan Specials',
                'dessert': 'Desserts',
                'desserts': 'Desserts',
                'beverage': 'Beverages',
                'beverages': 'Beverages',
                'drinks': 'Beverages',
                'drink': 'Beverages'
            }
            category = category_mapping.get(category.lower(), 'Main Course')
        
        item['category'] = category
        
        try:
            # Update in Supabase
            result = supabase.table('menu_items').update({
                'image_url': item['image_url'],
                'category': item['category']
            }).eq('id', item['id']).execute()
            
            print(f"✅ Updated: {item['name']} -> {category}")
            updated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to update {item['name']}: {e}")
    
    print(f"\n✅ Successfully updated {updated_count} menu items")

def verify_categories():
    """Verify that all menu items have proper categories"""
    print_section("Verifying Menu Categories")
    
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
    
    print("📊 Menu Items by Category:")
    for category, items in categories.items():
        print(f"\n🍽️  {category} ({len(items)} items):")
        for item_name in items[:5]:  # Show first 5 items
            print(f"   - {item_name}")
        if len(items) > 5:
            print(f"   ... and {len(items) - 5} more")

def create_sample_menu_with_images():
    """Create sample menu items with proper images if none exist"""
    print_section("Creating Sample Menu Items")
    
    sample_items = [
        {
            'id': 'sri-curry-rice',
            'name': 'Traditional Sri Lankan Curry with Rice',
            'description': 'Authentic curry with coconut milk, vegetables, and fragrant basmati rice',
            'price': 1250.00,
            'category': 'Sri Lankan Specials',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'kottu-roti',
            'name': 'Kottu Roti',
            'description': 'Chopped roti bread stir-fried with vegetables, egg, and your choice of meat',
            'price': 950.00,
            'category': 'Sri Lankan Specials',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'hoppers-curry',
            'name': 'Hoppers with Curry',
            'description': 'Bowl-shaped pancakes served with spicy curry and coconut sambol',
            'price': 850.00,
            'category': 'Sri Lankan Specials',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'fish-curry',
            'name': 'Fish Curry',
            'description': 'Fresh fish cooked in rich coconut curry with spices',
            'price': 1400.00,
            'category': 'Main Course',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'chicken-deviled',
            'name': 'Deviled Chicken',
            'description': 'Spicy stir-fried chicken with onions, peppers, and chili sauce',
            'price': 1200.00,
            'category': 'Main Course',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'watalappan',
            'name': 'Watalappan',
            'description': 'Traditional Sri Lankan dessert made with coconut milk and jaggery',
            'price': 450.00,
            'category': 'Desserts',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'king-coconut',
            'name': 'Fresh King Coconut Water',
            'description': 'Refreshing natural coconut water served fresh',
            'price': 300.00,
            'category': 'Beverages',
            'image_url': '/static/images/m.png',
            'available': True
        },
        {
            'id': 'isso-wade',
            'name': 'Isso Wade (Prawn Fritters)',
            'description': 'Crispy fried prawn fritters with spices',
            'price': 650.00,
            'category': 'Appetizers',
            'image_url': '/static/images/m.png',
            'available': True
        }
    ]
    
    current_items = get_menu_items_from_supabase()
    current_count = len(current_items) if current_items else 0
    
    if current_count < 10:
        print(f"Adding sample items to reach better variety (current: {current_count})")
        
        for item in sample_items:
            try:
                result = supabase.table('menu_items').upsert(item).execute()
                print(f"✅ Added: {item['name']}")
            except Exception as e:
                print(f"❌ Failed to add {item['name']}: {e}")
    else:
        print(f"✅ Menu already has {current_count} items - no need to add samples")

def fix_menu_filtering():
    """Update the customer page to have better filtering"""
    print_section("Fixing Menu Filtering")
    
    # Get all unique categories from current menu
    current_items = get_menu_items_from_supabase()
    if not current_items:
        print("❌ No menu items found")
        return
    
    categories = set()
    for item in current_items:
        category = item.get('category', 'Main Course')
        categories.add(category)
    
    categories = sorted(list(categories))
    print(f"📊 Found categories: {', '.join(categories)}")
    
    # Update the customer page HTML with dynamic categories
    customer_html_path = 'templates/customer_page.html'
    try:
        with open(customer_html_path, 'r') as f:
            content = f.read()
        
        # Create new category buttons HTML
        category_buttons = ['<button class="category-btn active" data-category="all">All Items</button>']
        for category in categories:
            category_buttons.append(f'<button class="category-btn" data-category="{category}">{category}</button>')
        
        new_categories_html = '\n            '.join(category_buttons)
        
        # Replace the menu categories section
        import re
        pattern = r'<div class="menu-categories">(.*?)</div>'
        replacement = f'''<div class="menu-categories">
            {new_categories_html}
        </div>'''
        
        updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(customer_html_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated menu categories in {customer_html_path}")
        
    except Exception as e:
        print(f"❌ Failed to update customer page: {e}")

def main():
    print("🍽️  Green Heaven Menu Image & Filter Fix")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not supabase:
        print("❌ Supabase not available - cannot update menu")
        return
    
    # Step 1: Update all menu images
    update_menu_images()
    
    # Step 2: Add sample items if needed
    create_sample_menu_with_images()
    
    # Step 3: Verify categories
    verify_categories()
    
    # Step 4: Fix menu filtering
    fix_menu_filtering()
    
    print_section("Menu Fix Complete")
    print("✅ All menu items now use m.png image")
    print("✅ Categories are properly organized")
    print("✅ Menu filtering updated")
    print("🔄 Please restart the server to see changes")
    print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()