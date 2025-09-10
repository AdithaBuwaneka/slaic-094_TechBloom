# 🚀 Smart Transit Companion - Backend API

**AI-Powered Transit Companion Backend for Sri Lankan Transportation**

A production-ready FastAPI backend with multi-agent AI system, real-time features, mobile app support, and admin dashboard integration designed specifically for Sri Lankan transportation needs.

## 🏆 **SLAIC 2025 Winner - Use Case 02**

### ✅ **Competition Requirements Exceeded**
- **🤖 10 AI Agents** (Required: 7) - Sophisticated multi-agent travel planning system
- **🇱🇰 Sri Lankan Transit Integration** - Train, Bus, Tuk-tuk, Uber with local data sources
- **📊 Sri Lankan Data Sources** - NTC buses, Sri Lanka Railways, GTFS integration
- **🌐 Multilingual Support** - English, Sinhala (සිංහල), Tamil (தமிழ්) with cultural context
- **👥 Community Data Platform** - Crowdsourced traffic, delays, fares, accessibility reports
- **💰 Advanced Fare Optimization** - AI-powered cost minimization with local pricing
- **⚠️ Intelligent Disruption Monitoring** - Real-time analysis with predictive capabilities

## 🎯 **System Architecture Overview**

### **🤖 Multi-Agent AI Core (10 Agents)**
```
User Request → LangGraph Orchestration → 10 Specialized AI Agents
├── 1. Input Processing Agent → Validates & preprocesses user input
├── 2. Mode Router Agent → Determines optimal routing strategy  
├── 3. Standard Route Agent → Handles direct point-to-point routing
├── 4. Transit Route Aggregation Agent → Multi-modal transport coordination
├── 5. Fare Calculation Agent → Real-time pricing from multiple sources
├── 6. Fare Optimization Agent → AI-powered cost minimization (SLAIC 2025)
├── 7. User Preference Analysis Agent → Personalization & learning
├── 8. Local Knowledge Agent → Sri Lankan context & cultural insights
├── 9. Disruption Monitoring Agent → Real-time alerts & predictions
└── 10. Route Optimization Agent → Final recommendations & alternatives
```

### **🏗️ Technical Stack**
- **Backend Framework**: FastAPI (Python 3.11+) with async/await
- **AI Orchestration**: LangGraph for multi-agent workflow management
- **Database**: MongoDB Atlas with Motor async driver (17 collections)
- **Vector Database**: ChromaDB for RAG chatbot system
- **Cache Layer**: Redis for rate limiting and session management
- **LLM Integration**: Google Gemini 2.0 Flash, Groq, Langfuse observability
- **Real-time**: WebSocket support for live updates
- **Authentication**: JWT with bcrypt, role-based access control

## 🚀 **Core Features**

### 🎯 **AI-Powered Travel Planning**
- **Multi-Agent Route Planning** - 10 specialized agents working in parallel/sequence
- **Real-time Optimization** - Dynamic route updates based on traffic and conditions
- **Fare Optimization** - AI algorithms minimize travel costs across all modes
- **Preference Learning** - Adaptive recommendations based on user behavior
- **Context-Aware Planning** - Sri Lankan cultural and geographical considerations

### 🤖 **RAG Chatbot System**
- **ChromaDB Vector Database** - Semantic search of transit knowledge base
- **Google Gemini 2.0 Flash** - Advanced natural language processing
- **Multilingual Support** - Conversations in English, Sinhala, Tamil
- **Context Retention** - Conversation history and user preference memory
- **Real-time Knowledge** - Integration with live traffic and transit data

### 🇱🇰 **Sri Lankan Transit Integration**
- **Sri Lanka Railways API** - Real-time train schedules and delays
- **NTC Bus Systems** - Government bus routes and timings
- **Private Bus Operators** - Integration with major private bus services
- **Tuk-tuk Services** - Local three-wheeler pricing and availability
- **Uber/Ride-sharing** - Dynamic pricing and availability
- **GTFS Data** - General Transit Feed Specification compliance

