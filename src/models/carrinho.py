"""
Módulo: models/carrinho.py
==========================

Descrição:
    Define a classe CarrinhoCompras que gerencia múltiplos produtos.
    
Responsabilidades:
    - Adicionar e remover produtos
    - Atualizar quantidades
    - Calcular total e quantidade de itens
    - Listar produtos no carrinho
    
Exemplo de uso:
    >>> carrinho = CarrinhoCompras()
    >>> carrinho.adicionar_produto(Produto("001", "Notebook", 2500))
    >>> carrinho.adicionar_produto(Produto("002", "Mouse", 150, quantidade=2))
    >>> carrinho.obter_total()
    2800.0
"""

from typing import List, Dict, Optional
from .produto import Produto


class CarrinhoCompras:
    """
    Classe que gerencia um carrinho de compras com múltiplos produtos.
    
    Esta classe é responsável por:
        - Armazenar produtos
        - Adicionar/remover items
        - Atualizar quantidades
        - Calcular valores totais
    
    Attributes:
        _produtos (List[Produto]): Lista interna de produtos
    
    Example:
        >>> carrinho = CarrinhoCompras()
        >>> carrinho.adicionar_produto(Produto("001", "Notebook", 2500))
        >>> carrinho.obter_total()
        2500.0
    """
    
    def __init__(self):
        """
        Inicializa um carrinho de compras vazio.
        """
        self._produtos: List[Produto] = []
    
    # ========== OPERAÇÕES DE ADIÇÃO ==========
    
    def adicionar_produto(self, produto: Produto) -> bool:
        """
        Adiciona um produto ao carrinho.
        
        Se o produto já existe, incrementa a quantidade.
        Se não existe, adiciona como novo item.
        
        Args:
            produto (Produto): Produto a ser adicionado
        
        Returns:
            bool: True se adicionado com sucesso
        
        Raises:
            TypeError: Se o argumento não é um Produto
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> p = Produto("001", "Notebook", 2500)
            >>> carrinho.adicionar_produto(p)
            True
            >>> carrinho.obter_quantidade_itens()
            1
        """
        if not isinstance(produto, Produto):
            raise TypeError("Argumento deve ser um objeto Produto")
        
        # Procura se o produto já existe
        produto_existente = self._encontrar_produto_por_id(produto.id)
        
        if produto_existente:
            # Se existe, incrementa quantidade
            produto_existente.quantidade += produto.quantidade
        else:
            # Se não existe, adiciona novo
            self._produtos.append(produto)
        
        return True
    
    # ========== OPERAÇÕES DE REMOÇÃO ==========
    
    def remover_produto(self, produto_id: str) -> bool:
        """
        Remove um produto do carrinho pelo ID.
        
        Args:
            produto_id (str): ID do produto a remover
        
        Returns:
            bool: True se removido, False se não encontrado
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150))
            True
            >>> carrinho.remover_produto("001")
            True
            >>> carrinho.obter_quantidade_itens()
            0
        """
        quantidade_inicial = len(self._produtos)
        self._produtos = [p for p in self._produtos if p.id != produto_id]
        
        foi_removido = len(self._produtos) < quantidade_inicial
        return foi_removido
    
    def limpar(self) -> None:
        """
        Remove todos os produtos do carrinho.
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150))
            True
            >>> carrinho.limpar()
            >>> carrinho.obter_quantidade_itens()
            0
        """
        self._produtos.clear()
    
    # ========== OPERAÇÕES DE ATUALIZAÇÃO ==========
    
    def atualizar_quantidade(self, produto_id: str, nova_quantidade: int) -> bool:
        """
        Atualiza a quantidade de um produto.
        
        Se a quantidade for 0 ou menor, remove o produto.
        
        Args:
            produto_id (str): ID do produto
            nova_quantidade (int): Nova quantidade desejada
        
        Returns:
            bool: True se atualizado com sucesso, False se não encontrado
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150, quantidade=1))
            True
            >>> carrinho.atualizar_quantidade("001", 5)
            True
            >>> carrinho.listar_produtos()[0]['quantidade']
            5
        """
        produto = self._encontrar_produto_por_id(produto_id)
        
        if not produto:
            return False
        
        # Se quantidade é 0 ou negativa, remove o produto
        if nova_quantidade <= 0:
            return self.remover_produto(produto_id)
        
        # Caso contrário, atualiza
        produto.quantidade = nova_quantidade
        return True
    
    # ========== OPERAÇÕES DE CONSULTA ==========
    
    def obter_total(self) -> float:
        """
        Calcula o valor total do carrinho.
        
        Returns:
            float: Soma de todos os subtotais dos produtos
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Notebook", 2500))
            True
            >>> carrinho.adicionar_produto(Produto("002", "Mouse", 150, quantidade=2))
            True
            >>> carrinho.obter_total()
            2800.0
        """
        return sum(p.obter_subtotal() for p in self._produtos)
    
    def obter_quantidade_itens(self) -> int:
        """
        Conta a quantidade total de itens no carrinho.
        
        Returns:
            int: Número total de itens (considerando quantidade de cada um)
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150, quantidade=3))
            True
            >>> carrinho.adicionar_produto(Produto("002", "Teclado", 450, quantidade=2))
            True
            >>> carrinho.obter_quantidade_itens()
            5
        """
        return sum(p.quantidade for p in self._produtos)
    
    def obter_quantidade_produtos(self) -> int:
        """
        Conta a quantidade de produtos DIFERENTES no carrinho.
        
        Retorna: Número de tipos diferentes de produtos
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150, quantidade=5))
            True
            >>> carrinho.adicionar_produto(Produto("002", "Teclado", 450, quantidade=2))
            True
            >>> carrinho.obter_quantidade_produtos()
            2
        """
        return len(self._produtos)
    
    def listar_produtos(self) -> List[Dict]:
        """
        Retorna lista de produtos no carrinho em formato dicionário.
        
        Returns:
            List[Dict]: Lista com dados de cada produto
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150, "Mouse sem fio", 2))
            True
            >>> produtos = carrinho.listar_produtos()
            >>> len(produtos)
            1
            >>> produtos[0]['subtotal']
            300.0
        """
        return [p.para_dicionario() for p in self._produtos]
    
    def obter_produto(self, produto_id: str) -> Optional[Produto]:
        """
        Obtém um produto específico do carrinho.
        
        Args:
            produto_id (str): ID do produto
        
        Returns:
            Produto ou None: O produto encontrado ou None
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> p = Produto("001", "Mouse", 150)
            >>> carrinho.adicionar_produto(p)
            True
            >>> encontrado = carrinho.obter_produto("001")
            >>> encontrado.titulo
            'Mouse'
        """
        return self._encontrar_produto_por_id(produto_id)
    
    # ========== MÉTODOS PRIVADOS (AUXILIARES) ==========
    
    def _encontrar_produto_por_id(self, produto_id: str) -> Optional[Produto]:
        """
        Procura um produto pelo ID (método interno).
        
        Args:
            produto_id (str): ID do produto a procurar
        
        Returns:
            Produto ou None: O produto encontrado ou None
        """
        for produto in self._produtos:
            if produto.id == produto_id:
                return produto
        return None
    
    # ========== MÉTODOS DE VALIDAÇÃO ==========
    
    def esta_vazio(self) -> bool:
        """
        Verifica se o carrinho está vazio.
        
        Returns:
            bool: True se carrinho vazio, False caso contrário
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.esta_vazio()
            True
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150))
            True
            >>> carrinho.esta_vazio()
            False
        """
        return len(self._produtos) == 0
    
    # ========== RELATÓRIOS ==========
    
    def obter_resumo(self) -> Dict:
        """
        Obtém um resumo completo do carrinho.
        
        Returns:
            Dict: Dicionário com informações resumidas
        
        Example:
            >>> carrinho = CarrinhoCompras()
            >>> carrinho.adicionar_produto(Produto("001", "Mouse", 150, quantidade=2))
            True
            >>> resumo = carrinho.obter_resumo()
            >>> resumo['quantidade_itens']
            2
            >>> resumo['total']
            300.0
        """
        return {
            'quantidade_produtos': self.obter_quantidade_produtos(),
            'quantidade_itens': self.obter_quantidade_itens(),
            'total': self.obter_total(),
            'produtos': self.listar_produtos(),
            'vazio': self.esta_vazio()
        }
    
    def __repr__(self) -> str:
        """
        Representação em string do carrinho.
        """
        return (
            f"CarrinhoCompras({self.obter_quantidade_produtos()} produtos, "
            f"{self.obter_quantidade_itens()} itens, "
            f"Total: R${self.obter_total():.2f})"
        )
