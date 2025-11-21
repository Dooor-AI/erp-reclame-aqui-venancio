from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import crud
from app.schemas.complaint import Complaint, ComplaintCreate, ComplaintStats
from app.core.database import get_db

router = APIRouter(prefix="/complaints", tags=["complaints"])


@router.get("", response_model=List[Complaint])
def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    sentiment: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List complaints with optional filters

    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **sentiment**: Filter by sentiment (Negativo, Neutro, Positivo)
    - **status**: Filter by status (Respondida, NÃ£o respondida, Resolvida)
    """
    complaints = crud.get_complaints(
        db, skip=skip, limit=limit, sentiment=sentiment, status=status
    )
    return complaints


@router.get("/stats", response_model=ComplaintStats)
def get_stats(db: Session = Depends(get_db)):
    """
    Get statistics about complaints

    Returns counts by sentiment, status, category and average urgency score
    """
    stats = crud.get_stats(db)
    return ComplaintStats(**stats)


@router.get("/{complaint_id}", response_model=Complaint)
def get_complaint_detail(complaint_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific complaint

    - **complaint_id**: The ID of the complaint
    """
    complaint = crud.get_complaint(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="ReclamaÃ§Ã£o nÃ£o encontrada")
    return complaint


@router.post("", response_model=Complaint, status_code=201)
def create_complaint_endpoint(
    complaint: ComplaintCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new complaint manually (for testing purposes)

    In production, complaints are created automatically by the scraper
    """
    return crud.create_complaint(db, complaint)


@router.patch("/{complaint_id}/analysis")
def update_analysis(
    complaint_id: int,
    sentiment: Optional[str] = None,
    sentiment_score: Optional[float] = None,
    urgency_score: Optional[float] = None,
    classification: Optional[list] = None,
    entities: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """
    Update complaint with AI analysis data (used by Chat B)

    - **complaint_id**: The ID of the complaint
    - **sentiment**: Sentiment classification
    - **sentiment_score**: Sentiment score (0-10)
    - **urgency_score**: Urgency score (0-10)
    - **classification**: List of categories
    - **entities**: Extracted entities
    """
    update_data = {}
    if sentiment is not None:
        update_data['sentiment'] = sentiment
    if sentiment_score is not None:
        update_data['sentiment_score'] = sentiment_score
    if urgency_score is not None:
        update_data['urgency_score'] = urgency_score
    if classification is not None:
        update_data['classification'] = classification
    if entities is not None:
        update_data['entities'] = entities

    complaint = crud.update_complaint_analysis(db, complaint_id, **update_data)
    if not complaint:
        raise HTTPException(status_code=404, detail="ReclamaÃ§Ã£o nÃ£o encontrada")

    return {"message": "Analysis updated", "complaint_id": complaint_id}


@router.patch("/{complaint_id}/response")
def update_response(
    complaint_id: int,
    response_generated: Optional[str] = None,
    response_edited: Optional[str] = None,
    coupon_code: Optional[str] = None,
    coupon_discount: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Update complaint with response data (used by Chat C)

    - **complaint_id**: The ID of the complaint
    - **response_generated**: AI-generated response
    - **response_edited**: Manually edited response
    - **coupon_code**: Generated coupon code
    - **coupon_discount**: Discount percentage
    """
    update_data = {}
    if response_generated is not None:
        update_data['response_generated'] = response_generated
    if response_edited is not None:
        update_data['response_edited'] = response_edited
    if coupon_code is not None:
        update_data['coupon_code'] = coupon_code
    if coupon_discount is not None:
        update_data['coupon_discount'] = coupon_discount

    complaint = crud.update_complaint_response(db, complaint_id, **update_data)
    if not complaint:
        raise HTTPException(status_code=404, detail="ReclamaÃ§Ã£o nÃ£o encontrada")

    return {"message": "Response updated", "complaint_id": complaint_id}
