"""
Módulo: api/routes/pagamento_routes.py
======================================

Descrição:
    Define os endpoints da API para integração com Mercado Pago.
    
Endpoints:
    POST /api/pagamento/<sessao_id>/gerar-link - Gera link de pagamento
    
Exemplo:
    POST /api/pagamento/sessao1/gerar-link
    {
        "email": "cliente@email.com"
    }
"""

from flask import Blueprint, request, jsonify
from ...services.instancias import carrinho_service, pagamento_service, ACCESS_TOKEN

# Criar blueprint de rotas
pagamento_bp = Blueprint('pagamento', __name__, url_prefix='/api/pagamento')


# ========== VALIDAÇÃO DE CONFIGURAÇÃO ==========

def verificar_configuracao():
    """
    Verifica se a aplicação está corretamente configurada.
    
    Returns:
        tuple: (configurado: bool, mensagem: str)
    """
    if not ACCESS_TOKEN:
        return False, "Variável MERCADOPAGO_ACCESS_TOKEN não configurada"
    
    if not pagamento_service:
        return False, "Serviço de pagamento não inicializado"
    
    return True, ""


# ========== OPERAÇÕES DE PAGAMENTO ==========

@pagamento_bp.route('/<sessao_id>/gerar-link', methods=['POST'])
def gerar_link_pagamento(sessao_id: str):
    """
    Endpoint: POST /api/pagamento/<sessao_id>/gerar-link
    
    Gera um link de pagamento no Mercado Pago para o carrinho.
    
    Body JSON (opcional):
        {
            "email": "cliente@email.com",           # Email do comprador
            "titulo": "Minha Compra",               # (opcional) Título
            "notificacao_url": "https://...",       # (opcional) Webhook
            "urls_retorno": {                       # (opcional)
                "success": "https://...",
                "failure": "https://...",
                "pending": "https://..."
            }
        }
    
    Returns:
        JSON com link de pagamento ou erro
    
    Example Response (200 - Sucesso):
        {
            "sucesso": true,
            "id": "987654321",
            "link_pagamento": "https://www.mercadopago.com.br/checkout/v1/...",
            "total": 2500.0
        }
    
    Example Response (400 - Erro):
        {
            "sucesso": false,
            "erro": "Carrinho vazio! Adicione produtos antes."
        }
    """
    
    # ========== VALIDAÇÃO DE CONFIGURAÇÃO ==========
    
    configurado, mensagem = verificar_configuracao()
    if not configurado:
        return jsonify({
            "sucesso": False,
            "erro": f"Configuração incompleta: {mensagem}"
        }), 500
    
    try:
        # ========== VALIDAÇÃO DO CARRINHO ==========
        
        carrinho = carrinho_service.obter_carrinho(sessao_id)
        
        if carrinho.esta_vazio():
            return jsonify({
                "sucesso": False,
                "erro": "Carrinho vazio! Adicione produtos antes de gerar link"
            }), 400
        
        # ========== PROCESSAR DADOS ==========
        
        dados = request.get_json() or {}
        
        email = dados.get('email', '').strip()
        titulo = dados.get('titulo', 'Sua Compra').strip()
        notificacao_url = dados.get('notificacao_url')
        urls_retorno = dados.get('urls_retorno')
        
        # ========== VALIDAR EMAIL ==========
        
        if email and '@' not in email:
            return jsonify({
                "sucesso": False,
                "erro": "Email inválido"
            }), 400
        
        # ========== GERAR LINK ==========
        
        resultado = pagamento_service.gerar_link_pagamento(
            carrinho=carrinho,
            email_comprador=email if email else None,
            titulo_preferencia=titulo,
            url_notificacao=notificacao_url,
            urls_retorno=urls_retorno
        )
        
        # ========== PROCESSAR RESULTADO ==========
        
        if resultado['sucesso']:
            # Limpar carrinho após gerar link com sucesso
            carrinho_service.limpar_carrinho(sessao_id)
            
            return jsonify(resultado), 200
        else:
            # Erro na geração do link
            return jsonify(resultado), 400
    
    except ValueError as erro:
        """Erro de validação do carrinho ou dados"""
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400
    
    except Exception as erro:
        """Erro geral"""
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao gerar link de pagamento: {str(erro)}"
        }), 500


