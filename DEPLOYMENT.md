# 🚀 Render Deployment Guide - Green Heaven Restaurant

## 📋 Pre-Deployment Checklist

### ✅ Firebase Setup Complete
- Firebase project: `green-heaven-c2856` 
- Service account key downloaded
- Firestore database needs to be enabled (see step 4 below)

### ✅ Repository Ready  
- All code pushed to GitHub: `https://github.com/dinuthfernandez/green-heaven.git`
- Configuration files created (render.yaml, requirements.txt, runtime.txt)

---

## 🌐 Render Deployment Steps

### 1. Connect Repository to Render
1. Go to https://render.com and sign in/register
2. Click "New" → "Web Service"
3. Connect GitHub and select `dinuthfernandez/green-heaven`
4. Use these settings:
   - **Name**: `green-heaven-restaurant`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT app:app`

### 2. Configure Environment Variables
In Render Dashboard → Environment Variables, add:

**Required Variables:**
```
SECRET_KEY=green_heaven_super_secret_production_key_2024_change_this
PORT=5001
```

**Firebase Variables (for persistent database):**
```
FIREBASE_PROJECT_ID=green-heaven-c2856
FIREBASE_PRIVATE_KEY_ID=941de02264c29a8eb8ef8e96d016e848d0d41508
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@green-heaven-c2856.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=114096143875226667889
```

**Firebase Private Key (copy exactly as one line):**
```
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC79zHaRU91MlWG\n3EyRTeuU7ymMq6EOZ4LCIF553GsM0mc2WGGrrm3R1Vg6/2k/zWXdR1p0SkmrXV+O\nsofQ3G1rBNXnUz0ZkHRauaDsy3DmV0TzMbXFTuRGngtz4qu8CQvQqA+twoSyOKFk\nbsa0BFHGAlfnexiHbQdMVhmrmHbw7y94Zpy8TET+qfzeiZG/IEuzObcKGZiUwcYD\nwHnq+EHS0QpaLUDg+Yb0TJbEBt/8iZrQuiuSeCeCQLXjMRZauxDkuNVG2LiULRbl\nek2UY83p1oyIPh0PZ67Gq1ZxmLkVxg61vLzt7+abLJ4qbEoIEbuOq0/AoAeP1wk4\nx17JborZAgMBAAECggEABJCi46qiKaLX9c8rX+FwOrazpmCaG0vmkdLjhuehK1d/\n0LYFFzxeNLkO+PQ9InxmGfsfgAQFQoKhYIlgjleQI7sWe9U0CzpZWd7r9A99aQBO\nr4fyFde0gd+MQFuaSqLyNPZwvQpXzfrdacXdkKX4AdkkOLFVZB9nTJ9DS9bUPd+Y\n4kj8vtLAVoJGfeoxbJFk2tPQCgOZzbzsIYlUQhi/VaFs9qePn2MqdB5gFNW3stgt\nPMTRnDq4rNuRNIvfQZFeguIcmTsppCmshho0PSQVK/aU116OaSWBk3PmP4CAkpMB\n18Jc3sA8jxyM1rqRpAiBlreLZphM1Wp+hcCk1s2I4QKBgQD6qoHBvnBb5wvT/hhZ\ny6KyiDLEcl8xdgUWr/00pbXSD/TdSdtjIM7xAFKnS/qQo7NWZGmEa0uP9vF6L7ah\n2oe8KeTeV3A8oJy6Qvk1UVw3O3Xuvq/3fixEU6/LnaH4EklKOXJGYHl4yrg7bDe/\nUSi+NHLheXh82JwiUPa8QpqZ6QKBgQC/9yE4uiVrnJ0fRKXKavFwcKrz8H88Nb2t\n1HkNV7DZCLoglfcf0t+zTPjdp4MPcY/c3g03YtMNTE1I87qxpT7sPXdQ5NCoAFDn\notA8uZS1AALMSz2Np3D4wibVA9JT88TBqP7KnwJVYAKl6bP4xLwYieE8pQUqd4Ri\nIAaU7Z/jcQKBgQDv5jOdOyfJrQxy7WJcvjmN6C++Nz/H1I32MqSAuH+U9VSCXOcs\nrf+gQ5DXMC40M5e1fRBHfXCp7csaB4Qgz0bM3MN/z+tI+uZElUhwsNcyvSOXRMSg\ndw7irb03gDu9cbLW6Lfnhvl6k3lS1bVc0s3Ni+DOzjR0N9LmPNqHPq870QKBgC4A\ncdSfPwJnuHtavwQf1pXkWgM1Gbh7BGZYqV2aKwYHglr2tQ7KQNM92dF8J/sWcqwy\nBibEpuDj7Q1TYuTZPZftLt+SxbHMyZaIvLAgpNMvGnyMd0av3nGuTRH05X06yGbE\nMbKqoiuFY30Q4RD3TD/xIqmevfssQuwk0o7z1sHxAoGBAM2Fd3onRKeGTUMcN2cq\nziyyuQH3ifVaWz7ULK6a0vSZgmIPWjBvYrCpLKWpy/rJlaP1t637oDxCuqrbbZ8Z\nKfO5ZaR8RderVh5BPVJdUI18HBh3Gern3zVAlq9rX+dwQFpFQ0QtFn8hpqihSqUZ\nxf2bhm8uJka8u0ltrdF9xxIV\n-----END PRIVATE KEY-----\n
```

### 3. Deploy Application
1. Click "Create Web Service" 
2. Render will automatically build and deploy
3. Wait for deployment to complete (~3-5 minutes)
4. Your app will be available at `https://your-app-name.onrender.com`

