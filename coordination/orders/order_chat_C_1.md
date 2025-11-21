# 📋 Order for Chat C - Round 1

**From:** Commander
**To:** Chat C
**Date:** 2025-11-17
**Priority:** 🟠 High
**Estimated Duration:** 6-8 hours (Dias 3-4)

---

## 🎯 Mission

Criar sistema de geração de respostas automáticas personalizadas e cupons de desconto usando Claude API.

---

## 📋 Background

Reclamações analisadas pelo Chat B precisam de respostas empáticas e personalizadas com cupons de desconto.

**Dependencies:**
- ⚠️ **Chat B deve estar 100% completo** (análise funcionando)
- ⚠️ **Chat A API** funcionando

---

## 🚀 Your Tasks

### Task 1: Templates de Resposta (2h)

Criar `app/ai/prompts/response_templates.py`:

```python
RESPONSE_TEMPLATES = {
    "produto": """
Olá {user_name},

Sentimos muito pelo problema que você enfrentou com {produto}. Sua satisfação é muito importante para nós.

Já identificamos o ocorrido e estamos tomando as medidas necessárias para que isso não se repita.

Como forma de desculpas, gostaríamos de oferecer um cupom de {discount}% de desconto para sua próxima compra: {coupon_code}

Estamos à disposição para qualquer dúvida.

Atenciosamente,
Equipe Venâncio
""",

    "atendimento": """
Olá {user_name},

Pedimos sinceras desculpas pela experiência negativa com nosso atendimento. Isso não reflete nossos padrões de qualidade.

Já repassamos o feedback para nossa equipe e estamos trabalhando para melhorar.

Para compensar o transtorno, gostaríamos de oferecer um cupom de {discount}% de desconto: {coupon_code}

Contamos com sua compreensão.

Atenciosamente,
Equipe Venâncio
""",

    "entrega": """
Olá {user_name},

Lamentamos profundamente o problema com a entrega do seu pedido. Entendemos a frustração causada.

Já estamos apurando o ocorrido com nossa logística para evitar que se repita.

Como compensação, preparamos um cupom de {discount}% de desconto: {coupon_code}

Agradecemos sua paciência.

Atenciosamente,
Equipe Venâncio
""",

    "preco": """
Olá {user_name},

Pedimos desculpas pela inconsistência no preço/cobrança. Já estamos verificando internamente.

Tomaremos as providências necessárias para corrigir a situação.

Como gesto de boa vontade, segue cupom de {discount}% de desconto: {coupon_code}

Estamos à disposição.

Atenciosamente,
Equipe Venâncio
""",

    "outros": """
Olá {user_name},

Agradecemos por compartilhar sua experiência conosco. Sentimos muito pelo ocorrido.

Levamos seu feedback muito a sério e já estamos trabalhando para melhorar.

Como forma de desculpas, preparamos um cupom de {discount}% de desconto: {coupon_code}

Conte conosco.

Atenciosamente,
Equipe Venâncio
"""
}
```

---

### Task 2: Gerador com LLM (3h)

Criar `app/ai/response_generator.py`:

```python
from app.ai.claude_client import ClaudeClient
from app.ai.prompts.response_templates import RESPONSE_TEMPLATES
import json

PERSONALIZATION_PROMPT = """Você é um especialista em atendimento ao cliente da Venâncio.

Reclamação original:
{complaint_text}

Análise:
- Sentimento: {sentiment}
- Categoria: {category}
- Urgência: {urgency}/10

Template base:
{template}

Tarefa: Personalize esta resposta mantendo:
1. Tom empático e profissional
2. Referência específica ao problema mencionado
3. Estrutura: reconhecimento → desculpa → solução → cupom
4. Máximo 150 palavras

Retorne APENAS a resposta personalizada, sem JSON ou formatação adicional."""

class ResponseGenerator:
    def __init__(self):
        self.client = ClaudeClient()

    async def generate_response(
        self,
        complaint_text: str,
        user_name: str,
        category: str,
        sentiment: str,
        urgency: float,
        entities: dict
    ) -> dict:
        """Gerar resposta personalizada"""

        # Selecionar template
        template = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["outros"])

        # Determinar desconto baseado em urgência
        discount = self._calculate_discount(urgency, sentiment)

        # Gerar cupom
        coupon_code = self._generate_coupon_code()

        # Personalizar com LLM
        prompt = PERSONALIZATION_PROMPT.format(
            complaint_text=complaint_text,
            sentiment=sentiment,
            category=category,
            urgency=urgency,
            template=template
        )

        personalized = await self.client.analyze_text(prompt, complaint_text)

        # Substituir variáveis
        response = personalized.format(
            user_name=user_name or "Cliente",
            produto=entities.get('produto', 'nosso produto'),
            discount=discount,
            coupon_code=coupon_code
        )

        return {
            'response_text': response,
            'coupon_code': coupon_code,
            'discount_percent': discount,
            'template_used': category
        }

    def _calculate_discount(self, urgency: float, sentiment: str) -> int:
        """Calcular desconto baseado em urgência"""
        if urgency >= 8.0 or sentiment == "Muito Negativo":
            return 20
        elif urgency >= 5.0:
            return 15
        else:
            return 10

    def _generate_coupon_code(self) -> str:
        """Gerar código único de cupom"""
        import random
        import string
        chars = string.ascii_uppercase + string.digits
        return 'VEN' + ''.join(random.choices(chars, k=8))
```

