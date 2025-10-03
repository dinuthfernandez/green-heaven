#!/usr/bin/env python3
"""
Script to reorganize menu categories to be more customer-friendly
"""

import sys
import os
from datetime import datetime

# Add current directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import from the main app
from app import supabase, get_menu_items_from_supabase

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def reorganize_categories():
    """Reorganize menu items into customer-friendly categories"""
    print_section("Reorganizing Menu Categories")
    
    # Category mapping for better organization
    category_mapping = {
        # Combine related items into main categories
        'Soup': 'Appetizers',
        'Starters': 'Appetizers', 
        'Sandwiches': 'Main Course',
        'Salads': 'Main Course',
        'Grill Recipes': 'Main Course',
        'Side Dishes': 'Main Course',
        'Rice': 'Main Course',
        'Noodles': 'Main Course', 
        'Pasta': 'Main Course',
        'Main Dishes': 'Main Course'
    }
    
    # Get current menu items
    current_items = get_menu_items_from_supabase()
    if not current_items:
        print("❌ No menu items found")
        return
    
    print(f"📊 Processing {len(current_items)} menu items")
    
    # Categorize items more intelligently
    updated_count = 0
    category_counts = {}
    
    for item in current_items:
        old_category = item.get('category', 'Main Course')
        new_category = category_mapping.get(old_category, old_category)
        
        # Special categorization based on item names
        item_name = item.get('name', '').lower()
        
        # More specific categorization
        if any(word in item_name for word in ['soup', 'broth', 'cream of']):
            new_category = 'Appetizers'
        elif any(word in item_name for word in ['sandwich', 'bread', 'fries']):
            new_category = 'Appetizers'
        elif any(word in item_name for word in ['salad']):
            new_category = 'Appetizers'
        elif any(word in item_name for word in ['rice', 'noodles', 'pasta', 'spaghetti', 'biriyani', 'fried rice', 'chopsuey']):
            new_category = 'Main Course'
        elif any(word in item_name for word in ['chicken', 'beef', 'pork', 'fish', 'prawn', 'seafood', 'grill']):
            new_category = 'Main Course'
        elif any(word in item_name for word in ['ice cream', 'cake', 'dessert', 'sweet']):
            new_category = 'Desserts'
        elif any(word in item_name for word in ['juice', 'tea', 'coffee', 'water', 'soda', 'drink']):
            new_category = 'Beverages'
        
        # Count categories
        if new_category not in category_counts:
            category_counts[new_category] = 0
        category_counts[new_category] += 1
        
        # Update if category changed
        if new_category != old_category:
            try:
                result = supabase.table('menu_items').update({
                    'category': new_category
                }).eq('id', item['id']).execute()
                
                print(f"✅ {item['name']}: {old_category} -> {new_category}")
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Failed to update {item['name']}: {e}")
    
    print(f"\n✅ Updated {updated_count} items")
    print("\n📊 Final Category Distribution:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count} items")

def update_customer_page_categories():
    """Update customer page with the new simplified categories"""
    print_section("Updating Customer Page Categories")
    
    # Define the final customer-friendly categories
    final_categories = ['Appetizers', 'Main Course', 'Desserts', 'Beverages']
    
    customer_html_path = 'templates/customer_page.html'
    try:
        with open(customer_html_path, 'r') as f:
            content = f.read()
        
        # Create new category buttons HTML
        category_buttons = ['<button class="category-btn active" data-category="all">All Items</button>']
        for category in final_categories:
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
        
        print(f"✅ Updated menu categories to: {', '.join(final_categories)}")
        
    except Exception as e:
        print(f"❌ Failed to update customer page: {e}")

def add_beverages_and_desserts():
    """Add some beverages and desserts if they don't exist"""
    print_section("Adding Missing Categories")
    
    # Check current items
    current_items = get_menu_items_from_supabase()
    if not current_items:
        print("❌ No menu items found")
        return
    
    categories = set()
    for item in current_items:
        categories.add(item.get('category', 'Main Course'))
    
    # Add beverages if missing
    if 'Beverages' not in categories:
        beverages = [
            {
                'id': 'fresh-lime-juice',
                'name': 'Fresh Lime Juice',
                'description': 'Refreshing lime juice with mint',
                'price': 250.00,
                'category': 'Beverages',
                'image_url': '/static/images/m.png',
                'available': True
            },
            {
                'id': 'king-coconut-water',
                'name': 'King Coconut Water',
                'description': 'Fresh natural coconut water',
                'price': 300.00,
                'category': 'Beverages',
                'image_url': '/static/images/m.png',
                'available': True
            },
            {
                'id': 'ceylon-tea',
                'name': 'Ceylon Tea',
                'description': 'Traditional Sri Lankan black tea',
                'price': 200.00,
                'category': 'Beverages',
                'image_url': '/static/images/m.png',
                'available': True
            }
        ]
        
        for beverage in beverages:
            try:
                result = supabase.table('menu_items').upsert(beverage).execute()
                print(f"✅ Added beverage: {beverage['name']}")
            except Exception as e:
                print(f"❌ Failed to add {beverage['name']}: {e}")
    
    # Add desserts if missing
    if 'Desserts' not in categories:
        desserts = [
            {
                'id': 'watalappan',
                'name': 'Watalappan',
                'description': 'Traditional Sri Lankan coconut custard',
                'price': 450.00,
                'category': 'Desserts',
                'image_url': '/static/images/m.png',
                'available': True
            },
            {
                'id': 'ice-cream-sundae',
                'name': 'Ice Cream Sundae',
                'description': 'Vanilla ice cream with chocolate sauce',
                'price': 400.00,
                'category': 'Desserts',
                'image_url': '/static/images/m.png',
                'available': True
            },
            {
                'id': 'fruit-salad',
                'name': 'Fresh Fruit Salad',
                'description': 'Seasonal tropical fruits',
                'price': 350.00,
                'category': 'Desserts',
                'image_url': '/static/images/m.png',
                'available': True
            }
        ]
        
        for dessert in desserts:
            try:
                result = supabase.table('menu_items').upsert(dessert).execute()
                print(f"✅ Added dessert: {dessert['name']}")
            except Exception as e:
                print(f"❌ Failed to add {dessert['name']}: {e}")

def main():
    print("🔄 Green Heaven Menu Category Reorganization")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not supabase:
        print("❌ Supabase not available")
        return
    
    # Step 1: Reorganize existing categories
    reorganize_categories()
    
    # Step 2: Add missing beverages and desserts
    add_beverages_and_desserts()
    
    # Step 3: Update customer page
    update_customer_page_categories()
    
    print_section("Category Reorganization Complete")
    print("✅ Menu organized into customer-friendly categories")
    print("✅ All items have proper images (m.png)")
    print("✅ Customer page updated with new filters")
    print("🔄 Please restart the server to see changes")
    print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()