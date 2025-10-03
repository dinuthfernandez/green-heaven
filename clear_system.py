#!/usr/bin/env python3
"""
Green Heaven Restaurant System - Data Clearing Script
Resets all data for a fresh system start
"""

import os
import json
import shutil
from datetime import datetime
import requests

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def backup_current_data():
    """Create a backup of current data before clearing"""
    print_section("Creating Backup")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f"data/backups/pre_clear_backup_{timestamp}"
    
    try:
        os.makedirs(backup_dir, exist_ok=True)
        
        # Backup files if they exist
        files_to_backup = [
            'data/orders.json',
            'data/daily_totals.json'
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                backup_path = os.path.join(backup_dir, filename)
                shutil.copy2(file_path, backup_path)
                print(f"✅ Backed up: {file_path} -> {backup_path}")
            else:
                print(f"⚠️  File not found: {file_path}")
        
        print(f"💾 Backup created in: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def clear_local_data():
    """Clear all local data files"""
    print_section("Clearing Local Data")
    
    # Initialize empty data structures
    empty_orders = []
    empty_daily_totals = {}
    
    try:
        # Clear orders.json
        orders_file = 'data/orders.json'
        with open(orders_file, 'w') as f:
            json.dump(empty_orders, f, indent=2)
        print(f"✅ Cleared: {orders_file}")
        
        # Clear daily_totals.json
        totals_file = 'data/daily_totals.json'
        with open(totals_file, 'w') as f:
            json.dump(empty_daily_totals, f, indent=2)
        print(f"✅ Cleared: {totals_file}")
        
        # Clean up old backups (keep only last 5)
        cleanup_old_backups()
        
        print("✅ Local data cleared successfully")
        
    except Exception as e:
        print(f"❌ Error clearing local data: {e}")

def cleanup_old_backups():
    """Remove old backup files, keeping only the last 5"""
    try:
        backup_dir = 'data/backups'
        if not os.path.exists(backup_dir):
            return
            
        # Get all backup directories
        backups = [d for d in os.listdir(backup_dir) 
                  if os.path.isdir(os.path.join(backup_dir, d)) and 'backup' in d]
        
        if len(backups) > 5:
            # Sort by creation time
            backups.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
            
            # Remove oldest backups
            for old_backup in backups[:-5]:
                old_path = os.path.join(backup_dir, old_backup)
                shutil.rmtree(old_path)
                print(f"🗑️  Removed old backup: {old_backup}")
        
    except Exception as e:
        print(f"⚠️  Error cleaning backups: {e}")

def clear_supabase_data():
    """Clear data from Supabase database"""
    print_section("Clearing Supabase Data")
    
    # Note: This would require API endpoints to clear Supabase data
    # For now, we'll just indicate what would be cleared
    
    print("📋 Supabase data that would be cleared:")
    print("   - orders table")
    print("   - manual_orders table")
    print("   - daily_analytics (if exists)")
    print("")
    print("⚠️  Supabase clearing requires manual database access or API endpoints")
    print("💡 You can clear Supabase data through the dashboard at:")
    print("   https://supabase.com/dashboard/project/yypxsoysfelebjwjcbtc")

def verify_system_state():
    """Verify the system is in a clean state"""
    print_section("Verifying Clean State")
    
    try:
        # Check orders file
        with open('data/orders.json', 'r') as f:
            orders = json.load(f)
        print(f"📊 Orders count: {len(orders)}")
        
        # Check daily totals
        with open('data/daily_totals.json', 'r') as f:
            totals = json.load(f)
        print(f"📈 Daily totals entries: {len(totals)}")
        
        # Check if server is running
        try:
            response = requests.get('http://localhost:5001/api/menu', timeout=5)
            if response.status_code == 200:
                menu = response.json()
                print(f"🍽️  Menu items available: {len(menu)}")
                print("✅ Server is running and responsive")
            else:
                print("⚠️  Server responded with error")
        except requests.RequestException:
            print("⚠️  Server is not running or not accessible")
        
        print("✅ System verification complete")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")

def show_fresh_start_info():
    """Show information for fresh system start"""
    print_section("Fresh Start Information")
    
    print("🎯 Your system is now ready for a fresh start!")
    print("")
    print("📱 Access Points:")
    print("   Customer Entry: http://localhost:5001/customer-entry")
    print("   Customer Menu:  http://localhost:5001/customer")
    print("   Staff Dashboard: http://localhost:5001/staff")
    print("   Menu Management: http://localhost:5001/menu")
    print("")
    print("🔧 What was cleared:")
    print("   ✅ All order history")
    print("   ✅ Daily sales totals")
    print("   ✅ Local data files")
    print("   📋 Menu items preserved")
    print("")
    print("📋 Next Steps:")
    print("   1. Test customer order flow")
    print("   2. Test staff dashboard functionality")
    print("   3. Verify sound notifications work")
    print("   4. Test order status progression")
    print("   5. Test customer call feature")
    print("")
    print("🔊 Sound Testing:")
    print("   - Go to Staff Dashboard > Settings")
    print("   - Use the sound test buttons")
    print("   - Adjust volume as needed")

def main():
    print("🧹 Green Heaven Restaurant System - Data Clear & Fresh Start")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Confirm action
    print("\n⚠️  WARNING: This will clear all order and sales data!")
    
    # Check for command line argument to skip confirmation
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("🤖 Force mode enabled - skipping confirmation")
        response = 'yes'
    else:
        response = input("Are you sure you want to continue? (yes/no): ").lower().strip()
    
    if response != 'yes':
        print("❌ Operation cancelled")
        return
    
    # Create backup first
    backup_dir = backup_current_data()
    
    # Clear local data
    clear_local_data()
    
    # Note about Supabase
    clear_supabase_data()
    
    # Verify clean state
    verify_system_state()
    
    # Show fresh start info
    show_fresh_start_info()
    
    print_section("Data Clear Complete")
    print("✅ System is ready for fresh start!")
    if backup_dir:
        print(f"💾 Your data backup is saved in: {backup_dir}")
    print(f"🕒 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()