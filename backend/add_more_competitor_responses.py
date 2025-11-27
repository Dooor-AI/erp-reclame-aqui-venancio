# -*- coding: utf-8 -*-
"""
Script para adicionar mais respostas de exemplo aos concorrentes.
Baseado em padroes reais de respostas do Reclame Aqui.
"""
from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint, Competitor
import random

# Mais exemplos de respostas bem avaliadas (baseado em padroes reais)
ADDITIONAL_RESPONSES = [
    # Respostas bem avaliadas (score >= 8)
    {
        "company_response": """Prezado(a) cliente,

Agradecemos por entrar em contato e nos dar a oportunidade de resolver essa situacao.

Apos analise do seu caso, identificamos o problema e ja tomamos as seguintes providencias:

1. Seu pedido foi localizado e sera reenviado hoje mesmo
2. Adicionamos um voucher de R$ 25,00 como pedido de desculpas
3. Voce recebera o codigo de rastreio por e-mail em ate 2 horas

Lamentamos profundamente pelo transtorno causado e estamos a disposicao para qualquer esclarecimento adicional.

Atenciosamente,
Equipe de Atendimento""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram muito rapido e ainda ganhei voucher. Otimo atendimento!"
    },
    {
        "company_response": """Ola!

Sentimos muito pelo ocorrido. Sua satisfacao e prioridade para nos.

Ja realizamos o estorno integral do valor em seu cartao. O prazo para compensacao e de ate 2 faturas, conforme regras da operadora.

Alem disso, como forma de compensacao, adicionamos 1500 pontos em seu programa de fidelidade.

Contamos com sua compreensao e esperamos atende-lo novamente em breve.

Equipe de Suporte ao Cliente""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Estorno realizado conforme prometido. Bom atendimento."
    },
    {
        "company_response": """Prezado cliente,

Recebemos sua reclamacao e lamentamos profundamente o inconveniente.

Sobre o seu caso:
- Identificamos a falha em nosso sistema de entregas
- Seu pedido foi priorizado e sera entregue amanha
- Voce nao precisara estar presente, deixaremos com o porteiro/vizinho conforme cadastro

Caso prefira, podemos agendar nova data de entrega de sua preferencia.

Pedimos desculpas pelo transtorno.

Atenciosamente,
Central de Relacionamento""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Entregaram no dia seguinte como prometido."
    },
    {
        "company_response": """Ola!

Obrigado por nos informar. Levamos sua reclamacao muito a serio.

Sobre a situacao relatada:
1. Ja acionamos nossa auditoria interna para investigar
2. A loja foi notificada e recebera treinamento
3. Como compensacao, oferecemos 30% de desconto na proxima compra

Enviaremos por e-mail o cupom de desconto em ate 24 horas.

Mais uma vez, pedimos desculpas e agradecemos pela paciencia.

Time de Qualidade""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Excelente! Foram muito profissionais e o desconto foi otimo."
    },
    {
        "company_response": """Prezado(a),

Sentimos muito pelo transtorno. Nosso compromisso e garantir sua satisfacao.

Verificamos seu pedido e constatamos o erro. Seguem as acoes tomadas:

- Reembolso integral solicitado (R$ 245,90)
- Prazo de compensacao: 7 dias uteis
- Cupom de 20% para proxima compra: DESCULPAS20

Estamos a disposicao pelo chat, WhatsApp ou SAC 0800-123-4567.

Com carinho,
Equipe de Atendimento""",
        "customer_score": 10.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Nota 10! Resolveram rapido e ainda deram cupom de desconto."
    },
    # Respostas medianas (score 6-7)
    {
        "company_response": """Prezado cliente,

Recebemos sua solicitacao e estamos analisando o caso.

Por favor, entre em contato com nosso SAC pelo telefone 0800-XXX-XXXX ou pelo chat do aplicativo para darmos continuidade ao atendimento.

Atenciosamente,
SAC""",
        "customer_score": 6.0,
        "was_resolved": True,
        "would_buy_again": False,
        "customer_evaluation": "Resolveram depois de eu ligar varias vezes."
    },
    {
        "company_response": """Ola,

Agradecemos o contato. Estamos verificando a situacao relatada.

Nossa equipe entrara em contato em ate 48 horas uteis para posiciona-lo sobre o andamento.

Pedimos desculpas pelo inconveniente.

Equipe de Suporte""",
        "customer_score": 7.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Demorou um pouco mas resolveram."
    },
    # Respostas ruins (score < 6)
    {
        "company_response": """Prezado cliente,

Lamentamos o ocorrido. Por favor, envie os seguintes documentos para analise:
- CPF
- Comprovante de pagamento
- Fotos do produto

Apos recebimento, analisaremos em ate 10 dias uteis.

Atenciosamente,
Central de Atendimento""",
        "customer_score": 4.0,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "Pediram um monte de documento e nao resolveram nada."
    },
    {
        "company_response": """Ola,

Sua reclamacao foi registrada sob o protocolo 123456.

Por favor, aguarde o prazo de 30 dias para analise.

Att,
SAC""",
        "customer_score": 3.0,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "Resposta padrao, sem solucao. Nunca mais compro."
    },
    # Mais respostas boas
    {
        "company_response": """Oi!

Obrigado por nos dar a chance de corrigir isso!

Ja falamos com a transportadora e seu pedido sera entregue amanha de manha. Voce recebera um SMS quando o entregador estiver a caminho.

Como pedido de desculpas, incluimos um brinde surpresa no pacote!

Abracos,
Time de Logistica""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Super atenciosos! Entregaram e ainda veio brinde."
    },
    {
        "company_response": """Prezado(a) cliente,

Pedimos sinceras desculpas pelo inconveniente. Entendemos como isso e frustrante.

Tomamos as seguintes medidas imediatas:
- Seu pedido foi cancelado e estornado
- Adicionamos R$50 em creditos na sua conta
- Acionamos o fornecedor para investigar o lote

Voce pode usar os creditos na sua proxima compra, sem prazo de validade.

Agradecemos sua paciencia.

Equipe de Relacionamento""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Muito satisfeita! Resolveram super rapido e ainda ganhei creditos."
    },
    {
        "company_response": """Ola!

Sentimos muito por essa experiencia negativa. Voce tem toda razao em reclamar.

Para resolver:
1. Agendamos a coleta do produto com defeito para amanha
2. Um novo produto sera enviado no mesmo dia da coleta
3. Frete por nossa conta, claro!

Mandaremos o link de rastreio por e-mail.

Obrigado pela paciencia!
Equipe de Trocas""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Processo de troca foi super tranquilo. Recomendo!"
    },
    {
        "company_response": """Prezado cliente,

Agradecemos por nos informar sobre o ocorrido. Lamentamos muito!

Ja identificamos o problema:
- O produto estava em promocao mas o preco nao foi atualizado no carrinho
- Corrigimos o bug em nosso sistema
- Voce recebera o reembolso da diferenca + 10% adicional como compensacao

O valor sera creditado em ate 5 dias uteis.

Atenciosamente,
Time de TI e Atendimento""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Reconheceram o erro e deram ate a mais. Top!"
    },
    {
        "company_response": """Ola!

Recebemos seu relato e pedimos sinceras desculpas pelo transtorno.

Infelizmente o produto que voce comprou esta em falta em nosso estoque. Mas temos opcoes:

1. Reembolso integral em ate 3 dias uteis
2. Troca por produto similar + R$30 de bonus
3. Vale-compras no valor + 15%

Por favor, nos informe sua preferencia respondendo esta mensagem.

Aguardamos seu retorno.
Equipe Comercial""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Deram varias opcoes e escolhi o vale-compras. Justo."
    },
    {
        "company_response": """Prezado(a),

Sua satisfacao e muito importante para nos!

Sobre o atraso na entrega:
- Houve um problema com a transportadora parceira
- Seu pedido foi redirecionado e chegara em 24h
- Oferecemos frete gratis na sua proxima compra como compensacao

Use o cupom FRETEGRATIS na proxima compra.

Pedimos desculpas e agradecemos a compreensao!
Time de Logistica""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Entrega chegou no dia seguinte. Cupom funcionou perfeitamente."
    },
]


