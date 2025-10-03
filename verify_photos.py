#!/usr/bin/env python3
"""
Verify all menu items have real food photos
"""

import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from supabase import create_client
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("❌ Required packages not installed")
    sys.exit(1)

def verify_real_photos():
    """Verify all menu items have real photos"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found")
        return
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
        
        # Get all menu items
        response = supabase.table('menu_items').select('id, name, image_url').execute()
        items = response.data if response.data else []
        
        if not items:
            print("❌ No menu items found")
            return
        
        print(f"📋 Checking {len(items)} menu items for real photos...")
        print("=" * 70)
        
        # Check each item
        real_photos = 0
        placeholder_photos = 0
        no_photos = 0
        
        for item in items:
            name = item.get('name', 'Unknown')
            image_url = item.get('image_url', '')
            
            if not image_url:
                status = "❌ NO IMAGE"
                no_photos += 1
            elif 'supabase.co' in image_url and ('real_' in image_url or 'food' in image_url):
                status = "✅ REAL PHOTO"
                real_photos += 1
            elif 'placeholder' in image_url or 'via.placeholder' in image_url:
                status = "⚠️ PLACEHOLDER"
                placeholder_photos += 1
            elif 'supabase.co' in image_url:
                status = "✅ REAL PHOTO"
                real_photos += 1
            else:
                status = "❓ UNKNOWN"
                no_photos += 1
            
            print(f"{status} | {name:<50} | {image_url[:50]}...")
        
        print("=" * 70)
        print(f"📊 SUMMARY:")
        print(f"   ✅ Real Photos: {real_photos}")
        print(f"   ⚠️ Placeholders: {placeholder_photos}")
        print(f"   ❌ No Images: {no_photos}")
        print(f"   📈 Success Rate: {(real_photos/len(items))*100:.1f}%")
        
        if real_photos == len(items):
            print("\n🎉 SUCCESS! All menu items have REAL food photos!")
        elif real_photos > len(items) * 0.8:
            print(f"\n✅ Good progress! {real_photos}/{len(items)} items have real photos")
        else:
            print(f"\n⚠️ More work needed. Only {real_photos}/{len(items)} items have real photos")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🍽️ Green Heaven - Photo Verification")
    print("=" * 50)
    verify_real_photos()