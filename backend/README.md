# 🚀 Transit Companion Backend - 100% Complete

**AI-Powered Transit Companion Backend for Sri Lankan Transportation**

A production-ready FastAPI backend with multi-agent AI system, real-time features, mobile app support, and admin dashboard.

## 🏆 **SLAIC 2025 Compliant** - Sri Lanka AI Challenge 2025 Use Case 02

### ✅ **Competition Requirements Met**
- **🎯 10 AI Agents** (Required: 7) - Multi-agent travel planning system
- **🇱🇰 Sri Lankan Transit Modes** - Train, Bus, Tuk-tuk, Uber support
- **📊 Sri Lankan Data Sources** - NTC buses, Sri Lanka Railways, GTFS integration
- **🌐 Multilingual Support** - English, Sinhala (සිංහල), Tamil (தமිழ්)
- **👥 Community Data Reporting** - Crowdsourced traffic, delays, fares, accessibility
- **💰 Fare Optimization Agent** - AI-powered cost minimization
- **📱 Real-time Disruption Monitoring** - Intelligent disruption analysis

## 🚀 **Features Overview**

### 🎯 **Core AI System**
- **Multi-Agent Travel Planning** - 10 specialized AI agents with LangGraph orchestration
- **RAG Chatbot System** - ChromaDB vector database with Google Gemini 2.0 Flash
- **Intelligent Disruption Analysis** - AI-powered monitoring and prediction
- **User Preference Learning** - Adaptive route recommendations
- **Fare Optimization** - Cost-minimization algorithms

### 📱 **Mobile App Ready**
- **Push Notifications** - Expo/FCM integration for real-time alerts
- **Device Registration** - Multi-device support with token management
- **Offline Data Support** - Route caching for offline usage
- **Location Services** - Real-time location tracking and updates
- **Mobile Configuration** - Feature flags and app settings API

### 👨‍💼 **Admin Dashboard**
- **User Management** - Complete CRUD operations with pagination
- **Analytics Dashboard** - User growth, travel mode preferences, API usage
- **System Health Monitoring** - Real-time service status and logs
- **Broadcast Notifications** - Push notifications to all users
- **Community Report Management** - Review and manage user reports

### 🔐 **Enterprise Security**
- **JWT Authentication** - Access/refresh token pattern with bcrypt
- **Role-based Access Control** - User/admin permissions
- **Rate Limiting** - Redis-based sliding window rate limiting
- **Centralized Error Handling** - Structured error responses
- **Input Validation** - Comprehensive request validation

### ⚡ **Real-time Features**
- **WebSocket Support** - Live disruption alerts and location tracking
- **Real-time Notifications** - Instant push notifications
- **Live Route Tracking** - Real-time route following and feedback
- **Background Tasks** - Periodic system updates and monitoring

### 🗄️ **Database & Storage**
- **MongoDB Atlas** - Cloud database with Motor async driver
- **17 Collections** - Comprehensive data modeling
- **Vector Database** - ChromaDB for AI chatbot
- **Redis Cache** - Rate limiting and session management

