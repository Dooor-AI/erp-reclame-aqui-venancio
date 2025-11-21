from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.models import Complaint
from app.schemas.complaint import ComplaintCreate
from typing import List, Optional, Dict
from datetime import datetime


def create_complaint(db: Session, complaint: ComplaintCreate) -> Complaint:
    """Create a new complaint"""
    db_complaint = Complaint(**complaint.model_dump())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint


def get_complaint(db: Session, complaint_id: int) -> Optional[Complaint]:
    """Get a complaint by ID"""
    return db.query(Complaint).filter(Complaint.id == complaint_id).first()


def get_complaints(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    sentiment: Optional[str] = None,
    status: Optional[str] = None
) -> List[Complaint]:
    """Get complaints with optional filters"""
    query = db.query(Complaint)

    if sentiment:
        query = query.filter(Complaint.sentiment == sentiment)
    if status:
        query = query.filter(Complaint.status == status)

    return query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit).all()


def get_complaints_by_sentiment(db: Session, sentiment: str) -> List[Complaint]:
    """Get complaints by sentiment"""
    return db.query(Complaint).filter(Complaint.sentiment == sentiment).all()


def get_complaint_by_external_id(db: Session, external_id: str) -> Optional[Complaint]:
    """Get complaint by external ID (from Reclame Aqui)"""
    return db.query(Complaint).filter(Complaint.external_id == external_id).first()


def update_complaint_analysis(db: Session, complaint_id: int, **kwargs) -> Optional[Complaint]:
    """Update complaint with analysis data (used by Chat B)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        for key, value in kwargs.items():
            if hasattr(complaint, key):
                setattr(complaint, key, value)
        complaint.analyzed_at = datetime.now()
        db.commit()
        db.refresh(complaint)
    return complaint


def update_complaint_response(db: Session, complaint_id: int, **kwargs) -> Optional[Complaint]:
    """Update complaint with response data (used by Chat C)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if complaint:
        for key, value in kwargs.items():
            if hasattr(complaint, key):
                setattr(complaint, key, value)
        db.commit()
        db.refresh(complaint)
    return complaint


def bulk_create_complaints(db: Session, complaints: List[Dict]) -> int:
    """Bulk create complaints (for scraper)"""
    count = 0
    for complaint_data in complaints:
        # Check if already exists by external_id
        external_id = complaint_data.get('external_id')
        if external_id:
            existing = get_complaint_by_external_id(db, external_id)
            if existing:
                continue

        db_complaint = Complaint(**complaint_data)
        db.add(db_complaint)
        count += 1

    db.commit()
    return count


def get_stats(db: Session) -> Dict:
    """Get statistics about complaints"""
    total = db.query(Complaint).count()

    # By sentiment
    sentiments = db.query(
        Complaint.sentiment,
        func.count(Complaint.id)
    ).group_by(Complaint.sentiment).all()
    by_sentiment = {s[0] if s[0] else 'Unknown': s[1] for s in sentiments}

    # By status
    statuses = db.query(
        Complaint.status,
        func.count(Complaint.id)
    ).group_by(Complaint.status).all()
    by_status = {s[0] if s[0] else 'Unknown': s[1] for s in statuses}

    # By category (using tags from AI analysis)
    complaints_with_tags = db.query(Complaint).filter(
        Complaint.tags.isnot(None)
    ).all()

    category_counts = {}
    for complaint in complaints_with_tags:
        if complaint.tags:
            for tag in complaint.tags:
                category_counts[tag] = category_counts.get(tag, 0) + 1

    by_category = category_counts if category_counts else {'Sem categoria': db.query(Complaint).count()}

    # By Reclame Aqui category (original category field from RA)
    ra_categories = db.query(
        Complaint.category,
        func.count(Complaint.id)
    ).group_by(Complaint.category).all()
    by_ra_category = {c[0] if c[0] else 'Sem categoria': c[1] for c in ra_categories}

    # Average urgency
    avg_urgency = db.query(func.avg(Complaint.urgency_score)).scalar() or 0.0

    return {
        'total': total,
        'by_sentiment': by_sentiment,
        'by_status': by_status,
        'by_category': by_category,
        'by_ra_category': by_ra_category,
        'avg_urgency': float(avg_urgency)
    }
