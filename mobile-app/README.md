# 📱 Smart Transit Companion - Mobile App

**AI-Powered Transit Companion for Sri Lankan Transportation**

A next-generation React Native mobile application with AI-driven route planning, real-time updates, and community-driven data for Sri Lankan commuters.

## 🏆 **SLAIC 2025 Winner Features**

### ✅ **Competition Requirements Met**
- **🤖 AI Integration** - Multi-agent system visualization and real-time communication
- **🇱🇰 Sri Lankan Focus** - Local transport modes (Bus, Train, Tuk-tuk, Uber)
- **🌐 Multilingual Support** - English, Sinhala (සිංහල), Tamil (தமிழ்)
- **👥 Community Features** - Crowdsourced reporting and social engagement
- **📱 Mobile-First Design** - Native performance with offline capabilities
- **⚡ Real-time Features** - Live updates, push notifications, WebSocket integration

## 🚀 **Key Features**

### 🎯 **Smart Route Planning**
- **Multi-Agent AI System** - Watch 10 AI agents work together to find optimal routes
- **Real-time Optimization** - Dynamic route updates based on traffic and weather
- **Sri Lankan Context** - Local knowledge integration for authentic travel experience
- **Fare Optimization** - AI-powered cost minimization for budget-conscious travelers

### 🗺️ **Comprehensive Navigation**
- **Multiple Transport Modes** - Bus, Train, Tuk-tuk, Uber, Walking, Driving
- **Route History** - Save and access frequently used routes
- **Offline Support** - Cached routes work without internet connection
- **Quick Destinations** - One-tap access to popular Sri Lankan locations

### 🤖 **AI Chat Assistant**
- **RAG-Powered Chatbot** - Intelligent responses with Sri Lankan transit knowledge
- **Multilingual Support** - Chat in English, Sinhala, or Tamil
- **Context-Aware** - Understands your travel preferences and history
- **Real-time Help** - Instant answers to transport-related questions

### 👥 **Community Platform**
- **Report Disruptions** - Share traffic delays, road closures, and service issues
- **Fare Information** - Crowdsourced pricing for accurate cost estimation
- **Safety Reports** - Community-driven safety insights and alerts
- **Accessibility Data** - Inclusive information for differently-abled travelers

### ⚡ **Real-time Features**
- **Live Updates** - Instant notifications about route changes and delays
- **Push Notifications** - Smart alerts for relevant travel information
- **WebSocket Integration** - Real-time communication with backend services
- **Background Sync** - Automatic data updates when app is closed

## 🛠️ **Technical Architecture**

### **Frontend Technologies**
- **React Native 0.79.5** - Latest cross-platform framework
- **Expo SDK 53** - Comprehensive development platform
- **TypeScript** - Full type safety and developer experience
- **NativeWind** - Tailwind CSS for React Native styling
- **React Navigation 7** - Type-safe routing and navigation

### **State Management**
- **React Context API** - Global application state
- **Custom Hooks** - Reusable stateful logic
- **AsyncStorage** - Persistent local storage
- **Secure Store** - Encrypted credential storage

### **Real-time Communication**
- **WebSocket Service** - Live data synchronization
- **Push Notifications** - Expo Notifications integration
- **Background Tasks** - Continuous data updates
- **Offline Queue** - Sync actions when connection restored

### **UI/UX Features**
- **Responsive Design** - Optimized for all screen sizes
- **Dark/Light Themes** - User preference-based theming
- **Smooth Animations** - React Native Reanimated 3
- **Accessibility** - Screen reader and voice control support
- **Gesture Support** - Intuitive touch interactions

## 🚦 **Getting Started**

### **Prerequisites**
- Node.js 18+ and npm/yarn
- Expo CLI (`npm install -g @expo/cli`)
- iOS Simulator (Mac) or Android Emulator
- Expo Go app (for quick testing)

### **Installation**

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd mobile-app
   npm install
   ```

2. **Configure Environment**
   - Backend API will auto-configure based on platform
   - iOS Simulator: `http://localhost:8000`
   - Android Emulator: `http://10.0.2.2:8000`
   - Physical Device: Update IP in `src/services/api/config.ts`

3. **Start Development Server**
   ```bash
   npm start
   # or
   npx expo start
   ```

4. **Run on Platform**
   ```bash
   # iOS Simulator
   npm run ios
   
   # Android Emulator
   npm run android
   
   # Web Browser
   npm run web
   ```

### **Backend Connection**
Ensure the backend is running on `http://localhost:8000` before starting the mobile app. The app will automatically detect and connect to the backend services.

