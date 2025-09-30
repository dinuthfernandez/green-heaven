#!/usr/bin/env python3
"""
Test Supabase Menu Items Integration
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def test_supabase_menu():
    """Test Supabase menu items functionality"""
    print("🧪 Testing Supabase Menu Items Integration...")
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Supabase credentials not found")
        return
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Connected to Supabase")
        
        # Test reading menu items
        result = supabase.table('menu_items').select('*').execute()
        
        if result.data:
            print(f"✅ Found {len(result.data)} menu items in Supabase:")
            for item in result.data:
                print(f"  - {item['name']} (${item['price']})")
        else:
            print("⚠️  No menu items found in Supabase")
            print("💡 Need to run the setup SQL script first")
            
        # Test the storage bucket
        try:
            buckets = supabase.storage.list_buckets()
            print(f"📦 Storage buckets: {[b.name for b in buckets]}")
            
            if 'menu-images' in [b.name for b in buckets]:
                print("✅ menu-images bucket exists")
            else:
                print("⚠️  menu-images bucket not found")
                
        except Exception as e:
            print(f"⚠️  Storage test failed: {e}")
            
    except Exception as e:
        print(f"❌ Supabase test failed: {e}")

if __name__ == "__main__":
    test_supabase_menu()