## 📁 **Project Structure**

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py                    # Main API routing
│   │   └── v1/
│   │       ├── travel_routes.py         # Multi-agent travel planning
│   │       ├── auth_routes.py           # Authentication & registration
│   │       ├── admin_routes.py          # Admin dashboard APIs
│   │       ├── mobile_routes.py         # Mobile app endpoints
│   │       ├── websocket_routes.py      # Real-time WebSocket APIs
│   │       ├── user_preferences_routes.py # User preference management
│   │       ├── chatbot_routes.py        # RAG chatbot endpoints
│   │       ├── weather_routes.py        # Weather integration
│   │       ├── sri_lanka_routes.py      # Sri Lankan transit data
│   │       └── community_routes.py      # Community reporting
│   ├── core/
│   │   ├── config.py                    # Environment configuration
│   │   ├── database.py                  # MongoDB connection
│   │   ├── auth_middleware.py           # JWT authentication
│   │   └── exceptions.py                # Custom exception handling
│   ├── middleware/
│   │   ├── error_handler.py             # Centralized error handling
│   │   └── rate_limiter.py              # Rate limiting middleware
│   ├── services/
│   │   ├── workflow.py                  # Multi-agent orchestration
│   │   ├── agent_nodes.py               # AI agent implementations
│   │   ├── auth_service.py              # Authentication service
│   │   ├── push_notification_service.py # Push notifications
│   │   ├── intelligent_disruption_service.py # AI disruption analysis
│   │   ├── llm_summarizer.py            # LLM summarization
│   │   ├── tool_functions.py            # LangChain tools
│   │   ├── google_maps_service.py       # Google Maps integration
│   │   ├── weather_service.py           # Weather API service
│   │   ├── community_service.py         # Community data management
│   │   ├── sri_lanka_transit_service.py # Sri Lankan transit data
│   │   ├── multilingual_service.py      # Translation services
│   │   ├── cache_manager.py             # Response caching
│   │   └── langfuse_service.py          # LLM observability
│   ├── models/
│   │   ├── travel_schema.py             # Travel planning models
│   │   ├── path.py                      # Route models
│   │   ├── user_preferences.py          # User preference models
│   │   ├── transit_data.py              # Transit data models
│   │   └── enhanced_route.py            # Enhanced route models
│   ├── chatbot/
│   │   ├── chatbot.py                   # RAG implementation
│   │   ├── transit_app_guide.txt        # Knowledge base
│   │   └── db/                          # ChromaDB storage
│   └── main.py                          # FastAPI application
├── requirements.txt                     # Python dependencies
├── .env.example                         # Environment variables template
└── README.md                            # This file
```

## 🚀 **Quick Start**

### 1. **Environment Setup**

```bash
# Clone repository
git clone <repository-url>
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Environment Configuration**

Create `.env` file from template:

```bash
cp .env.example .env
```

Configure required environment variables:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=transit_companion_db

# Security
SECRET_KEY=your-super-secret-jwt-key-here

# API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
GOOGLE_GEMINI_API_KEY=your-gemini-api-key
OPENWEATHER_API_KEY=your-openweather-api-key
SERPER_API_KEY=your-serper-api-key  # Optional
LANGCHAIN_API_KEY=your-langchain-api-key  # Optional

# LangFuse (Optional)
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# CORS
BACKEND_CORS_ORIGINS=["*"]
```

### 3. **Database Setup**

Ensure MongoDB is running:

```bash
# Local MongoDB
mongod

# Or use MongoDB Atlas cloud connection
# Update MONGODB_URL in .env with your Atlas connection string
```

### 4. **Start Application**

```bash
# Development mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 5. **Verify Installation**

Visit the following URLs to confirm everything is working:

- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **Database Status**: http://localhost:8000/api/v1/db-connection

## 📚 **API Documentation**

### 🔐 **Authentication Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/register` | User registration | ❌ |
| `POST` | `/api/v1/auth/login` | User login | ❌ |
| `POST` | `/api/v1/auth/refresh` | Token refresh | ❌ |
| `POST` | `/api/v1/auth/setup-preferences` | Setup initial preferences | ✅ |
| `GET` | `/api/v1/auth/onboarding-status` | Check onboarding status | ✅ |
| `GET` | `/api/v1/auth/profile` | Get user profile | ✅ |
| `PUT` | `/api/v1/auth/profile` | Update user profile | ✅ |
| `POST` | `/api/v1/auth/change-password` | Change password | ✅ |
| `POST` | `/api/v1/auth/logout` | User logout | ✅ |
| `GET` | `/api/v1/auth/verify-token` | Verify token validity | ✅ |

### 🤖 **AI Travel Planning**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/travel/plan-route` | **Main AI route planning** | ✅ |
| `GET` | `/api/v1/travel/user-preferences/{user_id}` | Get user preferences | ✅ |
| `POST` | `/api/v1/travel/report-disruption` | Report disruptions | ✅ |
| `GET` | `/api/v1/travel/active-disruptions` | Get current disruptions | ✅ |

