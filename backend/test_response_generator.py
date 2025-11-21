"""
Test script for response generator and coupon system
Generates 15 sample responses for different complaint scenarios
"""
import sys
import asyncio
from datetime import datetime
sys.path.insert(0, 'app')

from app.core.database import init_db, SessionLocal
from app.db.models import Complaint
from app.services.response_service import ResponseService


# Sample complaints for testing
SAMPLE_COMPLAINTS = [
    {
        "title": "Produto com defeito",
        "text": "Comprei uma geladeira e ela parou de funcionar depois de 2 semanas. Muito decepcionado!",
        "user_name": "João Silva",
        "sentiment": "Muito Negativo",
        "classification": ["produto"],
        "urgency_score": 9.0,
        "entities": {"produto": "geladeira"}
    },
    {
        "title": "Atendimento péssimo",
        "text": "Fui mal atendido na loja. O vendedor foi grosseiro e não quis me ajudar.",
        "user_name": "Maria Santos",
        "sentiment": "Negativo",
        "classification": ["atendimento"],
        "urgency_score": 7.5,
        "entities": {}
    },
    {
        "title": "Entrega atrasada",
        "text": "Meu pedido está 10 dias atrasado. Já liguei várias vezes e ninguém resolve.",
        "user_name": "Carlos Oliveira",
        "sentiment": "Muito Negativo",
        "classification": ["entrega"],
        "urgency_score": 8.5,
        "entities": {}
    },
    {
        "title": "Cobrança errada",
        "text": "Fui cobrado a mais no cartão. O valor estava diferente do anunciado.",
        "user_name": "Ana Paula",
        "sentiment": "Negativo",
        "classification": ["preco"],
        "urgency_score": 8.0,
        "entities": {}
    },
    {
        "title": "Produto diferente do anunciado",
        "text": "O notebook que recebi não é o modelo que comprei. Propaganda enganosa!",
        "user_name": "Pedro Costa",
        "sentiment": "Muito Negativo",
        "classification": ["produto"],
        "urgency_score": 9.5,
        "entities": {"produto": "notebook"}
    },
    {
        "title": "Dificuldade para trocar",
        "text": "Estou há uma semana tentando trocar um produto defeituoso e ninguém me atende.",
        "user_name": "Juliana Lima",
        "sentiment": "Negativo",
        "classification": ["atendimento"],
        "urgency_score": 7.0,
        "entities": {}
    },
    {
        "title": "Entrega no endereço errado",
        "text": "Meu pedido foi entregue em outro endereço e agora não sei onde está.",
        "user_name": "Ricardo Souza",
        "sentiment": "Muito Negativo",
        "classification": ["entrega"],
        "urgency_score": 9.0,
        "entities": {}
    },
    {
        "title": "Produto com arranhões",
        "text": "A TV chegou com arranhões. Embalagem estava péssima.",
        "user_name": "Fernanda Rocha",
        "sentiment": "Negativo",
        "classification": ["produto"],
        "urgency_score": 6.5,
        "entities": {"produto": "TV"}
    },
    {
        "title": "Preço diferente do site",
        "text": "No site estava R$ 500, mas me cobraram R$ 650. Quero explicação!",
        "user_name": "Marcos Pereira",
        "sentiment": "Muito Negativo",
        "classification": ["preco"],
        "urgency_score": 8.5,
        "entities": {}
    },
    {
        "title": "Vendedor mentiu sobre garantia",
        "text": "O vendedor disse que tinha 2 anos de garantia, mas o produto só tem 3 meses.",
        "user_name": "Luciana Alves",
        "sentiment": "Negativo",
        "classification": ["atendimento"],
        "urgency_score": 7.5,
        "entities": {}
    },
    {
        "title": "Produto não chegou",
        "text": "Paguei há 15 dias e o produto não chegou. Ninguém sabe informar nada.",
        "user_name": "Roberto Dias",
        "sentiment": "Muito Negativo",
        "classification": ["entrega"],
        "urgency_score": 9.5,
        "entities": {}
    },
    {
        "title": "Falta de peças",
        "text": "O fogão chegou sem os queimadores. Como vou usar assim?",
        "user_name": "Silvia Martins",
        "sentiment": "Negativo",
        "classification": ["produto"],
        "urgency_score": 8.0,
        "entities": {"produto": "fogão"}
    },
    {
        "title": "SAC não resolve",
        "text": "Já liguei 5 vezes para o SAC e ninguém resolve meu problema. Péssimo!",
        "user_name": "Paulo Henrique",
        "sentiment": "Muito Negativo",
        "classification": ["atendimento"],
        "urgency_score": 8.5,
        "entities": {}
    },
    {
        "title": "Cupom não funcionou",
        "text": "Tentei usar um cupom de desconto e disseram que não era válido.",
        "user_name": "Beatriz Campos",
        "sentiment": "Negativo",
        "classification": ["outros"],
        "urgency_score": 5.5,
        "entities": {}
    },
    {
        "title": "Loja suja e desorganizada",
        "text": "A loja estava muito suja e os produtos desorganizados. Falta de cuidado!",
        "user_name": "Gabriel Mendes",
        "sentiment": "Negativo",
        "classification": ["outros"],
        "urgency_score": 4.5,
        "entities": {}
    }
]


