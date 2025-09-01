from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
from enum import Enum
import uuid

from app.models.user import User
from app.api.auth import get_current_user
from app.core.database import db

router = APIRouter()

class PaymentMethod(str, Enum):
    CARD = "card"
    MOBILE_MONEY = "mobile_money"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"

class SubscriptionPlan(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "LKR"
    payment_method: PaymentMethod
    description: str
    metadata: Dict[str, Any] = {}

class SubscriptionUpgrade(BaseModel):
    plan: SubscriptionPlan
    payment_method: PaymentMethod
    billing_cycle: str = "monthly"  # monthly, yearly

class RefundRequest(BaseModel):
    transaction_id: str
    reason: str
    amount: Optional[float] = None  # Partial refund amount

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free Plan",
        "price": 0,
        "features": [
            "Basic route planning",
            "5 AI queries per day",
            "Standard support"
        ],
        "limits": {
            "ai_queries_per_day": 5,
            "offline_maps": False,
            "premium_features": False
        }
    },
    "basic": {
        "name": "Basic Plan",
        "price": 500,  # LKR per month
        "features": [
            "Unlimited route planning",
            "50 AI queries per day",
            "Offline maps",
            "Priority support",
            "Fare optimization"
        ],
        "limits": {
            "ai_queries_per_day": 50,
            "offline_maps": True,
            "premium_features": False
        }
    },
    "premium": {
        "name": "Premium Plan", 
        "price": 1200,  # LKR per month
        "features": [
            "Everything in Basic",
            "Unlimited AI queries",
            "Real-time tracking",
            "Advanced analytics",
            "Voice assistance",
            "24/7 support"
        ],
        "limits": {
            "ai_queries_per_day": -1,  # Unlimited
            "offline_maps": True,
            "premium_features": True
        }
    },
    "enterprise": {
        "name": "Enterprise Plan",
        "price": 2500,  # LKR per month
        "features": [
            "Everything in Premium",
            "Admin dashboard",
            "Team management",
            "Custom integrations",
            "Dedicated support"
        ],
        "limits": {
            "ai_queries_per_day": -1,
            "offline_maps": True,
            "premium_features": True,
            "admin_features": True
        }
    }
}

@router.get("/plans")
async def get_subscription_plans():
    """Get all available subscription plans"""
    return {
        "plans": SUBSCRIPTION_PLANS,
        "currencies": ["LKR", "USD"],
        "billing_cycles": ["monthly", "yearly"]
    }

