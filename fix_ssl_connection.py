#!/usr/bin/env python3
"""
SSL Connection Fix for Green Heaven Restaurant
Diagnoses and fixes Supabase SSL connection issues with Python 3.13+
"""

import os
import sys
import ssl
import urllib.request
import json
from datetime import datetime

def test_ssl_connection():
    """Test SSL connection to various endpoints"""
    print("🔍 Testing SSL connections...")
    
    # Test basic HTTPS connection
    try:
        response = urllib.request.urlopen('https://httpbin.org/json', timeout=10)
        print("✅ Basic HTTPS connection works")
    except Exception as e:
        print(f"❌ Basic HTTPS connection failed: {e}")
        return False
    
    # Test Supabase endpoint if available
    supabase_url = os.getenv('SUPABASE_URL')
    if supabase_url:
        try:
            # Try to reach Supabase endpoint
            test_url = f"{supabase_url}/rest/v1/"
            request = urllib.request.Request(test_url)
            request.add_header('apikey', os.getenv('SUPABASE_ANON_KEY', ''))
            response = urllib.request.urlopen(request, timeout=10)
            print("✅ Supabase endpoint is reachable")
        except Exception as e:
            print(f"⚠️ Supabase endpoint test failed: {e}")
    
    return True

def fix_ssl_environment():
    """Apply SSL environment fixes for Python 3.13+"""
    print("🔧 Applying SSL environment fixes...")
    
    # Set environment variables for SSL compatibility
    ssl_fixes = {
        'PYTHONHTTPSVERIFY': '0',  # Disable SSL verification as fallback
        'CURL_CA_BUNDLE': '',      # Clear CA bundle to use system default
        'REQUESTS_CA_BUNDLE': '',  # Clear requests CA bundle
    }
    
    for key, value in ssl_fixes.items():
        os.environ[key] = value
        print(f"  Set {key}={value}")
    
    # Configure SSL context globally
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        print("  ✅ Applied global SSL context fix")
    except Exception as e:
        print(f"  ⚠️ Global SSL context fix failed: {e}")

def test_supabase_connection():
    """Test Supabase connection with different methods"""
    print("🔗 Testing Supabase connection...")
    
    try:
        from supabase import create_client
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found in environment")
            return False
        
        # Try basic connection
        try:
            client = create_client(supabase_url, supabase_key)
            result = client.table('menu_items').select('id').limit(1).execute()
            print("✅ Supabase connection successful!")
            print(f"  Database accessible with {len(result.data)} test records")
            return True
            
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            
            # Show specific error types
            if "SSLSocket" in str(e):
                print("  🔍 Detected Python 3.13 SSL compatibility issue")
                print("  💡 Try running: pip install --upgrade supabase")
                print("  💡 Or downgrade to Python 3.11 if needed")
            
            return False
            
    except ImportError:
        print("❌ Supabase package not installed")
        print("  💡 Run: pip install supabase")
        return False

def create_ssl_test_script():
    """Create a test script for SSL issues"""
    script_content = '''#!/usr/bin/env python3
import ssl
import os
import sys

# Apply SSL fixes
os.environ['PYTHONHTTPSVERIFY'] = '0'
ssl._create_default_https_context = ssl._create_unverified_context

# Test Supabase
try:
    from supabase import create_client
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        client = create_client(supabase_url, supabase_key)
        result = client.table('menu_items').select('*').limit(1).execute()
        print("✅ Supabase connection works!")
        print(f"Test result: {result.data}")
    else:
        print("❌ Supabase credentials not found")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")
    sys.exit(1)
'''
    
    with open('test_supabase_ssl.py', 'w') as f:
        f.write(script_content)
    
    print("📝 Created test_supabase_ssl.py script")

def main():
    """Main diagnostic and fix function"""
    print("🩺 Green Heaven SSL Connection Diagnostics")
    print("=" * 50)
    print(f"🐍 Python version: {sys.version}")
    print(f"🔐 SSL version: {ssl.OPENSSL_VERSION}")
    print(f"📅 Timestamp: {datetime.now()}")
    print()
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Loaded environment variables from .env")
    except ImportError:
        print("⚠️ python-dotenv not available, using system environment")
    
    # Test basic SSL
    if not test_ssl_connection():
        print("❌ Basic SSL test failed - check internet connection")
        return
    
    # Apply SSL fixes
    fix_ssl_environment()
    
    # Test Supabase
    if test_supabase_connection():
        print("\n🎉 All tests passed! Your Supabase connection should work now.")
    else:
        print("\n❌ Supabase connection still failing.")
        print("\n🔧 Additional troubleshooting steps:")
        print("1. Check your Supabase credentials in .env file")
        print("2. Try: pip install --upgrade supabase httpx")
        print("3. Consider using Python 3.11 if the issue persists")
        print("4. Check if your firewall blocks HTTPS connections")
        
        # Create test script
        create_ssl_test_script()
        print("5. Run the created test_supabase_ssl.py script for isolated testing")

if __name__ == '__main__':
    main()