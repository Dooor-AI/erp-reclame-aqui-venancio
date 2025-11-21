"""
Test script for Google Gemini integration
"""
import asyncio
from app.ai.gemini_client import GeminiClient


async def test_gemini_basic():
    """Test basic Gemini functionality"""
    print("="*70)
    print("Testing Google Gemini Integration")
    print("="*70)
    print()

    try:
        client = GeminiClient()
        print("[OK] Gemini client initialized successfully")
        print()

        # Test 1: Sentiment Analysis
        print("Test 1: Sentiment Analysis")
        print("-"*70)
        prompt = """Analise o sentimento desta frase e retorne JSON:
{
  "sentiment": "Negativo/Neutro/Positivo",
  "score": 0-10,
  "reasoning": "explicação"
}

Responda APENAS com o JSON."""

        text = "Produto péssimo, quebrou em 2 dias! Nunca mais compro aqui."

        print(f"Analyzing: {text}")
        response = await client.analyze_text(prompt, text)
        print("Response:")
        print(response)
        print()

        # Test 2: Classification
        print("Test 2: Classification")
        print("-"*70)
        prompt2 = """Classifique esta reclamação em categorias:
- produto
- atendimento
- entrega
- preco
- outros

Retorne JSON:
{
  "categories": ["cat1", "cat2"],
  "primary_category": "principal"
}

Responda APENAS com o JSON."""

        text2 = "Comprei uma geladeira e ela chegou com defeito. O atendimento ao cliente também foi horrível."

        print(f"Analyzing: {text2}")
        response2 = await client.analyze_text(prompt2, text2)
        print("Response:")
        print(response2)
        print()

        # Test 3: Entity Extraction
        print("Test 3: Entity Extraction")
        print("-"*70)
        prompt3 = """Extraia entidades desta reclamação e retorne JSON:
{
  "produto": "nome do produto",
  "loja": "nome da loja",
  "funcionario": "nome do funcionário ou null"
}

Responda APENAS com o JSON."""

        text3 = "Comprei um fogão 5 bocas na loja do Shopping Center. O atendente Carlos foi muito rude."

        print(f"Analyzing: {text3}")
        response3 = await client.analyze_text(prompt3, text3)
        print("Response:")
        print(response3)
        print()

        print("="*70)
        print("[SUCCESS] All tests completed successfully!")
        print("="*70)
        print()
        print("Next steps:")
        print("1. Run full validation: python validate_analysis.py")
        print("2. Test API endpoints: uvicorn app.main:app --reload")
        print("3. Check documentation: VALIDATION_QUICKSTART.md")

    except Exception as e:
        print(f"[ERROR] {e}")
        print()
        print("Common issues:")
        print("- GEMINI_API_KEY not set in .env file")
        print("- Invalid API key (should start with 'AIza')")
        print("- No internet connection")
        print("- API key not activated yet (wait a few minutes)")
        print()
        print("To fix:")
        print("1. Get API key: https://makersuite.google.com/app/apikey")
        print("2. Add to backend/.env: GEMINI_API_KEY=your-key-here")
        print("3. Restart this script")


if __name__ == "__main__":
    print()
    print("Make sure GEMINI_API_KEY is set in .env file")
    print("Get your key at: https://makersuite.google.com/app/apikey")
    print()

    asyncio.run(test_gemini_basic())