@router.get("/user/subscription")
async def get_user_subscription(current_user: User = Depends(get_current_user)):
    """Get user's current subscription details"""
    try:
        # Get user's subscription from database
        subscription = await db.users_collection.find_one(
            {"_id": current_user.id},
            {"subscription": 1, "subscription_expires": 1, "usage_limits": 1}
        )
        
        current_plan = subscription.get("subscription", "free")
        expires_at = subscription.get("subscription_expires")
        usage_limits = subscription.get("usage_limits", {})
        
        # Check if subscription is expired
        is_expired = False
        if expires_at and expires_at < datetime.utcnow():
            is_expired = True
            current_plan = "free"
        
        # Get usage stats for current month
        start_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        usage_stats = await db.analytics_events_collection.count_documents({
            "user_id": current_user.id,
            "event_name": "ai_query",
            "timestamp": {"$gte": start_of_month}
        })
        
        return {
            "current_plan": current_plan,
            "plan_details": SUBSCRIPTION_PLANS.get(current_plan, SUBSCRIPTION_PLANS["free"]),
            "expires_at": expires_at.isoformat() if expires_at else None,
            "is_expired": is_expired,
            "usage_this_month": {
                "ai_queries": usage_stats,
                "limit": SUBSCRIPTION_PLANS[current_plan]["limits"]["ai_queries_per_day"] * 30
            },
            "features_enabled": SUBSCRIPTION_PLANS[current_plan]["limits"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get subscription details: {str(e)}"
        )

@router.post("/subscribe")
async def upgrade_subscription(
    subscription_data: SubscriptionUpgrade,
    current_user: User = Depends(get_current_user)
):
    """Upgrade user's subscription plan"""
    try:
        plan_details = SUBSCRIPTION_PLANS.get(subscription_data.plan)
        if not plan_details:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid subscription plan"
            )
        
        # Calculate amount based on billing cycle
        amount = plan_details["price"]
        if subscription_data.billing_cycle == "yearly":
            amount *= 10  # 20% discount for yearly
        
        # Create payment transaction
        transaction_id = str(uuid.uuid4())
        
        transaction = {
            "transaction_id": transaction_id,
            "user_id": current_user.id,
            "type": "subscription",
            "amount": amount,
            "currency": "LKR",
            "payment_method": subscription_data.payment_method,
            "status": TransactionStatus.PENDING,
            "description": f"Subscription upgrade to {plan_details['name']}",
            "plan": subscription_data.plan,
            "billing_cycle": subscription_data.billing_cycle,
            "created_at": datetime.utcnow(),
            "metadata": {
                "plan_name": plan_details["name"],
                "features": plan_details["features"]
            }
        }
        
        # Insert transaction
        await db.analytics_events_collection.insert_one({
            "event_type": "payment",
            "event_name": "subscription_upgrade_initiated",
            "user_id": current_user.id,
            "properties": transaction,
            "timestamp": datetime.utcnow()
        })
        
        # Simulate payment processing (in real app, integrate with payment gateway)
        # For demo purposes, we'll mark it as completed immediately
        transaction["status"] = TransactionStatus.COMPLETED
        transaction["processed_at"] = datetime.utcnow()
        
        # Update user's subscription
        expires_at = datetime.utcnow()
        if subscription_data.billing_cycle == "monthly":
            expires_at += timedelta(days=30)
        else:  # yearly
            expires_at += timedelta(days=365)
        
        await db.users_collection.update_one(
            {"_id": current_user.id},
            {
                "$set": {
                    "subscription": subscription_data.plan,
                    "subscription_expires": expires_at,
                    "billing_cycle": subscription_data.billing_cycle,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send confirmation notification
        notification = {
            "user_id": current_user.id,
            "title": "Subscription Upgraded!",
            "body": f"Welcome to {plan_details['name']}! Your premium features are now active.",
            "data": {
                "type": "subscription",
                "plan": subscription_data.plan,
                "transaction_id": transaction_id
            },
            "notification_type": "subscription",
            "sent_at": datetime.utcnow()
        }
        await db.notifications_collection.insert_one(notification)
        
        return {
            "message": "Subscription upgraded successfully",
            "transaction_id": transaction_id,
            "plan": subscription_data.plan,
            "expires_at": expires_at.isoformat(),
            "amount_paid": amount,
            "features_unlocked": plan_details["features"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Subscription upgrade failed: {str(e)}"
        )

@router.post("/pay")
async def process_payment(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_user)
):
    """Process a one-time payment (for bookings, top-ups, etc.)"""
    try:
        transaction_id = str(uuid.uuid4())
        
        # Validate payment method
        if payment_data.payment_method not in PaymentMethod:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment method"
            )
        
        # Create transaction record
        transaction = {
            "transaction_id": transaction_id,
            "user_id": current_user.id,
            "type": "payment",
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "payment_method": payment_data.payment_method,
            "status": TransactionStatus.PROCESSING,
            "description": payment_data.description,
            "created_at": datetime.utcnow(),
            "metadata": payment_data.metadata
        }
        
        # Log transaction initiation
        await db.analytics_events_collection.insert_one({
            "event_type": "payment",
            "event_name": "payment_initiated",
            "user_id": current_user.id,
            "properties": transaction,
            "timestamp": datetime.utcnow()
        })
        
        # Simulate payment processing based on payment method
        if payment_data.payment_method == PaymentMethod.MOBILE_MONEY:
            # In real implementation, integrate with mobile money API (Dialog, Mobitel, etc.)
            payment_result = await _process_mobile_money_payment(transaction)
        elif payment_data.payment_method == PaymentMethod.CARD:
            # In real implementation, integrate with card processing API
            payment_result = await _process_card_payment(transaction)
        else:
            # Other payment methods
            payment_result = await _process_generic_payment(transaction)
        
        # Update transaction status
        transaction["status"] = payment_result["status"]
        transaction["processed_at"] = datetime.utcnow()
        transaction["gateway_response"] = payment_result.get("gateway_response", {})
        
        # Log final transaction status
        await db.analytics_events_collection.insert_one({
            "event_type": "payment",
            "event_name": f"payment_{payment_result['status']}",
            "user_id": current_user.id,
            "properties": transaction,
            "timestamp": datetime.utcnow()
        })
        
        if payment_result["status"] == TransactionStatus.COMPLETED:
            # Send success notification
            notification = {
                "user_id": current_user.id,
                "title": "Payment Successful",
                "body": f"Your payment of {payment_data.amount} {payment_data.currency} has been processed successfully.",
                "data": {
                    "type": "payment",
                    "transaction_id": transaction_id,
                    "amount": payment_data.amount
                },
                "notification_type": "payment",
                "sent_at": datetime.utcnow()
            }
            await db.notifications_collection.insert_one(notification)
        
        return {
            "transaction_id": transaction_id,
            "status": payment_result["status"],
            "message": payment_result.get("message", "Payment processed"),
            "amount": payment_data.amount,
            "currency": payment_data.currency,
            "processed_at": transaction["processed_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )

@router.get("/transactions")
async def get_user_transactions(
    current_user: User = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    transaction_type: Optional[str] = Query(None)
):
    """Get user's transaction history"""
    try:
        query = {
            "user_id": current_user.id,
            "event_type": "payment"
        }
        
        if transaction_type:
            query["properties.type"] = transaction_type
        
        # Get transactions from analytics collection
        transactions_cursor = db.analytics_events_collection.find(query)\
            .sort("timestamp", -1)\
            .skip(offset)\
            .limit(limit)
        
        transactions = []
        async for transaction in transactions_cursor:
            props = transaction.get("properties", {})
            transactions.append({
                "transaction_id": props.get("transaction_id"),
                "type": props.get("type"),
                "amount": props.get("amount"),
                "currency": props.get("currency"),
                "status": props.get("status"),
                "description": props.get("description"),
                "payment_method": props.get("payment_method"),
                "created_at": transaction.get("timestamp").isoformat(),
                "processed_at": props.get("processed_at").isoformat() if props.get("processed_at") else None
            })
        
        total = await db.analytics_events_collection.count_documents(query)
        
        return {
            "transactions": transactions,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transactions: {str(e)}"
        )

@router.post("/refund")
async def request_refund(
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_user)
):
    """Request a refund for a transaction"""
    try:
        # Find the original transaction
        original_transaction = await db.analytics_events_collection.find_one({
            "user_id": current_user.id,
            "event_type": "payment",
            "properties.transaction_id": refund_data.transaction_id
        })
        
        if not original_transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found"
            )
        
        original_props = original_transaction.get("properties", {})
        
        # Check if refund is eligible (within 30 days, completed status)
        if original_props.get("status") != TransactionStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only completed transactions can be refunded"
            )
        
        transaction_date = original_transaction.get("timestamp", datetime.utcnow())
        if (datetime.utcnow() - transaction_date).days > 30:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund window has expired (30 days)"
            )
        
        refund_amount = refund_data.amount or original_props.get("amount", 0)
        refund_id = str(uuid.uuid4())
        
        # Create refund record
        refund_transaction = {
            "transaction_id": refund_id,
            "original_transaction_id": refund_data.transaction_id,
            "user_id": current_user.id,
            "type": "refund",
            "amount": refund_amount,
            "currency": original_props.get("currency", "LKR"),
            "status": TransactionStatus.PROCESSING,
            "reason": refund_data.reason,
            "created_at": datetime.utcnow()
        }
        
        # Log refund request
        await db.analytics_events_collection.insert_one({
            "event_type": "payment",
            "event_name": "refund_requested",
            "user_id": current_user.id,
            "properties": refund_transaction,
            "timestamp": datetime.utcnow()
        })
        
        # In real implementation, process refund through payment gateway
        # For demo, we'll mark as completed
        refund_transaction["status"] = TransactionStatus.COMPLETED
        refund_transaction["processed_at"] = datetime.utcnow()
        
        # Send confirmation notification
        notification = {
            "user_id": current_user.id,
            "title": "Refund Processed",
            "body": f"Your refund of {refund_amount} LKR has been processed and will appear in your account within 3-5 business days.",
            "data": {
                "type": "refund",
                "transaction_id": refund_id,
                "amount": refund_amount
            },
            "notification_type": "payment",
            "sent_at": datetime.utcnow()
        }
        await db.notifications_collection.insert_one(notification)
        
        return {
            "message": "Refund processed successfully",
            "refund_id": refund_id,
            "amount": refund_amount,
            "status": "completed",
            "estimated_arrival": "3-5 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refund processing failed: {str(e)}"
        )

