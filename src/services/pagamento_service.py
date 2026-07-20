"""
Módulo: services/pagamento_service.py
=====================================

Descrição:
    Serviço responsável por integração com Mercado Pago.
    
Responsabilidades:
    - Gerar links de pagamento
    - Criar preferências de pagamento
    - Comunicar com API do Mercado Pago
    - Tratar erros e respostas
    
Exemplo de uso:
    >>> servico = PagamentoService("SEU_ACCESS_TOKEN")
    >>> resultado = servico.gerar_link_pagamento(carrinho, "cliente@email.com")
    >>> if resultado['sucesso']:
    ...     print(resultado['link_pagamento'])
"""

from typing import Dict, Optional

try:
    import mercadopago
    MERCADOPAGO_DISPONIVEL = True
except ImportError:
    mercadopago = None
    MERCADOPAGO_DISPONIVEL = False

from ..models import CarrinhoCompras


class PagamentoService:
    """
    Serviço de integração com Mercado Pago.
    
    Responsável por comunicação com a API do Mercado Pago
    para gerar links de pagamento e preferências.
    
    Attributes:
        sdk (mercadopago.SDK): Cliente SDK do Mercado Pago
        access_token (str): Token de acesso da conta Mercado Pago
    
    Example:
        >>> servico = PagamentoService("APP_USR-seu-token")
        >>> resultado = servico.gerar_link_pagamento(carrinho)
        >>> resultado['sucesso']
        True
    """
    
    def __init__(self, access_token: str):
        """
        Inicializa o serviço de pagamento.
        
        Args:
            access_token (str): Token de acesso do Mercado Pago
        
        Raises:
            ValueError: Se access_token estiver vazio
        
        Example:
            >>> servico = PagamentoService("APP_USR-seu-token")
        """
        if not access_token or not isinstance(access_token, str):
            raise ValueError("Access token deve ser uma string não vazia")
        
        if not MERCADOPAGO_DISPONIVEL:
            raise ImportError(
                "O pacote 'mercadopago' não está instalado. "
                "Instale com: pip install mercadopago"
            )
        
        self.access_token = access_token
        self.sdk = mercadopago.SDK(access_token)
    
    # ========== OPERAÇÕES PRINCIPAIS ==========
    
    def gerar_link_pagamento(
        self,
        carrinho: CarrinhoCompras,
        email_comprador: Optional[str] = None,
        titulo_preferencia: str = "Sua Compra",
        url_notificacao: Optional[str] = None,
        urls_retorno: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Gera um link de pagamento a partir de um carrinho.
        
        Comunica com a API Mercado Pago para criar uma preferência
        de pagamento e retorna o link para o cliente pagar.
        
        Args:
            carrinho (CarrinhoCompras): Carrinho com produtos
            email_comprador (str, optional): Email do comprador
            titulo_preferencia (str): Título da preferência
            url_notificacao (str, optional): URL para notificações webhook
            urls_retorno (Dict, optional): URLs de retorno após pagamento
        
        Returns:
            Dict: Dicionário com resultado da operação
                {
                    'sucesso': bool,
                    'id': str (se sucesso),
                    'link_pagamento': str (se sucesso),
                    'qr_code': str (se disponível),
                    'total': float,
                    'erro': str (se falhou)
                }
        
        Raises:
            ValueError: Se carrinho está vazio
        
        Example:
            >>> servico = PagamentoService("SEU_TOKEN")
            >>> resultado = servico.gerar_link_pagamento(
            ...     carrinho,
            ...     email_comprador="cliente@email.com"
            ... )
            >>> if resultado['sucesso']:
            ...     print(resultado['link_pagamento'])
        """
        # ========== VALIDAÇÕES ==========
        
        if carrinho.esta_vazio():
            raise ValueError("Carrinho vazio! Adicione produtos antes.")
        
        # ========== PREPARAR DADOS ==========
        
        # Formatar items para API Mercado Pago
        items = self._formatar_items(carrinho)
        
        # Construir preferência de pagamento
        preferencia = self._construir_preferencia(
            items=items,
            email_comprador=email_comprador,
            titulo_preferencia=titulo_preferencia,
            url_notificacao=url_notificacao,
            urls_retorno=urls_retorno
        )
        
        # ========== EXECUTAR REQUISIÇÃO ==========
        
        try:
            resposta = self.sdk.preference().create(preferencia)
            return self._processar_resposta(resposta, carrinho.obter_total())
        
        except Exception as erro:
            return {
                'sucesso': False,
                'erro': f"Erro ao comunicar com Mercado Pago: {str(erro)}",
                'total': carrinho.obter_total()
            }
    
    # ========== MÉTODOS AUXILIARES ==========
    
    # ========== CONSULTA DE PAGAMENTO ==========

    def consultar_pagamento(self, pagamento_id: str) -> Dict:
        """
        Consulta o status de um pagamento no Mercado Pago pelo ID.

        Usado tanto pela rota de consulta manual quanto pelo webhook,
        que recebe o ID do pagamento e precisa confirmar o status real
        direto na API (nunca confie apenas no que chega no webhook).

        Args:
            pagamento_id (str): ID do pagamento no Mercado Pago

        Returns:
            dict: Dados do pagamento, incluindo 'status' e 'aprovado'.
        """
        try:
            resposta = self.sdk.payment().get(pagamento_id)
            status_code = resposta.get('status')
            dados = resposta.get('response', {})

            if status_code != 200 or not dados:
                return {
                    'sucesso': False,
                    'erro': f"Pagamento nao encontrado (HTTP {status_code})",
                    'pagamento_id': str(pagamento_id),
                }

            status = dados.get('status', 'unknown')

            return {
                'sucesso': True,
                'pagamento_id': str(pagamento_id),
                'status': status,
                'status_detalhe': dados.get('status_detail', ''),
                'aprovado': status == 'approved',
                'valor': dados.get('transaction_amount', 0),
                'email': (dados.get('payer') or {}).get('email', ''),
                'metodo': dados.get('payment_method_id', ''),
                'referencia_externa': dados.get('external_reference', ''),
                'data_aprovacao': dados.get('date_approved', ''),
            }

        except Exception as erro:
            return {
                'sucesso': False,
                'erro': f"Erro ao consultar pagamento: {str(erro)}",
                'pagamento_id': str(pagamento_id),
            }

    def _formatar_items(self, carrinho: CarrinhoCompras) -> list:
        """
        Formata os produtos do carrinho para o formato da API Mercado Pago.
        
        Args:
            carrinho (CarrinhoCompras): Carrinho com produtos
        
        Returns:
            list: Lista de items formatados para API
        
        Example:
            >>> items = servico._formatar_items(carrinho)
            >>> items[0]['title']
            'Notebook'
        """
        items = []
        
        for produto in carrinho.listar_produtos():
            item = {
                'id': produto['id'],
                'title': produto['titulo'],
                'description': produto['descricao'],
                'quantity': produto['quantidade'],
                'unit_price': produto['preco']
            }
            items.append(item)
        
        return items
    
    def _construir_preferencia(
        self,
        items: list,
        email_comprador: Optional[str] = None,
        titulo_preferencia: str = "Sua Compra",
        url_notificacao: Optional[str] = None,
        urls_retorno: Optional[Dict[str, str]] = None
    ) -> Dict:
        """
        Constrói o objeto de preferência para API Mercado Pago.
        
        Args:
            items (list): Lista de itens formatados
            email_comprador (str, optional): Email do comprador
            titulo_preferencia (str): Título da preferência
            url_notificacao (str, optional): URL de webhook
            urls_retorno (Dict, optional): URLs de retorno
        
        Returns:
            Dict: Objeto preferência para API
        
        Example:
            >>> pref = servico._construir_preferencia(items)
            >>> 'items' in pref
            True
        """
        # Estrutura base da preferência
        preferencia = {
            'items': items,
            'payer': {},
            'back_urls': urls_retorno or {
                'success': 'https://seu-site.com/sucesso',
                'failure': 'https://seu-site.com/erro',
                'pending': 'https://seu-site.com/pendente'
            },
            'auto_return': 'approved'
        }
        
        # Adicionar email se fornecido
        if email_comprador:
            preferencia['payer']['email'] = email_comprador
        
        # Adicionar URL de notificação se fornecida
        if url_notificacao:
            preferencia['notification_url'] = url_notificacao
        
        return preferencia
    
    def _processar_resposta(self, resposta: Dict, total: float) -> Dict:
        """
        Processa a resposta da API Mercado Pago.
        
        Args:
            resposta (Dict): Resposta da API
            total (float): Total do carrinho
        
        Returns:
            Dict: Resposta formatada
        
        Example:
            >>> resposta_raw = {'status': 201, 'response': {...}}
            >>> resultado = servico._processar_resposta(resposta_raw, 2500.0)
            >>> resultado['sucesso']
            True
        """
        if resposta.get('status') != 201:
            mensagem_erro = resposta.get('response', {}).get('message', 'Erro desconhecido')
            return {
                'sucesso': False,
                'erro': f"Mercado Pago retornou erro: {mensagem_erro}",
                'total': total
            }
        
        dados = resposta.get('response', {})
        
        return {
            'sucesso': True,
            'id': dados.get('id'),
            'link_pagamento': dados.get('init_point'),
            'qr_code': dados.get('sandbox_init_point'),
            'total': total
        }
    
    # ========== UTILITÁRIOS ==========
    
    def validar_access_token(self) -> bool:
        """
        Valida se o access token é válido fazendo uma requisição simples.
        
        Returns:
            bool: True se token é válido, False caso contrário
        
        Example:
            >>> servico = PagamentoService("SEU_TOKEN")
            >>> servico.validar_access_token()
            True
        """
        try:
            # Tenta fazer uma requisição simples
            self.sdk.preference().get()
            return True
        except:
            return False
    
    def __repr__(self) -> str:
        """Representação em string do serviço."""
        return f"PagamentoService(token_length={len(self.access_token)})"
