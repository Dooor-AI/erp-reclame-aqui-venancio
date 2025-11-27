"""
Smart tagger - generates specific tags for complaints
Focuses on middle distribution (not too common, not too rare)
"""
import json
from app.ai.gemini_client import GeminiClient
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

# Tags padronizadas - conjunto fixo de 12 tags
ALLOWED_TAGS = [
    "atraso-entrega",        # Pedidos que atrasaram
    "pedido-nao-entregue",   # Pedido nunca chegou
    "estorno-pendente",      # Aguardando reembolso/estorno
    "produto-avariado",      # Produto danificado, quebrado, vencido
    "atendimento-ruim",      # Mau atendimento, falta de resposta
    "produto-indisponivel",  # Produto fora de estoque após compra
    "cobranca-indevida",     # Cobrado errado, duplicado
    "erro-sistema",          # Problemas no site/app
    "cancelamento-problematico",  # Dificuldade para cancelar
    "troca-recusada",        # Empresa não aceita troca/devolução
    "pedido-incompleto",     # Faltou item no pedido
    "problema-receita",      # Problemas com receita médica
]

SMART_TAG_PROMPT = f"""Analise a reclamação e classifique usando APENAS as tags da lista abaixo.

TAGS PERMITIDAS (escolha de 1 a 3 tags mais relevantes):
{chr(10).join(f'- {tag}' for tag in ALLOWED_TAGS)}

REGRAS:
1. Use SOMENTE tags da lista acima
2. Escolha a tag que MELHOR representa o problema principal como "primary_tag"
3. Adicione 1-2 tags secundárias se aplicável
4. NÃO invente novas tags

DESCRIÇÃO DAS TAGS:
- atraso-entrega: Pedido atrasou mas ainda não foi entregue ou demorou muito
- pedido-nao-entregue: Pedido nunca chegou, extraviado
- estorno-pendente: Cliente aguarda reembolso ou estorno no cartão
- produto-avariado: Produto chegou danificado, quebrado, vencido ou estragado
- atendimento-ruim: Atendente grosseiro, sem resposta, descaso
- produto-indisponivel: Comprou mas produto estava fora de estoque
- cobranca-indevida: Cobrança errada, duplicada, preço diferente
- erro-sistema: Bug no site, app não funciona, erro no checkout
- cancelamento-problematico: Dificuldade para cancelar pedido
- troca-recusada: Empresa não aceita troca ou devolução
- pedido-incompleto: Faltou item, quantidade errada
- problema-receita: Problemas com receita médica, medicamento controlado

Retorne em formato JSON:
{{
  "tags": ["tag1", "tag2"],
  "primary_tag": "tag_principal"
}}"""


class SmartTagger:
    """Generates intelligent tags for complaints focusing on middle distribution"""

    def __init__(self):
        self.client = GeminiClient()

    async def generate_tags(self, text: str, title: str = "") -> Dict[str, any]:
        """
        Generate smart tags for a complaint using fixed tag set

        Args:
            text: Complaint text
            title: Complaint title (optional)

        Returns:
            Dict with:
                - tags: List of 1-3 tags from ALLOWED_TAGS
                - primary_tag: Main tag from ALLOWED_TAGS
        """
        try:
            # Combine title and text for better context
            full_text = f"Título: {title}\n\n{text}" if title else text

            response = await self.client.analyze_text(SMART_TAG_PROMPT, full_text)
            result = json.loads(response)

            tags = result.get('tags', [])
            # Normalize and validate tags against allowed list
            normalized_tags = []
            for tag in tags:
                norm_tag = self._normalize_tag(tag)
                if norm_tag in ALLOWED_TAGS:
                    normalized_tags.append(norm_tag)

            # Get primary tag
            primary = self._normalize_tag(result.get('primary_tag', ''))
            if primary not in ALLOWED_TAGS:
                primary = normalized_tags[0] if normalized_tags else 'atendimento-ruim'

            # Ensure we have at least one tag
            if not normalized_tags:
                normalized_tags = [primary]

            return {
                'tags': normalized_tags[:3],  # Max 3 tags
                'primary_tag': primary
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}\nResponse: {response}")
            return {
                'tags': ['atendimento-ruim'],
                'primary_tag': 'atendimento-ruim'
            }
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            raise

    def _normalize_tag(self, tag: str) -> str:
        """Normalize tag to lowercase, no accents, hyphenated"""
        if not tag:
            return ''

        # Remove accents
        import unicodedata
        tag = unicodedata.normalize('NFKD', tag)
        tag = ''.join(c for c in tag if not unicodedata.combining(c))

        # Lowercase and replace spaces with hyphens
        tag = tag.lower().strip()
        tag = tag.replace(' ', '-').replace('_', '-')

        # Remove special characters except hyphens
        tag = ''.join(c for c in tag if c.isalnum() or c == '-')

        # Remove multiple consecutive hyphens
        while '--' in tag:
            tag = tag.replace('--', '-')

        return tag.strip('-')