### 👥 **Community Data Platform**
- **Crowdsourced Reporting** - User-submitted traffic delays and disruptions
- **Fare Information Sharing** - Community-verified pricing data
- **Safety Reports** - Security and safety insights from travelers
- **Accessibility Data** - Information for differently-abled passengers
- **Real-time Verification** - AI-powered validation of community reports

### 📱 **Mobile App Backend**
- **Push Notifications** - Expo/FCM integration for real-time alerts
- **Device Management** - Multi-device token registration and management
- **Offline Data Sync** - Route caching for offline functionality
- **Location Services** - Real-time location tracking and geofencing
- **Background Tasks** - Continuous monitoring and updates

### 👨‍💼 **Admin Dashboard Backend**
- **User Management APIs** - Complete CRUD with pagination and search
- **Analytics Endpoints** - User growth, travel patterns, system metrics
- **System Health Monitoring** - Real-time service status and performance
- **Agent System Monitoring** - Multi-agent workflow visualization and metrics
- **Broadcast Notifications** - Mass push notification capabilities

### 🔐 **Enterprise Security**
- **JWT Authentication** - Access/refresh token pattern with automatic renewal
- **Role-based Access Control** - User, admin, and super-admin permissions
- **Rate Limiting** - Redis-based sliding window with customizable limits
- **Input Validation** - Comprehensive request validation with Pydantic
- **Error Handling** - Centralized exception handling with structured responses
- **API Versioning** - Future-proof API design with version management

### ⚡ **Real-time Features**
- **WebSocket Support** - Live disruption alerts and location tracking
- **Background Task Processing** - Celery-based async task management
- **Real-time Notifications** - Instant push notifications for relevant events
- **Live Route Tracking** - Real-time journey following and ETA updates
- **System Monitoring** - Live health checks and performance metrics

## 📁 **Project Structure**

```
backend/
├── app/
│   ├── api/
│   │   ├── routes.py                    # Main API routing & health checks
│   │   └── v1/                          # API version 1 endpoints
│   │       ├── travel_routes.py         # Multi-agent travel planning
│   │       ├── auth_routes.py           # Authentication & user management
│   │       ├── admin_routes.py          # Admin dashboard APIs
│   │       ├── mobile_routes.py         # Mobile app specific endpoints
│   │       ├── websocket_routes.py      # Real-time WebSocket APIs
│   │       ├── chatbot_routes.py        # RAG chatbot system
│   │       ├── community_routes.py      # Community reporting platform
│   │       ├── sri_lanka_routes.py      # Sri Lankan transit data
│   │       ├── weather_routes.py        # Weather integration
│   │       └── user_preferences_routes.py # User preference management
│   ├── core/
│   │   ├── config.py                    # Environment & app configuration
│   │   ├── database.py                  # MongoDB connection & management
│   │   ├── auth_middleware.py           # JWT authentication middleware
│   │   └── exceptions.py                # Custom exception definitions
│   ├── middleware/
│   │   ├── error_handler.py             # Centralized error handling
│   │   ├── rate_limiter.py              # Rate limiting implementation
│   │   └── cors_middleware.py           # CORS configuration
│   ├── services/
│   │   ├── workflow.py                  # Multi-agent orchestration engine
│   │   ├── agent_nodes.py               # Individual AI agent implementations
│   │   ├── auth_service.py              # Authentication business logic
│   │   ├── push_notification_service.py # Push notification management
│   │   ├── intelligent_disruption_service.py # AI disruption analysis
│   │   ├── community_service.py         # Community data management
│   │   ├── sri_lanka_transit_service.py # Sri Lankan transit integration
│   │   ├── multilingual_service.py      # Translation & localization
│   │   ├── google_maps_service.py       # Google Maps API integration
│   │   ├── weather_service.py           # Weather data integration
│   │   ├── cache_manager.py             # Response caching system
│   │   ├── langfuse_service.py          # LLM observability
│   │   └── llm_summarizer.py            # AI summarization services
│   ├── models/
│   │   ├── user.py                      # User data models
│   │   ├── travel_schema.py             # Travel & route models
│   │   ├── transit_data.py              # Transit system models
│   │   ├── user_preferences.py          # User preference models
│   │   ├── community_report.py          # Community reporting models
│   │   └── path.py                      # Route path models
│   ├── chatbot/
│   │   ├── chatbot.py                   # RAG chatbot implementation
│   │   ├── db/                          # Vector database storage
│   │   ├── documents/                   # Knowledge base documents
│   │   └── transit_app_guide.txt        # App usage guide
│   └── utils/
│       ├── sri_lanka_data.py            # Sri Lankan geographic data
│       ├── constants.py                 # Application constants
│       └── helpers.py                   # Utility functions
├── requirements.txt                     # Python dependencies
├── run.py                              # Application entry point
├── create_admin.py                     # Admin user creation script
└── .env                                # Environment configuration
```

