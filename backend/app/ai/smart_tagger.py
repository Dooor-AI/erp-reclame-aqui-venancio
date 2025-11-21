"""
Smart tagger - generates specific tags for complaints
Focuses on middle distribution (not too common, not too rare)
"""
import json
from app.ai.gemini_client import GeminiClient
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

SMART_TAG_PROMPT = """Analise a reclamação e gere TAGS ESPECÍFICAS que descrevam o problema.

REGRAS IMPORTANTES:
1. Evite tags muito genéricas como "problema", "reclamação", "insatisfação"
2. Evite tags muito específicas demais (ex: números de pedido, nomes próprios)
3. Foque em tags de média especificidade que ajudem a identificar padrões

EXEMPLOS DE BOAS TAGS:
- "produto-defeituoso", "prazo-estourado", "cobrança-indevida"
- "atendente-rude", "troca-recusada", "reembolso-pendente"
- "embalagem-danificada", "produto-errado", "falta-resposta"
- "propaganda-enganosa", "garantia-negada", "cupom-invalido"

Retorne de 2 a 5 tags relevantes em formato JSON:
{
  "tags": ["tag1", "tag2", "tag3"],
  "primary_tag": "tag_principal",
  "specificity_score": 0.0 a 1.0
}

Use hífen para separar palavras nas tags. Sem acentos."""


class SmartTagger:
    """Generates intelligent tags for complaints focusing on middle distribution"""

    def __init__(self):
        self.client = GeminiClient()

    async def generate_tags(self, text: str, title: str = "") -> Dict[str, any]:
        """
        Generate smart tags for a complaint

        Args:
            text: Complaint text
            title: Complaint title (optional)

        Returns:
            Dict with:
                - tags: List of 2-5 tags
                - primary_tag: Main tag
                - specificity_score: 0-1 (0.5 is ideal middle distribution)
        """
        try:
            # Combine title and text for better context
            full_text = f"Título: {title}\n\n{text}" if title else text

            response = await self.client.analyze_text(SMART_TAG_PROMPT, full_text)
            result = json.loads(response)

            tags = result.get('tags', [])
            # Normalize tags: lowercase, no accents, hyphenated
            normalized_tags = [self._normalize_tag(tag) for tag in tags]

            return {
                'tags': normalized_tags[:5],  # Max 5 tags
                'primary_tag': self._normalize_tag(result.get('primary_tag', tags[0] if tags else '')),
                'specificity_score': float(result.get('specificity_score', 0.5))
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}\nResponse: {response}")
            return {
                'tags': ['sem-classificacao'],
                'primary_tag': 'sem-classificacao',
                'specificity_score': 0.0
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
