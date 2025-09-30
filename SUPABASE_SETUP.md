# 🚀 Supabase Setup for Green Heaven Restaurant

## Step 1: Create Supabase Project

1. Go to **https://supabase.com**
2. Sign up/Login with GitHub
3. Click **"New Project"**
4. Fill in:
   - **Organization**: Your personal org
   - **Name**: `green-heaven-restaurant`
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to your location
   - **Pricing Plan**: Free tier (perfect for restaurants)

5. Click **"Create new project"** (takes ~2 minutes)

## Step 2: Get Your Credentials

After project is created, go to **Settings → API**:

```
Project URL: https://your-project-id.supabase.co
Anon key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Service role key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Step 3: Create Database Tables

Go to **SQL Editor** in Supabase dashboard and run this script:

```sql
-- Enable Row Level Security
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Orders table for real-time syncing
CREATE TABLE public.orders (
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
CREATE TABLE public.manual_orders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_name TEXT NOT NULL,
    table_number TEXT NOT NULL,
    items JSONB NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    order_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Daily totals for analytics
CREATE TABLE public.daily_totals (
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
CREATE TABLE public.staff_calls (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    customer_name TEXT NOT NULL,
    table_number TEXT NOT NULL,
    message TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'resolved')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for better performance
CREATE INDEX idx_orders_status ON public.orders(status);
CREATE INDEX idx_orders_table ON public.orders(table_number);
CREATE INDEX idx_orders_created ON public.orders(created_at DESC);
CREATE INDEX idx_manual_orders_date ON public.manual_orders(order_date);
CREATE INDEX idx_staff_calls_status ON public.staff_calls(status);
CREATE INDEX idx_daily_totals_date ON public.daily_totals(date);

-- Enable real-time subscriptions
ALTER PUBLICATION supabase_realtime ADD TABLE public.orders;
ALTER PUBLICATION supabase_realtime ADD TABLE public.staff_calls;
ALTER PUBLICATION supabase_realtime ADD TABLE public.daily_totals;

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER handle_orders_updated_at
    BEFORE UPDATE ON public.orders
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

CREATE TRIGGER handle_daily_totals_updated_at
    BEFORE UPDATE ON public.daily_totals
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE public.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.manual_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_totals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.staff_calls ENABLE ROW LEVEL SECURITY;

-- Create policies for access (allow all for now, can be restricted later)
CREATE POLICY "Allow all operations on orders" ON public.orders FOR ALL USING (true);
CREATE POLICY "Allow all operations on manual_orders" ON public.manual_orders FOR ALL USING (true);
CREATE POLICY "Allow all operations on daily_totals" ON public.daily_totals FOR ALL USING (true);
CREATE POLICY "Allow all operations on staff_calls" ON public.staff_calls FOR ALL USING (true);
```

## Step 4: Environment Variables

Add these to your Render environment variables:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
```

## Step 5: Test Connection

The app will automatically connect to Supabase once you add the environment variables!

## 🚀 Benefits You'll Get:

- ⚡ **Lightning fast queries** (PostgreSQL)
- 🔄 **Real-time updates** across all devices
- 📊 **Better analytics** with SQL queries
- 🔒 **Secure by default** with Row Level Security
- 🌐 **Global CDN** for faster access
- 💾 **Automatic backups** included
- 📈 **Scalable** for restaurant growth

Your Green Heaven restaurant will have enterprise-level database performance! 🌿