@pagamento_bp.route('/health', methods=['GET'])
def health_check_pagamento():
    """
    Endpoint: GET /api/pagamento/health
    
    Verifica se o serviço de pagamento está configurado.
    
    Returns:
        JSON com status
    
    Example Response (200):
        {
            "sucesso": true,
            "status": "OK",
            "mercadopago": true,
            "token_configurado": true
        }
    
    Example Response (500):
        {
            "sucesso": false,
            "status": "ERRO",
            "mercadopago": false,
            "token_configurado": false,
            "mensagem": "..."
        }
    """
    configurado, mensagem = verificar_configuracao()
    
    return jsonify({
        "sucesso": configurado,
        "status": "OK" if configurado else "ERRO",
        "mercadopago": bool(pagamento_service),
        "token_configurado": bool(ACCESS_TOKEN),
        "mensagem": mensagem if not configurado else "Serviço de pagamento operacional"
    }), 200 if configurado else 500


# ========== WEBHOOK E CONSULTA DE STATUS ==========

@pagamento_bp.route('/webhook', methods=['POST'])
def webhook_mercadopago():
    """
    Endpoint: POST /api/pagamento/webhook

    Recebe notificacoes automaticas do Mercado Pago quando o status
    de um pagamento muda. O Mercado Pago envia o ID do pagamento; este
    endpoint consulta a API para confirmar o status real e, se aprovado,
    executa as acoes necessarias.

    IMPORTANTE: sempre responder 200 rapidamente, senao o Mercado Pago
    reenvia a notificacao varias vezes.
    """
    if pagamento_service is None:
        # Ainda assim retornamos 200 para o MP nao ficar reenviando
        return jsonify({"recebido": True, "aviso": "servico nao configurado"}), 200

    try:
        # O MP manda o tipo e o id de formas diferentes dependendo do evento.
        # Tentamos extrair de query string e do corpo JSON.
        tipo = request.args.get('type') or request.args.get('topic')
        pagamento_id = request.args.get('data.id') or request.args.get('id')

        if not pagamento_id:
            corpo = request.get_json(silent=True) or {}
            tipo = tipo or corpo.get('type') or corpo.get('action')
            dados = corpo.get('data') or {}
            pagamento_id = dados.get('id') or corpo.get('id')

        # So nos interessa evento de pagamento
        if tipo and 'payment' not in str(tipo):
            return jsonify({"recebido": True, "ignorado": tipo}), 200

        if not pagamento_id:
            return jsonify({"recebido": True, "aviso": "sem id"}), 200

        # Confirma o status real na API do Mercado Pago
        info = pagamento_service.consultar_pagamento(str(pagamento_id))

        if info.get('sucesso') and info.get('aprovado'):
            # >>> PONTO DE INTEGRACAO <<<
            # Aqui o pagamento esta CONFIRMADO como aprovado.
            # Ex.: marcar pedido como pago, limpar carrinho, liberar produto.
            print(f"[WEBHOOK] Pagamento APROVADO: id={info['pagamento_id']} "
                  f"valor={info['valor']} email={info['email']}")
        else:
            print(f"[WEBHOOK] Pagamento id={pagamento_id} "
                  f"status={info.get('status')}")

        return jsonify({"recebido": True}), 200

    except Exception as erro:
        # Nunca deixar estourar erro pro MP; logamos e devolvemos 200
        print(f"[WEBHOOK] Erro ao processar: {erro}")
        return jsonify({"recebido": True}), 200


@pagamento_bp.route('/status/<pagamento_id>', methods=['GET'])
def consultar_status_pagamento(pagamento_id: str):
    """
    Endpoint: GET /api/pagamento/status/<pagamento_id>

    Consulta o status atual de um pagamento pelo ID. Util para verificar
    manualmente ou quando o cliente retorna para a tela de sucesso.

    Example Response (200):
        {
            "sucesso": true,
            "pagamento_id": "123456789",
            "status": "approved",
            "aprovado": true,
            "valor": 5500.0,
            "email": "cliente@email.com"
        }
    """
    if pagamento_service is None:
        return jsonify({
            "sucesso": False,
            "erro": "Servico de pagamento nao configurado"
        }), 500

    info = pagamento_service.consultar_pagamento(str(pagamento_id))
    return jsonify(info), 200 if info.get('sucesso') else 404
