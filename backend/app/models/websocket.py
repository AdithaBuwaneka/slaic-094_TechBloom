from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from .transport_data import Location, TransportMode
from .disruption_management import DisruptionAlert


class MessageType(str, Enum):
    # Connection management
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Subscriptions
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    SUBSCRIPTION_CONFIRMED = "subscription_confirmed"
    
    # Live updates
    LIVE_UPDATE = "live_update"
    BATCH_UPDATE = "batch_update"
    
    # Disruptions
    DISRUPTION_ALERT = "disruption_alert"
    DISRUPTION_UPDATE = "disruption_update"
    DISRUPTION_RESOLVED = "disruption_resolved"
    
    # Route monitoring
    ROUTE_UPDATE = "route_update"
    SCHEDULE_CHANGE = "schedule_change"
    DELAY_NOTIFICATION = "delay_notification"
    
    # Location tracking
    LOCATION_UPDATE = "location_update"
    ARRIVAL_NOTIFICATION = "arrival_notification"
    DEPARTURE_NOTIFICATION = "departure_notification"
    
    # System notifications
    SYSTEM_ALERT = "system_alert"
    MAINTENANCE_NOTIFICATION = "maintenance_notification"
    
    # Error handling
    ERROR = "error"
    WARNING = "warning"


class SubscriptionType(str, Enum):
    ROUTE_MONITORING = "route_monitoring"
    DISRUPTION_ALERTS = "disruption_alerts"
    SCHEDULE_UPDATES = "schedule_updates"
    LOCATION_TRACKING = "location_tracking"
    FARE_CHANGES = "fare_changes"
    SYSTEM_NOTIFICATIONS = "system_notifications"
    ALL_UPDATES = "all_updates"


