#!/usr/bin/env python3
"""
Production Environment Checker for Green Heaven on Render
Run this to diagnose issues in production deployment
"""

import os
import sys
import json
from datetime import datetime

def check_environment():
    """Check production environment configuration"""
    print("🔍 Green Heaven Production Environment Check")
    print("=" * 60)
    print(f"🕐 Timestamp: {datetime.now().isoformat()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Load environment variables if not in production
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("📁 Loaded .env file for local testing")
    except ImportError:
        print("📁 No .env file loading (production mode)")
    print()
    
    # Check if we're in production
    is_render = bool(os.getenv('RENDER'))
    is_production = bool(os.getenv('PORT')) or is_render
    
    print(f"🌍 Environment Type:")
    print(f"  - Production: {is_production}")
    print(f"  - Render Platform: {is_render}")
    print(f"  - Port: {os.getenv('PORT', 'not_set')}")
    print()
    
    # Check critical environment variables
    print("🔑 Environment Variables:")
    critical_vars = {
        'SUPABASE_URL': os.getenv('SUPABASE_URL'),
        'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY'),
        'SECRET_KEY': os.getenv('SECRET_KEY'),
        'PORT': os.getenv('PORT'),
        'RENDER': os.getenv('RENDER'),
        'PYTHONHTTPSVERIFY': os.getenv('PYTHONHTTPSVERIFY')
    }
    
    for var_name, var_value in critical_vars.items():
        if var_value:
            if 'KEY' in var_name or 'SECRET' in var_name:
                display_value = var_value[:10] + '...' if len(var_value) > 10 else var_value
            else:
                display_value = var_value
            print(f"  ✅ {var_name}: {display_value}")
        else:
            print(f"  ❌ {var_name}: NOT SET")
    print()
    
    # Test Supabase connection
    print("🔗 Testing Supabase Connection:")
    try:
        from supabase import create_client
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("  ❌ Supabase credentials missing")
            return False
        
        print(f"  🔄 Connecting to: {supabase_url[:50]}...")
        
        # Try connection
        client = create_client(supabase_url, supabase_key)
        result = client.table('menu_items').select('id').limit(1).execute()
        
        if result.data:
            print(f"  ✅ Connection successful!")
            
            # Get full menu count
            full_result = client.table('menu_items').select('*').execute()
            print(f"  📊 Total menu items: {len(full_result.data)}")
            
            # Show categories
            categories = set()
            for item in full_result.data:
                categories.add(item.get('category', 'Unknown'))
            print(f"  🏷️ Categories: {', '.join(sorted(categories))}")
            
            return True
        else:
            print("  ⚠️ Connection successful but no data returned")
            return False
            
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")
        
        # Specific error analysis
        error_str = str(e)
        if "SSLSocket" in error_str:
            print("  🔐 SSL/TLS compatibility issue detected")
            print("  💡 Try setting PYTHONHTTPSVERIFY=0 in environment variables")
        elif "timeout" in error_str.lower():
            print("  ⏱️ Network timeout - check connectivity")
        elif "authentication" in error_str.lower():
            print("  🔑 Authentication issue - check API keys")
        
        return False

def test_flask_app():
    """Test if Flask app can start"""
    print("🧪 Testing Flask Application:")
    try:
        # Import main app components
        from app import app, supabase, load_menu_items
        
        print("  ✅ App imports successful")
        print(f"  🔗 Supabase client: {'Available' if supabase else 'Not available'}")
        
        # Test menu loading
        menu_items = load_menu_items()
        print(f"  📋 Menu items loaded: {len(menu_items)}")
        
        if menu_items:
            sample_item = menu_items[0]
            if sample_item.get('id') == 'emergency-item-1':
                print("  ⚠️ WARNING: Using emergency fallback menu!")
                print("  🚨 Supabase connection is failing in production")
            else:
                print("  ✅ Real menu data loaded successfully")
                print(f"  📝 Sample item: {sample_item.get('name', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask app test failed: {e}")
        return False

def generate_fix_recommendations():
    """Generate recommendations for fixing issues"""
    print("🔧 Fix Recommendations:")
    print()
    
    # Check for common issues
    if not os.getenv('SUPABASE_URL'):
        print("❌ Missing SUPABASE_URL:")
        print("  1. Log into Render dashboard")
        print("  2. Go to your app settings")
        print("  3. Add environment variable: SUPABASE_URL")
        print("  4. Set value to your Supabase project URL")
        print()
    
    if not os.getenv('SUPABASE_ANON_KEY'):
        print("❌ Missing SUPABASE_ANON_KEY:")
        print("  1. Log into Render dashboard")
        print("  2. Go to your app settings")
        print("  3. Add environment variable: SUPABASE_ANON_KEY")
        print("  4. Set value to your Supabase anonymous key")
        print()
    
    if not os.getenv('PYTHONHTTPSVERIFY'):
        print("🔐 SSL Compatibility Fix:")
        print("  1. Add environment variable: PYTHONHTTPSVERIFY")
        print("  2. Set value to: 0")
        print("  3. This helps with SSL issues in production")
        print()
    
    print("📋 General Production Checklist:")
    print("  ✅ Ensure all environment variables are set in Render")
    print("  ✅ Verify Supabase project is active and accessible")
    print("  ✅ Check Render logs for detailed error messages")
    print("  ✅ Test menu API endpoint: /api/menu-debug")
    print("  ✅ Redeploy after making environment variable changes")

def main():
    """Main diagnostic function"""
    env_ok = check_environment()
    print()
    
    app_ok = test_flask_app()
    print()
    
    if not env_ok or not app_ok:
        generate_fix_recommendations()
    else:
        print("🎉 All checks passed! Your production environment looks good.")
    
    print()
    print("📋 Next Steps:")
    if not env_ok:
        print("  1. Fix environment variable issues")
        print("  2. Redeploy on Render")
    elif not app_ok:
        print("  1. Check application logs for detailed errors")
        print("  2. Test API endpoints directly")
    else:
        print("  1. Test your live application")
        print("  2. Verify menu filtering works correctly")
    
    print()
    print("🌐 Useful Render URLs:")
    print("  - Dashboard: https://dashboard.render.com")
    print("  - Environment Variables: Settings > Environment")
    print("  - Logs: Monitor > Logs")

if __name__ == '__main__':
    main()