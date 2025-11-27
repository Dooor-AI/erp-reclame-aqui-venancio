# -*- coding: utf-8 -*-
"""
Script para adicionar mais respostas de exemplo aos concorrentes - Batch 3.
Baseado em padroes reais de respostas do Reclame Aqui para farmacias.
"""
from app.core.database import SessionLocal
from app.db.models import CompetitorComplaint, Competitor

# Mais exemplos de respostas (batch 3) - completando a base
BATCH3_RESPONSES = [
    # Respostas excelentes - Entrega
    {
        "company_response": """Ola!

Muito obrigado pelo contato. Pedimos sinceras desculpas pelo atraso na sua entrega.

Ja tomamos as seguintes providencias:
- Localizamos seu pacote - estava retido na transportadora
- Liberamos para entrega prioritaria hoje
- Voce recebera SMS quando o entregador sair

Como forma de compensacao, adicionamos R$20 em creditos na sua conta.

Agradecemos a paciencia!
Time de Entregas""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Perfeito! Entregaram no mesmo dia e ainda ganhei creditos."
    },
    {
        "company_response": """Prezado cliente,

Lamentamos o transtorno com sua entrega. Verificamos que houve um problema no endereco cadastrado.

Corrigimos o endereco e seu pedido sera entregue amanha no periodo da manha.

Qualquer duvida, estamos a disposicao pelo chat ou telefone 0800-XXX-XXXX.

Atenciosamente,
Logistica""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram o problema do endereco. Entregaram certinho."
    },
    # Respostas excelentes - Financeiro
    {
        "company_response": """Oi!

Verificamos sua solicitacao e o estorno foi processado agora mesmo!

Detalhes:
- Valor: R$ 234,50
- Prazo: 3-5 dias uteis para credito
- Protocolo: EST20241126XXX

Tambem liberamos um cupom de 10% para sua proxima compra: VOLTEJA10

Obrigado pela paciencia!
Financeiro""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Estorno caiu em 2 dias. Rapidos e eficientes!"
    },
    {
        "company_response": """Prezado(a),

Identificamos a cobranca duplicada no seu cartao e ja solicitamos o estorno.

Acoes tomadas:
1. Estorno solicitado a operadora
2. Prazo: ate 7 dias uteis
3. Acompanhe pelo app da sua operadora de cartao

Pedimos desculpas pelo erro e agradecemos a compreensao.

Atenciosamente,
Financeiro""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Resolveram a cobranca duplicada. Estorno caiu certinho."
    },
    # Respostas excelentes - Atendimento loja
    {
        "company_response": """Ola!

Ficamos muito tristes em saber do ocorrido na loja. Voce tem toda razao!

O gerente da unidade foi notificado e entrara em contato nas proximas horas para pedir desculpas pessoalmente.

Alem disso:
- Equipe recebera novo treinamento
- Voce ganhou 1000 pontos de fidelidade
- Cupom de 15% na proxima compra: DESCULPAS15

Obrigado por nos ajudar a melhorar!
Ouvidoria""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "O gerente realmente ligou e foi super educado. Problema resolvido!"
    },
    {
        "company_response": """Prezado cliente,

Lamentamos profundamente o atendimento que voce recebeu. Isso nao representa nossos valores.

Providencias tomadas:
- Colaborador sera orientado
- Registro no programa de qualidade
- Cupom de desconto enviado por e-mail

Esperamos poder atende-lo melhor na proxima oportunidade.

Gestao de Pessoas""",
        "customer_score": 8.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Tomaram providencias. Voltei a loja e fui bem atendido."
    },
    # Respostas excelentes - Produto
    {
        "company_response": """Oi!

Que situacao chata! Pedimos mil desculpas pelo produto com defeito.

Ja providenciamos:
- Coleta do produto defeituoso em sua casa (amanha, periodo da tarde)
- Envio de produto novo junto com a coleta
- Brinde especial como pedido de desculpas

Voce nao precisa fazer nada, nosso motoboy vai ate ai!

Abracos,
Qualidade""",
        "customer_score": 10.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Incrivel! Vieram buscar e ja trouxeram outro. Nota 10!"
    },
    {
        "company_response": """Prezado(a),

Sentimos muito pelo problema com o produto. Isso nao deveria acontecer.

Solucao:
- Reembolso integral processado
- Pode descartar o produto (nao precisa devolver)
- Cupom de 20% para nova compra

O valor sera creditado em ate 5 dias uteis.

Atenciosamente,
SAC""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Nem precisei devolver! Estorno veio rapido."
    },
    # Respostas medianas
    {
        "company_response": """Ola,

Recebemos sua reclamacao e estamos analisando.

Por favor, envie por e-mail para sac@farmacia.com.br:
- Numero do pedido
- Fotos do problema
- Documento com CPF

Prazo de resposta: 10 dias uteis.

Att,
Atendimento""",
        "customer_score": 6.0,
        "was_resolved": True,
        "would_buy_again": False,
        "customer_evaluation": "Burocracia demais. Depois de enviar tudo, resolveram."
    },
    {
        "company_response": """Prezado cliente,

Sua solicitacao foi registrada. Estamos verificando junto ao setor responsavel.

Protocolo: 2024XXXXX
Prazo: 5 dias uteis

Em caso de duvidas, ligue 0800-XXX-XXXX.

SAC""",
        "customer_score": 7.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Demoraram um pouco mas resolveram no final."
    },
    # Mais respostas excelentes
    {
        "company_response": """Ola!

Obrigado por nos avisar! Ja resolvemos sua situacao:

1. Cupom aplicado retroativamente
2. Diferenca de R$35,90 estornada
3. Bonus extra de R$10 adicionado

O valor total sera creditado em 24h!

Abracos,
Equipe Promocoes""",
        "customer_score": 9.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Rapidos demais! Ja caiu o estorno. Otimos!"
    },
    {
        "company_response": """Prezado(a),

Pedimos desculpas pelo inconveniente com o Farmacia Popular.

Verificamos seu cadastro e regularizamos a situacao. Seu desconto ja esta ativo!

Para as proximas compras:
- Leve RG e receita medica
- Desconto sera aplicado automaticamente
- Em caso de duvida, peca ao atendente verificar

Obrigado pela paciencia!
Programa Farmacia Popular""",
        "customer_score": 8.5,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Regularizaram meu cadastro. Agora funciona perfeitamente."
    },
    {
        "company_response": """Oi!

Sentimos muito pelo erro no site! Voce tem razao, o preco anunciado deve ser respeitado.

Resolvemos assim:
- Voce recebera o produto pelo preco anunciado
- Diferenca sera estornada automaticamente
- Cupom de 15% para proxima compra

Obrigado por nos alertar sobre o bug!
Time de TI""",
        "customer_score": 9.0,
        "was_resolved": True,
        "would_buy_again": True,
        "customer_evaluation": "Honraram o preco anunciado. Isso sim e respeito ao cliente!"
    },
]