### 📱 **Mobile App Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/mobile/register-device` | Register device for push notifications | ✅ |
| `DELETE` | `/api/v1/mobile/unregister-device` | Unregister device | ✅ |
| `POST` | `/api/v1/mobile/send-test-notification` | Send test notification | ✅ |
| `GET` | `/api/v1/mobile/notifications` | Get notification history | ✅ |
| `PUT` | `/api/v1/mobile/notifications/{id}/read` | Mark notification as read | ✅ |
| `POST` | `/api/v1/mobile/update-location` | Update user location | ✅ |
| `GET` | `/api/v1/mobile/app-config` | Get mobile app configuration | ❌ |
| `POST` | `/api/v1/mobile/offline-data` | Prepare offline data | ✅ |
| `GET` | `/api/v1/mobile/health` | Mobile health check | ❌ |
| `GET` | `/api/v1/mobile/user-devices` | Get user's registered devices | ✅ |

### 👨‍💼 **Admin Dashboard**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/admin/dashboard` | Admin dashboard overview | 👑 Admin |
| `GET` | `/api/v1/admin/users` | Get all users (paginated) | 👑 Admin |
| `GET` | `/api/v1/admin/users/{user_id}` | Get user details | 👑 Admin |
| `PUT` | `/api/v1/admin/users/{user_id}/status` | Update user status | 👑 Admin |
| `DELETE` | `/api/v1/admin/users/{user_id}` | Delete user | 👑 Admin |
| `POST` | `/api/v1/admin/create-admin` | Create admin user | 👑 Admin |
| `GET` | `/api/v1/admin/analytics/user-growth` | User growth analytics | 👑 Admin |
| `GET` | `/api/v1/admin/analytics/travel-modes` | Travel mode analytics | 👑 Admin |
| `GET` | `/api/v1/admin/analytics/api-usage` | API usage analytics | 👑 Admin |
| `GET` | `/api/v1/admin/system-health` | System health status | 👑 Admin |
| `POST` | `/api/v1/admin/notifications/broadcast` | Send broadcast notification | 👑 Admin |
| `GET` | `/api/v1/admin/logs/recent` | Get recent system logs | 👑 Admin |
| `GET` | `/api/v1/admin/community/reports` | Get community reports | 👑 Admin |

### 🌐 **Real-time WebSocket**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `WS` | `/api/v1/ws/realtime?token={jwt}` | WebSocket connection | ✅ |
| `GET` | `/api/v1/ws/realtime/stats` | WebSocket statistics | ❌ |

### 🇱🇰 **Sri Lankan Transit Data**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/sri-lanka/railways/realtime` | Real-time train data | ❌ |
| `GET` | `/api/v1/sri-lanka/bus/timetables` | NTC bus schedules | ❌ |
| `GET` | `/api/v1/sri-lanka/bus/route-maps` | Bus route mapping | ❌ |
| `GET` | `/api/v1/sri-lanka/bus/fares` | Fare information | ❌ |
| `GET` | `/api/v1/sri-lanka/gtfs` | GTFS data | ❌ |

### 👥 **Community Reporting**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/community/traffic` | Report traffic conditions | ✅ |
| `POST` | `/api/v1/community/delays` | Report transit delays | ✅ |
| `POST` | `/api/v1/community/fares` | Report fare updates | ✅ |
| `POST` | `/api/v1/community/accessibility` | Report accessibility status | ✅ |

### 🤖 **Chatbot & AI**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/chatbot/ask` | RAG-powered Q&A | ❌ |
| `GET` | `/api/v1/chatbot/health` | Chatbot health check | ❌ |

### 🌤️ **Weather Integration**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/weather/current/{city}` | Current weather | ❌ |
| `GET` | `/api/v1/weather/forecast/{city}` | Weather forecast | ❌ |
| `GET` | `/api/v1/weather/travel-advice/{city}` | AI travel advice | ❌ |

### 🔧 **System Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API information | ❌ |
| `GET` | `/api/v1/health` | Health check | ❌ |
| `GET` | `/api/v1/db-connection` | Database status | ❌ |

## 🏗️ **Multi-Agent System Architecture**

### **10 AI Agents (LangGraph Workflow)**

