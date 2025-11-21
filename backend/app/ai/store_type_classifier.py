"""
Store type classifier - distinguishes between physical store and online complaints
"""
import json
from app.ai.gemini_client import GeminiClient
from typing import Dict
import logging

logger = logging.getLogger(__name__)

STORE_TYPE_PROMPT = """Analise a reclamação abaixo e determine se ela é sobre uma LOJA FÍSICA ou compra ONLINE.

Indicadores de LOJA FÍSICA:
- Menção de "loja", "filial", "unidade", "balcão"
- Nomes de bairros, shoppings, endereços físicos
- Interação presencial com funcionários
- "fui à loja", "quando cheguei", "no local"

Indicadores de COMPRA ONLINE:
- Menção de "site", "app", "aplicativo", "marketplace"
- "comprei pelo site", "pedido online", "e-commerce"
- Problemas de entrega, rastreamento
- "WhatsApp", "telefone", "SAC online"

Retorne APENAS o JSON:
{
  "store_type": "physical" ou "online" ou "unknown",
  "confidence": 0.0 a 1.0,
  "indicators": ["indicador1", "indicador2"]
}

Se não houver indícios claros, use "unknown"."""


class StoreTypeClassifier:
    """Classifies complaints as physical store or online purchase"""

    def __init__(self):
        self.client = GeminiClient()

    async def classify(self, text: str) -> Dict[str, any]:
        """
        Classify complaint as physical store or online

        Args:
            text: Complaint text

        Returns:
            Dict with:
                - store_type: "physical", "online", or "unknown"
                - confidence: float 0-1
                - indicators: list of indicators found
        """
        try:
            response = await self.client.analyze_text(STORE_TYPE_PROMPT, text)
            result = json.loads(response)

            return {
                'store_type': result.get('store_type', 'unknown'),
                'confidence': float(result.get('confidence', 0.0)),
                'indicators': result.get('indicators', [])
            }
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}\nResponse: {response}")
            return {
                'store_type': 'unknown',
                'confidence': 0.0,
                'indicators': []
            }
        except Exception as e:
            logger.error(f"Error classifying store type: {e}")
            raise
