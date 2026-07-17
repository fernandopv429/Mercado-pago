"""
Módulo: services/instancias.py
==============================

Instâncias compartilhadas dos serviços (singleton simples).

Garante que toda a aplicação use a MESMA instância do CarrinhoService,
evitando que rotas diferentes criem carrinhos isolados. Com Redis, isso
não é estritamente necessário (o estado fica no Redis), mas manter uma
instância única é mais correto e também faz o modo memória funcionar.
"""

import os
from .carrinho_service import CarrinhoService
from .pagamento_service import PagamentoService

# Instância única do serviço de carrinho (lê REDIS_URL do ambiente)
carrinho_service = CarrinhoService()

# Serviço de pagamento (só cria se houver token configurado)
ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
pagamento_service = PagamentoService(ACCESS_TOKEN) if ACCESS_TOKEN else None
