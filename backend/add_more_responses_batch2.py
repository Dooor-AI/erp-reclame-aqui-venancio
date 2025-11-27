# -*- coding: utf-8 -*-
"""
Script para adicionar mais respostas de exemplo aos concorrentes - Batch 2.
Baseado em padroes reais de respostas do Reclame Aqui para farmacias.
"""
from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint, Competitor

# Mais exemplos de respostas (batch 2) - focado em farmacias
BATCH2_RESPONSES = [
    # Respostas excelentes (score 9-10) - Padrao Droga Raia/Drogasil
    {
        "company_response": """Ola, bom dia!

Agradecemos por nos procurar. Sentimos muito pelo ocorrido e ja tomamos providencias para resolver sua situacao.

Identificamos que houve um erro no sistema de separacao de pedidos. Para corrigir:

1. Seu produto faltante sera enviado hoje mesmo via Sedex
2. Voce nao pagara frete adicional
3. Adicionamos R$15 em cashback na sua carteira digital

O codigo de rastreio sera enviado por SMS e e-mail assim que o produto sair para entrega.

Agradecemos sua paciencia e compreensao!

Com carinho,
Equipe de Atendimento""",
        "customer_score": 10.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Excelente! Resolveram no mesmo dia e ainda ganhei cashback. Super recomendo!"
    },
    {
        "company_response": """Prezado(a) cliente,

Lamentamos muito o transtorno! Voce tem toda razao em nos procurar.

Acabamos de verificar seu pedido e o reembolso foi processado agora. Confira os detalhes:

- Valor estornado: R$ 189,90
- Forma: mesma forma de pagamento original
- Prazo: ate 2 faturas do seu cartao

Alem disso, liberamos o cupom DESCULPAS15 com 15% OFF para sua proxima compra (valido por 30 dias).

Esperamos poder reconquistar sua confianca!

Atenciosamente,
Central de Relacionamento""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Rapidos demais! Em 30 minutos ja tinham resolvido. Otimo atendimento."
    },
    {
        "company_response": """Oi!

Obrigado por nos dar a oportunidade de resolver isso.

Ja conversamos com a loja e o gerente vai entrar em contato com voce ainda hoje para pedir desculpas pessoalmente.

Sobre seu medicamento:
- Separamos uma unidade em estoque
- Pode retirar a qualquer momento
- Seu desconto do programa de fidelidade foi aplicado

Como forma de pedido de desculpas, adicionamos 500 pontos extras no seu cadastro.

Obrigado pela paciencia!
Time de Qualidade""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "O gerente realmente ligou e pediu desculpas. Ficou tudo certo!"
    },
    # Respostas boas (score 8-8.5) - Padrao Pague Menos/Extrafarma
    {
        "company_response": """Prezado cliente,

Agradecemos o contato e pedimos sinceras desculpas pelo inconveniente.

Verificamos seu caso e o estorno foi solicitado com sucesso. Segue protocolo: 2024112601234

Prazo para estorno:
- PIX/Debito: ate 5 dias uteis
- Credito: ate 2 faturas

Em caso de duvidas, entre em contato pelo 0800-123-4567 informando o protocolo.

Atenciosamente,
SAC""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram dentro do prazo. Poderiam ser mais ageis, mas ok."
    },
    {
        "company_response": """Ola!

Sentimos muito pelo problema com sua entrega.

Ja reenviamos seu pedido e o prazo de entrega e de ate 3 dias uteis. Voce recebera o codigo de rastreio por e-mail.

Caso nao receba, por favor entre em contato novamente.

Pedimos desculpas pelo transtorno.

Equipe de Logistica""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Reenviaram o pedido. Chegou certinho dessa vez."
    },
    {
        "company_response": """Prezado(a),

Agradecemos por nos informar sobre o ocorrido. Lamentamos muito!

Apos analisar seu caso:
- Identificamos o erro no cadastro do programa Farmacia Popular
- Ja regularizamos sua situacao
- Na proxima compra o desconto sera aplicado automaticamente

Como compensacao, oferecemos frete gratis na proxima compra online. Use o cupom: FRETEZERO

Obrigado pela compreensao!
Equipe de Atendimento""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Regularizaram meu cadastro. Na semana seguinte ja consegui comprar com desconto."
    },
    # Respostas medianas (score 6-7.5)
    {
        "company_response": """Prezado cliente,

Recebemos sua solicitacao e estamos analisando.

Nosso prazo de resposta e de ate 5 dias uteis. Voce sera informado por e-mail sobre o andamento.

Protocolo: 123456789

Atenciosamente,
Central de Atendimento""",
        "customer_score": 7.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Demoraram mas resolveram. Podiam ser mais rapidos."
    },
    {
        "company_response": """Ola,

Lamentamos o inconveniente. Para dar continuidade ao seu atendimento, precisamos de algumas informacoes:

- Numero do pedido completo
- CPF do titular da compra
- Fotos do produto (se aplicavel)

Por favor, responda esta mensagem com os dados solicitados.

SAC""",
        "customer_score": 6.5,
        "was_resolved": True,
        "would_buy_again": False,
        "customer_evaluation": "Pediram um monte de coisa. Depois de enviar tudo, resolveram."
    },
    {
        "company_response": """Prezado(a) cliente,

Agradecemos o contato. Seu caso foi encaminhado para o setor responsavel.

Retornaremos em ate 72 horas uteis.

Atenciosamente,
Ouvidoria""",
        "customer_score": 7.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Demoraram um pouco mas a ouvidoria resolveu."
    },
    # Respostas ruins (score 3-5) - para aprender o que NAO fazer
    {
        "company_response": """Prezado cliente,

Informamos que sua solicitacao esta em analise.

Prazo de resposta: 30 dias.

Atenciosamente,
SAC""",
        "customer_score": 3.5,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "30 dias para analisar? Absurdo! Nunca mais compro aqui."
    },
    {
        "company_response": """Ola,

Para resolver sua situacao, dirija-se a loja mais proxima com o produto e nota fiscal.

Obrigado.""",
        "customer_score": 4.0,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "Querem que eu va ate a loja resolver um erro DELES? Sem nocao."
    },
    {
        "company_response": """Prezado,

Nao identificamos nenhum problema no seu pedido. Por favor, verifique se os dados informados estao corretos.

Att,
Suporte""",
        "customer_score": 2.0,
        "was_resolved": False,
        "would_buy_again": False,
        "customer_evaluation": "Me chamaram de mentiroso. Pior atendimento da minha vida."
    },
    # Mais respostas excelentes (para balancear)
    {
        "company_response": """Oi, tudo bem?

Puxa, que situacao chata! Pedimos mil desculpas por isso.

Ja resolvemos tudo pra voce:
- Estorno processado (cai em ate 48h)
- Cupom de 25% OFF: VOLTA25
- Frete gratis nas proximas 3 compras

Queremos muito que voce volte a comprar com a gente! Se precisar de algo, e so chamar.

Abracos,
Equipe de Atendimento""",
        "customer_score": 10.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "UAU! Superaram minhas expectativas. Atendimento nota 1000!"
    },
    {
        "company_response": """Prezado(a) cliente,

Primeiramente, gostaríamos de agradecer pela confianca em nossa empresa e pedir sinceras desculpas pelo transtorno.

Verificamos seu caso com prioridade maxima e seguem as providencias:

1. ESTORNO: ja processado no valor de R$ 267,80
2. COMPENSACAO: cupom de R$50 adicionado a sua conta
3. MELHORIA: acionamos a transportadora para evitar novos problemas

Seu feedback e muito importante para continuarmos melhorando!

Com carinho,
Diretoria de Atendimento""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Incrivel! Ate a diretoria se envolveu. Virei fa da marca."
    },
    {
        "company_response": """Ola!

Sentimos muito pelo problema com seu medicamento. Sabemos o quanto e importante ter acesso aos remedios no prazo certo.

Tomamos as seguintes acoes:
- Localizamos o produto em estoque na loja mais proxima de voce
- Agendamos entrega para HOJE ate as 18h
- Sem custo adicional

O entregador ligara quando estiver a caminho. Se preferir retirar na loja, tambem esta disponivel.

Obrigado pela paciencia e compreensao!
Time de Entregas""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Entregaram no mesmo dia! Muito bem resolvido."
    },
    {
        "company_response": """Prezado cliente,

Agradecemos por nos procurar e lamentamos profundamente o ocorrido.

Sobre a situacao relatada:
- Verificamos o lote do produto e retiramos de circulacao
- Seu reembolso foi processado imediatamente
- Como compensacao, oferecemos 30% de desconto na proxima compra

A qualidade dos nossos produtos e nossa prioridade. Agradecemos por nos ajudar a melhorar!

Atenciosamente,
Departamento de Qualidade""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Levaram a serio minha reclamacao. Tiraram o lote todo. Responsaveis!"
    },
    {
        "company_response": """Oi!

Que chato que isso aconteceu! Voce tem toda razao de estar insatisfeito(a).

Ja tomamos as providencias:
1. Nova entrega programada para amanha
2. Brinde surpresa incluso no pacote
3. Cupom de 20% para proximas compras: DESCULPA20

O rastreio sera enviado por WhatsApp assim que sair para entrega.

Esperamos que dessa vez tudo corra bem!

Abracos,
Equipe de Logistica""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Super atenciosos! Veio o produto e ainda um brinde fofo. Amei!"
    },
    {
        "company_response": """Prezado(a),

Obrigado por entrar em contato. Pedimos desculpas pelo transtorno.

Solucao aplicada:
- Estorno integral: R$ 156,90
- Bonus de R$25 para proxima compra
- Frete gratis no proximo pedido (cupom: FRETEBONUS)

O estorno ja foi processado e voce pode acompanhar pelo app.

Estamos a disposicao!
SAC Premium""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram rapido e ainda deram bonus. Satisfeito!"
    },
    {
        "company_response": """Ola!

Recebemos sua reclamacao e ja estamos trabalhando na solucao.

O que fizemos:
- Seu caso foi priorizado
- Entrega expressa agendada para hoje
- Cupom de desconto enviado por SMS

Se precisar de ajuda, estamos disponiveis 24h pelo chat do app!

Abracos,
Time de Suporte""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Entregaram no mesmo dia. Bom atendimento."
    },
    {
        "company_response": """Prezado cliente,

Agradecemos o contato e lamentamos o inconveniente.

Verificamos que houve uma falha no processamento do seu pagamento. Ja regularizamos a situacao:

- Pagamento confirmado
- Pedido liberado para entrega
- Previsao: 2 dias uteis

Pedimos desculpas pelo susto!

Atenciosamente,
Financeiro""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram o problema do pagamento. Pedido chegou certinho."
    },
]


