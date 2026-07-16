"""
Módulo: api/routes/produto_routes.py
====================================

Descrição:
    Define os endpoints da API para consultar produtos.
    
Endpoints:
    GET /api/produtos - Lista todos os produtos
    GET /api/produtos/<produto_id> - Detalhe de um produto
    
Exemplo:
    GET /api/produtos
    GET /api/produtos/001
"""

from flask import Blueprint, jsonify

# Criar blueprint de rotas
produto_bp = Blueprint('produto', __name__, url_prefix='/api/produtos')

# ========== CATÁLOGO DE PRODUTOS ==========
# Em produção, isso viria de um banco de dados
# Para este exemplo, usamos um dicionário em memória

PRODUTOS_DISPONIVEIS = [
    {
        'id': '001',
        'titulo': 'Notebook Dell XPS 13',
        'preco': 3500.00,
        'descricao': 'Notebook Intel Core i7, 16GB RAM, 512GB SSD',
        'categoria': 'Eletrônicos',
        'estoque': 10
    },
    {
        'id': '002',
        'titulo': 'Mouse Logitech MX Master',
        'preco': 250.00,
        'descricao': 'Mouse sem fio profissional com várias botões customizáveis',
        'categoria': 'Periféricos',
        'estoque': 50
    },
    {
        'id': '003',
        'titulo': 'Teclado Mecânico RGB',
        'preco': 450.00,
        'descricao': 'Teclado mecânico com backlighting RGB e switches rápidos',
        'categoria': 'Periféricos',
        'estoque': 30
    },
    {
        'id': '004',
        'titulo': 'Monitor LG 27 polegadas 4K',
        'preco': 1200.00,
        'descricao': 'Monitor 4K IPS 60Hz com cores precisas',
        'categoria': 'Monitores',
        'estoque': 5
    },
    {
        'id': '005',
        'titulo': 'Webcam HD 1080p',
        'preco': 180.00,
        'descricao': 'Webcam com microfone integrado, perfeita para reuniões',
        'categoria': 'Câmeras',
        'estoque': 25
    }
]


# ========== ENDPOINTS ==========

@produto_bp.route('', methods=['GET'])
@produto_bp.route('/', methods=['GET'])
def listar_produtos():
    """
    Endpoint: GET /api/produtos
    
    Lista todos os produtos disponíveis no catálogo.
    
    Returns:
        JSON com lista de produtos
    
    Example Response (200):
        {
            "sucesso": true,
            "total": 5,
            "produtos": [
                {
                    "id": "001",
                    "titulo": "Notebook Dell XPS 13",
                    "preco": 3500.00,
                    "descricao": "...",
                    "categoria": "Eletrônicos",
                    "estoque": 10
                },
                ...
            ]
        }
    """
    return jsonify({
        "sucesso": True,
        "total": len(PRODUTOS_DISPONIVEIS),
        "produtos": PRODUTOS_DISPONIVEIS
    }), 200


@produto_bp.route('/<produto_id>', methods=['GET'])
def obter_produto(produto_id: str):
    """
    Endpoint: GET /api/produtos/<produto_id>
    
    Obtém os detalhes de um produto específico.
    
    Args:
        produto_id (str): ID do produto
    
    Returns:
        JSON com dados do produto
    
    Example Response (200):
        {
            "sucesso": true,
            "produto": {
                "id": "001",
                "titulo": "Notebook Dell XPS 13",
                "preco": 3500.00,
                "descricao": "...",
                "categoria": "Eletrônicos",
                "estoque": 10
            }
        }
    
    Example Response (404):
        {
            "sucesso": false,
            "erro": "Produto não encontrado"
        }
    """
    
    # Procurar produto
    produto = None
    for p in PRODUTOS_DISPONIVEIS:
        if p['id'] == produto_id:
            produto = p
            break
    
    # Retornar resultado
    if produto:
        return jsonify({
            "sucesso": True,
            "produto": produto
        }), 200
    else:
        return jsonify({
            "sucesso": False,
            "erro": f"Produto com ID '{produto_id}' não encontrado"
        }), 404


@produto_bp.route('/categoria/<categoria>', methods=['GET'])
def listar_por_categoria(categoria: str):
    """
    Endpoint: GET /api/produtos/categoria/<categoria>
    
    Lista produtos de uma categoria específica.
    
    Args:
        categoria (str): Nome da categoria
    
    Returns:
        JSON com produtos da categoria
    
    Example Response (200):
        {
            "sucesso": true,
            "categoria": "Periféricos",
            "total": 2,
            "produtos": [...]
        }
    """
    
    # Filtrar por categoria
    produtos_filtrados = [
        p for p in PRODUTOS_DISPONIVEIS 
        if p['categoria'].lower() == categoria.lower()
    ]
    
    return jsonify({
        "sucesso": True,
        "categoria": categoria,
        "total": len(produtos_filtrados),
        "produtos": produtos_filtrados
    }), 200


@produto_bp.route('/em-estoque', methods=['GET'])
def listar_em_estoque():
    """
    Endpoint: GET /api/produtos/em-estoque
    
    Lista apenas produtos que têm estoque disponível.
    
    Returns:
        JSON com produtos em estoque
    
    Example Response (200):
        {
            "sucesso": true,
            "total": 5,
            "produtos": [...]
        }
    """
    
    # Filtrar produtos em estoque
    em_estoque = [
        p for p in PRODUTOS_DISPONIVEIS 
        if p['estoque'] > 0
    ]
    
    return jsonify({
        "sucesso": True,
        "total": len(em_estoque),
        "produtos": em_estoque
    }), 200