def add_responses_batch3():
    """Adiciona mais respostas de exemplo aos concorrentes (batch 3)."""
    db = SessionLocal()
    try:
        # Pega reclamacoes sem resposta
        complaints = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.is_(None)
        ).limit(len(BATCH3_RESPONSES)).all()

        if not complaints:
            print("Todas as reclamacoes ja tem respostas!")
            return

        updated = 0
        for i, complaint in enumerate(complaints):
            if i >= len(BATCH3_RESPONSES):
                break

            response = BATCH3_RESPONSES[i]

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

        # Estatisticas finais
        total = db.query(CompetitorComplaint).count()
        with_response = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.company_response.isnot(None)
        ).count()
        high_score = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.customer_score >= 8
        ).count()
        medium_score = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.customer_score >= 6,
            CompetitorComplaint.customer_score < 8
        ).count()
        low_score = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.customer_score < 6
        ).count()
        resolved = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.was_resolved == True
        ).count()
        would_buy = db.query(CompetitorComplaint).filter(
            CompetitorComplaint.would_buy_again == True
        ).count()

        print(f"\n{'='*50}")
        print(f"ESTATISTICAS FINAIS")
        print(f"{'='*50}")
        print(f"  Total reclamacoes: {total}")
        print(f"  Com respostas: {with_response} ({100*with_response/total:.1f}%)")
        print(f"  Score alto (8+): {high_score} ({100*high_score/with_response:.1f}% das respondidas)")
        print(f"  Score medio (6-7.9): {medium_score} ({100*medium_score/with_response:.1f}% das respondidas)")
        print(f"  Score baixo (<6): {low_score} ({100*low_score/with_response:.1f}% das respondidas)")
        print(f"  Resolvidas: {resolved} ({100*resolved/with_response:.1f}% das respondidas)")
        print(f"  Compraria novamente: {would_buy} ({100*would_buy/with_response:.1f}% das respondidas)")

    finally:
        db.close()


if __name__ == "__main__":
    add_responses_batch3()