---

### Task 3: Sistema de Cupons (2h)

Adicionar modelo em `app/db/models.py`:

```python
class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    discount_percent = Column(Integer, nullable=False)
    complaint_id = Column(Integer, ForeignKey('complaints.id'))

    valid_from = Column(DateTime, server_default=func.now())
    valid_until = Column(DateTime)  # 30 dias

    is_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    complaint = relationship("Complaint", back_populates="coupon")
```

Criar `app/services/coupon_service.py`:

```python
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
        """Criar cupom único"""

        # Gerar código único
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
        """Gerar código único (evitar duplicatas)"""
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
            return {"valid": False, "reason": "Cupom não encontrado"}

        if coupon.is_used:
            return {"valid": False, "reason": "Cupom já utilizado"}

        if datetime.now() > coupon.valid_until:
            return {"valid": False, "reason": "Cupom expirado"}

        return {
            "valid": True,
            "discount_percent": coupon.discount_percent,
            "valid_until": coupon.valid_until
        }
```

---

### Task 4: API de Respostas (1h)

Criar `app/api/endpoints/responses.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.response_service import ResponseService
from app.core.database import get_db

router = APIRouter(prefix="/responses", tags=["responses"])

@router.post("/generate/{complaint_id}")
async def generate_response(
    complaint_id: int,
    db: Session = Depends(get_db)
):
    """Gerar resposta para reclamação"""
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
    """Ver resposta gerada para reclamação"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Reclamação não encontrada")

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
    edited_response: str,
    db: Session = Depends(get_db)
):
    """Editar resposta antes de enviar"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Reclamação não encontrada")

    complaint.response_edited = edited_response
    db.commit()

    return {"message": "Resposta editada com sucesso"}

@router.post("/{complaint_id}/send")
def mark_as_sent(complaint_id: int, db: Session = Depends(get_db)):
    """Marcar resposta como enviada (MOCK)"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Reclamação não encontrada")

    complaint.response_sent = True
    complaint.response_sent_at = datetime.now()
    db.commit()

    return {"message": "Resposta marcada como enviada"}
```

Criar `app/services/response_service.py`:

```python
from sqlalchemy.orm import Session
from app.ai.response_generator import ResponseGenerator
from app.services.coupon_service import CouponService
from app.db.models import Complaint
from app.db.crud import update_complaint_analysis

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
```

---

## 📝 Deliverables

1. **`answer_chat_C_1.md`** - Results with 10-15 sample responses
2. **Backend code** - All modules
3. **Validation** - Manual review of response quality

**Answer Must Include:**
- 10-15 exemplos de respostas geradas
- Avaliação de qualidade (100% coerentes e empáticas?)
- Cupons gerados
- Issues encontrados

---

## ⏰ Time Tracking

```markdown
| Task | Estimated | Actual | Status |
|------|-----------|--------|--------|
| Task 1: Templates | 2h | - | ⏳ |
| Task 2: Generator | 3h | - | ⏳ |
| Task 3: Coupons | 2h | - | ⏳ |
| Task 4: API | 1h | - | ⏳ |
```

---

## 🎯 Success Criteria

- ✅ Templates criados para cada categoria
- ✅ Respostas personalizadas (não genéricas)
- ✅ 100% das respostas são coerentes e empáticas
- ✅ Cupons únicos e rastreáveis
- ✅ API funcional
- ✅ 10-15 exemplos validados manualmente

---

## 📞 Questions?

**Bloqueadores:**
- Chat B não completo → Create alert
- Respostas genéricas → Refine prompts
- Cupons duplicados → Fix generator

---

## 🔄 Related Tasks

- **Chat D** will integrate your API into dashboard
- **Chat E** will document response templates
- **Chat B** provides the analysis you need

**At 100%:** Notify Chat D can integrate response generator!

---

**Start when Chat B is 100%! Good luck! 🚀**
