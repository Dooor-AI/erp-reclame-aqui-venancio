"""
API endpoints for complaint responses
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.response_service import ResponseService
from app.core.database import get_db
from app.db.models import Complaint
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/responses", tags=["responses"])


class EditResponseRequest(BaseModel):
    edited_response: str


@router.post("/generate/{complaint_id}")
async def generate_response(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Gerar resposta para reclamaÃ§Ã£o"""
    service = ResponseService()

    try:
        result = await service.generate_and_save_response(db, complaint_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resposta: {str(e)}")


@router.get("/{complaint_id}")
def get_response(complaint_id: int, db: Session = Depends(get_db)):
    """Ver resposta gerada para reclamaÃ§Ã£o"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="ReclamaÃ§Ã£o nÃ£o encontrada")

    return {
        "complaint_id": complaint.id,
        "response_generated": complaint.response_generated,
        "response_edited": complaint.response_edited,
        "coupon_code": complaint.coupon_code,
        "coupon_discount": complaint.coupon_discount,
        "response_sent": complaint.response_sent
    }


@router.put("/{complaint_id}")
def edit_response(
    complaint_id: int,
    request: EditResponseRequest,
    db: Session = Depends(get_db)
):
    """Editar resposta antes de enviar"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="ReclamaÃ§Ã£o nÃ£o encontrada")

    complaint.response_edited = request.edited_response
    db.commit()

    return {"message": "Resposta editada com sucesso"}


@router.post("/{complaint_id}/send")
def mark_as_sent(complaint_id: int, db: Session = Depends(get_db)):
    """Marcar resposta como enviada (MOCK)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="ReclamaÃ§Ã£o nÃ£o encontrada")

    complaint.response_sent = True
    complaint.response_sent_at = datetime.now()
    db.commit()

    return {"message": "Resposta marcada como enviada"}
