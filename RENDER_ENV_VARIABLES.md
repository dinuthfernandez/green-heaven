# 🚀 Render Environment Variables for Green Heaven

## Copy these EXACT values to your Render Dashboard

Go to: **Render Dashboard → Your Service → Environment Variables**

---

## 🔑 Required Environment Variables

### Flask Configuration
```
SECRET_KEY=green_heaven_super_secret_production_key_2024
PORT=10000
```

### 🔧 Render Service Configuration
**In Render Dashboard → Settings:**
- **Start Command**: `gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:$PORT app:app --timeout 120`
- **Build Command**: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`

### Supabase Database Configuration
```
SUPABASE_URL=https://yypxsoysfelebjwjcbtc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHhzb3lzZmVsZWJqd2pjYnRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc3MDI5NDMsImV4cCI6MjA0MzI3ODk0M30.X0f_rGCPbsDx7vR-dXLXHINbX4z84-TvGKnxCUpzc9o
```

---

## 📋 Step-by-Step Instructions

### 1. Go to Render Dashboard
- Visit: https://dashboard.render.com
- Find your `green-heaven` service
- Click on your service name

### 2. Add Environment Variables
- Click **"Environment"** tab on the left sidebar
- Click **"Add Environment Variable"** button
- Add each variable below:

### 3. Add These Variables One by One:

**Variable 1:**
- Key: `SECRET_KEY`
- Value: `green_heaven_super_secret_production_key_2024`

**Variable 2:**
- Key: `PORT`
- Value: `10000`

**Variable 3:**
- Key: `SUPABASE_URL`
- Value: `https://yypxsoysfelebjwjcbtc.supabase.co`

**Variable 4:**
- Key: `SUPABASE_ANON_KEY`
- Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl5cHhzb3lzZmVsZWJqd2pjYnRjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjc3MDI5NDMsImV4cCI6MjA0MzI3ODk0M30.X0f_rGCPbsDx7vR-dXLXHINbX4z84-TvGKnxCUpzc9o`

### 4. Deploy
- After adding all variables, click **"Deploy"** or wait for auto-deployment
- Your app will restart with Supabase connection

---

## ✅ Expected Results After Adding Variables

### Before (Current):
```
❌ Supabase error for orders: illegal request line
❌ Supabase error for manual_orders: illegal request line
❌ Error loading menu items from Supabase: illegal request line
📁 Falling back to local storage
```

### After (With Variables):
```
🚀 Supabase client available - enabling real-time database!
✅ Supabase connected: https://yypxsoysfelebjwjcbtc.supabase.co
🔄 Real-time database active - lightning fast performance!
✅ Orders loaded from Supabase
✅ Menu items loaded from Supabase
💾 Real-time database fully operational
```

---

## 🎯 Why This Fixes Everything

1. **Real-time Database**: Supabase connection enables live updates
2. **Data Persistence**: Orders and menu items stored in cloud database
3. **Multi-device Sync**: Staff can use multiple devices simultaneously
4. **Performance**: Faster data loading and real-time notifications
5. **Reliability**: Cloud backup of all restaurant data

---

## 🚨 Important Notes

- **Copy-paste exactly**: Don't modify the SUPABASE_ANON_KEY
- **Case sensitive**: Environment variable names must match exactly
- **Auto-deploy**: Render will restart your service automatically
- **Test afterwards**: Visit your staff dashboard to verify connection

---

## 🔗 Quick Links

- **Render Dashboard**: https://dashboard.render.com
- **Your Staff Dashboard**: https://green-heaven-ovd6.onrender.com/staff
- **Customer Interface**: https://green-heaven-ovd6.onrender.com/

After adding these variables, your Green Heaven restaurant system will have full real-time database capabilities! 🎉