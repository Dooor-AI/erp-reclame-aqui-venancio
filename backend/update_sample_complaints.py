# -*- coding: utf-8 -*-
"""
Script para atualizar as reclamações de concorrentes com dados completos de exemplo.
"""
from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint, Competitor

# Dados completos de exemplo (reclamações + respostas reais baseadas em padrões do Reclame Aqui)
COMPLETE_EXAMPLES = [
    {
        "title": "Entrega não realizada e falsificação de assinatura por motoboy da farmácia",
        "text": """Efetuei uma compra ontem para entrega delivery e o moto uber contratado pela farmácia desonestou não entregou a mercadoria e colocou uma assinatura falsa como se tivesse entregue.

Já entrei em contato com a farmácia por telefone mas não consegui resolver. Preciso do reembolso urgente pois são medicamentos que preciso tomar diariamente.

Número do pedido: 123456
Valor: R$ 187,50
Data da compra: 20/11/2024""",
        "company_response": """Olá!

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
        "title": "Atraso na entrega de medicamento controlado e falta de comunicação",
        "text": """Comprei um medicamento controlado (tarja preta) com prazo de entrega de 2 dias úteis. Já se passaram 7 dias e nada do medicamento chegar.

Liguei no SAC 3 vezes e sempre me pedem para aguardar. O medicamento é essencial para meu tratamento e estou sem tomar há 5 dias por conta desse atraso absurdo.

Preciso de uma solução URGENTE! Se não resolverem vou procurar o Procon.

Pedido: 789012
Medicamento: Rivotril 2mg""",
        "company_response": """Prezado(a) cliente,

Sentimos muito pelo ocorrido. Sua satisfação é nossa prioridade e não mediremos esforços para resolver esta situação.

Já estamos trabalhando na solução:
- Nossa equipe de logística foi acionada
- Prazo máximo de resolução: 48 horas
- Caso prefira, podemos fazer o estorno imediato

Por favor, entre em contato pelo nosso SAC 0800-725-4000 ou responda esta mensagem para darmos continuidade.

Pedimos desculpas novamente e contamos com sua compreensão.

Equipe de Suporte""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Foram muito atenciosos e resolveram o problema. O medicamento chegou no dia seguinte após a reclamação."
    },
    {
        "title": "Produto vencido vendido na loja física",
        "text": """Comprei um protetor solar na loja da Rua Augusta e quando cheguei em casa percebi que o produto estava com a validade vencida há 2 meses!

Isso é um absurdo! Produto vencido pode causar problemas de saúde. A loja precisa ter mais cuidado com a verificação do estoque.

Quero o reembolso e uma explicação de como isso aconteceu.

Loja: Rua Augusta, 1500
Produto: Protetor Solar FPS 50
Validade: Set/2024 (comprado em Nov/2024)""",
        "company_response": """Olá!

Recebemos seu relato e entendemos perfeitamente sua insatisfação. Lamentamos muito pelo inconveniente.

Estamos entrando em contato para:
✓ Resolver o problema do seu pedido
✓ Oferecer reembolso integral
✓ Garantir que isso não se repita

Nossa equipe especializada já está cuidando do seu caso. A loja foi notificada para fazer uma varredura completa no estoque.

Mais uma vez, pedimos desculpas e agradecemos pela paciência.

Abraços,
Time de Atendimento""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Gostei do atendimento, resolveram rápido e ainda me deram outro protetor novo."
    },
    {
        "title": "Atendimento ineficiente e restrição indevida do programa Farmácia Popular",
        "text": """Quero registrar 02 reclamações: a primeira contra a filial de Santa Isabel-Pa, que hoje no balcão de atendimento informou que a medicação que preciso não poderia ser vendida pelo programa Farmácia Popular, sendo que em outras redes consigo comprar normalmente.

A segunda reclamação é sobre o atendimento do SAC, que não conseguiu me dar uma explicação clara sobre o motivo da restrição.

Sou cliente há anos e nunca tive esse problema. Preciso de uma posição oficial da empresa.""",
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
        "title": "Pedido incompleto: Falta de produto no pedido",
        "text": """Fiz um pedido no site da farmácia e recebi hoje, mas um dos produtos está faltando.

Eu pedi 2 unidades do protetor solar da marca X e só veio 1. A nota fiscal consta as 2 unidades e fui cobrado por ambas.

Preciso receber o produto que falta ou ter o valor estornado.

Pedido: 456789
Produto faltante: Protetor Solar FPS 70 (1 unidade)
Valor unitário: R$ 89,90""",
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
        "title": "Propaganda enganosa no site - preço diferente no carrinho",
        "text": """O site estava anunciando um medicamento por R$ 29,90 mas quando coloco no carrinho o preço muda para R$ 45,90.

Isso é propaganda enganosa! Tirei print das duas telas como prova.

Quero comprar pelo preço anunciado ou vou denunciar no Procon.""",
        "company_response": """Prezado(a),

Recebemos sua reclamação e estamos muito preocupados com o ocorrido.

Gostaríamos de entender melhor a situação. Por favor, entre em contato conosco pelo WhatsApp (11) 99999-9999 ou pelo e-mail atendimento@farmacia.com.br

Aguardamos seu retorno para resolvermos juntos.

Atenciosamente""",
        "customer_score": 6.0,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "Pediram pra eu entrar em contato por outro canal, não resolveram pelo RA."
    },
    {
        "title": "Cobrança duplicada no cartão de crédito",
        "text": """Fiz uma compra no valor de R$ 156,80 e fui cobrado duas vezes no cartão de crédito.

Já entrei em contato com o banco e eles confirmaram que são duas cobranças distintas vindas da farmácia.

Preciso do estorno imediato de uma das cobranças!

Data da compra: 15/11/2024
Valor de cada cobrança: R$ 156,80
Cartão final: 4532""",
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
        "title": "Demora excessiva no atendimento da loja física",
        "text": """Fui à loja do Shopping Center Norte e esperei mais de 40 minutos para ser atendido, mesmo tendo poucos clientes na fila.

Os funcionários estavam conversando entre si e não demonstravam nenhuma urgência em atender.

Isso é uma falta de respeito com o cliente! Precisamos de mais agilidade no atendimento.""",
        "company_response": """Prezado cliente,

Agradecemos seu contato e pedimos sinceras desculpas pelo inconveniente.

Nossa equipe já está analisando seu caso com prioridade máxima. Em até 2 dias úteis você terá uma posição definitiva.

Contamos com sua compreensão.

Atenciosamente,
SAC""",
        "customer_score": 7.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Demorou um pouco mas resolveram. A gerente da loja entrou em contato pedindo desculpas."
    },
]


def update_complaints():
    db = SessionLocal()
    try:
        # Get complaints with responses (the ones we seeded before)
        complaints = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.isnot(None)
        ).order_by(CompetitorComplaint.id).limit(len(COMPLETE_EXAMPLES)).all()

        if not complaints:
            print("No complaints found to update!")
            return

        updated = 0
        for i, complaint in enumerate(complaints):
            if i >= len(COMPLETE_EXAMPLES):
                break

            example = COMPLETE_EXAMPLES[i]

            # Update with complete data
            complaint.title = example["title"]
            complaint.text = example["text"]
            complaint.company_response = example["company_response"]
            complaint.customer_score = example["customer_score"]
            complaint.was_resolved = example["was_resolved"]
            complaint.would_buy_again = example["would_buy_again"]
            complaint.customer_evaluation = example["customer_evaluation"]

            updated += 1
            print(f"Updated complaint {complaint.id}: {example['title'][:50]}...")

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
    update_complaints()
