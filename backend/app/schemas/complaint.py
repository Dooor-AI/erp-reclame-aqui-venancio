from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict


class ComplaintBase(BaseModel):
    """Base schema for complaint"""
    title: Optional[str] = None
    text: str
    user_name: Optional[str] = None
    complaint_date: Optional[datetime] = None
    status: Optional[str] = "Não respondida"
    category: Optional[str] = None
    location: Optional[str] = None


class ComplaintCreate(ComplaintBase):
    """Schema for creating a new complaint"""
    external_id: Optional[str] = None


class Complaint(ComplaintBase):
    """Schema for returning complaint data"""
    id: int
    external_id: Optional[str] = None

    # Store type and tags
    store_type: Optional[str] = None
    tags: Optional[List[str]] = None

    # Analysis fields
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    urgency_score: Optional[float] = None
    classification: Optional[List[str]] = None
    entities: Optional[Dict] = None

    # Company response from Reclame Aqui
    company_response_text: Optional[str] = None
    company_response_date: Optional[datetime] = None
    customer_evaluation: Optional[str] = None
    evaluation_date: Optional[datetime] = None

    # Response fields (AI generated)
    response_generated: Optional[str] = None
    response_edited: Optional[str] = None
    coupon_code: Optional[str] = None
    coupon_discount: Optional[int] = None
    response_sent: bool = False
    response_sent_at: Optional[datetime] = None

    # Timestamps
    scraped_at: datetime
    analyzed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComplaintStats(BaseModel):
    """Schema for statistics"""
    total: int
    by_sentiment: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    by_category: Dict[str, int] = {}
    by_ra_category: Dict[str, int] = {}
    avg_urgency: float = 0.0
