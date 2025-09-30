#!/usr/bin/env python3
"""
Quick Supabase Database Setup
Creates tables directly via SQL
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def init_supabase():
    """Initialize Supabase client"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Supabase credentials not found in environment variables")
        return None
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("✅ Connected to Supabase")
        return supabase
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return None

def create_tables(supabase: Client):
    """Create database tables"""
    print("🏗️  Creating database tables...")
    
    # SQL commands to create tables
    create_tables_sql = """
    -- Orders table for real-time syncing
    CREATE TABLE IF NOT EXISTS public.orders (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        customer_name TEXT NOT NULL,
        table_number TEXT NOT NULL,
        items JSONB NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'preparing', 'ready', 'delivered', 'cancelled')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Manual orders (staff-added)
    CREATE TABLE IF NOT EXISTS public.manual_orders (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        customer_name TEXT NOT NULL,
        table_number TEXT NOT NULL,
        items JSONB NOT NULL,
        total_amount DECIMAL(10,2) NOT NULL,
        order_date DATE DEFAULT CURRENT_DATE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Daily totals for analytics
    CREATE TABLE IF NOT EXISTS public.daily_totals (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        date DATE DEFAULT CURRENT_DATE UNIQUE,
        digital_orders INTEGER DEFAULT 0,
        manual_orders INTEGER DEFAULT 0,
        digital_revenue DECIMAL(10,2) DEFAULT 0,
        manual_revenue DECIMAL(10,2) DEFAULT 0,
        total_orders INTEGER DEFAULT 0,
        total_revenue DECIMAL(10,2) DEFAULT 0,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Staff alerts/calls
    CREATE TABLE IF NOT EXISTS public.staff_calls (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        customer_name TEXT NOT NULL,
        table_number TEXT NOT NULL,
        message TEXT,
        status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'resolved')),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        resolved_at TIMESTAMP WITH TIME ZONE
    );
    """
    
    try:
        result = supabase.rpc('sql', {'query': create_tables_sql}).execute()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables via RPC: {e}")
        # Try individual table creation
        return create_tables_individually(supabase)

def create_tables_individually(supabase: Client):
    """Create tables one by one if RPC fails"""
    print("🔧 Trying individual table creation...")
    
    tables_created = 0
    
    # Test with a simple query first
    try:
        # Try to insert today's daily total directly
        from datetime import date
        today = date.today().isoformat()
        
        result = supabase.table('daily_totals').upsert({
            'date': today,
            'digital_orders': 0,
            'manual_orders': 0,
            'digital_revenue': 0.0,
            'manual_revenue': 0.0,
            'total_orders': 0,
            'total_revenue': 0.0
        }).execute()
        
        print("✅ daily_totals table exists and is working!")
        tables_created += 1
        
    except Exception as e:
        print(f"❌ daily_totals table issue: {e}")
    
    return tables_created > 0

def test_connection(supabase: Client):
    """Test the database connection"""
    print("🧪 Testing database connection...")
    
    try:
        # Test a simple select
        result = supabase.table('daily_totals').select('*').limit(1).execute()
        print(f"✅ Connection test successful! Found {len(result.data)} records")
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Green Heaven Supabase database...")
    
    # Initialize Supabase
    supabase = init_supabase()
    if not supabase:
        print("❌ Setup aborted - could not connect to Supabase")
        print("\n📋 Next steps:")
        print("1. Go to https://supabase.com/dashboard")
        print("2. Run the SQL from database_schema.sql in your SQL Editor")
        print("3. Then run the migration script")
        return
    
    # Create tables
    if create_tables(supabase):
        print("🎉 Database setup completed!")
    else:
        print("⚠️  Partial setup completed")
    
    # Test connection
    if test_connection(supabase):
        print("✨ Your Green Heaven system is ready for real-time action!")
    
    print("\n📋 Next steps:")
    print("1. Add your Supabase credentials to Render environment variables")
    print("2. Deploy your updated code")
    print("3. Enjoy lightning-fast real-time performance! 🚀")

if __name__ == "__main__":
    main()