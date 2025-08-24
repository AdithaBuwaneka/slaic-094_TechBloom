from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import hashlib
import secrets
import jwt
from email_validator import validate_email
import bcrypt

from app.models.user_management import (
    User, UserPreferences, UserSession, UserActivity, AuthToken,
    PasswordResetRequest, UserVerification, UserRegistrationRequest,
    UserLoginRequest, UserProfileUpdateRequest, UserStats, UserFeedback,
    UserNotification, UserDevice, UserRole, UserStatus, LanguagePreference,
    NotificationPreference
)
from app.models.transport_data import Location


class UserService:
    def __init__(self):
        # Configuration
        self.jwt_secret = "your-secret-key-here"  # Should be in environment variables
        self.jwt_algorithm = "HS256"
        self.access_token_expire_hours = 24
        self.refresh_token_expire_days = 30
        self.password_reset_expire_hours = 1
        self.email_verification_expire_hours = 24

    def _hash_password(self, password: str) -> tuple[str, str]:
        """Generate password hash and salt"""
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8'), salt.decode('utf-8')

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    def _generate_token(self, user_id: str, token_type: str = "access") -> tuple[str, datetime]:
        """Generate JWT token"""
        if token_type == "access":
            expire_delta = timedelta(hours=self.access_token_expire_hours)
        elif token_type == "refresh":
            expire_delta = timedelta(days=self.refresh_token_expire_days)
        else:
            expire_delta = timedelta(hours=1)
        
        expires_at = datetime.utcnow() + expire_delta
        payload = {
            "user_id": user_id,
            "token_type": token_type,
            "exp": expires_at,
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token, expires_at

    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    async def register_user(self, registration_data: UserRegistrationRequest) -> Dict[str, Any]:
        """Register a new user"""
        try:
            # Check if user already exists (simulate database check)
            existing_user = await self._find_user_by_email_or_username(
                registration_data.email, registration_data.username
            )
            if existing_user:
                return {
                    "status": "error",
                    "message": "User with this email or username already exists"
                }
            
            # Hash password
            password_hash, salt = self._hash_password(registration_data.password)
            
            # Create user
            user = User(
                email=registration_data.email,
                username=registration_data.username,
                password_hash=password_hash,
                salt=salt,
                full_name=registration_data.full_name,
                phone_number=registration_data.phone_number,
                language_preference=registration_data.language_preference,
                notification_preferences=registration_data.notification_preferences,
                marketing_consent=registration_data.marketing_consent,
                data_sharing_consent=registration_data.data_sharing_consent,
                home_location=registration_data.home_location
            )
            
            # Generate email verification token
            verification_token = secrets.token_urlsafe(32)
            verification = UserVerification(
                user_id=user.user_id,
                verification_type="email",
                verification_token=verification_token,
                expires_at=datetime.utcnow() + timedelta(hours=self.email_verification_expire_hours)
            )
            
            # Create default preferences
            preferences = UserPreferences(user_id=user.user_id)
            
            # Log registration activity
            activity = UserActivity(
                user_id=user.user_id,
                activity_type="user_registration",
                activity_data={"registration_method": "email", "consent_marketing": registration_data.marketing_consent}
            )
            
            return {
                "status": "success",
                "message": "User registered successfully. Please verify your email.",
                "data": {
                    "user_id": user.user_id,
                    "email": user.email,
                    "username": user.username,
                    "verification_token": verification_token,
                    "verification_expires_at": verification.expires_at.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Registration failed: {str(e)}"
            }

    async def authenticate_user(self, login_data: UserLoginRequest) -> Dict[str, Any]:
        """Authenticate user login"""
        try:
            # Find user by email or username
            user = await self._find_user_by_email_or_username(
                login_data.username_or_email, login_data.username_or_email
            )
            
            if not user:
                return {
                    "status": "error",
                    "message": "Invalid credentials"
                }
            
            # Verify password
            if not self._verify_password(login_data.password, user.password_hash):
                return {
                    "status": "error",
                    "message": "Invalid credentials"
                }
            
            # Check user status
            if user.status != UserStatus.ACTIVE:
                if user.status == UserStatus.PENDING_VERIFICATION:
                    return {
                        "status": "error",
                        "message": "Please verify your email before logging in"
                    }
                elif user.status == UserStatus.SUSPENDED:
                    return {
                        "status": "error",
                        "message": "Account is suspended"
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Account is not active"
                    }
            
            # Generate tokens
            access_token, access_expires = self._generate_token(user.user_id, "access")
            refresh_token, refresh_expires = self._generate_token(user.user_id, "refresh")
            
            # Create session
            session_expire_hours = 720 if login_data.remember_me else 24  # 30 days vs 1 day
            session = UserSession(
                user_id=user.user_id,
                expires_at=datetime.utcnow() + timedelta(hours=session_expire_hours),
                device_id=login_data.device_id,
                login_method="password"
            )
            
            # Update user login stats
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            
            # Log login activity
            activity = UserActivity(
                user_id=user.user_id,
                session_id=session.session_id,
                activity_type="login",
                activity_data={
                    "login_method": "password",
                    "device_id": login_data.device_id,
                    "remember_me": login_data.remember_me
                }
            )
            
            return {
                "status": "success",
                "message": "Login successful",
                "data": {
                    "user": {
                        "user_id": user.user_id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role,
                        "language_preference": user.language_preference
                    },
                    "tokens": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "access_expires_at": access_expires.isoformat(),
                        "refresh_expires_at": refresh_expires.isoformat()
                    },
                    "session": {
                        "session_id": session.session_id,
                        "expires_at": session.expires_at.isoformat()
                    }
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Authentication failed: {str(e)}"
            }

    async def update_profile(self, user_id: str, update_data: UserProfileUpdateRequest) -> Dict[str, Any]:
        """Update user profile"""
        try:
            # Simulate finding and updating user
            user = await self._find_user_by_id(user_id)
            if not user:
                return {"status": "error", "message": "User not found"}
            
            # Update fields
            if update_data.full_name is not None:
                user.full_name = update_data.full_name
            if update_data.bio is not None:
                user.bio = update_data.bio
            if update_data.phone_number is not None:
                user.phone_number = update_data.phone_number
            if update_data.profile_picture_url is not None:
                user.profile_picture_url = update_data.profile_picture_url
            if update_data.home_location is not None:
                user.home_location = update_data.home_location
            if update_data.work_location is not None:
                user.work_location = update_data.work_location
            if update_data.language_preference is not None:
                user.language_preference = update_data.language_preference
            if update_data.accessibility_features is not None:
                user.accessibility_features = update_data.accessibility_features
            
            user.updated_at = datetime.utcnow()
            
            # Log activity
            activity = UserActivity(
                user_id=user_id,
                activity_type="profile_update",
                activity_data={"updated_fields": list(update_data.model_dump(exclude_unset=True).keys())}
            )
            
            return {
                "status": "success",
                "message": "Profile updated successfully",
                "data": {
                    "user_id": user.user_id,
                    "updated_at": user.updated_at.isoformat()
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Profile update failed: {str(e)}"
            }

    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        try:
            preferences = await self._get_user_preferences(user_id)
            return {
                "status": "success",
                "data": preferences.model_dump() if preferences else {}
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get preferences: {str(e)}"
            }

    async def update_user_preferences(self, user_id: str, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences"""
        try:
            preferences = UserPreferences(user_id=user_id, **preferences_data)
            
            # Log activity
            activity = UserActivity(
                user_id=user_id,
                activity_type="preferences_update",
                activity_data={"updated_preferences": list(preferences_data.keys())}
            )
            
            return {
                "status": "success",
                "message": "Preferences updated successfully",
                "data": preferences.model_dump()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Preferences update failed: {str(e)}"
            }

    async def verify_email(self, verification_token: str) -> Dict[str, Any]:
        """Verify user email"""
        try:
            # Find verification request
            verification = await self._find_verification_request(verification_token)
            if not verification or verification.status != "pending" or verification.expires_at < datetime.utcnow():
                return {"status": "error", "message": "Invalid or expired verification token"}
            
            # Update user status
            user = await self._find_user_by_id(verification.user_id)
            user.is_email_verified = True
            user.status = UserStatus.ACTIVE
            user.updated_at = datetime.utcnow()
            
            # Update verification
            verification.status = "completed"
            verification.verified_at = datetime.utcnow()
            
            # Log activity
            activity = UserActivity(
                user_id=user.user_id,
                activity_type="email_verification",
                activity_data={"verification_method": "email_token"}
            )
            
            return {
                "status": "success",
                "message": "Email verified successfully",
                "data": {
                    "user_id": user.user_id,
                    "is_email_verified": user.is_email_verified,
                    "status": user.status
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Email verification failed: {str(e)}"
            }

    async def get_user_stats(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            # Generate sample stats
            stats = UserStats(
                user_id=user_id,
                total_journeys=47,
                total_distance_km=234.5,
                total_time_saved_minutes=180,
                transport_mode_stats={
                    "bus": 25,
                    "train": 15,
                    "walking": 7
                },
                favorite_routes=["Route A", "Route B", "Metro Line 1"],
                searches_performed=156,
                alerts_received=23,
                notifications_sent=89,
                stats_period_start=datetime.utcnow() - timedelta(days=period_days),
                stats_period_end=datetime.utcnow()
            )
            
            return {
                "status": "success",
                "data": stats.model_dump()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get user stats: {str(e)}"
            }

    # Helper methods (simulate database operations)
    async def _find_user_by_email_or_username(self, email: str, username: str) -> Optional[User]:
        """Simulate finding user by email or username"""
        # In real implementation, this would query the database
        if email == "testuser@example.com" or username == "testuser":
            # Return a test user for login testing
            password_hash, salt = self._hash_password("password123")
            return User(
                user_id="user_test_123",
                email="testuser@example.com",
                username="testuser",
                password_hash=password_hash,
                salt=salt,
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                full_name="Test User"
            )
        return None

    async def _find_user_by_id(self, user_id: str) -> Optional[User]:
        """Simulate finding user by ID"""
        if user_id:
            return User(
                user_id=user_id,
                email="user@example.com",
                username="sampleuser",
                password_hash="$2b$12$dummy_hash",
                salt="$2b$12$dummy_salt",
                status=UserStatus.ACTIVE,
                is_email_verified=True
            )
        return None

    async def _get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """Simulate getting user preferences"""
        if user_id:
            return UserPreferences(user_id=user_id)
        return None

    async def _find_verification_request(self, verification_token: str) -> Optional[UserVerification]:
        """Simulate finding verification request"""
        if verification_token:
            return UserVerification(
                user_id="user_123",
                verification_type="email",
                verification_token=verification_token,
                status="pending",
                expires_at=datetime.utcnow() + timedelta(hours=24)
            )
        return None