1. **Input Processing Agent** - Validates and processes user input
2. **Mode Router Agent** - Routes requests based on travel mode
3. **Standard Route Agent** - Handles driving, two_wheeler, uber, tuk-tuk
4. **Transit Route Aggregation Agent** - Manages public transit routing
5. **Fare Calculation Agent** - Calculates step-by-step fares
6. **Fare Optimization Agent** ⭐ **SLAIC 2025** - Finds lowest-cost combinations
7. **User Preference Analysis Agent** - Applies user preferences to routes
8. **Local Knowledge Agent** - Gathers contextual information via web search
9. **Disruption Monitoring Agent** - Uses Gemini 2.0 Flash for intelligent analysis
10. **Route Optimization Agent** - Final route ranking and recommendations

### **Workflow Execution**

```
START → input_processing → mode_router → 
[standard_route OR transit_route_aggregation] → 
fare_calculation → fare_optimization → 
user_preference_analysis → local_knowledge_agent → 
route_optimization → disruption_monitoring → 
response_compilation → END
```

## 📊 **Database Schema**

### **17 MongoDB Collections**

#### **Core Collections**
- `users` - User accounts and profiles
- `transit_routes` - Route information and metadata
- `transit_fares` - Fare database with step-by-step pricing
- `transit_disruptions` - Disruption reports and status

#### **User Management**
- `user_preferences` - Travel preferences and learning data
- `user_history` - User interaction history
- `route_selections` - Route selection analytics
- `user_locations` - Real-time location data
- `device_tokens` - Push notification device registration

#### **Mobile & Notifications**
- `notifications` - Notification history and status
- `active_routes` - Currently tracked routes
- `route_feedback` - Real-time route feedback

#### **Community Data**
- `community_traffic_reports` - Crowdsourced traffic data
- `community_delay_reports` - Transit delay reports
- `community_fare_reports` - Fare update submissions
- `community_accessibility_reports` - Accessibility status

#### **System Collections**
- `travel_requests` - API request logging
- `error_logs` - Error tracking and debugging

## 🔐 **Security Features**

### **Authentication**
- **JWT Tokens** - Access (24h) and refresh (7d) token pattern
- **Password Security** - bcrypt hashing with salt
- **Role-based Access** - User and admin role separation
- **Token Validation** - Middleware-based auth checking

### **Rate Limiting**
- **Redis-based** - Sliding window rate limiting
- **Endpoint-specific** - Different limits per endpoint type
- **User-aware** - Per-user and per-IP limiting
- **Graceful degradation** - Memory fallback if Redis unavailable

### **Input Validation**
- **Pydantic Models** - Comprehensive request validation
- **Error Handling** - Centralized exception management
- **Sanitization** - Input cleaning and validation

## 🚀 **Performance Features**

### **Caching**
- **Response Caching** - Frequently accessed data caching
- **Connection Pooling** - Database connection optimization
- **Rate Limiting** - Request throttling for stability

### **Monitoring**
- **Health Checks** - Comprehensive service monitoring
- **Error Logging** - Centralized error tracking
- **Performance Metrics** - Response time monitoring
- **LLM Observability** - Langfuse integration for AI monitoring

## 📱 **Mobile App Integration**

### **Push Notifications**
- **Expo Support** - React Native Expo push notifications
- **FCM Support** - Firebase Cloud Messaging
- **Multi-device** - Multiple device registration per user
- **Real-time Alerts** - Disruption and route notifications

### **Offline Support**
- **Route Caching** - Offline route data
- **Preference Sync** - Settings synchronization
- **Background Updates** - Periodic data refresh

### **Location Services**
- **Real-time Tracking** - Live location updates
- **Geofencing** - Location-based notifications
- **Privacy Control** - User-controlled location sharing

## 🔄 **Real-time Features**

### **WebSocket Support**
- **Live Connections** - Persistent real-time connections
- **Subscription Model** - Topic-based message routing
- **Connection Management** - Automatic reconnection and cleanup

### **Real-time Updates**
- **Disruption Alerts** - Instant disruption notifications
- **Route Tracking** - Live route following
- **Location Updates** - Real-time location sharing
- **System Status** - Live system health updates

## 🌍 **Sri Lankan Integration**

### **Transit Modes**
- **🚌 Bus** - NTC and private bus integration
- **🚂 Train** - Sri Lanka Railways integration
- **🛺 Tuk-tuk** - Three-wheeler routing
- **🚗 Uber** - Ride-sharing integration