def add_responses_batch2():
    """Adiciona mais respostas de exemplo aos concorrentes (batch 2)."""
    db = SessionLocal()
    try:
        # Pega reclamacoes sem resposta
        complaints = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.is_(None)
        ).limit(len(BATCH2_RESPONSES)).all()

        if not complaints:
            print("Todas as reclamacoes ja tem respostas!")
            return

        updated = 0
        for i, complaint in enumerate(complaints):
            if i >= len(BATCH2_RESPONSES):
                break

            response = BATCH2_RESPONSES[i]

            complaint.company_response = response["company_response"]
            complaint.customer_score = response["customer_score"]
            complaint.was_resolved = response["was_resolved"]
            complaint.would_buy_again = response["would_buy_again"]
            complaint.customer_evaluation = response["customer_evaluation"]

            updated += 1
            score = response['customer_score']
            status = "OK" if response['was_resolved'] else "NAO RESOLVIDO"
            print(f"Atualizado ID {complaint.id}: Score={score} ({status})")

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
        low_score = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.customer_score < 6
        ).count()
        resolved = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.was_resolved == True
        ).count()

        print(f"\nEstatisticas atualizadas:")
        print(f"  Total reclamacoes: {total}")
        print(f"  Com respostas: {with_response}")
        print(f"  Score alto (8+): {high_score}")
        print(f"  Score baixo (<6): {low_score}")
        print(f"  Resolvidas: {resolved}")

    finally:
        db.close()


if __name__ == "__main__":
    add_responses_batch2()
