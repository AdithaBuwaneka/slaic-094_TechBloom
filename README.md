# 🚀 Smart Transit Companion - SLAIC 2025

**AI-Powered Transit Companion for Sri Lankan Transportation**

**🇱🇰 Sri Lanka AI Challenge 2025 - Use Case 02: Transportation & Logistics**

A comprehensive, production-ready AI transportation platform featuring 10 specialized AI agents, real-time optimization, and community-driven data designed specifically for Sri Lankan commuters and travelers.

---

## 🎯 **Project Overview**

The **Smart Transit Companion** revolutionizes how Sri Lankans navigate their daily commute by combining cutting-edge AI technology with deep local knowledge. Our platform integrates multiple transportation modes (buses, trains, tuk-tuks, ride-sharing) with intelligent route planning, real-time disruption monitoring, and community-driven insights.

### **🏅 SLAIC 2025 Competition Entry**

**Requirements Addressed:**
- ✅ **10 AI Agents** (Required: 7) - Sophisticated multi-agent orchestration
- ✅ **Sri Lankan Focus** - Deep integration with local transport systems
- ✅ **Community Data** - Crowdsourced reporting and verification platform
- ✅ **Real-time Intelligence** - Live updates and predictive analytics
- ✅ **Multilingual Support** - English, Sinhala, Tamil with cultural context
- ✅ **Production Ready** - Enterprise-grade architecture and security

---

## 🏗️ **System Architecture**

