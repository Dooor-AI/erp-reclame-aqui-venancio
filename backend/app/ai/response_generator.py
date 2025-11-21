"""
Response generator using Gemini API for personalized customer responses
"""
from app.ai.gemini_client import GeminiClient
from app.ai.prompts.response_templates import RESPONSE_TEMPLATES
import json
import random
import string

PERSONALIZATION_PROMPT = """VocÃª Ã© um especialista em atendimento ao cliente da VenÃ¢ncio.

ReclamaÃ§Ã£o original:
{complaint_text}

AnÃ¡lise:
- Sentimento: {sentiment}
- Categoria: {category}
- UrgÃªncia: {urgency}/10

Template base:
{template}

Tarefa: Personalize esta resposta mantendo:
1. Tom empÃ¡tico e profissional
2. ReferÃªncia especÃ­fica ao problema mencionado
3. Estrutura: reconhecimento â desculpa â soluÃ§Ã£o â cupom
4. MÃ¡ximo 150 palavras

Retorne APENAS a resposta personalizada, sem JSON ou formataÃ§Ã£o adicional."""


class ResponseGenerator:
    def __init__(self):
        self.client = GeminiClient()

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

        # Determinar desconto baseado em urgÃªncia
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

        # Substituir variÃ¡veis
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
        """Calcular desconto baseado em urgÃªncia"""
        if urgency >= 8.0 or sentiment == "Muito Negativo":
            return 20
        elif urgency >= 5.0:
            return 15
        else:
            return 10

    def _generate_coupon_code(self) -> str:
        """Gerar cÃ³digo Ãºnico de cupom"""
        chars = string.ascii_uppercase + string.digits
        return 'VEN' + ''.join(random.choices(chars, k=8))