async def test_response_generation():
    """Test the response generation system"""
    print("=" * 80)
    print("TESTE DO SISTEMA DE GERAÇÃO DE RESPOSTAS - CHAT C")
    print("=" * 80)
    print()

    # Initialize database
    print("Inicializando banco de dados...")
    init_db()
    db = SessionLocal()

    # Create service
    service = ResponseService()

    results = []

    try:
        # Create and process each complaint
        for i, complaint_data in enumerate(SAMPLE_COMPLAINTS, 1):
            print(f"\n{'=' * 80}")
            print(f"RECLAMAÇÃO {i}/15")
            print(f"{'=' * 80}")

            # Create complaint
            complaint = Complaint(**complaint_data)
            db.add(complaint)
            db.commit()
            db.refresh(complaint)

            print(f"Título: {complaint.title}")
            print(f"Cliente: {complaint.user_name}")
            print(f"Categoria: {complaint.classification[0]}")
            print(f"Sentimento: {complaint.sentiment}")
            print(f"Urgência: {complaint.urgency_score}/10")
            print()

            # Generate response
            print("Gerando resposta personalizada...")
            result = await service.generate_and_save_response(db, complaint.id)

            results.append({
                'complaint': complaint_data,
                'result': result
            })

            print()
            print("RESPOSTA GERADA:")
            print("-" * 80)
            print(result['response'])
            print("-" * 80)
            print()
            print(f"Cupom: {result['coupon']['code']}")
            print(f"Desconto: {result['coupon']['discount']}%")
            print(f"Válido até: {result['coupon']['valid_until']}")
            print()

        # Summary
        print("\n" + "=" * 80)
        print("RESUMO DOS TESTES")
        print("=" * 80)
        print(f"Total de respostas geradas: {len(results)}")

        # Count by category
        categories = {}
        for r in results:
            cat = r['complaint']['classification'][0]
            categories[cat] = categories.get(cat, 0) + 1

        print("\nDistribuição por categoria:")
        for cat, count in categories.items():
            print(f"  - {cat}: {count}")

        # Count by discount
        discounts = {}
        for r in results:
            discount = r['result']['coupon']['discount']
            discounts[discount] = discounts.get(discount, 0) + 1

        print("\nDistribuição de descontos:")
        for discount, count in sorted(discounts.items()):
            print(f"  - {discount}%: {count} cupons")

        print("\n✅ TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")

        return results

    finally:
        db.close()


if __name__ == "__main__":
    results = asyncio.run(test_response_generation())
