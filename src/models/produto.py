"""
Módulo: models/produto.py
========================

Descrição:
    Define a classe Produto que representa um item individual no carrinho.
    
Responsabilidades:
    - Armazenar informações do produto (id, título, preço, etc)
    - Calcular subtotal (preço × quantidade)
    - Validar dados do produto
    
Exemplo de uso:
    >>> produto = Produto(
    ...     id="001",
    ...     titulo="Notebook Dell",
    ...     preco=2500.00,
    ...     descricao="Notebook Intel Core i7"
    ... )
    >>> produto.obter_subtotal()
    2500.0
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Produto:
    """
    Classe que representa um produto no sistema de carrinho.
    
    Attributes:
        id (str): Identificador único do produto
        titulo (str): Nome/título do produto
        preco (float): Preço unitário do produto em reais
        descricao (str): Descrição detalhada do produto (opcional)
        quantidade (int): Quantidade do produto no carrinho (padrão: 1)
    
    Raises:
        ValueError: Se id, título ou preço forem inválidos
    
    Example:
        >>> p = Produto("001", "Mouse", 150.00, "Mouse sem fio", 2)
        >>> p.obter_subtotal()
        300.0
    """
    
    id: str
    titulo: str
    preco: float
    descricao: str = ""
    quantidade: int = 1
    
    def __post_init__(self):
        """
        Valida os dados do produto após inicialização.
        
        Verifica:
            - ID não está vazio
            - Título não está vazio
            - Preço é positivo
            - Quantidade é positiva
        
        Raises:
            ValueError: Se alguma validação falhar
        """
        if not self.id or not isinstance(self.id, str):
            raise ValueError("ID do produto deve ser uma string não vazia")
        
        if not self.titulo or not isinstance(self.titulo, str):
            raise ValueError("Título do produto deve ser uma string não vazia")
        
        if self.preco <= 0:
            raise ValueError("Preço deve ser maior que zero")
        
        if self.quantidade <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
    
    def obter_subtotal(self) -> float:
        """
        Calcula o valor total do produto (preço × quantidade).
        
        Returns:
            float: Subtotal do produto
        
        Example:
            >>> p = Produto("001", "Teclado", 450.00, quantidade=3)
            >>> p.obter_subtotal()
            1350.0
        """
        return self.preco * self.quantidade
    
    def atualizar_quantidade(self, nova_quantidade: int) -> bool:
        """
        Atualiza a quantidade do produto.
        
        Args:
            nova_quantidade (int): Nova quantidade desejada
        
        Returns:
            bool: True se atualizado com sucesso, False caso contrário
        
        Example:
            >>> p = Produto("001", "Mouse", 150.00, quantidade=1)
            >>> p.atualizar_quantidade(5)
            True
            >>> p.quantidade
            5
        """
        if nova_quantidade <= 0:
            return False
        
        self.quantidade = nova_quantidade
        return True
    
    def para_dicionario(self) -> dict:
        """
        Converte o produto para um dicionário.
        
        Útil para serialização JSON ou envio via API.
        
        Returns:
            dict: Dicionário com os dados do produto
        
        Example:
            >>> p = Produto("001", "Mouse", 150.00, "Mouse sem fio", 2)
            >>> p.para_dicionario()
            {
                'id': '001',
                'titulo': 'Mouse',
                'preco': 150.0,
                'quantidade': 2,
                'subtotal': 300.0
            }
        """
        return {
            'id': self.id,
            'titulo': self.titulo,
            'preco': self.preco,
            'descricao': self.descricao,
            'quantidade': self.quantidade,
            'subtotal': self.obter_subtotal()
        }
    
    def __repr__(self) -> str:
        """
        Representação em string do produto.
        
        Returns:
            str: Representação legível do produto
        """
        return (
            f"Produto(id='{self.id}', titulo='{self.titulo}', "
            f"preco=R${self.preco:.2f}, quantidade={self.quantidade})"
        )
