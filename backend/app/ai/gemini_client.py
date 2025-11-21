"""
Google Gemini API client for sentiment analysis and text classification
"""
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Google Gemini client for text analysis"""

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def analyze_text(self, prompt: str, text: str) -> str:
        """
        AnÃ¡lise de texto genÃ©rica usando Gemini API

        Args:
            prompt: Prompt de instruÃ§Ã£o para o modelo
            text: Texto a ser analisado

        Returns:
            Resposta do modelo Gemini em formato string (geralmente JSON)

        Raises:
            Exception: Se houver erro na chamada da API
        """
        try:
            # Combine prompt and text
            full_prompt = f"{prompt}\n\nTexto:\n{text}"

            # Generate content
            response = self.model.generate_content(full_prompt)

            # Extract text from response
            result_text = response.text

            # Clean up markdown formatting if present
            if result_text.startswith("```json"):
                result_text = result_text.replace("```json", "").replace("```", "").strip()
            elif result_text.startswith("```"):
                result_text = result_text.replace("```", "").strip()

            return result_text

        except Exception as e:
            logger.error(f"Erro na API Gemini: {e}")
            raise
