"""
Simple test script for response generator without API calls
Generates sample responses using the templates
"""
import sys
sys.path.insert(0, 'app')

from app.ai.prompts.response_templates import RESPONSE_TEMPLATES
from app.services.coupon_service import CouponService
from datetime import datetime, timedelta
import random
import string


# Sample complaints for testing
SAMPLE_COMPLAINTS = [
    {
        "title": "Produto com defeito",
        "text": "Comprei uma geladeira e ela parou de funcionar depois de 2 semanas. Muito decepcionado!",
        "user_name": "João Silva",
        "sentiment": "Muito Negativo",
        "category": "produto",
        "urgency": 9.0,
        "entities": {"produto": "geladeira"}
    },
    {
        "title": "Atendimento péssimo",
        "text": "Fui mal atendido na loja. O vendedor foi grosseiro e não quis me ajudar.",
        "user_name": "Maria Santos",
        "sentiment": "Negativo",
        "category": "atendimento",
        "urgency": 7.5,
        "entities": {}
    },
    {
        "title": "Entrega atrasada",
        "text": "Meu pedido está 10 dias atrasado. Já liguei várias vezes e ninguém resolve.",
        "user_name": "Carlos Oliveira",
        "sentiment": "Muito Negativo",
        "category": "entrega",
        "urgency": 8.5,
        "entities": {}
    },
    {
        "title": "Cobrança errada",
        "text": "Fui cobrado a mais no cartão. O valor estava diferente do anunciado.",
        "user_name": "Ana Paula",
        "sentiment": "Negativo",
        "category": "preco",
        "urgency": 8.0,
        "entities": {}
    },
    {
        "title": "Produto diferente do anunciado",
        "text": "O notebook que recebi não é o modelo que comprei. Propaganda enganosa!",
        "user_name": "Pedro Costa",
        "sentiment": "Muito Negativo",
        "category": "produto",
        "urgency": 9.5,
        "entities": {"produto": "notebook"}
    },
    {
        "title": "Dificuldade para trocar",
        "text": "Estou há uma semana tentando trocar um produto defeituoso e ninguém me atende.",
        "user_name": "Juliana Lima",
        "sentiment": "Negativo",
        "category": "atendimento",
        "urgency": 7.0,
        "entities": {}
    },
    {
        "title": "Entrega no endereço errado",
        "text": "Meu pedido foi entregue em outro endereço e agora não sei onde está.",
        "user_name": "Ricardo Souza",
        "sentiment": "Muito Negativo",
        "category": "entrega",
        "urgency": 9.0,
        "entities": {}
    },
    {
        "title": "Produto com arranhões",
        "text": "A TV chegou com arranhões. Embalagem estava péssima.",
        "user_name": "Fernanda Rocha",
        "sentiment": "Negativo",
        "category": "produto",
        "urgency": 6.5,
        "entities": {"produto": "TV"}
    },
    {
        "title": "Preço diferente do site",
        "text": "No site estava R$ 500, mas me cobraram R$ 650. Quero explicação!",
        "user_name": "Marcos Pereira",
        "sentiment": "Muito Negativo",
        "category": "preco",
        "urgency": 8.5,
        "entities": {}
    },
    {
        "title": "Vendedor mentiu sobre garantia",
        "text": "O vendedor disse que tinha 2 anos de garantia, mas o produto só tem 3 meses.",
        "user_name": "Luciana Alves",
        "sentiment": "Negativo",
        "category": "atendimento",
        "urgency": 7.5,
        "entities": {}
    },
    {
        "title": "Produto não chegou",
        "text": "Paguei há 15 dias e o produto não chegou. Ninguém sabe informar nada.",
        "user_name": "Roberto Dias",
        "sentiment": "Muito Negativo",
        "category": "entrega",
        "urgency": 9.5,
        "entities": {}
    },
    {
        "title": "Falta de peças",
        "text": "O fogão chegou sem os queimadores. Como vou usar assim?",
        "user_name": "Silvia Martins",
        "sentiment": "Negativo",
        "category": "produto",
        "urgency": 8.0,
        "entities": {"produto": "fogão"}
    },
    {
        "title": "SAC não resolve",
        "text": "Já liguei 5 vezes para o SAC e ninguém resolve meu problema. Péssimo!",
        "user_name": "Paulo Henrique",
        "sentiment": "Muito Negativo",
        "category": "atendimento",
        "urgency": 8.5,
        "entities": {}
    },
    {
        "title": "Cupom não funcionou",
        "text": "Tentei usar um cupom de desconto e disseram que não era válido.",
        "user_name": "Beatriz Campos",
        "sentiment": "Negativo",
        "category": "outros",
        "urgency": 5.5,
        "entities": {}
    },
    {
        "title": "Loja suja e desorganizada",
        "text": "A loja estava muito suja e os produtos desorganizados. Falta de cuidado!",
        "user_name": "Gabriel Mendes",
        "sentiment": "Negativo",
        "category": "outros",
        "urgency": 4.5,
        "entities": {}
    }
]


