"""
Módulo: api/routes/carrinho_routes.py
=====================================

Descrição:
    Define os endpoints da API para gerenciar carrinhos.
    
Endpoints:
    GET /api/carrinho/<sessao_id> - Obter carrinho
    POST /api/carrinho/<sessao_id>/adicionar - Adicionar produto
    DELETE /api/carrinho/<sessao_id>/remover/<produto_id> - Remover produto
    PUT /api/carrinho/<sessao_id>/atualizar-quantidade - Atualizar qtd
    DELETE /api/carrinho/<sessao_id>/limpar - Limpar carrinho
    
Exemplo:
    POST /api/carrinho/sessao1/adicionar
    {
        "id": "001",
        "titulo": "Notebook",
        "preco": 2500.00,
        "quantidade": 1
    }
"""

from flask import Blueprint, request, jsonify
from ...models import Produto
from ...services.instancias import carrinho_service

# Criar blueprint de rotas
carrinho_bp = Blueprint('carrinho', __name__, url_prefix='/api/carrinho')


# ========== OPERAÇÕES DE CONSULTA ==========

@carrinho_bp.route('/<sessao_id>', methods=['GET'])
def obter_carrinho(sessao_id: str):
    """
    Endpoint: GET /api/carrinho/<sessao_id>
    
    Obtém o carrinho de uma sessão com todos os produtos.
    
    Args:
        sessao_id (str): ID da sessão
    
    Returns:
        JSON com carrinho e total
    
    Example Response (200):
        {
            "sucesso": true,
            "produtos": [...],
            "total": 2500.0,
            "quantidade_itens": 1
        }
    """
    try:
        resumo = carrinho_service.obter_resumo_carrinho(sessao_id)
        
        return jsonify({
            "sucesso": True,
            "sessao_id": sessao_id,
            "produtos": resumo['produtos'],
            "total": resumo['total'],
            "quantidade_itens": resumo['quantidade_itens'],
            "vazio": resumo['vazio']
        }), 200
    
    except Exception as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 400


# ========== OPERAÇÕES DE ADIÇÃO ==========

@carrinho_bp.route('/<sessao_id>/adicionar', methods=['POST'])
def adicionar_produto(sessao_id: str):
    """
    Endpoint: POST /api/carrinho/<sessao_id>/adicionar
    
    Adiciona um produto ao carrinho.
    
    Body JSON obrigatório:
        {
            "id": "001",           # ID do produto
            "titulo": "Notebook",  # Nome do produto
            "preco": 2500.00,      # Preço unitário
            "descricao": "...",    # (opcional) Descrição
            "quantidade": 1        # (opcional) Quantidade
        }
    
    Returns:
        JSON com resultado e carrinho atualizado
    
    Example Response (200):
        {
            "sucesso": true,
            "mensagem": "Produto 'Notebook' adicionado",
            "total": 2500.0,
            "quantidade_itens": 1
        }
    """
    try:
        dados = request.get_json()
        
        # ========== VALIDAÇÕES ==========
        
        campos_obrigatorios = ['id', 'titulo', 'preco']
        campos_faltantes = [c for c in campos_obrigatorios if c not in dados]
        
        if campos_faltantes:
            return jsonify({
                "sucesso": False,
                "erro": f"Campos obrigatórios faltando: {', '.join(campos_faltantes)}"
            }), 400
        
        # ========== CRIAR PRODUTO ==========
        
        try:
            produto = Produto(
                id=str(dados['id']),
                titulo=str(dados['titulo']),
                preco=float(dados['preco']),
                descricao=str(dados.get('descricao', '')),
                quantidade=int(dados.get('quantidade', 1))
            )
        except ValueError as e:
            return jsonify({
                "sucesso": False,
                "erro": f"Dados inválidos: {str(e)}"
            }), 400
        
        # ========== ADICIONAR AO CARRINHO ==========
        
        carrinho_service.adicionar_produto(sessao_id, produto)
        
        resumo = carrinho_service.obter_resumo_carrinho(sessao_id)
        
        return jsonify({
            "sucesso": True,
            "mensagem": f"Produto '{produto.titulo}' adicionado ao carrinho",
            "produto": produto.para_dicionario(),
            "total": resumo['total'],
            "quantidade_itens": resumo['quantidade_itens']
        }), 200
    
    except Exception as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 500


