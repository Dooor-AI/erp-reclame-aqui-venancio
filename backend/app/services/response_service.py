"""
Response service for generating and managing complaint responses
"""
from sqlalchemy.orm import Session
from app.ai.response_generator import ResponseGenerator
from app.services.coupon_service import CouponService
from app.db.models import Complaint
from datetime import datetime


class ResponseService:
    def __init__(self):
        self.generator = ResponseGenerator()
        self.coupon_service = CouponService()

    async def generate_and_save_response(self, db: Session, complaint_id: int):
        """Pipeline: Gerar resposta + cupom + salvar"""

        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise ValueError("Complaint not found")

        if not complaint.sentiment:
            raise ValueError("Complaint not analyzed yet - run Chat B first")

        # Gerar resposta
        result = await self.generator.generate_response(
            complaint_text=f"{complaint.title}\n\n{complaint.text}",
            user_name=complaint.user_name,
            category=complaint.classification[0] if complaint.classification else 'outros',
            sentiment=complaint.sentiment,
            urgency=complaint.urgency_score or 5.0,
            entities=complaint.entities or {}
        )

        # Criar cupom
        coupon = self.coupon_service.create_coupon(
            db,
            complaint_id=complaint.id,
            discount_percent=result['discount_percent']
        )

        # Atualizar complaint
        complaint.response_generated = result['response_text']
        complaint.coupon_code = coupon.code
        complaint.coupon_discount = coupon.discount_percent
        db.commit()

        return {
            "complaint_id": complaint.id,
            "response": result['response_text'],
            "coupon": {
                "code": coupon.code,
                "discount": coupon.discount_percent,
                "valid_until": coupon.valid_until
            }
        }