## 🗄️ **Database Architecture**

### **MongoDB Collections (17 Total)**
```
📊 Core Collections:
├── users                    # User profiles & authentication
├── user_preferences         # Travel preferences & settings
├── route_history           # User travel history
├── user_sessions           # Active session management
├── mobile_devices          # Device registration & tokens

🚌 Transit Collections:
├── sri_lanka_routes        # Local transit route data
├── sri_lanka_stops         # Bus/train stop information
├── transit_data            # Real-time transit information
├── fare_data              # Dynamic pricing information

👥 Community Collections:
├── community_reports       # User-submitted reports
├── disruption_reports      # Traffic & service disruptions
├── community_votes         # Report verification votes

🎯 System Collections:
├── api_logs               # API usage & performance logs
├── error_logs            # Error tracking & debugging
├── system_config         # Configuration management
├── analytics_data        # Usage analytics & metrics
└── notification_logs     # Push notification tracking
```

### **Vector Database (ChromaDB)**
- **Transit Knowledge Base** - Embeddings of Sri Lankan transit information
- **User Query History** - Semantic search of past user interactions
- **FAQ Database** - Common questions and AI-generated responses
- **Document Embeddings** - App guides and transit documentation

## 🚦 **Getting Started**

### **Prerequisites**
- **Python 3.11+** with pip
- **MongoDB** (local or Atlas cloud)
- **Redis** (for rate limiting and caching)
- **Google Cloud API Key** (for Maps and Gemini)
- **Groq API Key** (for additional LLM support)

### **Installation**

1. **Clone Repository & Install Dependencies**
   ```bash
   git clone <repository-url>
   cd backend
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and database URLs
   ```

3. **Database Setup**
   ```bash
   # MongoDB will auto-create collections on first use
   # Ensure MongoDB is running on configured port
   
   # Redis setup (for rate limiting)
   # Ensure Redis is running on configured port
   ```

4. **Create Admin User**
   ```bash
   python create_admin.py
   # Creates admin user with credentials:
   # Email: admin@example.com
   # Password: admin123456
   ```

5. **Initialize Vector Database**
   ```bash
   # ChromaDB will initialize automatically on first chatbot request
   # Ensure documents are in app/chatbot/documents/
   ```

6. **Start Development Server**
   ```bash
   python run.py
   # Server starts on http://localhost:8000
   # API docs available at http://localhost:8000/docs
   ```

### **Production Deployment**
```bash
# Using Uvicorn for production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Using Gunicorn with Uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔑 **Environment Variables**

### **Required Configuration**
```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=transit_companion

# Redis Configuration (optional, falls back to memory)
REDIS_URL=redis://localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Google API Keys
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
GOOGLE_GENERATIVE_AI_API_KEY=your-gemini-api-key

# Additional LLM APIs
GROQ_API_KEY=your-groq-api-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key

# External APIs
OPENWEATHER_API_KEY=your-openweather-api-key
SERPER_API_KEY=your-serper-api-key

# Application Configuration
DEBUG=False
CORS_ORIGINS=["http://localhost:3000", "http://localhost:19006"]
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

## 🛣️ **API Endpoints**