# ========== OPERAÇÕES DE REMOÇÃO ==========

@carrinho_bp.route('/<sessao_id>/remover/<produto_id>', methods=['DELETE'])
def remover_produto(sessao_id: str, produto_id: str):
    """
    Endpoint: DELETE /api/carrinho/<sessao_id>/remover/<produto_id>
    
    Remove um produto específico do carrinho.
    
    Args:
        sessao_id (str): ID da sessão
        produto_id (str): ID do produto a remover
    
    Returns:
        JSON com resultado
    
    Example Response (200):
        {
            "sucesso": true,
            "mensagem": "Produto removido",
            "total": 0.0
        }
    
    Example Response (404):
        {
            "sucesso": false,
            "erro": "Produto não encontrado"
        }
    """
    foi_removido = carrinho_service.remover_produto(sessao_id, produto_id)
    
    if not foi_removido:
        return jsonify({
            "sucesso": False,
            "erro": "Produto não encontrado no carrinho"
        }), 404
    
    resumo = carrinho_service.obter_resumo_carrinho(sessao_id)
    
    return jsonify({
        "sucesso": True,
        "mensagem": "Produto removido do carrinho",
        "total": resumo['total'],
        "quantidade_itens": resumo['quantidade_itens']
    }), 200


@carrinho_bp.route('/<sessao_id>/limpar', methods=['DELETE'])
def limpar_carrinho(sessao_id: str):
    """
    Endpoint: DELETE /api/carrinho/<sessao_id>/limpar
    
    Remove todos os produtos do carrinho.
    
    Args:
        sessao_id (str): ID da sessão
    
    Returns:
        JSON com resultado
    
    Example Response (200):
        {
            "sucesso": true,
            "mensagem": "Carrinho limpo"
        }
    """
    carrinho_service.limpar_carrinho(sessao_id)
    
    return jsonify({
        "sucesso": True,
        "mensagem": "Carrinho limpo com sucesso"
    }), 200


# ========== OPERAÇÕES DE ATUALIZAÇÃO ==========

@carrinho_bp.route('/<sessao_id>/atualizar-quantidade', methods=['PUT'])
def atualizar_quantidade(sessao_id: str):
    """
    Endpoint: PUT /api/carrinho/<sessao_id>/atualizar-quantidade
    
    Atualiza a quantidade de um produto no carrinho.
    
    Body JSON obrigatório:
        {
            "produto_id": "001",
            "quantidade": 5
        }
    
    Returns:
        JSON com resultado
    
    Example Response (200):
        {
            "sucesso": true,
            "mensagem": "Quantidade atualizada",
            "total": 2500.0
        }
    
    Example Response (400):
        {
            "sucesso": false,
            "erro": "Quantidade deve ser maior que zero"
        }
    """
    try:
        dados = request.get_json()
        
        # ========== VALIDAÇÕES ==========
        
        if 'produto_id' not in dados or 'quantidade' not in dados:
            return jsonify({
                "sucesso": False,
                "erro": "Campos obrigatórios: 'produto_id' e 'quantidade'"
            }), 400
        
        try:
            quantidade = int(dados['quantidade'])
            if quantidade < 0:
                raise ValueError("Quantidade não pode ser negativa")
        except ValueError as e:
            return jsonify({
                "sucesso": False,
                "erro": f"Quantidade inválida: {str(e)}"
            }), 400
        
        # ========== ATUALIZAR ==========
        
        foi_atualizado = carrinho_service.atualizar_quantidade(
            sessao_id,
            str(dados['produto_id']),
            quantidade
        )
        
        if not foi_atualizado:
            return jsonify({
                "sucesso": False,
                "erro": "Produto não encontrado"
            }), 404
        
        resumo = carrinho_service.obter_resumo_carrinho(sessao_id)
        
        return jsonify({
            "sucesso": True,
            "mensagem": "Quantidade atualizada",
            "total": resumo['total'],
            "quantidade_itens": resumo['quantidade_itens']
        }), 200
    
    except Exception as erro:
        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 500
