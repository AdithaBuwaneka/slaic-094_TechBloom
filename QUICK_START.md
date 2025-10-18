# Quick Start Guide - After Fixes

## ✅ What's Already Done

- ✅ Merged `dev-nithila1` into `dev-aditha1`
- ✅ Fixed all import errors in backend
- ✅ Cleared Metro bundler cache
- ✅ Killed conflicting process on port 8081
- ✅ Backend code ready for Python 3.13

## 🚨 ONE THING YOU MUST DO

**Change DNS to Google DNS** (this fixes all 500 errors)

### Option 1: Automated (Recommended)
```powershell
# Right-click PowerShell → Run as Administrator
cd F:\Ai_Challenge
.\fix_dns.ps1
```

### Option 2: Manual
1. **Open PowerShell as Administrator**
2. Run these commands:
```powershell
netsh interface ipv4 set dns name="Wi-Fi" static 8.8.8.8 primary
netsh interface ipv4 add dns name="Wi-Fi" 8.8.4.4 index=2
ipconfig /flushdns
```

## 🎯 After DNS Fix - Start Everything

### Terminal 1: Backend
```bash
cd F:\Ai_Challenge\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Look for:**
```
✓ MongoDB connection established successfully
✓ INFO: Application startup complete
```

### Terminal 2: Mobile App
```bash
cd F:\Ai_Challenge\mobile-app
npx expo start --clear
```

**Then:**
- Press `a` for Android
- Press `i` for iOS
- Or scan QR code with Expo Go app

## ✅ Everything Should Work Now

- ✅ Route planning (Colombo → Kandy)
- ✅ Save routes to database
- ✅ View route history
- ✅ AI chatbot
- ✅ Real-time updates

## 📋 Quick Test

1. Open mobile app
2. Login or register
3. Go to Home tab
4. Enter: From "Colombo" To "Kandy"
5. Select "Transit" mode
6. Click "Plan Route"
7. Should see route with NO errors

## 🆘 If You Still See Errors

1. Verify DNS changed:
   ```bash
   ipconfig /all | findstr "DNS"
   ```
   Should show `8.8.8.8`

2. Restart backend server (Ctrl+C, then start again)

3. Check backend logs for MongoDB connection success

4. See full guide: `FIX_ALL_ISSUES.md`

## 📞 Need Help?

All detailed instructions are in:
- `FIX_ALL_ISSUES.md` - Complete troubleshooting guide
- `fix_dns.ps1` - Automated DNS fix script

---

**Summary:** Just run `fix_dns.ps1` as Administrator, then start both servers. Everything else is already fixed!