### **Authentication & Users**
```
POST   /api/v1/auth/register        # User registration
POST   /api/v1/auth/login           # User login
POST   /api/v1/auth/refresh         # Token refresh
GET    /api/v1/auth/verify-token    # Token verification
GET    /api/v1/auth/me              # Current user profile
PUT    /api/v1/auth/profile         # Update user profile
```

### **Multi-Agent Travel Planning**
```
POST   /api/v1/travel/plan-route    # Main route planning endpoint
GET    /api/v1/travel/route/{id}    # Get specific route details
POST   /api/v1/travel/save-route    # Save route to favorites
GET    /api/v1/travel/history       # User's travel history
POST   /api/v1/travel/feedback      # Route feedback & rating
```

### **RAG Chatbot**
```
POST   /api/v1/chatbot/chat         # Chat with AI assistant
GET    /api/v1/chatbot/history      # Chat conversation history
POST   /api/v1/chatbot/feedback     # Chat response feedback
GET    /api/v1/chatbot/suggestions  # Suggested questions
```

### **Community Platform**
```
GET    /api/v1/community/reports    # Get community reports
POST   /api/v1/community/report     # Submit new report
POST   /api/v1/community/vote       # Vote on report accuracy
GET    /api/v1/community/leaderboard # Community contributors
```

### **Sri Lankan Transit Data**
```
GET    /api/v1/sri-lanka/routes     # Local transit routes
GET    /api/v1/sri-lanka/stops      # Bus/train stops
GET    /api/v1/sri-lanka/schedules  # Real-time schedules
GET    /api/v1/sri-lanka/fares      # Current fare information
```

### **Mobile App Support**
```
POST   /api/v1/mobile/register-device    # Register device for push notifications
POST   /api/v1/mobile/update-location    # Update user location
GET    /api/v1/mobile/nearby-stops       # Find nearby transit stops
GET    /api/v1/mobile/app-config         # App configuration & feature flags
```

### **Admin Dashboard**
```
GET    /api/v1/admin/dashboard            # System overview statistics
GET    /api/v1/admin/users               # User management with pagination
PUT    /api/v1/admin/users/{id}/status   # Update user status
GET    /api/v1/admin/analytics/*         # Various analytics endpoints
GET    /api/v1/admin/agent-system/workflow # Multi-agent system monitoring
POST   /api/v1/admin/notifications/broadcast # Send push notifications
```

### **Real-time Features**
```
WebSocket: /api/v1/ws/realtime         # Real-time updates
WebSocket: /api/v1/ws/location         # Location tracking
WebSocket: /api/v1/ws/disruptions      # Disruption alerts
```

## 🤖 **Multi-Agent System Details**

### **Agent Workflow Process**
1. **Input Processing Agent** - Validates and normalizes user request
2. **Mode Router Agent** - Determines single vs multi-modal routing strategy
3. **Route Planning Agents** - Parallel execution for different transport modes
4. **Fare Agents** - Calculate and optimize costs across all options
5. **Preference Agent** - Apply user preferences and learning
6. **Local Knowledge Agent** - Add Sri Lankan context and insights
7. **Disruption Agent** - Check for real-time disruptions and alternatives
8. **Optimization Agent** - Final route selection and recommendations

### **Agent Communication**
- **LangGraph State Management** - Shared state across all agents
- **Parallel Execution** - Independent agents run concurrently
- **Sequential Dependencies** - Some agents wait for others to complete
- **Error Handling** - Graceful fallbacks if individual agents fail
- **Performance Monitoring** - Track execution time and success rates

## 📊 **Monitoring & Analytics**

### **System Health Monitoring**
- **API Response Times** - Track endpoint performance
- **Database Query Performance** - Monitor slow queries and optimization
- **Agent Execution Metrics** - Individual agent performance tracking
- **Error Rate Monitoring** - Track and alert on error spikes
- **Resource Usage** - CPU, memory, and network monitoring

### **Business Analytics**
- **User Growth Metrics** - Registration trends and user retention
- **Travel Pattern Analysis** - Popular routes and transport modes
- **Community Engagement** - Report submission and verification rates
- **Feature Usage** - Track adoption of new features
- **Revenue Metrics** - Fare savings and cost optimization impact

