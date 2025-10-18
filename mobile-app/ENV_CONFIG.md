# Environment Configuration Guide

## Overview

The Transit Companion mobile app uses environment variables to configure the backend API connection. This allows developers to easily switch between different backend servers without modifying the source code.

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your configuration:**
   ```bash
   # For Android Emulator (default)
   EXPO_PUBLIC_API_HOST=10.0.2.2
   
   # For iOS Simulator
   # EXPO_PUBLIC_API_HOST=localhost
   
   # For physical device on the same network
   # EXPO_PUBLIC_API_HOST=192.168.1.100
   ```

3. **Install dependencies** (if you haven't already):
   ```bash
   npm install
   ```

4. **Start the app:**
   ```bash
   npm start
   ```

## Environment Variables

### Required Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_API_HOST` | `10.0.2.2` | Backend API host address |
| `EXPO_PUBLIC_API_PORT` | `8000` | Backend API port |
| `EXPO_PUBLIC_API_PROTOCOL` | `http` | Protocol (http or https) |
| `EXPO_PUBLIC_WS_PROTOCOL` | `ws` | WebSocket protocol (ws or wss) |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXPO_PUBLIC_PRODUCTION_API_URL` | `https://your-production-domain.com` | Production API URL |

## Common Configurations

### Android Emulator
```env
EXPO_PUBLIC_API_HOST=10.0.2.2
EXPO_PUBLIC_API_PORT=8000
EXPO_PUBLIC_API_PROTOCOL=http
```

**Note:** `10.0.2.2` is a special IP address that points to your host machine's `localhost` from the Android emulator.

### iOS Simulator
```env
EXPO_PUBLIC_API_HOST=localhost
EXPO_PUBLIC_API_PORT=8000
EXPO_PUBLIC_API_PROTOCOL=http
```

### Physical Device (Same WiFi Network)
```env
# Replace with your computer's local IP address
EXPO_PUBLIC_API_HOST=192.168.1.100
EXPO_PUBLIC_API_PORT=8000
EXPO_PUBLIC_API_PROTOCOL=http
```

**How to find your local IP:**
- **macOS/Linux:** Run `ifconfig | grep inet` in terminal
- **Windows:** Run `ipconfig` in command prompt
- Look for your WiFi adapter's IPv4 address (usually starts with 192.168.x.x or 10.x.x.x)

### Expo Go on Physical Device
Same as physical device configuration above - use your computer's local network IP.

## File Structure

```
mobile-app/
├── .env                    # Your local configuration (git-ignored)
├── .env.example            # Template for developers
├── app.config.js           # Expo config that reads .env variables
└── src/
    └── services/
        └── api/
            └── config.ts   # API configuration using env variables
```

## Troubleshooting

### "Cannot connect to backend"

1. **Verify your backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check your `.env` configuration:**
   - For Android Emulator: Use `10.0.2.2`
   - For iOS Simulator: Use `localhost`
   - For physical device: Use your computer's local IP

3. **Ensure both devices are on the same network** (for physical device testing)

4. **Restart the Expo server** after changing `.env`:
   ```bash
   npm start -- --clear
   ```

### "Environment variables not updating"

- Clear Expo cache: `npm start -- --clear`
- Restart the app completely (close and reopen)
- Make sure you're using variables with the `EXPO_PUBLIC_` prefix

## Important Notes

- ⚠️ **Never commit your `.env` file** - it's already in `.gitignore`
- ✅ **Always update `.env.example`** when adding new environment variables
- 🔄 **Restart Expo** after modifying environment variables
- 📱 **Different configurations** may be needed for emulators vs physical devices

## Production Deployment

For production builds, set:
```env
EXPO_PUBLIC_PRODUCTION_API_URL=https://your-production-domain.com
```

The app automatically uses development URLs when `__DEV__` is true and production URL otherwise.