### **Data Sources**
- **NTC Buses** - Real-time bus schedules and routes
- **Sri Lanka Railways** - Train schedules and live tracking
- **GTFS Data** - Standardized transit data format
- **Community Reports** - Crowdsourced local data

### **Multilingual Support**
- **English** - Default language
- **Sinhala (සිංහල)** - Local language support
- **Tamil (தமிழ்)** - Regional language support

## 🧪 **Testing & Development**

### **API Testing**

Use the interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **WebSocket Testing**

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/realtime?token=YOUR_JWT_TOKEN');

// Subscribe to disruptions
ws.send(JSON.stringify({
    type: 'subscribe_disruptions'
}));

// Send location update
ws.send(JSON.stringify({
    type: 'location_update',
    data: {
        latitude: 6.9271,
        longitude: 79.8612,
        accuracy: 10.0
    }
}));
```

### **Sample API Calls**

```bash
# Register new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "password123",
    "phone": "+94771234567",
    "preferred_language": "en"
  }'

# Plan a route with AI agents
curl -X POST "http://localhost:8000/api/v1/travel/plan-route" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "source": "Colombo Fort",
    "destination": "Kandy",
    "mode": "transit",
    "preferred_transit": "train"
  }'

# Register mobile device
curl -X POST "http://localhost:8000/api/v1/mobile/register-device" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_token": "ExponentPushToken[XXXXXXXXXXXXXXXXXXXXXX]",
    "platform": "ios",
    "app_version": "1.0.0",
    "device_info": {
      "model": "iPhone 14",
      "os_version": "16.0"
    }
  }'
```

## 🚀 **Deployment**

### **Environment Variables**

Ensure all required environment variables are set:

```env
# Required
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your-super-secret-key
GOOGLE_MAPS_API_KEY=your-api-key
GOOGLE_GEMINI_API_KEY=your-api-key

# Optional
OPENWEATHER_API_KEY=your-api-key
SERPER_API_KEY=your-api-key
LANGFUSE_PUBLIC_KEY=your-key
LANGFUSE_SECRET_KEY=your-key
```

### **Production Checklist**

- [ ] Environment variables configured
- [ ] MongoDB Atlas connection established
- [ ] Redis server configured for rate limiting
- [ ] SSL/TLS certificates configured
- [ ] CORS origins restricted to frontend domains
- [ ] API keys secured and rotated regularly
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented

## 🆘 **Troubleshooting**

### **Common Issues**

1. **Database Connection Failed**
   ```bash
   # Check MongoDB status
   mongod --version
   # Verify connection string in .env
   ```

2. **API Key Errors**
   ```bash
   # Verify API keys in .env
   echo $GOOGLE_MAPS_API_KEY
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

4. **WebSocket Connection Issues**
   ```bash
   # Check JWT token validity
   # Verify WebSocket URL format
   ```

## 📞 **Support**

For issues and questions:
- Check the API documentation at `/docs`
- Review error logs in the database
- Verify environment configuration
- Test endpoints with provided examples

## 📄 **License**

This project is developed for the SLAIC 2025 competition.

---

## 🎯 **Backend Completion Status: 100% ✅**

### ✅ **Authentication System** - Complete
- JWT-based auth with refresh tokens
- User registration with preferences setup
- Role-based access control
- Password management

### ✅ **Mobile App Support** - Complete
- Push notification system
- Device registration
- Offline data support
- Mobile-optimized endpoints

### ✅ **Admin Dashboard** - Complete
- User management CRUD
- Analytics and reporting
- System health monitoring
- Broadcast notifications

### ✅ **Real-time Features** - Complete
- WebSocket support
- Live disruption alerts
- Real-time location tracking
- Background tasks

### ✅ **Production Ready** - Complete
- Rate limiting middleware
- Centralized error handling
- Comprehensive logging
- Health monitoring

### ✅ **SLAIC 2025 Compliance** - Complete
- 10 AI agents (required: 7)
- Sri Lankan transit integration
- Multilingual support
- Community reporting
- Fare optimization

**The backend is now 100% complete and ready for frontend development! 🚀**