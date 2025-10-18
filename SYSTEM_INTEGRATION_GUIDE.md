# 🔗 System Integration Guide
## Understanding Admin Dashboard, Mobile App & Backend Integration

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Backend Architecture](#backend-architecture)
3. [Mobile App Architecture](#mobile-app-architecture)
4. [Admin Dashboard Architecture](#admin-dashboard-architecture)
5. [Data Flow & Communication](#data-flow--communication)
6. [Complete User Journey](#complete-user-journey)
7. [Admin Operations](#admin-operations)
8. [Real-Time Features](#real-time-features)

---

## 🎯 System Overview

### **Three Main Components**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SMART TRANSIT COMPANION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📱 MOBILE APP                                                   │
│  React Native + Expo                                            │
│  ├─ User Interface (Commuters)                                  │
│  ├─ Route Planning UI                                           │
│  ├─ AI Agent Visualization                                      │
│  ├─ RAG Chatbot Interface                                       │
│  └─ Community Reporting                                         │
│                                                                  │
│  🖥️ ADMIN DASHBOARD                                             │
│  Next.js 15 + React 19                                          │
│  ├─ System Monitoring                                           │
│  ├─ User Management                                             │
│  ├─ Analytics & Reports                                         │
│  ├─ AI Agent Monitoring                                         │
│  └─ Push Notifications                                          │
│                                                                  │
│  🚀 BACKEND API                                                  │
│  FastAPI + Python                                               │
│  ├─ 10 AI Agents (LangGraph)                                    │
│  ├─ RAG Chatbot (ChromaDB)                                      │
│  ├─ REST API Endpoints                                          │
│  ├─ WebSocket Server                                            │
│  ├─ MongoDB Database                                            │
│  ├─ Redis Cache                                                 │
│  └─ External API Integrations                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Backend Architecture

### **File Structure**

```
backend/
├── app/
│   ├── main.py                      # FastAPI application entry point
│   ├── api/
│   │   └── v1/                      # API version 1
│   │       ├── travel_routes.py     # Route planning endpoints
│   │       ├── auth_routes.py       # Authentication
│   │       ├── admin_routes.py      # Admin operations
│   │       ├── chatbot_routes.py    # RAG chatbot
│   │       ├── community_routes.py  # Community features
│   │       └── websocket_routes.py  # Real-time updates
│   │
│   ├── services/                    # Business logic
│   │   ├── agent_nodes.py           # 10 AI Agents (101 KB)
│   │   ├── workflow.py              # LangGraph orchestration
│   │   ├── tool_functions.py        # Agent tools
│   │   ├── google_maps_service.py   # Maps integration
│   │   ├── intelligent_disruption_service.py
│   │   └── llm_summarizer.py        # AI summarization
│   │
│   ├── chatbot/
│   │   ├── chatbot.py               # RAG implementation
│   │   ├── db/                      # ChromaDB storage
│   │   └── transit_app_guide.txt    # Knowledge base
│   │
│   ├── models/                      # Data models
│   │   ├── travel_schema.py         # Travel request schemas
│   │   ├── enhanced_route.py        # Route data models
│   │   └── user_preferences.py      # User preferences
│   │
│   ├── core/                        # Core configuration
│   │   ├── config.py                # Settings
│   │   ├── database.py              # MongoDB connection
│   │   └── security.py              # JWT & encryption
│   │
│   └── middleware/                  # Request middleware
│       ├── auth_middleware.py       # JWT validation
│       ├── rate_limiter.py          # Redis rate limiting
│       └── error_handler.py         # Error handling
│
├── run.py                           # Application starter
└── requirements.txt                 # Python dependencies
```

### **Backend Responsibilities**

#### **1. API Gateway**
```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Transit Companion Backend API",
    description="AI-Powered Transit Companion",
    version="1.0.0"
)

# CORS - Allow mobile app and admin dashboard to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mobile app, Admin dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Authentication middleware
app.add_middleware(AuthMiddleware)

# Rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include all route modules
app.include_router(router, prefix="/api/v1")
```

#### **2. Authentication Service**
```python
# app/api/v1/auth_routes.py

@router.post("/register")
async def register(user_data: UserCreate):
    """
    Mobile app calls this to create new user
    """
    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user in MongoDB
    user = await db.users.insert_one({
        "email": user_data.email,
        "password_hash": hashed_password,
        "full_name": user_data.full_name,
        "role": "user",
        "created_at": datetime.utcnow()
    })

    # Generate JWT tokens
    access_token = create_access_token({"sub": str(user.inserted_id)})
    refresh_token = create_refresh_token({"sub": str(user.inserted_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_data
    }

@router.post("/login")
async def login(credentials: LoginRequest):
    """
    Mobile app & Admin dashboard use this
    """
    # Find user
    user = await db.users.find_one({"email": credentials.email})

    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate tokens
    access_token = create_access_token({"sub": str(user["_id"])})

    return {
        "access_token": access_token,
        "user": {
            "user_id": str(user["_id"]),
            "email": user["email"],
            "role": user["role"]
        }
    }
```

#### **3. Route Planning Service (Core Feature)**
```python
# app/api/v1/travel_routes.py

@router.post("/plan-route")
async def plan_route(request: RouteRequest, current_user: User = Depends(get_current_user)):
    """
    Mobile app submits route planning request
    Backend runs 10 AI agents to find optimal routes
    """

    # Create travel state
    initial_state = TravelState(
        source=request.source,
        destination=request.destination,
        mode=request.mode,
        user_id=current_user.user_id
    )

    # Run LangGraph workflow (10 agents)
    result = await run_travel_agent(
        source=request.source,
        destination=request.destination,
        mode=request.mode,
        user_id=current_user.user_id
    )

    # Save to route history
    await db.route_history.insert_one({
        "request_id": result["request_id"],
        "user_id": current_user.user_id,
        "source": request.source,
        "destination": request.destination,
        "routes_found": len(result["response"]["all_routes"]),
        "agents_used": result["agents_used"],
        "processing_time": result["processing_time"],
        "timestamp": datetime.utcnow()
    })

    return result
```

#### **4. AI Agent Workflow**
```python
# app/services/workflow.py

async def run_travel_agent(source, destination, mode, user_id):
    """
    Orchestrates 10 AI agents using LangGraph
    """

    # Create workflow
    workflow = create_travel_agent_workflow()

    # Execute agents sequentially
    final_state = await workflow.ainvoke({
        "source": source,
        "destination": destination,
        "mode": mode,
        "user_id": user_id
    })

    # Agents executed:
    # 1. Input Processing → Validates & loads preferences
    # 2. Mode Router → Determines route type
    # 3. Standard/Transit Route → Gets route options
    # 4. Fare Calculation → Calculates costs
    # 5. Fare Optimization → Finds cheapest
    # 6. Preference Analysis → Personalizes
    # 7. Local Knowledge → Adds context
    # 8. Route Optimization → Ranks routes
    # 9. Disruption Monitoring → Checks for delays
    # 10. Response Compilation → Formats output

    return {
        "status": "success",
        "request_id": generate_uuid(),
        "response": final_state.final_response,
        "agents_used": final_state.agents_completed,
        "processing_time": calculate_time(final_state)
    }
```

#### **5. RAG Chatbot Service**
```python
# app/chatbot/chatbot.py

@router.post("/query")
async def chatbot_query(request: QuestionRequest):
    """
    Mobile app sends chat message
    RAG system retrieves relevant docs and generates response
    """

    # Vector search in ChromaDB
    relevant_docs = vectordb.similarity_search(
        request.question,
        k=3  # Top 3 most relevant documents
    )

    # Generate response with Gemini
    llm_response = llm.invoke({
        "context": "\n".join([doc.page_content for doc in relevant_docs]),
        "question": request.question
    })

    # Save chat history
    await db.chat_history.insert_one({
        "user_id": request.user_id,
        "question": request.question,
        "answer": llm_response,
        "timestamp": datetime.utcnow()
    })

    return {
        "answer": llm_response,
        "sources": [doc.metadata for doc in relevant_docs]
    }
```

#### **6. Admin Dashboard API**
```python
# app/api/v1/admin_routes.py

@router.get("/dashboard/overview")
async def get_dashboard_overview(admin: User = Depends(require_admin)):
    """
    Admin dashboard fetches this on load
    """

    # Aggregate statistics from MongoDB
    stats = {
        "total_users": await db.users.count_documents({}),
        "active_users": await db.users.count_documents({
            "last_login": {"$gte": datetime.utcnow() - timedelta(days=7)}
        }),
        "total_trips": await db.route_history.count_documents({}),
        "community_reports": await db.community_reports.count_documents({}),
        "recent_activity": await db.activity_logs.find().sort("timestamp", -1).limit(10).to_list(10)
    }

    return stats

@router.post("/notifications/broadcast")
async def broadcast_notification(
    message: NotificationMessage,
    admin: User = Depends(require_admin)
):
    """
    Admin sends push notification to all users
    """

    # Get all user device tokens
    users = await db.users.find({"is_active": True}).to_list(None)
    tokens = [u["push_token"] for u in users if "push_token" in u]

    # Send via push notification service
    result = await push_notification_service.send_bulk(
        tokens=tokens,
        title=message.title,
        body=message.body
    )

    return {
        "sent": result.success_count,
        "failed": result.failure_count
    }
```

#### **7. WebSocket Server**
```python
# app/api/v1/websocket_routes.py

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Mobile app connects for real-time updates
    """
    await websocket.accept()

    # Store connection
    connections[user_id] = websocket

    try:
        while True:
            # Listen for messages
            data = await websocket.receive_text()

            # Send real-time disruption alerts
            if new_disruption:
                await websocket.send_json({
                    "type": "disruption_alert",
                    "message": "Traffic jam on your route",
                    "severity": "high"
                })

    except WebSocketDisconnect:
        del connections[user_id]
```

---

## 📱 Mobile App Architecture

### **File Structure**

```
mobile-app/
├── app/                             # Expo Router (file-based routing)
│   ├── _layout.tsx                  # Root layout
│   ├── index.tsx                    # App entry point
│   │
│   ├── (onboarding)/                # First-time user flow
│   │   ├── welcome.tsx
│   │   ├── features.tsx
│   │   └── permissions.tsx
│   │
│   ├── (auth)/                      # Authentication screens
│   │   ├── login.tsx
│   │   ├── register.tsx
│   │   └── forgot-password.tsx
│   │
│   └── (main)/                      # Main app (after login)
│       └── (tabs)/                  # Bottom tab navigation
│           ├── home.tsx             # Route planning ⭐
│           ├── routes.tsx           # Route history
│           ├── chat.tsx             # RAG chatbot
│           ├── community.tsx        # Community reports
│           └── profile.tsx          # User profile
│
├── src/
│   ├── components/                  # Reusable UI components
│   │   ├── MultiAgentAnimation.tsx  # AI agent visualization
│   │   ├── RouteCard.tsx            # Route display
│   │   ├── MapView.tsx              # Interactive map
│   │   └── ChatBubble.tsx           # Chat interface
│   │
│   ├── services/                    # Business logic
│   │   ├── api/                     # API communication
│   │   │   ├── config.ts            # API configuration
│   │   │   ├── auth.ts              # Auth endpoints
│   │   │   ├── travelService.ts     # Route planning API
│   │   │   └── chatService.ts       # Chatbot API
│   │   │
│   │   ├── notifications/
│   │   │   └── push.ts              # Push notifications
│   │   │
│   │   └── websocket/
│   │       └── client.ts            # WebSocket connection
│   │
│   ├── contexts/                    # Global state management
│   │   ├── AppContext.tsx           # App-wide state
│   │   ├── AuthContext.tsx          # Authentication state
│   │   └── ThemeContext.tsx         # Theme settings
│   │
│   ├── types/                       # TypeScript types
│   │   ├── api.ts
│   │   ├── route.ts
│   │   └── user.ts
│   │
│   └── utils/                       # Utility functions
│       ├── storage.ts               # AsyncStorage helpers
│       └── formatters.ts            # Data formatting
│
├── package.json
└── app.config.js                    # Expo configuration
```

### **Mobile App Responsibilities**

#### **1. Route Planning UI (Home Screen)**

**File**: `app/(main)/(tabs)/home.tsx`

```typescript
export default function Home() {
  const { user } = useAuth();
  const { setCurrentRoute, addToRouteHistory } = useApp();

  const [routeRequest, setRouteRequest] = useState({
    source: '',
    destination: '',
    mode: 'transit',
    user_id: user?.user_id
  });

  const handlePlanRoute = async () => {
    // Show AI agent animation
    setShowAgentAnimation(true);

    // Call backend API
    const response = await travelService.planRoute(routeRequest);

    // Response contains:
    // - best_route (recommended by AI)
    // - all_routes (alternatives)
    // - agents_used (list of 10 agents)
    // - processing_time
    // - ai_disruption_analysis
    // - destination_summary

    // Store route in app state
    setCurrentRoute(response.data.response.best_route);

    // Save to AsyncStorage for offline access
    await addToRouteHistory(response.data.response);

    // Navigate to routes screen
    router.push('/(main)/(tabs)/routes');
  };

  return (
    <View>
      {/* Source input */}
      <TextInput
        placeholder="From"
        value={routeRequest.source}
        onChangeText={(text) => setRouteRequest({...routeRequest, source: text})}
      />

      {/* Destination input */}
      <TextInput
        placeholder="To"
        value={routeRequest.destination}
        onChangeText={(text) => setRouteRequest({...routeRequest, destination: text})}
      />

      {/* Mode selector */}
      <SriLankanModeSelector
        selectedMode={routeRequest.mode}
        onSelect={(mode) => setRouteRequest({...routeRequest, mode})}
      />

      {/* Plan button */}
      <TouchableOpacity onPress={handlePlanRoute}>
        <Text>🤖 Plan My Route</Text>
      </TouchableOpacity>

      {/* Multi-Agent Animation Modal */}
      <MultiAgentAnimation
        visible={showAgentAnimation}
        onComplete={handleAgentAnimationComplete}
      />
    </View>
  );
}
```

#### **2. API Communication Layer**

**File**: `src/services/api/travelService.ts`

```typescript
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

// API configuration
const API_HOST = process.env.EXPO_PUBLIC_API_HOST;
const API_PORT = process.env.EXPO_PUBLIC_API_PORT;
const BASE_URL = `http://${API_HOST}:${API_PORT}/api/v1`;

class TravelService {
  private api = axios.create({
    baseURL: BASE_URL,
    timeout: 30000  // 30 seconds for AI processing
  });

  constructor() {
    // Add JWT token to all requests
    this.api.interceptors.request.use(async (config) => {
      const token = await AsyncStorage.getItem('accessToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });
  }

  async planRoute(request: RouteRequest): Promise<RouteResponse> {
    try {
      const response = await this.api.post('/travel/plan-route', request);

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error('Route planning failed:', error);
      return {
        success: false,
        error: error.message
      };
    }
  }

  async getRouteHistory(): Promise<Route[]> {
    const response = await this.api.get('/travel/routes');
    return response.data.routes;
  }
}

export const travelService = new TravelService();
```

#### **3. Real-Time WebSocket**

**File**: `src/services/websocket/client.ts`

```typescript
import { useEffect, useRef } from 'react';

export function useWebSocket(userId: string) {
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to backend WebSocket
    ws.current = new WebSocket(
      `ws://${API_HOST}:${API_PORT}/api/v1/ws`
    );

    ws.current.onopen = () => {
      console.log('WebSocket connected');

      // Authenticate
      ws.current?.send(JSON.stringify({
        type: 'auth',
        user_id: userId
      }));
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'disruption_alert') {
        // Show push notification
        showNotification({
          title: 'Route Alert',
          body: data.message
        });

        // Update current route
        updateRouteDisruption(data);
      }

      if (data.type === 'route_update') {
        // Real-time ETA update
        updateRouteETA(data.eta);
      }
    };

    return () => ws.current?.close();
  }, [userId]);

  return ws.current;
}
```

#### **4. Multi-Agent Animation**

**File**: `src/components/MultiAgentAnimation.tsx`

```typescript
export default function MultiAgentAnimation({ visible, onComplete, requestData }) {
  const [activeAgent, setActiveAgent] = useState(0);

  const agents = [
    { name: 'Input Processing', icon: '📝', duration: 0.5 },
    { name: 'Mode Router', icon: '🔀', duration: 0.3 },
    { name: 'Transit Aggregation', icon: '🚌', duration: 2.0 },
    { name: 'Fare Calculation', icon: '💰', duration: 0.8 },
    { name: 'Fare Optimization', icon: '📊', duration: 1.2 },
    { name: 'Preference Analysis', icon: '👤', duration: 0.6 },
    { name: 'Local Knowledge', icon: '🏛️', duration: 1.5 },
    { name: 'Route Optimization', icon: '⚡', duration: 1.0 },
    { name: 'Disruption Monitoring', icon: '⚠️', duration: 0.8 },
    { name: 'Response Compilation', icon: '✅', duration: 0.5 }
  ];

  useEffect(() => {
    if (!visible) return;

    // Simulate agent execution
    let currentAgent = 0;
    const interval = setInterval(() => {
      if (currentAgent < agents.length) {
        setActiveAgent(currentAgent);
        currentAgent++;
      } else {
        clearInterval(interval);
        onComplete();
      }
    }, 800);

    return () => clearInterval(interval);
  }, [visible]);

  return (
    <Modal visible={visible}>
      <View>
        <Text>🤖 AI Agents Working...</Text>

        {agents.map((agent, index) => (
          <View key={index}>
            <Text>{agent.icon} {agent.name}</Text>
            <View>
              {index < activeAgent && '✅ Complete'}
              {index === activeAgent && '🔄 Processing...'}
              {index > activeAgent && '⏳ Waiting...'}
            </View>
          </View>
        ))}
      </View>
    </Modal>
  );
}
```

#### **5. Global State Management**

**File**: `src/contexts/AppContext.tsx`

```typescript
interface AppContextType {
  currentRoute: Route | null;
  setCurrentRoute: (route: Route) => void;
  routeHistory: Route[];
  addToRouteHistory: (route: Route) => Promise<void>;
}

export const AppProvider = ({ children }) => {
  const [currentRoute, setCurrentRoute] = useState<Route | null>(null);
  const [routeHistory, setRouteHistory] = useState<Route[]>([]);

  // Load route history from AsyncStorage on app start
  useEffect(() => {
    loadRouteHistory();
  }, []);

  const loadRouteHistory = async () => {
    const history = await AsyncStorage.getItem('routeHistory');
    if (history) {
      setRouteHistory(JSON.parse(history));
    }
  };

  const addToRouteHistory = async (route: Route) => {
    const updatedHistory = [route, ...routeHistory].slice(0, 50); // Keep last 50
    setRouteHistory(updatedHistory);
    await AsyncStorage.setItem('routeHistory', JSON.stringify(updatedHistory));
  };

  return (
    <AppContext.Provider value={{
      currentRoute,
      setCurrentRoute,
      routeHistory,
      addToRouteHistory
    }}>
      {children}
    </AppContext.Provider>
  );
};
```

---

## 🖥️ Admin Dashboard Architecture

### **File Structure**

```
admin-dashboard/
├── src/
│   ├── app/                         # Next.js App Router
│   │   ├── layout.tsx               # Root layout
│   │   ├── page.tsx                 # Landing page
│   │   │
│   │   ├── login/
│   │   │   └── page.tsx             # Admin login
│   │   │
│   │   └── dashboard/
│   │       ├── layout.tsx           # Dashboard layout
│   │       ├── page.tsx             # Dashboard home ⭐
│   │       │
│   │       ├── users/
│   │       │   └── page.tsx         # User management
│   │       │
│   │       ├── analytics/
│   │       │   └── page.tsx         # Analytics
│   │       │
│   │       ├── agents/
│   │       │   └── page.tsx         # AI agent monitoring
│   │       │
│   │       ├── notifications/
│   │       │   └── page.tsx         # Push notifications
│   │       │
│   │       ├── reports/
│   │       │   └── page.tsx         # Community reports
│   │       │
│   │       └── settings/
│   │           └── page.tsx         # System settings
│   │
│   ├── components/                  # React components
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   │
│   │   ├── charts/
│   │   │   ├── UserGrowthChart.tsx
│   │   │   └── RouteMetrics.tsx
│   │   │
│   │   └── tables/
│   │       ├── UserTable.tsx
│   │       └── ReportTable.tsx
│   │
│   └── lib/
│       ├── api.ts                   # API client
│       └── auth.ts                  # Authentication
│
└── package.json
```

### **Admin Dashboard Responsibilities**

#### **1. Dashboard Overview**

**File**: `src/app/dashboard/page.tsx`

```typescript
'use client';

import { useState, useEffect } from 'react';
import { dashboardAPI } from '@/lib/api';

export default function DashboardPage() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    // Call backend API
    const data = await dashboardAPI.getOverview();

    setOverview(data);
  };

  return (
    <div>
      {/* Stats Cards */}
      <div className="grid grid-cols-4 gap-6">
        <StatCard
          title="Total Users"
          value={overview?.total_users || 0}
          icon="👥"
        />
        <StatCard
          title="Total Trips"
          value={overview?.route_history_count || 0}
          icon="📈"
        />
        <StatCard
          title="Community Reports"
          value={overview?.total_community_reports || 0}
          icon="💬"
        />
        <StatCard
          title="System Status"
          value="Healthy"
          icon="✅"
        />
      </div>

      {/* Recent Activity */}
      <div>
        <h2>Recent Activity</h2>
        {overview?.recent_activity.map((activity) => (
          <div key={activity.id}>
            <p>{activity.description}</p>
            <span>{activity.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### **2. API Client**

**File**: `src/lib/api.ts`

```typescript
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('adminToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const dashboardAPI = {
  async getOverview() {
    const response = await api.get('/admin/dashboard/overview');
    return response.data;
  },

  async getUsers(filters?: UserFilters) {
    const response = await api.get('/admin/users', { params: filters });
    return response.data;
  },

  async broadcastNotification(message: string) {
    return await api.post('/admin/notifications/broadcast', {
      title: 'System Announcement',
      body: message,
      target: 'all'
    });
  },

  async getAgentMetrics() {
    const response = await api.get('/admin/agents/metrics');
    return response.data;
  }
};
```

#### **3. User Management**

**File**: `src/app/dashboard/users/page.tsx`

```typescript
export default function UsersPage() {
  const [users, setUsers] = useState([]);
  const [filters, setFilters] = useState({
    role: 'all',
    status: 'all'
  });

  useEffect(() => {
    loadUsers();
  }, [filters]);

  const loadUsers = async () => {
    const data = await dashboardAPI.getUsers(filters);
    setUsers(data.users);
  };

  const handleSuspendUser = async (userId: string) => {
    await dashboardAPI.suspendUser(userId);
    loadUsers(); // Refresh list
  };

  return (
    <div>
      <h1>User Management</h1>

      {/* Filters */}
      <div>
        <select onChange={(e) => setFilters({...filters, role: e.target.value})}>
          <option value="all">All Roles</option>
          <option value="user">Users</option>
          <option value="admin">Admins</option>
        </select>

        <select onChange={(e) => setFilters({...filters, status: e.target.value})}>
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {/* User Table */}
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Name</th>
            <th>Role</th>
            <th>Last Login</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.user_id}>
              <td>{user.email}</td>
              <td>{user.full_name}</td>
              <td>{user.role}</td>
              <td>{formatDate(user.last_login)}</td>
              <td>
                <button onClick={() => handleSuspendUser(user.user_id)}>
                  Suspend
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 🔄 Data Flow & Communication

### **Complete Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER ACTION                            │
│  "I want to go from Colombo Fort to Kandy by train"           │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                     MOBILE APP (Home Screen)                    │
│  - User fills form:                                            │
│    Source: "Colombo Fort"                                      │
│    Destination: "Kandy"                                        │
│    Mode: "Train"                                               │
│  - Taps "Plan Route" button                                    │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              MOBILE APP (API Service Layer)                     │
│  travelService.planRoute({                                     │
│    source: "Colombo Fort",                                     │
│    destination: "Kandy",                                       │
│    mode: "train",                                              │
│    user_id: "user_123"                                         │
│  })                                                            │
│                                                                │
│  → HTTP POST /api/v1/travel/plan-route                        │
│  → Headers: Authorization: Bearer <JWT>                        │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (API Gateway)                         │
│  1. CORS Middleware → Allow request                            │
│  2. Auth Middleware → Verify JWT token                         │
│  3. Rate Limiter → Check request limit                         │
│  4. Request Handler → Route to travel_routes.py                │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (Route Planning Handler)                   │
│  travel_routes.py:plan_route()                                 │
│  1. Validate request data                                      │
│  2. Create TravelState object                                  │
│  3. Call workflow.run_travel_agent()                           │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│            BACKEND (LangGraph Workflow Execution)               │
│                                                                │
│  🤖 AGENT 1: Input Processing                                  │
│  - MongoDB query: Get user preferences                         │
│  - Validate source & destination                               │
│  Duration: 0.5s                                                │
│                                                                │
│  🤖 AGENT 2: Mode Router                                       │
│  - Decision: "train" → use transit aggregation                 │
│  Duration: 0.3s                                                │
│                                                                │
│  🤖 AGENT 3: Transit Aggregation                               │
│  - Google Maps API: Get train routes                           │
│  - Find alternatives (bus, mixed)                              │
│  Duration: 2.0s                                                │
│                                                                │
│  🤖 AGENT 4: Fare Calculation                                  │
│  - MongoDB query: Train fare database                          │
│  - Calculate: LKR 180 (2nd class)                              │
│  Duration: 0.8s                                                │
│                                                                │
│  🤖 AGENT 5: Fare Optimization ⭐                              │
│  - Compare all alternatives                                    │
│  - Find cheapest: Train = LKR 180                              │
│  - Alternative: Bus = LKR 150 (but 1h slower)                  │
│  Duration: 1.2s                                                │
│                                                                │
│  🤖 AGENT 6: Preference Analysis                               │
│  - MongoDB query: User history                                 │
│  - User prefers: Trains, 2nd class                             │
│  - Boost train option score                                    │
│  Duration: 0.6s                                                │
│                                                                │
│  🤖 AGENT 7: Local Knowledge                                   │
│  - Gemini LLM: Generate insights                               │
│  - Add context: "Temple of Tooth nearby"                       │
│  Duration: 1.5s                                                │
│                                                                │
│  🤖 AGENT 8: Route Optimization                                │
│  - Score all routes (time, cost, comfort)                      │
│  - Best: Train #1005 (score: 0.87)                             │
│  Duration: 1.0s                                                │
│                                                                │
│  🤖 AGENT 9: Disruption Monitoring                             │
│  - Weather API: Light rain expected                            │
│  - Community reports: No major issues                          │
│  - AI analysis: Minor delay possible                           │
│  Duration: 0.8s                                                │
│                                                                │
│  🤖 AGENT 10: Response Compilation                             │
│  - Format final response                                       │
│  - Include all data from agents                                │
│  Duration: 0.5s                                                │
│                                                                │
│  TOTAL PROCESSING TIME: 4.2 seconds                            │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (Database Operations)                      │
│                                                                │
│  MongoDB Operations:                                           │
│  1. INSERT into route_history                                  │
│  2. UPDATE user analytics                                      │
│  3. INSERT into activity_logs                                  │
│                                                                │
│  Redis Cache:                                                  │
│  1. CACHE route result (5 min TTL)                             │
│  2. UPDATE user session                                        │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND (Response to Client)                       │
│  JSON Response:                                                │
│  {                                                             │
│    "status": "success",                                        │
│    "request_id": "req_abc123",                                 │
│    "processing_time": 4.2,                                     │
│    "agents_used": [10 agent names],                            │
│    "response": {                                               │
│      "best_route": {                                           │
│        "route_id": "route_001",                                │
│        "mode": "train",                                        │
│        "train_number": "1005",                                 │
│        "duration_text": "3 hours 15 mins",                     │
│        "distance_text": "115 km",                              │
│        "estimated_cost": 180,                                  │
│        "cost_currency": "LKR",                                 │
│        "class": "2nd Class",                                   │
│        "recommendation_score": 0.87,                           │
│        "is_recommended": true,                                 │
│        "steps": [...]                                          │
│      },                                                        │
│      "all_routes": [route1, route2, route3],                   │
│      "ai_disruption_analysis": "Light rain...",                │
│      "destination_summary": "Temple of Tooth..."               │
│    }                                                           │
│  }                                                             │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              MOBILE APP (Response Processing)                   │
│  - Receives JSON response                                      │
│  - Transforms to UI format                                     │
│  - Stores in AppContext                                        │
│  - Saves to AsyncStorage (offline access)                      │
│  - Navigates to Routes screen                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              MOBILE APP (Display Results)                       │
│  Routes Screen shows:                                          │
│                                                                │
│  ┌────────────────────────────────────────────────────┐        │
│  │ 🚂 Train #1005 → Kandy          ⭐ AI Recommended │        │
│  │ ⏱️ 3h 15min  📏 115 km  💰 LKR 180                │        │
│  │                                                   │        │
│  │ 📍 Steps:                                         │        │
│  │ 1. Walk to Colombo Fort Station (5 min)          │        │
│  │ 2. Board Train #1005 - 10:30 AM                   │        │
│  │ 3. Journey to Kandy - 3h 10min                    │        │
│  │ 4. Arrive Kandy Station - 1:40 PM                 │        │
│  │                                                   │        │
│  │ 💡 AI Insights:                                   │        │
│  │ "Most scenic route - enjoy mountain views!"       │        │
│  │ "Light rain expected - carry umbrella"            │        │
│  │ "Temple of Tooth nearby - remove shoes"           │        │
│  │                                                   │        │
│  │ [⭐ Save] [🗺️ View Map] [▶️ Start]              │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                │
│  Alternative Routes:                                           │
│  • Bus Route 1-1: LKR 150, 4h 30min                            │
│  • Uber: LKR 12,500, 2h 45min                                  │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│              ADMIN DASHBOARD (Real-Time Update)                 │
│  - Dashboard receives WebSocket notification                   │
│  - Updates statistics:                                         │
│    • Total Trips: 5,832 → 5,833                                │
│    • Active Users: 892 → 893                                   │
│  - Adds to recent activity feed:                               │
│    "user@example.com planned route (Colombo → Kandy)"         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Key Integration Points

### **1. Authentication Flow**

```
Mobile App → POST /api/v1/auth/login
           ↓
Backend    → Verify credentials in MongoDB
           → Generate JWT tokens
           ↓
Mobile App ← Receives access_token + refresh_token
           → Stores in AsyncStorage
           → All future requests include token

Admin Dashboard → Same flow but requires role="admin"
```

### **2. Route Planning Flow**

```
Mobile App → POST /api/v1/travel/plan-route
           ↓
Backend    → Run 10 AI agents (LangGraph)
           → Query MongoDB (fares, preferences)
           → Call Google Maps API
           → Call Weather API
           → Call Gemini LLM
           → Save to route_history
           ↓
Mobile App ← Receive route recommendations
           → Display in UI
           → Save to AsyncStorage
```

### **3. Real-Time Updates Flow**

```
Mobile App → WebSocket connect ws://backend:8000/api/v1/ws
           ↓
Backend    → Store connection
           → Monitor for disruptions
           → On new disruption:
             → Send to all connected clients
           ↓
Mobile App ← Receive disruption alert
           → Show push notification
           → Update active route
```

### **4. Admin Operations Flow**

```
Admin Dashboard → POST /api/v1/admin/notifications/broadcast
                ↓
Backend         → Get all user tokens from MongoDB
                → Call push notification service
                → Send to all devices
                ↓
Mobile Apps     ← Receive push notification
                → Display alert
```

---

## 📊 Summary

### **Backend is responsible for:**
✅ API Gateway (FastAPI)
✅ 10 AI Agents (LangGraph)
✅ RAG Chatbot (ChromaDB + Gemini)
✅ Database operations (MongoDB)
✅ Caching (Redis)
✅ Authentication (JWT)
✅ External API integration
✅ WebSocket server

### **Mobile App is responsible for:**
✅ User interface
✅ Route planning UI
✅ Agent visualization
✅ Chatbot interface
✅ Community reporting
✅ Offline storage
✅ Push notifications
✅ Real-time updates

### **Admin Dashboard is responsible for:**
✅ System monitoring
✅ User management
✅ Analytics visualization
✅ AI agent monitoring
✅ Push notification broadcasting
✅ Community report moderation

---

**All three components work together seamlessly to provide the complete Smart Transit Companion experience! 🚀**