![System Architecture](https://raw.githubusercontent.com/your-username/your-repo-name/main/System_Architecture.png)

> **System Architecture Overview**: Complete system showing Frontend Applications, Security Layer, FastAPI Backend, 10 AI Agents, Data Layer, Real-time Services, and Sri Lankan Transit API Integrations.

### **🤖 Multi-Agent AI Core**
```
User Request → LangGraph Orchestration → 10 Specialized AI Agents

1. 🔍 Input Processing Agent      → Validates & preprocesses requests
2. 🎯 Mode Router Agent          → Determines routing strategy  
3. 🛣️  Standard Route Agent       → Direct point-to-point routing
4. 🚌 Transit Aggregation Agent  → Multi-modal coordination
5. 💰 Fare Calculation Agent     → Real-time pricing analysis
6. 📊 Fare Optimization Agent    → Cost minimization (SLAIC 2025)
7. 👤 Preference Analysis Agent  → Personalization & learning
8. 🏙️  Local Knowledge Agent     → Sri Lankan context & insights
9. ⚠️  Disruption Monitor Agent   → Real-time alerts & predictions
10. ⚡ Route Optimization Agent  → Final recommendations
```

### **🏢 Platform Components**

#### **📱 Mobile Application**
- **React Native 0.79.5** + **Expo SDK 53**
- Cross-platform iOS/Android support
- Real-time multi-agent visualization
- Offline route caching
- Push notifications integration

#### **🖥️ Admin Dashboard**
- **Next.js 15.5.2** + **React 19**
- Real-time analytics and monitoring
- User management with advanced filtering
- AI agent system visualization
- Push notification broadcasting

#### **🚀 Backend API**
- **FastAPI** with async/await architecture
- **10 AI agents** orchestrated by LangGraph
- **MongoDB Atlas** with 17 collections
- **ChromaDB** vector database for RAG
- **Redis** caching and rate limiting

---

## 🌟 **Key Features**

### **🎯 AI-Powered Route Planning**
- **Multi-Agent Intelligence**: 10 specialized agents work together for optimal route discovery
- **Real-time Optimization**: Dynamic updates based on traffic, weather, and disruptions
- **Fare Optimization**: AI algorithms minimize travel costs across all transport modes
- **Preference Learning**: Adaptive recommendations based on user behavior patterns
- **Sri Lankan Context**: Local knowledge integration for culturally-aware suggestions

### **🇱🇰 Sri Lankan Transit Integration**
- **Sri Lanka Railways**: Real-time train schedules and delay notifications
- **NTC Bus Systems**: Government bus routes with live tracking
- **Private Operators**: Integration with major private bus services
- **Tuk-tuk Services**: Local three-wheeler pricing and availability
- **Ride-sharing**: Uber/PickMe integration with dynamic pricing

### **👥 Community-Driven Platform**
- **Crowdsourced Reports**: User-submitted traffic, delays, and safety information
- **Real-time Verification**: AI-powered validation of community contributions
- **Accessibility Data**: Information for differently-abled travelers
- **Fare Sharing**: Community-verified pricing across all transport modes
- **Safety Insights**: Crowd-sourced security and safety recommendations

### **🤖 RAG Chatbot Assistant**
- **ChromaDB Vector Database**: Semantic search of Sri Lankan transit knowledge
- **Google Gemini 2.0 Flash**: Advanced natural language processing
- **Multilingual Support**: Conversations in English, Sinhala (සිංහල), Tamil (தமிழ்)
- **Context Retention**: Remembers user preferences and conversation history
- **Live Integration**: Real-time data from traffic and transit systems

### **⚡ Real-time Intelligence**
- **Live Updates**: Instant notifications about route changes and delays
- **Disruption Monitoring**: AI-powered prediction and alert system
- **Location Tracking**: Real-time journey following with ETA updates
- **Weather Integration**: Weather-aware route planning and suggestions
- **Background Sync**: Continuous data updates for optimal performance

---

## 📁 **Project Structure**

```
Ai_Challenge/
├── 📱 mobile-app/              # React Native + Expo mobile application
│   ├── app/                    # File-based routing with Expo Router
│   ├── src/                    # Source code and services
│   ├── components/             # Reusable UI components
│   └── README.md              # Mobile app documentation
│
├── 🖥️ admin-dashboard/         # Next.js admin dashboard
│   ├── src/app/               # App Router pages and layouts
│   ├── src/components/        # Dashboard UI components
│   ├── src/lib/               # API integration and utilities
│   └── README.md              # Dashboard documentation
│
├── 🚀 backend/                 # FastAPI backend with AI agents
│   ├── app/                   # Application code
│   │   ├── api/v1/           # API endpoints
│   │   ├── services/         # Business logic and AI agents
│   │   ├── models/           # Data models and schemas
│   │   ├── chatbot/          # RAG system and vector DB
│   │   └── core/             # Configuration and middleware
│   ├── requirements.txt       # Python dependencies
│   └── README.md             # Backend documentation
│
├── 📊 System_Architecture.png  # System architecture diagram
└── 📖 README.md               # This main project documentation
```

---

## 🚦 **Quick Start Guide**

### **Prerequisites**
- **Node.js 18+** with npm/yarn
- **Python 3.11+** with pip
- **MongoDB** (local or Atlas)
- **Redis** (optional, for enhanced caching)
- **Google Cloud API Keys** (Maps, Gemini)

### **🚀 1. Backend Setup**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configure API keys in .env file
python create_admin.py
python run.py
# Backend runs on http://localhost:8000
```

### **🖥️ 2. Admin Dashboard Setup**
```bash
cd admin-dashboard
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev
# Dashboard runs on http://localhost:3000
# Login: admin@example.com / admin123456
```

### **📱 3. Mobile App Setup**
```bash
cd mobile-app
npm install
npx expo start
# Follow Expo instructions to run on device/simulator
```

### **🎯 4. Access the System**
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000
- **Mobile App**: Through Expo Go or device build

---

## 🛠️ **Technology Stack**

### **🎨 Frontend Technologies**
- **Mobile**: React Native 0.79.5, Expo SDK 53, TypeScript, NativeWind
- **Dashboard**: Next.js 15.5.2, React 19, TypeScript, Tailwind CSS
- **UI Libraries**: Lucide React, Recharts, React Native Reanimated

### **⚙️ Backend Technologies**
- **Framework**: FastAPI (Python 3.11+) with async/await
- **AI Orchestration**: LangGraph for multi-agent workflow management
- **LLM Integration**: Google Gemini 2.0 Flash, Groq, Langfuse
- **Databases**: MongoDB Atlas (17 collections), ChromaDB (vector), Redis
- **Authentication**: JWT with bcrypt, role-based access control

### **🌐 External Integrations**
- **Google APIs**: Maps, Geocoding, Places, Generative AI
- **Sri Lankan APIs**: Railways, NTC Bus Systems, Private Operators
- **Weather**: OpenWeather API with local station data
- **Search**: Serper API for real-time information retrieval

---

## 🎯 **Core AI Capabilities**

### **🤖 Multi-Agent System (10 Agents)**

1. **Input Processing Agent**
   - Validates and normalizes user input
   - Extracts location entities and travel preferences
   - Handles multilingual input processing

2. **Mode Router Agent**
   - Determines single vs multi-modal routing strategy
   - Analyzes travel distance and time constraints
   - Selects optimal agent execution path

3. **Standard Route Agent**
   - Handles direct point-to-point routing
   - Integrates with Google Maps API
   - Provides driving, walking, cycling directions

4. **Transit Route Aggregation Agent**
   - Coordinates multi-modal transport options
   - Integrates bus, train, tuk-tuk, and ride-sharing
   - Optimizes transfer connections and timings

5. **Fare Calculation Agent**
   - Real-time pricing from multiple sources
   - Dynamic fare estimation for all transport modes
   - Currency conversion and price comparison

6. **Fare Optimization Agent** *(SLAIC 2025 Feature)*
   - AI-powered cost minimization algorithms
   - Identifies cheapest route combinations
   - Considers travel time vs cost trade-offs

7. **User Preference Analysis Agent**
   - Learns from user behavior patterns
   - Personalizes recommendations
   - Adapts to accessibility requirements

8. **Local Knowledge Agent**
   - Sri Lankan cultural and geographical context
   - Local traffic patterns and peak hours
   - Cultural considerations for route suggestions

9. **Disruption Monitoring Agent**
   - Real-time traffic and service disruption analysis
   - Predictive analytics for potential delays
   - Alternative route recommendations

10. **Route Optimization Agent**
    - Final route selection and ranking
    - Multi-criteria optimization (time, cost, comfort)
    - Real-time adjustment based on current conditions

### **🧠 RAG Chatbot System**
- **Knowledge Base**: 50+ documents about Sri Lankan transportation
- **Vector Search**: Semantic similarity matching with ChromaDB
- **Context Awareness**: Conversation history and user preferences
- **Multilingual**: Natural conversations in English, Sinhala, Tamil
- **Live Integration**: Real-time data fusion with chat responses

---

## 📊 **Analytics & Monitoring**

### **📈 Business Intelligence**
- **User Growth**: Registration trends and retention analysis
- **Travel Patterns**: Popular routes and transport mode preferences
- **Community Engagement**: Report submission and verification metrics
- **Cost Savings**: Aggregate fare optimization impact
- **Performance Metrics**: Agent execution times and success rates

### **🔧 System Monitoring**
- **Real-time Dashboards**: Live system health and performance
- **API Monitoring**: Response times, error rates, and throughput
- **AI Agent Performance**: Individual agent success rates and optimization
- **Database Performance**: Query optimization and connection monitoring
- **User Experience**: Mobile app performance and crash reporting

---

## 🔐 **Security & Privacy**

### **🛡️ Security Features**
- **JWT Authentication**: Access/refresh token pattern with automatic renewal
- **Role-based Access**: User, admin, and super-admin permission levels
- **Rate Limiting**: Redis-based sliding window protection
- **Input Validation**: Comprehensive request validation with Pydantic
- **API Security**: CORS, request size limits, and XSS prevention

### **🔒 Data Protection**
- **Encryption**: Data encrypted at rest and in transit
- **Privacy Compliance**: GDPR-compliant data handling
- **Secure Storage**: Sensitive data encryption with proper key management
- **Audit Logging**: Comprehensive access and modification tracking
- **Anonymous Analytics**: User behavior tracking without personal identification

---

## 🌍 **Sri Lankan Integration**

### **🚌 Local Transport Systems**
- **Sri Lanka Railways**: Real-time schedules, delays, fare information
- **National Transport Commission**: Government bus routes and timings
- **Private Bus Operators**: Major private transport companies
- **Three-wheeler Services**: Local tuk-tuk pricing and availability
- **Ride-sharing**: Uber, PickMe, and local ride-sharing integration

### **🗺️ Geographic & Cultural Context**
- **Major Cities**: Colombo, Kandy, Galle, Jaffna, Anuradhapura
- **Popular Destinations**: Tourist spots, business districts, universities
- **Cultural Considerations**: Religious events, local festivals, peak hours
- **Accessibility**: Information for differently-abled travelers
- **Language Support**: Native script support for Sinhala and Tamil

### **👥 Community Features**
- **Crowdsourced Data**: User-contributed traffic and delay information
- **Local Knowledge**: Community-verified route tips and alternatives
- **Safety Reports**: Crowd-sourced security and safety insights
- **Fare Verification**: Community-validated pricing information
- **Social Features**: User ratings, reviews, and recommendations

---

## 🏆 **SLAIC 2025 Competition Features**

### **✅ Technical Implementation**
- **Advanced AI**: 10-agent system addressing 7-agent requirement
- **Production Ready**: Enterprise-grade architecture and deployment
- **Real-time Intelligence**: Live data processing and decision making
- **Scalable Design**: Horizontal scaling and cloud-native architecture
- **Security First**: Comprehensive security and privacy implementation

### **🇱🇰 Sri Lankan Impact**
- **Local Integration**: Deep integration with Sri Lankan transport systems
- **Cultural Awareness**: Language support and cultural considerations
- **Community Building**: Platform for collective intelligence and sharing
- **Economic Benefit**: Cost optimization saving money for commuters
- **Accessibility**: Inclusive design for all Sri Lankan travelers

### **🚀 Innovation & Technology**
- **Multi-Agent AI**: Sophisticated orchestration with LangGraph
- **RAG System**: Advanced retrieval-augmented generation
- **Real-time Processing**: Live data integration and decision making
- **Mobile Excellence**: Cross-platform native mobile experience
- **Admin Intelligence**: Comprehensive monitoring and analytics

---

## 📱 **How to Use the App**

The **Smart Transit Companion** is your AI-powered travel assistant designed specifically for Sri Lankan transportation. To get started, simply download the app and create your account with basic information like name, email, and preferred language (English, Sinhala, or Tamil). Once logged in, use the **Home tab** to plan your journey by entering your starting point and destination - the app supports all major Sri Lankan locations from Colombo Fort to Jaffna, and even recognizes local landmarks. Select your preferred travel mode including buses, trains, tuk-tuks, or driving, and watch as our **10 specialized AI agents** work together in real-time to find the best routes for you.

Navigate to the **Routes tab** to view your journey history and save frequently used routes for quick access. The **Chat tab** features an intelligent RAG-powered assistant that can answer questions about Sri Lankan transportation, provide real-time updates, and offer travel tips in your preferred language. Use the **Community tab** to report traffic delays, share fare information, or contribute accessibility details to help fellow travelers. The **Profile tab** allows you to customize your travel preferences, view your trip statistics including money saved and carbon footprint reduced, and manage notification settings.

The app excels in providing **real-time updates** through push notifications about route disruptions, weather alerts, and traffic changes. Its **multi-agent AI system** continuously learns from your travel patterns to provide increasingly personalized recommendations, while the **community-driven data** ensures you have the most current information about fares, delays, and route conditions.

---

## 🤝 **Contributing**

We welcome contributions to improve the Smart Transit Companion platform!

### **Development Setup**
1. Fork the repository
2. Set up all three components (backend, dashboard, mobile)
3. Make your changes following our coding standards
4. Submit a pull request with detailed description

### **Contribution Areas**
- **AI Agent Optimization**: Improve agent performance and accuracy
- **Sri Lankan Data**: Add more local transport data sources
- **UI/UX Improvements**: Enhance user experience and accessibility
- **Performance**: Optimize system performance and scalability
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve documentation and guides

---

## 📞 **Support & Contact**

### **Competition Contact**
- **Event**: Sri Lanka AI Challenge 2025
- **Use Case**: 02 - Transportation & Logistics
- **Team**: Smart Transit Companion Development Team

### **Documentation**
- **Backend API**: [Backend Documentation](./backend/README.md)
- **Mobile App**: [Mobile App Documentation](./mobile-app/README.md)
- **Admin Dashboard**: [Dashboard Documentation](./admin-dashboard/README.md)
- **API Reference**: http://localhost:8000/docs (when running)

### **Resources**
- **Live Demo**: Available upon request
- **Technical Presentation**: Comprehensive system walkthrough
- **Performance Metrics**: Real-time system analytics
- **User Testing**: Community feedback and usage statistics

---

## 🎯 **Future Roadmap**

### **Phase 2: Enhanced AI**
- **Predictive Analytics**: Advanced traffic and disruption prediction
- **Voice Interface**: Voice-controlled navigation and assistance
- **Computer Vision**: Real-time bus/train recognition and tracking
- **Autonomous Integration**: Self-driving vehicle route coordination

### **Phase 3: Platform Expansion**
- **Regional Expansion**: Extend to other South Asian countries
- **Commercial Integration**: B2B solutions for transport companies
- **Government Partnership**: Official integration with transport authorities
- **Sustainability**: Carbon footprint tracking and eco-friendly routing

---

## 🏆 **Competition Details**

**SLAIC 2025 Competition Entry**
- **Category**: Use Case 02 - Transportation & Logistics
- **Technology Stack**: Multi-Agent AI, FastAPI, React Native, Next.js
- **Features**: 10 AI Agents, Real-time Processing, Community Platform
- **Focus**: Sri Lankan Transportation Solutions

---

**🇱🇰 Built with Pride in Sri Lanka**  
**🏆 SLAIC 2025 - Transportation Innovation Excellence**  
**🚀 World-Class AI Technology for Local Impact**