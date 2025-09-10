# 🖥️ Smart Transit Companion - Admin Dashboard

**Enterprise-Grade Administration Panel for Sri Lankan Transit System**

A comprehensive Next.js admin dashboard with real-time analytics, user management, AI agent monitoring, and system administration for the Smart Transit Companion platform.

## 🏆 **SLAIC 2025 Admin Excellence**

### ✅ **Competition Requirements Met**
- **📊 AI Agent System Monitoring** - Visual workflow diagrams and performance metrics
- **👥 User Management** - Complete CRUD operations with advanced filtering
- **📈 Advanced Analytics** - Interactive data visualizations and insights
- **🇱🇰 Sri Lankan Context** - Localized metrics and cultural considerations
- **🔔 Push Notification System** - Broadcast messaging with templates
- **🏗️ Enterprise Architecture** - Scalable, secure, and maintainable design

## 🚀 **Core Features**

### 📈 **Dashboard Overview**
- **Real-time System Statistics** - Live user count, trips, community reports
- **System Health Monitoring** - Database, API services, and infrastructure status
- **Recent Activity Feed** - User actions with timestamps and role information
- **Performance Metrics** - Response times, uptime, and system efficiency
- **Visual Status Indicators** - Color-coded health states and alerts

### 👥 **Advanced User Management**
- **Comprehensive User Listing** - Paginated views with search and filtering
- **Detailed User Profiles** - Travel statistics, preferences, and activity history
- **User Status Control** - Activate/deactivate accounts with audit trails
- **Role-based Management** - User and admin permission handling
- **Bulk Operations** - Mass user actions and data export capabilities
- **Advanced Search** - Real-time filtering by name, email, status, and role

### 🤖 **AI Agent System Monitoring**
- **Multi-Agent Workflow Visualization** - Dynamic Mermaid diagrams
- **Real-time Performance Tracking** - Individual agent metrics and success rates
- **System Statistics Dashboard** - Request processing, response times, usage patterns
- **Agent Health Monitoring** - Status tracking for all 10 AI agents
- **Performance Analytics** - Success rates, execution times, and optimization insights
- **Integrated Tools Status** - External service dependencies and health checks

### 📊 **Advanced Analytics & Insights**
- **Interactive Data Visualizations** - Recharts integration with multiple chart types
- **User Growth Analytics** - Line charts showing registration trends and patterns
- **Travel Mode Preferences** - Pie charts displaying transport mode distribution
- **API Usage Statistics** - Bar charts showing endpoint usage and performance
- **Time-based Filtering** - Configurable periods (7, 30, 90 days)
- **Sri Lankan Context Insights** - Localized data analysis and cultural metrics

### 🔔 **Smart Notification System**
- **Broadcast Push Notifications** - Send to all users or targeted segments
- **Predefined Message Templates** - Quick access to common notification types
- **Delivery Analytics** - Real-time tracking of notification performance
- **Best Practices Guidelines** - Built-in recommendations for effective messaging
- **Template Categories**:
  - System maintenance alerts
  - Weather and traffic updates
  - New feature announcements
  - Emergency notifications

### 👥 **Community Management**
- **User-Generated Content Moderation** - Review and manage community reports
- **Report Categorization** - Organize by type, priority, and verification status
- **Community Engagement Metrics** - Track participation and contribution levels
- **Content Quality Control** - Spam detection and content verification

### ⚙️ **System Administration**
- **Configuration Management** - System-wide settings and feature flags
- **Backup and Recovery** - Data protection and disaster recovery tools
- **Security Monitoring** - Login attempts, access logs, and security alerts
- **Performance Optimization** - System tuning and resource management

## 🛠️ **Technical Architecture**

### **Frontend Technologies**
- **Next.js 15.5.2** - Latest React framework with App Router
- **React 19** - Cutting-edge React with concurrent features
- **TypeScript** - Full type safety and enhanced developer experience
- **Tailwind CSS 3.4.17** - Modern utility-first CSS framework
- **Lucide React** - Beautiful and consistent icon system

