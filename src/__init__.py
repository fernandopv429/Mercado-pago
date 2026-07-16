"""
Pacote: src
===========

Estrutura modular para sistema de carrinho com Mercado Pago.

Submódulos:
    - models: Modelos de dados (Produto, CarrinhoCompras)
    - services: Serviços de negócio (Carrinho, Pagamento)
    - api: Aplicação Flask e rotas
    - config: Configurações
    
Exemplo de uso:
    from src.api import criar_app
    from src.models import Produto, CarrinhoCompras
    from src.services import PagamentoService
    
    app = criar_app()
    app.run()
"""

from .api import criar_app, criar_app_debug
from .models import Produto, CarrinhoCompras
from .services import CarrinhoService, PagamentoService
from .config import obter_config

__version__ = "1.0.0"
__all__ = [
    'criar_app',
    'criar_app_debug',
    'Produto',
    'CarrinhoCompras',
    'CarrinhoService',
    'PagamentoService',
    'obter_config'
]
