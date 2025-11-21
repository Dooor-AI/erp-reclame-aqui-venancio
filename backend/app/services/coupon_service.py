"""
Coupon service for managing discount coupons
"""
from sqlalchemy.orm import Session
from app.db.models import Coupon
from datetime import datetime, timedelta
import random
import string


class CouponService:
    def create_coupon(
        self,
        db: Session,
        complaint_id: int,
        discount_percent: int
    ) -> Coupon:
        """Criar cupom Ãºnico"""

        # Gerar cÃ³digo Ãºnico
        code = self._generate_unique_code(db)

        # Validade: 30 dias
        valid_until = datetime.now() + timedelta(days=30)

        coupon = Coupon(
            code=code,
            discount_percent=discount_percent,
            complaint_id=complaint_id,
            valid_until=valid_until
        )

        db.add(coupon)
        db.commit()
        db.refresh(coupon)

        return coupon

    def _generate_unique_code(self, db: Session) -> str:
        """Gerar cÃ³digo Ãºnico (evitar duplicatas)"""
        while True:
            chars = string.ascii_uppercase + string.digits
            code = 'VEN' + ''.join(random.choices(chars, k=8))

            existing = db.query(Coupon).filter(Coupon.code == code).first()
            if not existing:
                return code

    def validate_coupon(self, db: Session, code: str) -> dict:
        """Validar cupom"""
        coupon = db.query(Coupon).filter(Coupon.code == code).first()

        if not coupon:
            return {"valid": False, "reason": "Cupom nÃ£o encontrado"}

        if coupon.is_used:
            return {"valid": False, "reason": "Cupom jÃ¡ utilizado"}

        if datetime.now() > coupon.valid_until:
            return {"valid": False, "reason": "Cupom expirado"}

        return {
            "valid": True,
            "discount_percent": coupon.discount_percent,
            "valid_until": coupon.valid_until
        }
