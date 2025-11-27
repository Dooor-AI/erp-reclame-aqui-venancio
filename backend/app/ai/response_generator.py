"""
Response generator using Gemini API for personalized customer responses.
Uses competitor best practices as examples for better response quality.
"""
from app.ai.gemini_client import GeminiClient
from app.ai.prompts.response_templates import RESPONSE_TEMPLATES
from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint, Competitor
from sqlalchemy import desc
import json
import random
import string

PERSONALIZATION_PROMPT_WITH_EXAMPLES = """Você é um especialista em atendimento ao cliente da Drogaria Venâncio.

## RECLAMAÇÃO DO CLIENTE:
{complaint_text}

## ANÁLISE DA RECLAMAÇÃO:
- Sentimento: {sentiment}
- Categoria: {category}
- Urgência: {urgency}/10
- Nome do cliente: {user_name}

## EXEMPLOS DE RESPOSTAS BEM AVALIADAS DE CONCORRENTES (Nota 8+):
Estes são exemplos reais de respostas que receberam notas altas dos clientes. Use-os como inspiração para estrutura e tom:

{competitor_examples}

## PADRÕES DE SUCESSO IDENTIFICADOS:
Com base nas melhores respostas dos concorrentes, os elementos que mais satisfazem os clientes são:
- Pedido de desculpas sincero e específico ao problema
- Solução concreta com prazo definido
- Oferta de compensação quando apropriado
- Canal direto para acompanhamento
- Tom empático e profissional

## SUA TAREFA:
Crie uma resposta personalizada para a Drogaria Venâncio que:
1. Comece com saudação usando o nome do cliente
2. Reconheça o problema específico mencionado
3. Peça desculpas de forma genuína
4. Apresente uma solução concreta com prazo
5. Ofereça o cupom de desconto como compensação: {discount}% OFF, código {coupon_code}
6. Forneça canal de contato (SAC 0800 ou WhatsApp)
7. Finalize reforçando compromisso com qualidade
8. Máximo 200 palavras

IMPORTANTE: Adapte o tom e urgência baseado no sentimento do cliente. Clientes muito insatisfeitos precisam de mais empatia.

Retorne APENAS a resposta personalizada, sem JSON, markdown ou formatação adicional."""

# Fallback prompt when no competitor examples available
PERSONALIZATION_PROMPT_SIMPLE = """Você é um especialista em atendimento ao cliente da Drogaria Venâncio.

## RECLAMAÇÃO DO CLIENTE:
{complaint_text}

## ANÁLISE:
- Sentimento: {sentiment}
- Categoria: {category}
- Urgência: {urgency}/10
- Nome do cliente: {user_name}

## TEMPLATE BASE:
{template}

## SUA TAREFA:
Personalize esta resposta:
1. Use o nome do cliente na saudação
2. Reconheça o problema específico
3. Peça desculpas sinceras
4. Apresente solução com prazo
5. Ofereça cupom: {discount}% OFF, código {coupon_code}
6. Máximo 150 palavras

Retorne APENAS a resposta personalizada."""


class ResponseGenerator:
    def __init__(self):
        self.client = GeminiClient()

    def _get_best_competitor_responses(self, limit: int = 3) -> list:
        """Busca as melhores respostas de concorrentes do banco de dados."""
        db = SessionLocal()
        try:
            responses = db.query(CompetitorComplaint).join(
                Competitor, CompetitorComplaint.competitor_id == Competitor.id
            ).filter(
                CompetitorComplaint.company_response.isnot(None),
                CompetitorComplaint.customer_score >= 8
            ).order_by(
                desc(CompetitorComplaint.customer_score)
            ).limit(limit).all()

            examples = []
            for r in responses:
                competitor = db.query(Competitor).filter(Competitor.id == r.competitor_id).first()
                examples.append({
                    'competitor': competitor.name if competitor else 'Concorrente',
                    'score': r.customer_score,
                    'complaint_summary': (r.title or '')[:100],
                    'response': r.company_response[:500] if r.company_response else '',
                    'was_resolved': r.was_resolved
                })
            return examples
        finally:
            db.close()

    def _format_competitor_examples(self, examples: list) -> str:
        """Formata os exemplos de concorrentes para o prompt."""
        if not examples:
            return "Nenhum exemplo disponível no momento."

        formatted = []
        for i, ex in enumerate(examples, 1):
            resolved_text = "✓ Resolvido" if ex['was_resolved'] else ""
            formatted.append(f"""
### Exemplo {i} - {ex['competitor']} (Nota: {ex['score']}) {resolved_text}
**Reclamação:** {ex['complaint_summary']}...
**Resposta:**
{ex['response']}
""")
        return "\n".join(formatted)

    async def generate_response(
        self,
        complaint_text: str,
        user_name: str,
        category: str,
        sentiment: str,
        urgency: float,
        entities: dict
    ) -> dict:
        """Gerar resposta personalizada baseada nas melhores práticas dos concorrentes."""

        # Determinar desconto baseado em urgência
        discount = self._calculate_discount(urgency, sentiment)

        # Gerar código do cupom
        coupon_code = self._generate_coupon_code()

        # Buscar exemplos de concorrentes
        competitor_examples = self._get_best_competitor_responses(limit=3)

        if competitor_examples:
            # Usar prompt com exemplos dos concorrentes
            formatted_examples = self._format_competitor_examples(competitor_examples)
            prompt = PERSONALIZATION_PROMPT_WITH_EXAMPLES.format(
                complaint_text=complaint_text,
                sentiment=sentiment,
                category=category,
                urgency=urgency,
                user_name=user_name or "Cliente",
                competitor_examples=formatted_examples,
                discount=discount,
                coupon_code=coupon_code
            )
        else:
            # Fallback para prompt simples sem exemplos
            template = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES.get("outros", ""))
            prompt = PERSONALIZATION_PROMPT_SIMPLE.format(
                complaint_text=complaint_text,
                sentiment=sentiment,
                category=category,
                urgency=urgency,
                user_name=user_name or "Cliente",
                template=template,
                discount=discount,
                coupon_code=coupon_code
            )

        # Chamar LLM para personalizar
        personalized = await self.client.analyze_text(prompt, complaint_text)

        return {
            'response_text': personalized,
            'coupon_code': coupon_code,
            'discount_percent': discount,
            'template_used': category,
            'used_competitor_examples': len(competitor_examples) > 0
        }

    def _calculate_discount(self, urgency: float, sentiment: str) -> int:
        """Calcular desconto baseado em urgência e sentimento."""
        if urgency >= 8.0 or sentiment in ["Muito Negativo", "muito_negativo"]:
            return 20
        elif urgency >= 5.0 or sentiment in ["Negativo", "negativo"]:
            return 15
        else:
            return 10

    def _generate_coupon_code(self) -> str:
        """Gerar código único de cupom."""
        chars = string.ascii_uppercase + string.digits
        return 'VEN' + ''.join(random.choices(chars, k=8))
