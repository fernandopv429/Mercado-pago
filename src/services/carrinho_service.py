"""
Módulo: services/carrinho_service.py
====================================

Descrição:
    Serviço responsável por gerenciar carrinhos por sessão.
    
Responsabilidades:
    - Manter registry de carrinhos
    - Obter/criar carrinhos por sessão ID
    - Limpar carrinhos antigos (se necessário)
    
Exemplo de uso:
    >>> servico = CarrinhoService()
    >>> carrinho = servico.obter_carrinho("sessao_123")
    >>> produto = Produto("001", "Mouse", 150)
    >>> servico.adicionar_produto("sessao_123", produto)
"""

from typing import Dict, Optional
import threading
from ..models import CarrinhoCompras, Produto


class CarrinhoService:
    """
    Serviço de gerenciamento de carrinhos por sessão.
    
    Mantém um registro de carrinhos associados a IDs de sessão.
    Thread-safe para ambientes multi-thread.
    
    Attributes:
        _carrinhos (Dict): Dicionário de carrinhos por sessão
        _lock (threading.Lock): Lock para thread-safety
    
    Example:
        >>> servico = CarrinhoService()
        >>> carrinho = servico.obter_carrinho("sessao_1")
        >>> servico.adicionar_produto("sessao_1", produto)
    """
    
    def __init__(self):
        """Inicializa o serviço de carrinho."""
        self._carrinhos: Dict[str, CarrinhoCompras] = {}
        self._lock = threading.Lock()
    
    # ========== OPERAÇÕES COM CARRINHOS ==========
    
    def obter_carrinho(self, sessao_id: str) -> CarrinhoCompras:
        """
        Obtém ou cria um carrinho para uma sessão.
        
        Se a sessão não existe, cria um novo carrinho vazio.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            CarrinhoCompras: Carrinho da sessão
        
        Raises:
            ValueError: Se sessao_id estiver vazio
        
        Example:
            >>> servico = CarrinhoService()
            >>> carrinho = servico.obter_carrinho("sessao_1")
            >>> isinstance(carrinho, CarrinhoCompras)
            True
        """
        if not sessao_id:
            raise ValueError("Sessão ID não pode estar vazio")
        
        with self._lock:
            if sessao_id not in self._carrinhos:
                self._carrinhos[sessao_id] = CarrinhoCompras()
            
            return self._carrinhos[sessao_id]
    
    def existe_sessao(self, sessao_id: str) -> bool:
        """
        Verifica se uma sessão existe.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            bool: True se sessão existe, False caso contrário
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.existe_sessao("sessao_1")
            False
            >>> servico.obter_carrinho("sessao_1")
            >>> servico.existe_sessao("sessao_1")
            True
        """
        with self._lock:
            return sessao_id in self._carrinhos
    
    # ========== OPERAÇÕES COM PRODUTOS ==========
    
    def adicionar_produto(self, sessao_id: str, produto: Produto) -> bool:
        """
        Adiciona um produto ao carrinho da sessão.
        
        Args:
            sessao_id (str): ID da sessão
            produto (Produto): Produto a adicionar
        
        Returns:
            bool: True se adicionado com sucesso
        
        Raises:
            TypeError: Se produto não é um Produto
        
        Example:
            >>> servico = CarrinhoService()
            >>> p = Produto("001", "Mouse", 150)
            >>> servico.adicionar_produto("sessao_1", p)
            True
        """
        if not isinstance(produto, Produto):
            raise TypeError("Argumento deve ser um Produto")
        
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.adicionar_produto(produto)
    
    def remover_produto(self, sessao_id: str, produto_id: str) -> bool:
        """
        Remove um produto do carrinho.
        
        Args:
            sessao_id (str): ID da sessão
            produto_id (str): ID do produto
        
        Returns:
            bool: True se removido, False se não encontrado
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.remover_produto("sessao_1", "001")
            False  # produto não existia
        """
        if not self.existe_sessao(sessao_id):
            return False
        
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.remover_produto(produto_id)
    
    def atualizar_quantidade(
        self,
        sessao_id: str,
        produto_id: str,
        quantidade: int
    ) -> bool:
        """
        Atualiza a quantidade de um produto.
        
        Args:
            sessao_id (str): ID da sessão
            produto_id (str): ID do produto
            quantidade (int): Nova quantidade
        
        Returns:
            bool: True se atualizado, False se não encontrado
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.adicionar_produto("s1", Produto("001", "Mouse", 150))
            True
            >>> servico.atualizar_quantidade("s1", "001", 5)
            True
        """
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.atualizar_quantidade(produto_id, quantidade)
    
    # ========== OPERAÇÕES DE CONSULTA ==========
    
    def obter_resumo_carrinho(self, sessao_id: str) -> Dict:
        """
        Obtém um resumo completo do carrinho.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            Dict: Resumo do carrinho com total, quantidade, etc
        
        Example:
            >>> servico = CarrinhoService()
            >>> resumo = servico.obter_resumo_carrinho("sessao_1")
            >>> resumo['total']
            0.0
        """
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.obter_resumo()
    
    def listar_produtos(self, sessao_id: str) -> list:
        """
        Lista todos os produtos do carrinho.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            list: Lista de produtos (dicionários)
        
        Example:
            >>> servico = CarrinhoService()
            >>> produtos = servico.listar_produtos("sessao_1")
            >>> len(produtos)
            0
        """
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.listar_produtos()
    
    def obter_total(self, sessao_id: str) -> float:
        """
        Obtém o total do carrinho.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            float: Total do carrinho
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.obter_total("sessao_1")
            0.0
        """
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.obter_total()
    
    # ========== LIMPEZA ==========
    
    def limpar_carrinho(self, sessao_id: str) -> bool:
        """
        Limpa todos os produtos de um carrinho.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            bool: True se limpou, False se não existia
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.adicionar_produto("s1", Produto("001", "Mouse", 150))
            True
            >>> servico.limpar_carrinho("s1")
            True
            >>> servico.obter_total("s1")
            0.0
        """
        if not self.existe_sessao(sessao_id):
            return False
        
        carrinho = self.obter_carrinho(sessao_id)
        carrinho.limpar()
        return True
    
    def remover_sessao(self, sessao_id: str) -> bool:
        """
        Remove completamente uma sessão do sistema.
        
        Args:
            sessao_id (str): ID da sessão
        
        Returns:
            bool: True se removeu, False se não existia
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.obter_carrinho("s1")
            >>> servico.remover_sessao("s1")
            True
        """
        with self._lock:
            if sessao_id in self._carrinhos:
                del self._carrinhos[sessao_id]
                return True
            return False
    
    def listar_sessoes(self) -> list:
        """
        Lista todos os IDs de sessão ativas.
        
        Returns:
            list: Lista com IDs das sessões
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.obter_carrinho("s1")
            >>> servico.obter_carrinho("s2")
            >>> servico.listar_sessoes()
            ['s1', 's2']
        """
        with self._lock:
            return list(self._carrinhos.keys())
    
    def obter_quantidade_sessoes(self) -> int:
        """
        Retorna quantas sessões estão ativas.
        
        Returns:
            int: Número de sessões
        
        Example:
            >>> servico = CarrinhoService()
            >>> servico.obter_carrinho("s1")
            >>> servico.obter_carrinho("s2")
            >>> servico.obter_quantidade_sessoes()
            2
        """
        with self._lock:
            return len(self._carrinhos)
    
    def __repr__(self) -> str:
        """Representação em string do serviço."""
        return f"CarrinhoService({self.obter_quantidade_sessoes()} sessões ativas)"
