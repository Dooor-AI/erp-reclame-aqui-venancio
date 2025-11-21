"""
Response templates for automated customer complaint responses
"""

RESPONSE_TEMPLATES = {
    "produto": """
OlÃ¡ {user_name},

Sentimos muito pelo problema que vocÃª enfrentou com {produto}. Sua satisfaÃ§Ã£o Ã© muito importante para nÃ³s.

JÃ¡ identificamos o ocorrido e estamos tomando as medidas necessÃ¡rias para que isso nÃ£o se repita.

Como forma de desculpas, gostarÃ­amos de oferecer um cupom de {discount}% de desconto para sua prÃ³xima compra: {coupon_code}

Estamos Ã  disposiÃ§Ã£o para qualquer dÃºvida.

Atenciosamente,
Equipe VenÃ¢ncio
""",

    "atendimento": """
OlÃ¡ {user_name},

Pedimos sinceras desculpas pela experiÃªncia negativa com nosso atendimento. Isso nÃ£o reflete nossos padrÃµes de qualidade.

JÃ¡ repassamos o feedback para nossa equipe e estamos trabalhando para melhorar.

Para compensar o transtorno, gostarÃ­amos de oferecer um cupom de {discount}% de desconto: {coupon_code}

Contamos com sua compreensÃ£o.

Atenciosamente,
Equipe VenÃ¢ncio
""",

    "entrega": """
OlÃ¡ {user_name},

Lamentamos profundamente o problema com a entrega do seu pedido. Entendemos a frustraÃ§Ã£o causada.

JÃ¡ estamos apurando o ocorrido com nossa logÃ­stica para evitar que se repita.

Como compensaÃ§Ã£o, preparamos um cupom de {discount}% de desconto: {coupon_code}

Agradecemos sua paciÃªncia.

Atenciosamente,
Equipe VenÃ¢ncio
""",

    "preco": """
OlÃ¡ {user_name},

Pedimos desculpas pela inconsistÃªncia no preÃ§o/cobranÃ§a. JÃ¡ estamos verificando internamente.

Tomaremos as providÃªncias necessÃ¡rias para corrigir a situaÃ§Ã£o.

Como gesto de boa vontade, segue cupom de {discount}% de desconto: {coupon_code}

Estamos Ã  disposiÃ§Ã£o.

Atenciosamente,
Equipe VenÃ¢ncio
""",

    "outros": """
OlÃ¡ {user_name},

Agradecemos por compartilhar sua experiÃªncia conosco. Sentimos muito pelo ocorrido.

Levamos seu feedback muito a sÃ©rio e jÃ¡ estamos trabalhando para melhorar.

Como forma de desculpas, preparamos um cupom de {discount}% de desconto: {coupon_code}

Conte conosco.

Atenciosamente,
Equipe VenÃ¢ncio
"""
}