### **Data Visualization**
- **Recharts 3.2.0** - Powerful React charting library
- **Mermaid 11.11.0** - Dynamic diagram generation for workflows
- **Interactive Charts** - Real-time data updates and user interactions
- **Responsive Design** - Charts adapt to different screen sizes

### **API Integration**
- **Axios HTTP Client** - Robust API communication with interceptors
- **JWT Authentication** - Secure token-based authentication system
- **Real-time Updates** - Polling and WebSocket integration
- **Error Handling** - Comprehensive error management and user feedback

### **State Management**
- **React Hooks** - Modern state management with useState and useEffect
- **Context API** - Global state sharing where needed
- **Local Storage** - Persistent user preferences and session data
- **Optimistic Updates** - Immediate UI feedback with server sync

## 🚦 **Getting Started**

### **Prerequisites**
- Node.js 18+ with npm/yarn
- Backend API running on `http://localhost:8000`
- Modern web browser (Chrome, Firefox, Safari, Edge)

### **Installation**

1. **Clone and Install Dependencies**
   ```bash
   git clone <repository-url>
   cd admin-dashboard
   npm install
   ```

2. **Environment Configuration**
   ```bash
   # Create .env.local file
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   # or with Turbopack (faster)
   npm run dev -- --turbo
   ```

4. **Access Dashboard**
   - Open `http://localhost:3000` in your browser
   - Login with demo credentials:
     - Email: `admin@example.com`
     - Password: `admin123456`

### **Production Build**
```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📱 **Dashboard Pages & Routes**

### **Authentication**
- **`/login`** - Admin login with demo credentials
- **Security Features**: JWT token management, session validation

### **Main Dashboard**
- **`/dashboard`** - System overview with real-time metrics
- **Components**: Stats cards, activity feed, system health

### **User Management**
- **`/dashboard/users`** - Complete user administration
- **Features**: Search, pagination, status management, detailed profiles

### **AI Agent Monitoring**
- **`/dashboard/agents`** - Multi-agent system visualization
- **Features**: Workflow diagrams, performance metrics, health monitoring

### **Analytics & Insights**
- **`/dashboard/analytics`** - Data visualization dashboard
- **Features**: Interactive charts, time filtering, Sri Lankan insights

### **Notification Management**
- **`/dashboard/notifications`** - Push notification system
- **Features**: Broadcast messaging, templates, delivery analytics

### **Community Reports**
- **`/dashboard/reports`** - User-generated content management
- **Features**: Report moderation, categorization, quality control

### **System Settings**
- **`/dashboard/settings`** - Configuration management
- **Features**: System preferences, feature flags, maintenance mode

## 🎨 **User Interface Design**

### **Design System**
- **Color Palette**: Professional blue primary with semantic colors
- **Typography**: Clean, readable fonts with proper hierarchy
- **Spacing**: Consistent 8px grid system
- **Components**: Reusable UI elements with consistent styling

### **Responsive Design**
- **Mobile-First Approach** - Works seamlessly on all devices
- **Breakpoint Strategy** - Tailwind responsive utilities
- **Touch-Friendly** - Proper sizing for mobile interactions
- **Progressive Enhancement** - Core functionality works everywhere

### **Accessibility Features**
- **ARIA Labels** - Proper semantic markup for screen readers
- **Keyboard Navigation** - Full keyboard accessibility support
- **Color Contrast** - WCAG compliant color combinations
- **Focus Management** - Clear focus indicators and logical tab order

## 📊 **Data Visualization Features**

### **Chart Types**
- **Line Charts** - Time-series data like user growth trends
- **Bar Charts** - Categorical comparisons like API usage by mode
- **Pie Charts** - Proportional data like travel mode preferences
- **Area Charts** - Cumulative metrics and trend analysis

### **Interactive Features**
- **Hover Tooltips** - Detailed information on data points
- **Zoom and Pan** - Detailed exploration of large datasets
- **Legend Interaction** - Toggle data series visibility
- **Real-time Updates** - Live data refresh without page reload

### **Export Capabilities**
- **PNG/JPEG Export** - High-quality chart images
- **CSV Data Export** - Raw data for further analysis
- **PDF Reports** - Formatted reports with charts and data

## 🔐 **Security & Authentication**

### **Authentication System**
- **JWT Tokens** - Secure, stateless authentication
- **Token Refresh** - Automatic session extension
- **Role-based Access** - Admin-only access control
- **Session Management** - Secure logout and session cleanup

### **API Security**
- **Request Interceptors** - Automatic token injection
- **Error Handling** - Secure error messages without data leakage
- **CORS Protection** - Cross-origin request security
- **Rate Limiting** - Backend rate limiting support

### **Data Protection**
- **Encrypted Storage** - Secure local storage of sensitive data
- **No Password Storage** - Tokens only, no credential persistence
- **Secure Endpoints** - All API calls require authentication
- **Input Sanitization** - XSS and injection attack prevention

## 📈 **Performance Optimization**

### **Frontend Performance**
- **Next.js App Router** - Server-side rendering and static generation
- **Code Splitting** - Automatic bundle optimization
- **Image Optimization** - Next.js Image component with lazy loading
- **Caching Strategy** - Efficient data caching and revalidation

### **API Integration**
- **Request Deduplication** - Avoid duplicate API calls
- **Background Updates** - Non-blocking data refresh
- **Optimistic UI** - Immediate feedback with server reconciliation
- **Error Recovery** - Automatic retry with exponential backoff

## 🧪 **Development & Testing**

### **Code Quality**
```bash
# Linting
npm run lint

