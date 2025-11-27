"""
Script para popular dados de exemplo de respostas dos concorrentes.
Isso é usado para demonstração quando não há tempo de fazer scraping.
"""
from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint, Competitor

# Dados de exemplo de respostas bem avaliadas (baseado em padrões reais)
SAMPLE_RESPONSES = [
    {
        "company_response": """Olá, [Nome do cliente]!

Primeiramente, pedimos sinceras desculpas pelo transtorno causado. Entendemos sua frustração e lamentamos muito que sua experiência não tenha sido positiva.

Já identificamos o problema e tomamos as seguintes providências:
1. Entraremos em contato com você em até 24h para resolver a questão
2. O reembolso será processado em até 5 dias úteis
3. Como compensação, oferecemos 20% de desconto na próxima compra

Agradecemos por nos informar e pela oportunidade de melhorar nossos serviços.

Atenciosamente,
Equipe de Atendimento""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram rapidamente e ainda deram desconto. Atendimento excelente!"
    },
    {
        "company_response": """Prezado(a) cliente,

Sentimos muito pelo ocorrido. Sua satisfação é nossa prioridade e não mediremos esforços para resolver esta situação.

Já estamos trabalhando na solução:
- Nossa equipe de logística foi acionada
- Prazo máximo de resolução: 48 horas
- Caso preferira, podemos fazer o estorno imediato

Por favor, entre em contato pelo nosso SAC 0800-XXX-XXXX ou responda esta mensagem para darmos continuidade.

Pedimos desculpas novamente e contamos com sua compreensão.

Equipe de Suporte""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Foram muito atenciosos e resolveram o problema."
    },
    {
        "company_response": """Olá!

Recebemos seu relato e entendemos perfeitamente sua insatisfação. Lamentamos muito pelo inconveniente.

Estamos entrando em contato para:
✓ Resolver o problema do seu pedido
✓ Oferecer reembolso integral se preferir
✓ Garantir que isso não se repita

Nossa equipe especializada já está cuidando do seu caso. Você receberá uma atualização em breve.

Mais uma vez, pedimos desculpas e agradecemos pela paciência.

Abraços,
Time de Atendimento""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Gostei do atendimento, resolveram rápido."
    },
    {
        "company_response": """Prezado cliente,

Lamentamos profundamente o ocorrido e assumimos total responsabilidade pelo erro.

Ações tomadas:
1. Identificamos a falha no processo
2. Seu caso foi escalado para resolução prioritária
3. Garantimos o reembolso completo
4. Adicionamos um crédito de R$30 em sua conta como pedido de desculpas

Estamos comprometidos em reconquistar sua confiança.

Atenciosamente,
Gestão de Qualidade""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Excelente! Resolveram super rápido e ainda deram crédito extra. Vou continuar comprando."
    },
    {
        "company_response": """Olá,

Obrigado por entrar em contato. Pedimos desculpas pelo transtorno causado.

Verificamos seu pedido e providenciamos a solução:
- Nova entrega agendada para amanhã
- Sem custo adicional
- Brinde surpresa como agradecimento pela compreensão

Qualquer dúvida, estamos à disposição.

Att,
Equipe""",
        "customer_score": 10.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Perfeito! Resolveram no mesmo dia e ainda mandaram brinde!"
    },
    {
        "company_response": """Prezado(a),

Recebemos sua reclamação e estamos muito preocupados com o ocorrido.

Gostaríamos de entender melhor a situação. Por favor, entre em contato conosco pelo WhatsApp (XX) XXXXX-XXXX ou pelo e-mail atendimento@empresa.com.br

Aguardamos seu retorno para resolvermos juntos.

Atenciosamente""",
        "customer_score": 6.0,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "Pediram pra eu entrar em contato por outro canal, não resolveram pelo RA."
    },
    {
        "company_response": """Olá!

Sentimos muito pelo ocorrido e já providenciamos a solução.

O estorno já foi solicitado e cairá em sua conta em até 7 dias úteis. Também registramos seu feedback para melhoria contínua dos nossos processos.

Esperamos poder atendê-lo novamente em breve, desta vez com a qualidade que você merece.

Abraços,
Equipe de Atendimento ao Cliente""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "O estorno caiu certinho. Bom atendimento."
    },
    {
        "company_response": """Prezado cliente,

Agradecemos seu contato e pedimos sinceras desculpas pelo inconveniente.

Nossa equipe já está analisando seu caso com prioridade máxima. Em até 2 dias úteis você terá uma posição definitiva.

Contamos com sua compreensão.

Atenciosamente,
SAC""",
        "customer_score": 7.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Demorou um pouco mas resolveram."
    },
]


def seed_responses():
    db = SessionLocal()
    try:
        # Get complaints without responses
        complaints = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.is_(None)
        ).limit(len(SAMPLE_RESPONSES)).all()

        if not complaints:
            print("No complaints without responses found!")
            return

        updated = 0
        for i, complaint in enumerate(complaints):
            if i >= len(SAMPLE_RESPONSES):
                break

            sample = SAMPLE_RESPONSES[i]
            complaint.company_response = sample["company_response"]
            complaint.customer_score = sample["customer_score"]
            complaint.was_resolved = sample["was_resolved"]
            complaint.would_buy_again = sample["would_buy_again"]
            complaint.customer_evaluation = sample["customer_evaluation"]
            updated += 1
            print(f"Updated complaint {complaint.id}: Score={sample['customer_score']}")

        db.commit()
        print(f"\nTotal updated: {updated}")

        # Show stats
        total = db.query(CompetitorComplaint).count()
        with_response = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.isnot(None)
        ).count()
        high_score = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.customer_score >= 8
        ).count()

        print(f"\nStats:")
        print(f"  Total complaints: {total}")
        print(f"  With responses: {with_response}")
        print(f"  High score (8+): {high_score}")

    finally:
        db.close()


if __name__ == "__main__":
    seed_responses()
