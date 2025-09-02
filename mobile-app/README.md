# Smart Transit Companion - Mobile App 🚌🚆📱

[![React Native](https://img.shields.io/badge/React%20Native-0.74.5-blue.svg)](https://reactnative.dev/)
[![Expo](https://img.shields.io/badge/Expo-51.0.28-black.svg)](https://expo.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3.3-blue.svg)](https://www.typescriptlang.org/)
[![NativeWind](https://img.shields.io/badge/NativeWind-4.0.1-06B6D4.svg)](https://www.nativewind.dev/)

## 🎯 Project Overview

The **Smart Transit Companion** is an AI-driven mobile application designed for the Sri Lanka AI Challenge 2025. It transforms fragmented public transport information into a unified, real-time, and personalized travel experience for Sri Lankan commuters.

### 🌟 Key Features

- **🤖 AI-Powered Journey Planning**: Natural language queries for intelligent route suggestions
- **🚌 Multi-Modal Transportation**: Seamless integration of buses, trains, and walking routes
- **🌍 Real-Time Updates**: Live disruption alerts and dynamic re-routing
- **👤 Personalized Experience**: User preferences and accessibility needs
- **🌐 Multi-Language Support**: Sinhala, Tamil, and English interfaces
- **♿ Accessibility First**: Voice assistance and visual adaptations
- **📍 Location Intelligence**: GPS-based smart recommendations
- **💰 Fare Optimization**: Cost-effective travel combinations

## 🏗️ Architecture

This mobile app connects to a FastAPI backend with specialized AI agents:

```
Mobile App (React Native + Expo)
     ↓
FastAPI Backend + AI Agents
     ↓
MongoDB Atlas Database
```

### 🔧 Tech Stack

- **Framework**: React Native with Expo SDK 51
- **Language**: TypeScript
- **Styling**: NativeWind (Tailwind CSS for React Native)
- **Routing**: Expo Router (file-based routing)
- **State Management**: React Context + useReducer
- **Authentication**: JWT tokens with secure storage
- **Maps**: Expo Location + Maps integration
- **Internationalization**: expo-localization + i18next
- **Storage**: AsyncStorage for offline data
- **Notifications**: Expo Notifications

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Expo CLI: `npm install -g @expo/cli`
- Android Studio (for Android development) or Xcode (for iOS development)

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start the development server**
   ```bash
   npx expo start
   ```

3. **Run on your device**
   - Scan QR code with Expo Go app (Android/iOS)
   - Press `a` for Android emulator
   - Press `i` for iOS simulator

## 📱 App Structure

```
mobile-app/
├── app/                    # File-based routing
│   ├── (auth)/            # Authentication screens
│   │   ├── login.tsx      # User login
│   │   ├── register.tsx   # User registration
│   │   └── welcome.tsx    # Welcome screen
│   ├── (tabs)/            # Main app tabs
│   │   ├── index.tsx      # Home/Journey Planning
│   │   ├── history.tsx    # Journey History
│   │   ├── favorites.tsx  # Saved Routes
│   │   └── profile.tsx    # User Profile
│   ├── _layout.tsx        # Root layout
│   └── +not-found.tsx     # 404 page
├── components/            # Reusable UI components
├── constants/             # App configuration
├── context/              # Global state management
├── i18n/                 # Multi-language support
├── services/             # API and external services
└── types/                # TypeScript type definitions
```

## 🔌 Backend Integration

The mobile app connects to the FastAPI backend running on `http://localhost:8000`:

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login  
- `GET /api/v1/auth/me` - Get user profile
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/refresh-token` - Refresh JWT tokens

### Journey Planning Endpoints
- `POST /api/v1/plan-journey/agentic` - AI-powered journey planning
- `POST /api/v1/plan-journey/direct` - Direct route planning
- `GET /api/v1/rn/routes/popular` - Popular routes
- `GET /api/v1/disruptions/active` - Active disruptions

### User Data Endpoints
- `POST /api/v1/auth/update-location` - Update user location
- `PUT /api/v1/auth/me` - Update user profile

## 🌐 Multi-Language Support

Supports three languages:
- **English** (default)
- **Sinhala** (සිංහල)
- **Tamil** (தமிழ்)

Language files located in `/i18n/locales/`:
```
i18n/
├── locales/
│   ├── en.json    # English translations
│   ├── si.json    # Sinhala translations
│   └── ta.json    # Tamil translations
└── index.ts       # i18n configuration
```

## 🔐 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Biometric Authentication**: Fingerprint/Face ID login
- **Secure Storage**: Encrypted token storage
- **API Key Protection**: Environment-based configuration
- **Input Validation**: Form validation and sanitization

## 📊 State Management

Global app state managed through React Context:

```typescript
// App Context provides:
interface AppContextType {
  user: User | null;
  isAuthenticated: boolean;
  currentLocation: Location | null;
  language: string;
  theme: 'light' | 'dark';
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  getCurrentLocation: () => Promise<void>;
  changeLanguage: (language: string) => Promise<void>;
}
```

## 🔧 Development Scripts

```bash
# Start development server
npm start

# Start with cleared cache  
npm run start:clear

# Run TypeScript type checking
npm run type-check

# Run linting
npm run lint

# Build for production
npm run build

# Run tests
npm test
```

## 📱 Platform Support

- **iOS**: iOS 13.4+ 
- **Android**: Android 6.0+ (API 23+)
- **Web**: Modern browsers (PWA ready)

## 🌟 Key Screens

### 1. Authentication Flow
- **Welcome Screen**: App introduction and language selection
- **Login/Register**: Secure user authentication
- **Biometric Setup**: Optional biometric authentication

### 2. Main Application
- **Home**: Journey planning with AI-powered search
- **Map View**: Interactive route visualization  
- **History**: Past journey records
- **Favorites**: Saved routes and locations
- **Profile**: User settings and preferences

### 3. Journey Planning
- **Natural Language Input**: "I need to go from Colombo to Kandy"
- **Route Options**: Multiple transport mode combinations
- **Real-Time Updates**: Live departure times and delays
- **Accessibility Options**: Wheelchair accessible routes

## 🚨 Error Handling

- **Network Errors**: Offline mode with cached data
- **Authentication Errors**: Automatic token refresh
- **Location Errors**: Fallback to manual location entry
- **API Errors**: User-friendly error messages

## 🔄 Offline Support

- **Cached Routes**: Recently viewed routes available offline
- **Offline Maps**: Basic map functionality without internet
- **Queue Sync**: Sync data when connection restored
- **Offline Indicators**: Clear offline/online status

## 🧪 Testing

```bash
# Run unit tests
npm test

# Run integration tests  
npm run test:integration

# Run end-to-end tests
npm run test:e2e
```

## 📦 Build & Deployment

### Development Build
```bash
# Create development build
npx expo build:android --type apk
npx expo build:ios
```

### Production Build
```bash
# Create production build
eas build --platform android
eas build --platform ios
```

## 🌈 Customization

### Themes
Update theme configuration in `constants/Colors.ts`

### Styling
NativeWind classes are used throughout. Customize in component files:
```tsx
<View className="bg-blue-500 p-4 rounded-lg">
  <Text className="text-white font-bold">Hello World</Text>
</View>
```

### API Configuration  
Update backend URLs in `constants/Config.ts`:
```typescript
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8000',
  ENDPOINTS: {
    // ... endpoint definitions
  }
};
```

## 🤝 Contributing

This mobile app is part of the Sri Lanka AI Challenge 2025 submission. The app addresses key transportation challenges in Sri Lanka through AI-powered solutions.

## 📄 License

This project is developed for the Sri Lanka AI Challenge 2025.

## 🎯 Challenge Alignment

This mobile application directly addresses the Sri Lanka AI Challenge 2025 requirements:

✅ **Multi-Agent AI Integration**: Connects to 7 specialized AI agents  
✅ **Real-Time Data**: Live transport updates and disruption management  
✅ **Multi-Modal Planning**: Bus, train, and walking route combinations  
✅ **Personalization**: User preferences and accessibility needs  
✅ **Inclusivity**: Multi-language support and accessibility features  
✅ **Sri Lankan Context**: Local transport modes and cultural considerations  

## 📞 Support

For technical questions or issues related to this Sri Lanka AI Challenge 2025 submission, please refer to the project documentation or contact the development team.

---

**Smart Transit Companion** - Transforming public transportation in Sri Lanka through AI-driven innovation 🇱🇰✨