### **LLM Observability (Langfuse)**
- **Token Usage Tracking** - Monitor LLM costs and usage patterns
- **Response Quality Metrics** - Track chatbot effectiveness
- **User Satisfaction Scores** - Feedback-based quality assessment
- **Performance Optimization** - Identify slow or expensive LLM calls

## 🔐 **Security Implementation**

### **Authentication Security**
- **JWT Tokens** - Short-lived access tokens with refresh mechanism
- **Password Security** - bcrypt hashing with salt rounds
- **Rate Limiting** - Prevent brute force attacks
- **Session Management** - Secure token storage and invalidation

### **API Security**
- **Input Validation** - Pydantic models prevent injection attacks
- **SQL Injection Protection** - MongoDB parameterized queries
- **XSS Prevention** - Input sanitization and output encoding
- **CORS Configuration** - Restrict cross-origin requests
- **Request Size Limits** - Prevent DoS attacks

### **Data Protection**
- **Encrypted Storage** - Sensitive data encrypted at rest
- **Secure Transmission** - HTTPS/TLS for all communications
- **Data Privacy** - GDPR-compliant data handling
- **Access Logging** - Audit trail for all data access

## 🧪 **Testing & Quality Assurance**

### **Testing Strategy**
```bash
# Unit Tests
pytest tests/unit/

# Integration Tests
pytest tests/integration/

# API Tests
pytest tests/api/

# Load Testing
locust -f tests/load/locustfile.py

# Code Coverage
coverage run -m pytest
coverage report -m
```

### **Code Quality Tools**
- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting and style checking
- **mypy** - Type checking
- **bandit** - Security vulnerability scanning

## 🚀 **Deployment & Scaling**

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Cloud Deployment Options**
- **AWS** - ECS, Lambda, or EC2 with RDS and ElastiCache
- **Google Cloud** - Cloud Run, App Engine, or GKE
- **Azure** - Container Instances or App Service
- **DigitalOcean** - App Platform or Kubernetes

### **Scaling Considerations**
- **Horizontal Scaling** - Multiple server instances behind load balancer
- **Database Scaling** - MongoDB sharding and read replicas
- **Cache Layer** - Redis cluster for improved performance
- **CDN Integration** - Static asset delivery optimization
- **Background Jobs** - Celery with Redis/RabbitMQ for async tasks

## 🤝 **Contributing**

### **Development Guidelines**
1. Follow PEP 8 Python style guide
2. Write comprehensive docstrings
3. Add type hints to all functions
4. Write unit tests for new features
5. Update API documentation

### **Git Workflow**
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push and create pull request
git push origin feature/your-feature-name
```

## 📚 **Documentation & Resources**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [MongoDB Motor Documentation](https://motor.readthedocs.io/)
- [Google Gemini API](https://ai.google.dev/docs)
- [ChromaDB Documentation](https://docs.trychroma.com/)

## 🏆 **SLAIC 2025 Excellence**

This backend system demonstrates:

- **🤖 Advanced Multi-Agent AI** - 10 specialized agents exceeding competition requirements
- **🇱🇰 Deep Sri Lankan Integration** - Authentic local transit data and cultural context
- **👥 Community-Driven Innovation** - Crowdsourced data platform with AI validation
- **⚡ Real-time Intelligence** - Live updates, disruption monitoring, and predictive analytics
- **🏗️ Enterprise Architecture** - Production-ready, scalable, and secure design
- **📱 Mobile-First Backend** - Comprehensive support for native mobile applications
- **📊 Advanced Analytics** - Data-driven insights for continuous improvement
- **🔐 Security Excellence** - Enterprise-grade security and privacy protection
- **🌐 Multilingual AI** - Natural language processing in multiple Sri Lankan languages
- **💰 Economic Impact** - AI-powered fare optimization saving money for commuters

---

**🏆 Built for SLAIC 2025 - Sri Lanka AI Challenge Use Case 02**  
**🇱🇰 Proudly Engineered in Sri Lanka - World-Class AI Technology**