# Type checking
npx tsc --noEmit

# Build verification
npm run build
```

### **Development Tools**
- **ESLint** - Code quality and consistency
- **TypeScript** - Type checking and IntelliSense
- **Prettier** - Automatic code formatting
- **Next.js DevTools** - Development debugging and optimization

## 🔧 **Configuration & Customization**

### **Environment Variables**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=true
NEXT_PUBLIC_ENABLE_NOTIFICATIONS=true
```

### **Theme Customization**
- **Tailwind Configuration** - Custom color schemes and spacing
- **Component Styling** - Consistent design system implementation
- **Dark Mode Support** - Toggle between light and dark themes
- **Brand Customization** - Easy logo and color scheme updates

## 🤝 **Contributing & Development**

### **Development Guidelines**
1. Follow TypeScript best practices
2. Use semantic commit messages
3. Implement proper error handling
4. Write comprehensive tests
5. Follow Next.js conventions

### **Code Standards**
- **Component Structure** - Consistent file organization
- **Naming Conventions** - Clear and descriptive names
- **API Integration** - Standardized service layers
- **State Management** - Efficient and predictable state updates

## 🔧 **Troubleshooting**

### **Common Issues**
1. **Backend Connection Errors**
   - Verify backend is running on port 8000
   - Check API URL in environment variables
   - Confirm admin credentials are correct

2. **Build Issues**
   - Clear Next.js cache: `rm -rf .next`
   - Update dependencies: `npm update`
   - Check TypeScript errors: `npx tsc --noEmit`

3. **Performance Issues**
   - Check browser console for errors
   - Verify API response times
   - Monitor network tab for slow requests

## 📚 **Documentation & Resources**

- [Next.js Documentation](https://nextjs.org/docs)
- [React 19 Features](https://react.dev/blog/2024/04/25/react-19)
- [Tailwind CSS Guide](https://tailwindcss.com/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Recharts Documentation](https://recharts.org/)

## 🏆 **SLAIC 2025 Admin Excellence**

This admin dashboard showcases:
- **🎯 Advanced AI System Monitoring** - Real-time multi-agent workflow visualization
- **📊 Data-Driven Decision Making** - Comprehensive analytics and insights
- **🇱🇰 Sri Lankan Context Integration** - Localized metrics and cultural considerations
- **👥 Enterprise User Management** - Professional admin tools and workflows
- **🔔 Smart Communication** - Intelligent notification system with templates
- **🏗️ Production-Ready Architecture** - Scalable, secure, and maintainable design
- **🎨 Professional UI/UX** - Modern, accessible, and responsive interface

---

**🏆 Built for SLAIC 2025 - Sri Lanka AI Challenge**  
**🇱🇰 Enterprise Admin Excellence - Made in Sri Lanka**