# Helper functions for payment processing (mock implementations)
async def _process_mobile_money_payment(transaction: dict) -> dict:
    """Process mobile money payment (mock implementation)"""
    # In real implementation, integrate with Dialog, Mobitel, Hutch APIs
    return {
        "status": TransactionStatus.COMPLETED,
        "message": "Mobile money payment successful",
        "gateway_response": {"provider": "dialog", "reference": "DLG12345"}
    }

async def _process_card_payment(transaction: dict) -> dict:
    """Process card payment (mock implementation)"""
    # In real implementation, integrate with Stripe, PayHere, or local payment processor
    return {
        "status": TransactionStatus.COMPLETED,
        "message": "Card payment successful",
        "gateway_response": {"provider": "payhere", "reference": "PH98765"}
    }

async def _process_generic_payment(transaction: dict) -> dict:
    """Process other payment methods (mock implementation)"""
    return {
        "status": TransactionStatus.COMPLETED,
        "message": "Payment successful",
        "gateway_response": {"provider": "generic", "reference": "GEN54321"}
    }

@router.get("/methods")
async def get_payment_methods():
    """Get available payment methods for Sri Lankan users"""
    return {
        "payment_methods": [
            {
                "id": "mobile_money",
                "name": "Mobile Money",
                "providers": ["Dialog", "Mobitel", "Hutch"],
                "description": "Pay using your mobile account balance",
                "fees": "Free for amounts under 5000 LKR"
            },
            {
                "id": "card",
                "name": "Credit/Debit Card",
                "providers": ["Visa", "Mastercard", "American Express"],
                "description": "Pay using your bank card",
                "fees": "2.5% processing fee"
            },
            {
                "id": "bank_transfer",
                "name": "Bank Transfer",
                "providers": ["Commercial Bank", "Peoples Bank", "BOC", "HNB"],
                "description": "Direct bank account transfer",
                "fees": "Free"
            },
            {
                "id": "digital_wallet",
                "name": "Digital Wallet",
                "providers": ["eZ Cash", "mCash", "Genie"],
                "description": "Pay using your digital wallet",
                "fees": "1% processing fee"
            }
        ],
        "supported_currencies": ["LKR", "USD"]
    }