"""
Módulo: services
================

Contém serviços de negócio:
    - CarrinhoService: Gerencia carrinhos por sessão
    - PagamentoService: Integra com Mercado Pago
"""

from .carrinho_service import CarrinhoService
from .pagamento_service import PagamentoService

__all__ = ['CarrinhoService', 'PagamentoService']
