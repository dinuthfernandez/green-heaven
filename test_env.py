#!/usr/bin/env python3
"""
Quick environment variable test for Render deployment
"""
import os

print("🔍 Environment Variable Check")
print("=" * 40)

# Check all required environment variables
env_vars = {
    'SECRET_KEY': os.getenv('SECRET_KEY'),
    'PORT': os.getenv('PORT'),
    'SUPABASE_URL': os.getenv('SUPABASE_URL'),
    'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY')
}

for key, value in env_vars.items():
    if value:
        if key == 'SUPABASE_ANON_KEY':
            # Only show first and last 10 characters of API key
            masked = value[:10] + "..." + value[-10:] if len(value) > 20 else value
            print(f"✅ {key}: {masked}")
        else:
            print(f"✅ {key}: {value}")
    else:
        print(f"❌ {key}: NOT SET")

print("=" * 40)

# Test Supabase connection if available
try:
    from supabase import create_client
    supabase_url = env_vars['SUPABASE_URL']
    supabase_key = env_vars['SUPABASE_ANON_KEY']
    
    if supabase_url and supabase_key:
        print("🧪 Testing Supabase connection...")
        try:
            supabase = create_client(supabase_url, supabase_key)
            # Simple test query
            result = supabase.table('menu_items').select('*').limit(1).execute()
            print(f"✅ Supabase connection successful! Found {len(result.data)} test record(s)")
        except Exception as e:
            print(f"❌ Supabase connection failed: {str(e)}")
    else:
        print("⚠️ Missing Supabase credentials - skipping connection test")
        
except ImportError:
    print("📦 Supabase library not available")

print("=" * 40)
print("🏁 Environment check complete")