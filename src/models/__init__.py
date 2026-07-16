"""
Módulo: models
==============

Contém os modelos de dados do sistema:
    - Produto: Representa um item individual
    - CarrinhoCompras: Gerencia múltiplos produtos
"""

from .produto import Produto
from .carrinho import CarrinhoCompras

__all__ = ['Produto', 'CarrinhoCompras']
