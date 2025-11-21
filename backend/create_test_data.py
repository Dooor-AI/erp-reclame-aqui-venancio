"""
Script to create test complaint data for validation
"""
from app.core.database import SessionLocal
from app.db.models import Complaint
from datetime import datetime, timedelta
import random

# Sample complaints with varied sentiments, categories, and entities
SAMPLE_COMPLAINTS = [
    # Negative - Produto
    {
        "title": "Geladeira quebrou em 3 dias",
        "text": "Comprei uma geladeira Frost Free 400L na loja do Shopping Center e ela simplesmente parou de funcionar após 3 dias de uso. Entrei em contato com a assistência técnica e até agora nada foi resolvido. Produto de péssima qualidade! Isso é inaceitável, vou entrar em contato com o Procon.",
        "user_name": "João Silva",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    {
        "title": "Produto defeituoso e sem solução",
        "text": "Adquiri um fogão 5 bocas que apresentou defeito logo na primeira semana. Já solicitei a troca mas ninguém resolve. A empresa não está cumprindo com suas obrigações. Péssimo atendimento também.",
        "user_name": "Maria Santos",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    # Negative - Atendimento
    {
        "title": "Atendimento horrível",
        "text": "Fui muito mal atendido na loja da Avenida Principal. O funcionário Carlos foi extremamente rude e não quis me ajudar. Inadmissível esse tipo de tratamento ao cliente.",
        "user_name": "Pedro Oliveira",
        "status": "Não respondida",
        "category": "Atendimento"
    },
    {
        "title": "Ninguém resolve meu problema",
        "text": "Ligo para o SAC há dias e ninguém resolve. Falam que vão retornar e nunca acontece. Descaso total com o consumidor. Vou processar judicialmente se não resolverem.",
        "user_name": "Ana Costa",
        "status": "Não respondida",
        "category": "Atendimento"
    },
    # Negative - Entrega
    {
        "title": "Entrega atrasada há 2 meses",
        "text": "Comprei um sofá há 2 meses e até hoje não foi entregue. Ligo todos os dias e ninguém sabe informar quando vai chegar. Isso é um absurdo, já cancelei o pedido e vou exigir estorno total.",
        "user_name": "Ricardo Souza",
        "status": "Não respondida",
        "category": "Móveis"
    },
    {
        "title": "Entrega foi para endereço errado",
        "text": "O produto que comprei foi entregue no endereço errado e agora estou sem o produto e sem resposta. Prejuízo total. Quero meu dinheiro de volta urgente!",
        "user_name": "Juliana Lima",
        "status": "Não respondida",
        "category": "Eletrônicos"
    },
    # Negative - Preço
    {
        "title": "Cobrança indevida no cartão",
        "text": "Fui cobrado duas vezes pela mesma compra. Já reclamei no banco e na loja mas ninguém resolve. Isso parece fraude! Vou abrir reclamação formal no Procon.",
        "user_name": "Fernando Alves",
        "status": "Não respondida",
        "category": "Cobrança"
    },
    {
        "title": "Preço diferente do anunciado",
        "text": "O site anunciava um preço e na hora de finalizar a compra cobraram outro valor muito mais alto. Propaganda enganosa. Exijo que respeitem o preço divulgado.",
        "user_name": "Carla Mendes",
        "status": "Não respondida",
        "category": "Cobrança"
    },
    # Negative - Múltiplas categorias
    {
        "title": "Problemas com tudo",
        "text": "Comprei um ar condicionado que chegou com defeito, o entregador foi grosseiro, o atendimento ao cliente é péssimo e ainda por cima me cobraram frete indevido. Empresa horrível, nunca mais compro aqui!",
        "user_name": "Roberto Castro",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    # Neutro
    {
        "title": "Produto ok mas poderia melhorar",
        "text": "A máquina de lavar funciona bem, mas achei o consumo de energia um pouco alto. Atendimento foi razoável, nada excepcional. Produto atende, mas esperava mais pelo preço pago.",
        "user_name": "Beatriz Rocha",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    {
        "title": "Experiência mediana",
        "text": "Comprei um micro-ondas. Entrega foi no prazo, produto funciona normalmente. Nada de excepcional mas também nada de ruim para reclamar.",
        "user_name": "Lucas Martins",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    # Positivo
    {
        "title": "Excelente atendimento",
        "text": "Fui muito bem atendido pela funcionária Amanda na loja do centro. Ela foi super atenciosa e me ajudou a escolher o melhor produto. Recomendo!",
        "user_name": "Marcos Vieira",
        "status": "Não respondida",
        "category": "Atendimento"
    },
    {
        "title": "Produto de qualidade",
        "text": "Comprei uma geladeira e estou muito satisfeito. Chegou no prazo, instalação perfeita, produto de excelente qualidade. Parabéns!",
        "user_name": "Patrícia Gomes",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    # Mais negativos graves
    {
        "title": "Vou processar a empresa",
        "text": "Comprei um fogão que explodiu e quase causou um incêndio na minha casa. Minha família poderia ter se machucado gravemente. Isso é crime! Já procurei um advogado e vou processá-los. Situação gravíssima e inadmissível.",
        "user_name": "Sandra Fernandes",
        "status": "Não respondida",
        "category": "Eletrodomésticos"
    },
    {
        "title": "Produto falsificado",
        "text": "Recebi um produto que não é original, parece ser falsificado. Paguei caro por algo genuíno e recebi uma imitação. Isso é golpe, fraude! Vou denunciar às autoridades competentes.",
        "user_name": "Eduardo Barros",
        "status": "Não respondida",
        "category": "Eletrônicos"
    },
    # Negativos leves
    {
        "title": "Pequeno problema na entrega",
        "text": "O produto chegou um dia depois do prazo previsto. Fiquei um pouco chateado mas nada grave. O produto em si é bom.",
        "user_name": "Renata Dias",
        "status": "Não respondida",
        "category": "Móveis"
    },
    {
        "title": "Embalagem danificada",
        "text": "Recebi o produto com a caixa amassada, mas o conteúdo estava intacto. Acho que poderiam ter mais cuidado no transporte.",
        "user_name": "Paulo Ribeiro",
        "status": "Não respondida",
        "category": "Eletrônicos"
    },
    # Mais variedade
    {
        "title": "Prazo de troca muito curto",
        "text": "A política de troca de apenas 7 dias é muito restritiva. Outros concorrentes oferecem 30 dias. Isso precisa melhorar.",
        "user_name": "Aline Cardoso",
        "status": "Não respondida",
        "category": "Políticas"
    },
    {
        "title": "Site com problemas",
        "text": "Tentei comprar pelo site mas o sistema de pagamento apresentou erro várias vezes. Tive que ir na loja física. Site precisa de melhorias urgentes.",
        "user_name": "Gabriel Torres",
        "status": "Não respondida",
        "category": "Site/Online"
    },
    {
        "title": "Garantia negada sem motivo",
        "text": "Meu produto está na garantia mas a empresa se recusa a fazer o reparo alegando motivos absurdos. Isso é desrespeito ao código de defesa do consumidor. Vou ao Procon.",
        "user_name": "Camila Freitas",
        "status": "Não respondida",
        "category": "Garantia"
    },
]


def create_test_complaints():
    """Create sample complaints for testing"""
    db = SessionLocal()

    try:
        # Check if already has data
        existing_count = db.query(Complaint).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} complaints.")
            response = input("Do you want to add more test data? (y/n): ")
            if response.lower() != 'y':
                print("Skipping data creation.")
                return existing_count

        # Create complaints
        created = 0
        for i, complaint_data in enumerate(SAMPLE_COMPLAINTS):
            # Add some variation to dates
            days_ago = random.randint(1, 30)
            complaint_date = datetime.now() - timedelta(days=days_ago)

            complaint = Complaint(
                **complaint_data,
                complaint_date=complaint_date,
                external_id=f"TEST_{i+1:03d}",
                scraped_at=datetime.now()
            )
            db.add(complaint)
            created += 1

        db.commit()
        total = db.query(Complaint).count()
        print(f"Created {created} test complaints successfully!")
        print(f"Total complaints in database: {total}")
        return total

    except Exception as e:
        db.rollback()
        print(f"Error creating test data: {e}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    print("Creating test complaint data...")
    print("-" * 50)
    count = create_test_complaints()
    print("-" * 50)
    print(f"Database ready with {count} complaints for testing!")