class ConnectionStatus(str, Enum):
    CONNECTING = "connecting"
    CONNECTED = "connected"
    SUBSCRIBED = "subscribed"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class WebSocketMessage(BaseModel):
    id: str = Field(default_factory=lambda: f"msg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    type: MessageType
    payload: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: Optional[str] = None
    recipient: Optional[str] = None
    correlation_id: Optional[str] = None  # For request-response correlation
    
    # Message metadata
    priority: int = Field(default=5, ge=1, le=10)  # 1 = highest priority
    ttl_seconds: Optional[int] = None  # Time to live
    retry_count: int = 0
    max_retries: int = 3


class SubscriptionRequest(BaseModel):
    subscription_type: SubscriptionType
    filters: Dict[str, Any] = {}
    
    # Location-based filtering
    location: Optional[Location] = None
    radius_km: Optional[float] = Field(default=10.0, gt=0)
    
    # Route-specific filtering
    route_ids: List[str] = []
    transport_modes: List[TransportMode] = []
    
    # Time-based filtering
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Update frequency
    update_interval_seconds: int = Field(default=30, ge=1, le=300)
    include_historical: bool = False


class ClientConnection(BaseModel):
    connection_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Connection details
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    last_ping: datetime = Field(default_factory=datetime.utcnow)
    status: ConnectionStatus = ConnectionStatus.CONNECTED
    
    # Subscriptions
    active_subscriptions: List[SubscriptionRequest] = []
    subscription_count: int = 0
    max_subscriptions: int = 10
    
    # Client information
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    platform: Optional[str] = None  # mobile, web, desktop
    app_version: Optional[str] = None
    
    # Performance tracking
    messages_sent: int = 0
    messages_received: int = 0
    bytes_sent: int = 0
    bytes_received: int = 0
    last_activity: datetime = Field(default_factory=datetime.utcnow)


class LiveUpdate(BaseModel):
    update_id: str = Field(default_factory=lambda: f"upd_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    update_type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Targeting
    subscription_types: List[SubscriptionType] = []
    target_locations: List[Location] = []
    target_routes: List[str] = []
    target_users: List[str] = []
    
    # Metadata
    source: str = "system"
    confidence_level: float = Field(default=0.8, ge=0.0, le=1.0)
    expires_at: Optional[datetime] = None


class RouteUpdateData(BaseModel):
    route_id: str
    transport_mode: TransportMode
    current_location: Optional[Location] = None
    next_stop: Optional[str] = None
    estimated_arrival: Optional[datetime] = None
    delay_minutes: int = 0
    occupancy_level: Optional[str] = None  # empty, moderate, full
    service_alerts: List[str] = []


class DisruptionAlertData(BaseModel):
    disruption: DisruptionAlert
    affected_routes: List[str] = []
    alternative_suggestions: List[str] = []
    estimated_resolution: Optional[datetime] = None


class ScheduleChangeData(BaseModel):
    route_id: str
    transport_mode: TransportMode
    change_type: str  # delay, cancellation, early_departure, route_change
    original_time: datetime
    new_time: Optional[datetime] = None
    reason: str
    affected_stops: List[str] = []


class LocationUpdateData(BaseModel):
    vehicle_id: str
    route_id: str
    transport_mode: TransportMode
    current_location: Location
    heading: Optional[float] = None  # Direction in degrees
    speed_kmh: Optional[float] = None
    next_stop_id: Optional[str] = None
    next_stop_eta: Optional[datetime] = None
    passenger_count: Optional[int] = None


class NotificationData(BaseModel):
    notification_id: str = Field(default_factory=lambda: f"notif_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    title: str
    message: str
    notification_type: str  # info, warning, alert, success
    
    # Targeting and delivery
    target_users: List[str] = []
    target_subscriptions: List[SubscriptionType] = []
    location_filters: List[Location] = []
    
    # Interaction options
    actions: List[Dict[str, str]] = []  # [{"label": "View Details", "action": "view_disruption"}]
    deep_link: Optional[str] = None
    
    # Scheduling
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    auto_dismiss_after_seconds: Optional[int] = None


class WebSocketError(BaseModel):
    error_code: str
    error_message: str
    details: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    recoverable: bool = True
    retry_after_seconds: Optional[int] = None


class ConnectionMetrics(BaseModel):
    total_connections: int = 0
    active_connections: int = 0
    subscriptions_count: int = 0
    messages_per_minute: float = 0.0
    
    # Performance metrics
    average_response_time_ms: float = 0.0
    message_queue_size: int = 0
    error_rate: float = 0.0
    
    # Resource usage
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    network_throughput_kbps: float = 0.0
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class WebSocketConfig(BaseModel):
    # Connection settings
    max_connections: int = 1000
    connection_timeout_seconds: int = 30
    ping_interval_seconds: int = 30
    ping_timeout_seconds: int = 10
    
    # Message settings
    max_message_size_bytes: int = 64 * 1024  # 64KB
    message_queue_size: int = 100
    batch_size: int = 10
    flush_interval_seconds: int = 1
    
    # Subscription settings
    max_subscriptions_per_client: int = 10
    default_update_interval_seconds: int = 30
    min_update_interval_seconds: int = 5
    max_update_interval_seconds: int = 300
    
    # Performance settings
    enable_compression: bool = True
    enable_heartbeat: bool = True
    enable_metrics: bool = True
    metrics_collection_interval_seconds: int = 60
    
    # Security settings
    enable_rate_limiting: bool = True
    max_messages_per_minute: int = 100
    require_authentication: bool = False
    allowed_origins: List[str] = ["*"]


class StreamingQuery(BaseModel):
    query_id: str = Field(default_factory=lambda: f"query_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    query_type: str
    parameters: Dict[str, Any] = {}
    
    # Streaming settings
    stream_updates: bool = True
    update_interval_seconds: int = 30
    max_duration_seconds: Optional[int] = None
    
    # Filtering
    filters: Dict[str, Any] = {}
    location_filter: Optional[Location] = None
    radius_km: Optional[float] = 10.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None


class BatchUpdateMessage(BaseModel):
    batch_id: str = Field(default_factory=lambda: f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}")
    updates: List[LiveUpdate] = []
    batch_size: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sequence_number: int = 0
    is_final_batch: bool = True