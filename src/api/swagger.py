"""
Módulo: src/api/swagger.py
==========================

Documentação interativa da API (Swagger UI / OpenAPI 3).

Expõe duas rotas:
    GET /docs            -> Interface visual do Swagger UI
    GET /openapi.json    -> Especificação OpenAPI consumida pelo Swagger UI

Não requer bibliotecas extras: o Swagger UI é carregado via CDN e a
especificação é um dicionário Python servido como JSON.
"""

from flask import Blueprint, jsonify, Response

swagger_bp = Blueprint('swagger', __name__)


# ========== ESPECIFICAÇÃO OPENAPI ==========

def _openapi_spec() -> dict:
    """Monta a especificação OpenAPI 3 da API."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "API de Carrinho de Compras + Mercado Pago",
            "description": (
                "API REST para carrinho de compras com integração de pagamentos "
                "via Mercado Pago (Checkout Pro). Inclui catálogo de produtos, "
                "carrinho persistente com Redis e detecção de pagamento por webhook."
            ),
            "version": "1.0.0",
            "contact": {"name": "Nexus Dev Hub"},
        },
        "servers": [
            {"url": "/", "description": "Servidor atual"},
        ],
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Chave de acesso da API. Envie no header X-API-Key.",
                }
            }
        },
        "security": [{"ApiKeyAuth": []}],
        "tags": [
            {"name": "Status", "description": "Saúde da API"},
            {"name": "Produtos", "description": "Catálogo de produtos"},
            {"name": "Carrinho", "description": "Gerenciamento do carrinho"},
            {"name": "Pagamento", "description": "Pagamentos e detecção via webhook"},
        ],
        "paths": {
            # ---------- STATUS ----------
            "/api/health": {
                "get": {
                    "tags": ["Status"],
                    "summary": "Status geral da API",
                    "responses": {
                        "200": {
                            "description": "API operacional",
                            "content": {"application/json": {"example": {
                                "status": "OK", "versao": "1.0.0",
                                "ambiente": "production"}}},
                        }
                    },
                }
            },
            "/api/pagamento/health": {
                "get": {
                    "tags": ["Status"],
                    "summary": "Status do serviço de pagamento",
                    "responses": {
                        "200": {
                            "description": "Serviço de pagamento operacional",
                            "content": {"application/json": {"example": {
                                "status": "OK", "sucesso": True,
                                "mercadopago": True, "token_configurado": True}}},
                        }
                    },
                }
            },
            # ---------- PRODUTOS ----------
            "/api/produtos": {
                "get": {
                    "tags": ["Produtos"],
                    "summary": "Lista todos os produtos",
                    "responses": {"200": {"description": "Lista de produtos"}},
                }
            },
            "/api/produtos/{id}": {
                "get": {
                    "tags": ["Produtos"],
                    "summary": "Detalhe de um produto",
                    "parameters": [{
                        "name": "id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "001"}],
                    "responses": {
                        "200": {"description": "Produto encontrado"},
                        "404": {"description": "Produto não encontrado"}},
                }
            },
            "/api/produtos/categoria/{categoria}": {
                "get": {
                    "tags": ["Produtos"],
                    "summary": "Produtos por categoria",
                    "parameters": [{
                        "name": "categoria", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "Eletrônicos"}],
                    "responses": {"200": {"description": "Lista filtrada"}},
                }
            },
            "/api/produtos/em-estoque": {
                "get": {
                    "tags": ["Produtos"],
                    "summary": "Produtos com estoque disponível",
                    "responses": {"200": {"description": "Lista de produtos em estoque"}},
                }
            },
            # ---------- CARRINHO ----------
            "/api/carrinho/{sessao_id}": {
                "get": {
                    "tags": ["Carrinho"],
                    "summary": "Ver carrinho da sessão",
                    "parameters": [{
                        "name": "sessao_id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "sessao1"}],
                    "responses": {"200": {"description": "Conteúdo do carrinho"}},
                }
            },
            "/api/carrinho/{sessao_id}/adicionar": {
                "post": {
                    "tags": ["Carrinho"],
                    "summary": "Adicionar produto ao carrinho",
                    "parameters": [{
                        "name": "sessao_id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "sessao1"}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["id", "titulo", "preco"],
                                "properties": {
                                    "id": {"type": "string", "example": "001"},
                                    "titulo": {"type": "string", "example": "Notebook"},
                                    "preco": {"type": "number", "example": 2500.00},
                                    "quantidade": {"type": "integer", "example": 1},
                                    "descricao": {"type": "string", "example": ""},
                                },
                            }
                        }},
                    },
                    "responses": {
                        "200": {"description": "Produto adicionado"},
                        "400": {"description": "Dados inválidos"}},
                }
            },
            "/api/carrinho/{sessao_id}/atualizar-quantidade": {
                "put": {
                    "tags": ["Carrinho"],
                    "summary": "Atualizar quantidade de um produto",
                    "parameters": [{
                        "name": "sessao_id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "sessao1"}],
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["produto_id", "quantidade"],
                                "properties": {
                                    "produto_id": {"type": "string", "example": "001"},
                                    "quantidade": {"type": "integer", "example": 3},
                                },
                            }
                        }},
                    },
                    "responses": {
                        "200": {"description": "Quantidade atualizada"},
                        "400": {"description": "Dados inválidos"}},
                }
            },
            "/api/carrinho/{sessao_id}/remover/{produto_id}": {
                "delete": {
                    "tags": ["Carrinho"],
                    "summary": "Remover um produto do carrinho",
                    "parameters": [
                        {"name": "sessao_id", "in": "path", "required": True,
                         "schema": {"type": "string"}, "example": "sessao1"},
                        {"name": "produto_id", "in": "path", "required": True,
                         "schema": {"type": "string"}, "example": "001"}],
                    "responses": {
                        "200": {"description": "Produto removido"},
                        "404": {"description": "Produto/sessão não encontrado"}},
                }
            },
            "/api/carrinho/{sessao_id}/limpar": {
                "delete": {
                    "tags": ["Carrinho"],
                    "summary": "Limpar o carrinho inteiro",
                    "parameters": [{
                        "name": "sessao_id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "sessao1"}],
                    "responses": {"200": {"description": "Carrinho limpo"}},
                }
            },
            # ---------- PAGAMENTO ----------
            "/api/pagamento/{sessao_id}/gerar-link": {
                "post": {
                    "tags": ["Pagamento"],
                    "summary": "Gerar link de pagamento (Checkout Pro)",
                    "parameters": [{
                        "name": "sessao_id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "sessao1"}],
                    "requestBody": {
                        "required": False,
                        "content": {"application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "email": {"type": "string",
                                              "example": "cliente@email.com"},
                                    "titulo": {"type": "string",
                                               "example": "Sua Compra"},
                                    "notificacao_url": {"type": "string"},
                                },
                            }
                        }},
                    },
                    "responses": {
                        "200": {"description": "Link gerado",
                                "content": {"application/json": {"example": {
                                    "sucesso": True,
                                    "link_pagamento": "https://www.mercadopago.com.br/checkout/...",
                                    "total": 5500.0}}}},
                        "400": {"description": "Carrinho vazio ou dados inválidos"},
                        "500": {"description": "Token não configurado / erro MP"}},
                }
            },
            "/api/pagamento/webhook": {
                "post": {
                    "tags": ["Pagamento"],
                    "summary": "Webhook do Mercado Pago (notificação automática)",
                    "description": (
                        "Recebe notificações do Mercado Pago quando o status de um "
                        "pagamento muda. Confirma o status real na API e responde 200."
                    ),
                    "parameters": [
                        {"name": "type", "in": "query", "required": False,
                         "schema": {"type": "string"}, "example": "payment"},
                        {"name": "data.id", "in": "query", "required": False,
                         "schema": {"type": "string"}, "example": "123456789"}],
                    "responses": {"200": {"description": "Notificação recebida"}},
                }
            },
            "/api/pagamento/status/{pagamento_id}": {
                "get": {
                    "tags": ["Pagamento"],
                    "summary": "Consultar status de um pagamento",
                    "parameters": [{
                        "name": "pagamento_id", "in": "path", "required": True,
                        "schema": {"type": "string"}, "example": "123456789"}],
                    "responses": {
                        "200": {"description": "Status do pagamento",
                                "content": {"application/json": {"example": {
                                    "sucesso": True, "pagamento_id": "123456789",
                                    "status": "approved", "aprovado": True,
                                    "valor": 5500.0,
                                    "email": "cliente@email.com"}}}},
                        "404": {"description": "Pagamento não encontrado"}},
                }
            },
            "/api/pagamento/webhook-destino": {
                "get": {
                    "tags": ["Pagamento"],
                    "summary": "Ver a URL de destino cadastrada",
                    "responses": {"200": {"description": "URL de destino atual"}},
                },
                "post": {
                    "tags": ["Pagamento"],
                    "summary": "Cadastrar/trocar a URL de destino dos eventos",
                    "description": (
                        "Define a URL para onde os eventos de pagamento aprovado "
                        "serão reenviados (painel, n8n, Discord, etc)."
                    ),
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["url"],
                                "properties": {
                                    "url": {"type": "string",
                                            "example": "https://meu-painel.com/webhook"},
                                },
                            }
                        }},
                    },
                    "responses": {
                        "200": {"description": "URL cadastrada"},
                        "400": {"description": "URL inválida ou ausente"}},
                },
                "delete": {
                    "tags": ["Pagamento"],
                    "summary": "Remover a URL de destino",
                    "responses": {"200": {"description": "URL removida"}},
                },
            },
            "/api/pagamento/webhook-destino/testar": {
                "post": {
                    "tags": ["Pagamento"],
                    "summary": "Enviar um evento de teste para a URL de destino",
                    "responses": {
                        "200": {"description": "Evento de teste enviado"},
                        "400": {"description": "Falha ao enviar ou URL não cadastrada"}},
                }
            },
        },
    }


# ========== ROTAS ==========

@swagger_bp.route('/openapi.json', methods=['GET'])
def openapi_json():
    """Retorna a especificação OpenAPI em JSON."""
    return jsonify(_openapi_spec())


# HTML do Swagger UI (carregado via CDN)
_SWAGGER_HTML = """<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>API de Carrinho + Mercado Pago — Documentação</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet"
          href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body { margin: 0; background: #fafafa; }
        .topbar { display: none; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script>
        window.onload = function () {
            window.ui = SwaggerUIBundle({
                url: '/openapi.json',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIBundle.SwaggerUIStandalonePreset
                ],
                layout: "BaseLayout"
            });
        };
    </script>
</body>
</html>"""


@swagger_bp.route('/docs', methods=['GET'])
def swagger_docs():
    """Serve a interface visual do Swagger UI."""
    return Response(_SWAGGER_HTML, mimetype='text/html')
