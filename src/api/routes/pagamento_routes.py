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
from ..services import CarrinhoService, PagamentoService
import os

# Criar blueprint de rotas
pagamento_bp = Blueprint('pagamento', __name__, url_prefix='/api/pagamento')

# Obter access token da variável de ambiente
ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')

# Instâncias globais dos serviços
carrinho_service = CarrinhoService()
pagamento_service = PagamentoService(ACCESS_TOKEN) if ACCESS_TOKEN else None


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
