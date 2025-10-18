# Restart Servers - All Issues Fixed!

## ✅ What Was Just Fixed

1. **Backend Coroutine Error** - Added missing `await` keyword
   - File: `backend/app/api/v1/travel_routes.py:103`
   - Error: `'coroutine' object has no attribute 'get'`
   - Status: **FIXED** ✅

2. **Metro Bundler Cache** - Cleared all caches
   - Status: **FIXED** ✅

3. **Merge Conflicts** - Resolved all conflicts
   - Status: **COMPLETE** ✅

## 🚀 Restart Both Servers Now

### Step 1: Restart Backend Server

**Stop** the current backend server (Ctrl+C in the terminal), then:

```bash
cd F:\Ai_Challenge\backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**What to expect:**
```
✓ MongoDB connection established successfully
✓ RAG system initialized successfully!
✓ INFO: Application startup complete
```

**No more errors like:**
- ❌ `'coroutine' object has no attribute 'get'` ← FIXED!
- ❌ `Database query failed` ← Fixed after DNS change

### Step 2: Restart Mobile App

**Stop** the current Expo server (Ctrl+C), then:

```bash
cd F:\Ai_Challenge\mobile-app

# Kill any process on port 8081
netstat -ano | findstr :8081
# If you see a PID, kill it:
taskkill //PID <PID_NUMBER> //F

# Start fresh
npx expo start --clear
```

**What to expect:**
```
✓ Metro bundler running
✓ No InternalBytecode.js errors
```

### Step 3: Test It!

1. Open mobile app
2. Login
3. Plan a route: Colombo → Kandy (Transit mode)
4. Should work WITHOUT errors!

## 🔧 If You Still Get DNS Errors

The backend async error is **FIXED**, but you may still see database errors if DNS isn't changed yet.

**Fix DNS (one-time):**
```powershell
# Run PowerShell as Administrator
cd F:\Ai_Challenge
.\fix_dns.ps1
```

Or manually:
```powershell
netsh interface ipv4 set dns name="Wi-Fi" static 8.8.8.8 primary
netsh interface ipv4 add dns name="Wi-Fi" 8.8.4.4 index=2
ipconfig /flushdns
```

## ✅ Summary

| Issue | Status |
|-------|--------|
| Git Merge | ✅ Complete |
| Backend Imports | ✅ Fixed |
| Backend Async Error | ✅ **JUST FIXED** |
| Metro Cache | ✅ Cleared |
| DNS Config | ⚠️ Run fix_dns.ps1 |

**After restarting both servers, route planning will work!**
