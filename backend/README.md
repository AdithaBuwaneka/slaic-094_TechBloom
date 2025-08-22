# Transit Companion Backend

A FastAPI backend application with MongoDB database integration for the Transit Companion app.

## Features

- FastAPI web framework with automatic API documentation
- MongoDB database connection using Motor (async driver)
- Health check endpoint with database status monitoring
- Database connection endpoint with collections info
- Welcome endpoint with backend information
- CORS middleware enabled for any frontend URL
- Environment-based configuration with .env support
- Production-ready with uvicorn ASGI server

## Project Structure

```
BACKEND/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # Database connection
│   │   └── __init__.py
│   ├── main.py                # FastAPI app initialization
│   └── __init__.py
├── .env.example               # Environment variables template
├── .gitignore                # Git ignore rules
├── requirements.txt          # Python dependencies
├── run.py                    # Development server runner
├── start.bat                 # Windows startup script
└── README.md                 # This file
```

## Setup

### Prerequisites

- Python 3.8+
- MongoDB database

### Installation

1. Clone the repository and navigate to the backend directory:
   ```bash
   cd BACKEND
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note**: The backend uses `motor` and `pymongo` for MongoDB connection.

5. Set up environment variables:
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` file with your database configuration:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=transit_companion_db
   SECRET_KEY=your-secret-key-here-change-in-production
   BACKEND_CORS_ORIGINS=["*"]
   ```
   
   **Important**: Make sure MongoDB is running and accessible at the specified URL.

### Running the Application

#### Development Mode

```bash
python run.py
```

Or use the Windows batch file:
```bash
start.bat
```

The API will be available at: `http://localhost:8000`

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Welcome
- **GET** `/api/v1/`
  - Returns welcome message and backend information
  - Response:
    ```json
    {
      "message": "Welcome to Transit Companion Backend API",
      "app_name": "Transit Companion Backend",
      "version": "1.0.0",
      "status": "running"
    }
    ```

### Health Check
- **GET** `/api/v1/health`
  - Returns application and database health status
  - Response (healthy):
    ```json
    {
      "status": "healthy",
      "database": "connected",
      "mongodb_url_configured": true,
      "database_name": "transit_companion_db"
    }
    ```
  - Response (degraded):
    ```json
    {
      "status": "degraded",
      "database": "connection failed",
      "mongodb_url_configured": true,
      "database_name": "transit_companion_db"
    }
    ```

### Database Connection
- **GET** `/api/v1/db-connection`
  - Returns detailed database connection status and collections info
  - Response (connected):
    ```json
    {
      "connection_status": "connected",
      "database_name": "transit_companion_db",
      "mongodb_url": "mongodb://localhost:27017",
      "collections_count": 0,
      "collections": []
    }
    ```

## API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Configuration

The application uses environment variables for configuration. Key settings:

- `MONGODB_URL`: MongoDB connection string (format: `mongodb://host:port`)
- `DATABASE_NAME`: MongoDB database name (default: transit_companion_db)
- `SECRET_KEY`: Secret key for security operations
- `DEBUG`: Enable/disable debug mode (default: True)
- `API_V1_STR`: API version prefix (default: /api/v1)
- `APP_NAME`: Application name (default: Transit Companion Backend)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins - set to `["*"]` to allow any frontend URL

## Development

### Adding New Endpoints

1. Add new routes in `app/api/routes.py`
2. Import and include the router in `app/main.py`

### Database Operations

Currently, the backend provides basic MongoDB connectivity testing and collections listing. Motor (async MongoDB driver) is used for database connections. Database operations can be added by implementing MongoDB models and services.

## Testing

### Quick Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Test Welcome Endpoint
```bash
curl http://localhost:8000/api/v1/
```

### Test Database Connection
```bash
curl http://localhost:8000/api/v1/db-connection
```

### Access Interactive Documentation
Open in browser: `http://localhost:8000/docs`

## Troubleshooting

### Database Connection Issues

1. **MongoDB Server**: Verify MongoDB is running on the specified host and port
2. **Connection URL**: Check MONGODB_URL in `.env` file
3. **Database Name**: Ensure DATABASE_NAME is correctly configured
4. **Network**: Check firewall/network connectivity to MongoDB host
5. **Health Check**: Use `/api/v1/health` and `/api/v1/db-connection` endpoints to see specific error messages

### Common Error Messages

- `"motor not installed"` → Run `pip install motor pymongo`
- `"connection refused"` → MongoDB server not running or wrong host/port
- `"ServerSelectionTimeoutError"` → MongoDB server not accessible or firewall blocking connection

### Import Errors

Make sure you're in the correct directory and virtual environment is activated:
```bash
# Check current directory
pwd

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
```

## Current Status

✅ **API Server**: Running on `http://localhost:8000`  
✅ **Database**: Connected to MongoDB (`transit_companion_db`)  
✅ **Health Check**: Operational at `/api/v1/health`  
✅ **Database Connection**: Detailed info at `/api/v1/db-connection`  
✅ **Welcome Endpoint**: Available at `/api/v1/`  
✅ **CORS**: Enabled for all origins  
✅ **Documentation**: Available at `/docs`