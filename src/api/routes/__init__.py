"""
Módulo: api/routes
==================

Contém todos os blueprints de rotas da API:
    - carrinho_routes: Endpoints de carrinho
    - pagamento_routes: Endpoints de pagamento
    - produto_routes: Endpoints de produtos
"""

from .carrinho_routes import carrinho_bp
from .pagamento_routes import pagamento_bp
from .produto_routes import produto_bp

__all__ = ['carrinho_bp', 'pagamento_bp', 'produto_bp']