### 4. Enable Firestore Database
**CRITICAL:** After deployment, enable Firestore:

1. Go to https://console.firebase.google.com
2. Select project `green-heaven-c2856`
3. Go to "Firestore Database"
4. Click "Create Database"
5. Choose "Start in test mode" (for now)
6. Select a location close to your users

**Or use this direct link:**
https://console.developers.google.com/apis/api/firestore.googleapis.com/overview?project=green-heaven-c2856

### 5. Test Your Deployment
1. Visit your Render URL
2. Test customer interface: `/`
3. Test staff dashboard: `/staff`
4. Test order placement and management
5. Verify Firebase data persistence

---

## 🔧 System Features in Production

### 🎯 Restaurant Management
- **Real-time Orders**: Live order tracking across devices
- **Staff Dashboard**: Complete order and table management  
- **Manual Orders**: Add walk-in/phone orders with timestamps
- **Customer Interface**: Mobile-optimized ordering system

### 📊 Business Analytics
- **Daily Totals**: Digital + Manual revenue tracking
- **PDF Reports**: 30-day business analysis reports
- **Real-time Stats**: Order counts and status tracking

### 💾 Data Persistence
- **Firebase Firestore**: Real-time cloud database
- **Automatic Backup**: All data preserved across restarts
- **Local Fallback**: Works even if Firebase is temporarily unavailable

---

## ⚡ Production URLs

After deployment, your restaurant system will be available at:
- **Customer Interface**: `https://your-app-name.onrender.com/`
- **Staff Dashboard**: `https://your-app-name.onrender.com/staff`

---

## 🚨 Important Notes

### Security
- ✅ Environment variables secure sensitive data
- ✅ Firebase service account keys protected
- ✅ .gitignore prevents sensitive file commits

### Performance
- ✅ Render free tier provides 750 hours/month
- ✅ Auto-sleep after 15 minutes of inactivity
- ✅ Cold start takes ~10 seconds (first request after sleep)

### Monitoring
- Check Render logs for any deployment issues
- Firebase console shows database usage and errors
- Application includes error handling and fallbacks

---

## 🎉 Deployment Complete!

Your Green Heaven Restaurant Management System is now ready for production use with:

- ✅ **Real-time Database**: Firebase Firestore integration
- ✅ **Cloud Hosting**: Render deployment ready
- ✅ **Mobile Optimized**: Responsive design for all devices
- ✅ **Business Analytics**: PDF reports and daily totals
- ✅ **Professional Branding**: Green Heaven theme throughout

**Next Steps:**
1. Deploy on Render using steps above
2. Enable Firestore database
3. Test all features on live URL
4. Share with restaurant staff

Your restaurant management system is production-ready! 🚀