## 📱 **App Structure**

### **Navigation Flow**
```
App Entry → Authentication Check
├── Not Authenticated → (auth) stack
│   ├── Login Screen
│   └── Register Screen
├── New User → (onboarding) stack
│   ├── Welcome Screen
│   └── Preferences Setup
└── Authenticated → (main) stack
    └── (tabs) - Bottom Tab Navigation
        ├── Home - Route Planning
        ├── Routes - History & Saved Routes
        ├── Chat - AI Assistant
        ├── Community - Social Features
        └── Profile - User Settings
```

### **Key Components**
- **MultiAgentAnimation** - Visualizes AI agents working on route planning
- **SriLankanModeSelector** - Transport mode selection with local context
- **ThemeProvider** - Global theming system
- **LanguageProvider** - Internationalization support
- **AppProvider** - Central state management

## 🌍 **Internationalization**

### **Supported Languages**
- **English** - Primary language
- **Sinhala (සිංහල)** - Native script support
- **Tamil (தமிழ்)** - Full localization

### **Language Features**
- Dynamic language switching
- RTL text support for Tamil
- Cultural context in translations
- Local number and date formatting

## 📊 **Performance & Analytics**

### **Optimization Features**
- **Lazy Loading** - Components load on demand
- **Image Caching** - Expo Image with cache optimization
- **Bundle Splitting** - Reduced initial load time
- **Memory Management** - Efficient state cleanup

### **Analytics Integration**
- User behavior tracking
- Performance monitoring
- Crash reporting
- Usage statistics

## 🔐 **Security Features**

### **Authentication & Authorization**
- JWT token management with refresh
- Biometric authentication support
- Secure token storage with Expo SecureStore
- Automatic session management

### **Data Protection**
- API request encryption
- Local data encryption
- Secure communication with WebSocket
- Privacy-compliant data handling

## 🧪 **Testing & Quality**

### **Development Tools**
- ESLint for code quality
- TypeScript for type safety
- Expo development tools
- React Developer Tools

### **Testing Strategy**
```bash
# Lint code
npm run lint

# Type checking
npx tsc --noEmit

# Test on multiple devices
npx expo start
```

## 📦 **Build & Deployment**

### **Development Build**
```bash
# Create development build
npx eas build --platform all --profile development

# Install on device
npx eas install
```

### **Production Build**
```bash
# Build for app stores
npx eas build --platform all --profile production

# Submit to stores
npx eas submit
```

## 🤝 **Contributing**

### **Development Guidelines**
1. Follow TypeScript best practices
2. Use semantic commit messages
3. Test on both iOS and Android
4. Maintain accessibility standards
5. Follow React Native performance guidelines

### **Code Style**
- Use functional components with hooks
- Implement proper error boundaries
- Follow naming conventions
- Add comprehensive TypeScript types

## 📋 **System Requirements**

### **Minimum Requirements**
- iOS 13+ / Android 8+ (API level 26+)
- 2GB RAM, 1GB free storage
- Active internet connection for full features
- GPS capability for location services

### **Recommended Specifications**
- iOS 15+ / Android 11+
- 4GB RAM, 2GB free storage
- Stable Wi-Fi or 4G/5G connection
- Hardware biometric authentication

## 🔧 **Troubleshooting**

### **Common Issues**
1. **Backend Connection Failed**
   - Verify backend is running on correct port
   - Check network connectivity
   - Update IP address in config for physical devices

2. **Expo Build Issues**
   - Clear Expo cache: `npx expo r -c`
   - Update Expo CLI: `npm install -g @expo/cli@latest`
   - Check Expo service status

3. **Performance Issues**
   - Clear app cache and data
   - Restart development server
   - Close other running emulators/simulators

## 📚 **Documentation Links**

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Guides](https://reactnative.dev/docs/getting-started)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [NativeWind Documentation](https://www.nativewind.dev/)

## 🎯 **SLAIC 2025 Competition Features**

This mobile app demonstrates:
- **Advanced AI Integration** with multi-agent system visualization
- **Sri Lankan Cultural Context** with local transport modes and languages
- **Community-Driven Data** with crowdsourced reporting
- **Real-time Intelligence** with live updates and notifications
- **Professional Mobile Development** with modern React Native practices
- **Accessibility & Inclusion** supporting diverse user needs
- **Scalable Architecture** ready for production deployment

---

**🏆 Built for SLAIC 2025 - Sri Lanka AI Challenge**
**🇱🇰 Proudly Made in Sri Lanka**