def add_responses():
    """Adiciona mais respostas de exemplo aos concorrentes."""
    db = SessionLocal()
    try:
        # Pega reclamacoes sem resposta
        complaints = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.is_(None)
        ).limit(len(ADDITIONAL_RESPONSES)).all()

        if not complaints:
            print("Todas as reclamacoes ja tem respostas!")
            return

        updated = 0
        for i, complaint in enumerate(complaints):
            if i >= len(ADDITIONAL_RESPONSES):
                break

            response = ADDITIONAL_RESPONSES[i]

            complaint.company_response = response["company_response"]
            complaint.customer_score = response["customer_score"]
            complaint.was_resolved = response["was_resolved"]
            complaint.would_buy_again = response["would_buy_again"]
            complaint.customer_evaluation = response["customer_evaluation"]

            updated += 1
            print(f"Atualizado ID {complaint.id}: Score={response['customer_score']}")

        db.commit()
        print(f"\nTotal atualizado: {updated}")

        # Estatisticas
        total = db.query(CompetitorComplaint).count()
        with_response = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.isnot(None)
        ).count()
        high_score = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.customer_score >= 8
        ).count()
        resolved = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.was_resolved == True
        ).count()

        print(f"\nEstatisticas:")
        print(f"  Total reclamacoes: {total}")
        print(f"  Com respostas: {with_response}")
        print(f"  Score alto (8+): {high_score}")
        print(f"  Resolvidas: {resolved}")

    finally:
        db.close()


if __name__ == "__main__":
    add_responses()