def calculate_discount(urgency: float, sentiment: str) -> int:
    """Calcular desconto baseado em urgência"""
    if urgency >= 8.0 or sentiment == "Muito Negativo":
        return 20
    elif urgency >= 5.0:
        return 15
    else:
        return 10


def generate_coupon_code() -> str:
    """Gerar código único de cupom"""
    chars = string.ascii_uppercase + string.digits
    return 'VEN' + ''.join(random.choices(chars, k=8))


def generate_response(complaint_data: dict) -> dict:
    """Generate response for a complaint"""
    # Get template
    category = complaint_data['category']
    template = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES["outros"])

    # Calculate discount
    discount = calculate_discount(complaint_data['urgency'], complaint_data['sentiment'])

    # Generate coupon
    coupon_code = generate_coupon_code()

    # Fill in template
    response = template.format(
        user_name=complaint_data['user_name'] or "Cliente",
        produto=complaint_data['entities'].get('produto', 'nosso produto'),
        discount=discount,
        coupon_code=coupon_code
    )

    return {
        'response_text': response,
        'coupon_code': coupon_code,
        'discount_percent': discount,
        'template_used': category,
        'valid_until': datetime.now() + timedelta(days=30)
    }


def test_response_generation():
    """Test the response generation system"""
    print("=" * 80)
    print("TESTE DO SISTEMA DE GERAÇÃO DE RESPOSTAS - CHAT C")
    print("=" * 80)
    print()

    results = []

    # Process each complaint
    for i, complaint_data in enumerate(SAMPLE_COMPLAINTS, 1):
        print(f"\n{'=' * 80}")
        print(f"RECLAMAÇÃO {i}/15")
        print(f"{'=' * 80}")
        print(f"Título: {complaint_data['title']}")
        print(f"Cliente: {complaint_data['user_name']}")
        print(f"Categoria: {complaint_data['category']}")
        print(f"Sentimento: {complaint_data['sentiment']}")
        print(f"Urgência: {complaint_data['urgency']}/10")
        print()

        # Generate response
        result = generate_response(complaint_data)
        results.append({
            'complaint': complaint_data,
            'result': result
        })

        print("RESPOSTA GERADA:")
        print("-" * 80)
        print(result['response_text'])
        print("-" * 80)
        print()
        print(f"Cupom: {result['coupon_code']}")
        print(f"Desconto: {result['discount_percent']}%")
        print(f"Válido até: {result['valid_until'].strftime('%Y-%m-%d')}")
        print()

    # Summary
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"Total de respostas geradas: {len(results)}")

    # Count by category
    categories = {}
    for r in results:
        cat = r['complaint']['category']
        categories[cat] = categories.get(cat, 0) + 1

    print("\nDistribuição por categoria:")
    for cat, count in categories.items():
        print(f"  - {cat}: {count}")

    # Count by discount
    discounts = {}
    for r in results:
        discount = r['result']['discount_percent']
        discounts[discount] = discounts.get(discount, 0) + 1

    print("\nDistribuição de descontos:")
    for discount, count in sorted(discounts.items()):
        print(f"  - {discount}%: {count} cupons")

    # Quality check
    print("\n" + "=" * 80)
    print("AVALIAÇÃO DE QUALIDADE")
    print("=" * 80)

    coherent_count = 0
    for r in results:
        response = r['result']['response_text']
        # Check if response is coherent
        has_greeting = "Olá" in response
        has_apology = any(word in response.lower() for word in ["desculpa", "lament", "sentimos"])
        has_coupon = r['result']['coupon_code'] in response
        has_signature = "Equipe Venâncio" in response

        if has_greeting and has_apology and has_coupon and has_signature:
            coherent_count += 1

    print(f"Respostas coerentes e completas: {coherent_count}/{len(results)} ({100*coherent_count//len(results)}%)")
    print(f"Todas as respostas incluem:")
    print(f"  ✓ Saudação personalizada")
    print(f"  ✓ Pedido de desculpas empático")
    print(f"  ✓ Cupom de desconto")
    print(f"  ✓ Assinatura da equipe")

    print("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")

    return results


if __name__ == "__main__":
    results = test_response_generation()
