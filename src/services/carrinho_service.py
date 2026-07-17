"""
Módulo: services/carrinho_service.py
====================================

Descrição:
    Serviço responsável por gerenciar carrinhos por sessão.

    Suporta dois modos de armazenamento:
    - Redis (produção): carrinhos compartilhados entre todos os workers
      e persistentes mesmo se a aplicação reiniciar.
    - Memória (desenvolvimento/fallback): usado automaticamente quando
      o Redis não está configurado ou indisponível.

    O modo é escolhido pela variável de ambiente REDIS_URL. Se ela existir
    e a conexão funcionar, usa Redis; caso contrário, usa memória.

Exemplo de uso:
    >>> servico = CarrinhoService()
    >>> produto = Produto("001", "Mouse", 150)
    >>> servico.adicionar_produto("sessao_123", produto)
"""

import os
import json
import threading
from typing import Dict, Optional

from ..models import CarrinhoCompras, Produto

# Import opcional do Redis (não quebra se não estiver instalado)
try:
    import redis
    REDIS_DISPONIVEL = True
except ImportError:
    redis = None
    REDIS_DISPONIVEL = False


# Tempo de expiração dos carrinhos no Redis (em segundos). 7 dias.
CARRINHO_TTL = 60 * 60 * 24 * 7


class CarrinhoService:
    """
    Serviço de gerenciamento de carrinhos por sessão.

    Usa Redis quando disponível (compartilhado entre workers) ou memória
    como fallback. A API pública é a mesma nos dois casos.

    Attributes:
        _redis: Cliente Redis (ou None se usando memória)
        _carrinhos (Dict): Armazenamento em memória (fallback)
        _lock (threading.Lock): Lock para thread-safety no modo memória

    Example:
        >>> servico = CarrinhoService()
        >>> servico.adicionar_produto("sessao_1", produto)
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Inicializa o serviço de carrinho.

        Args:
            redis_url (str, optional): URL de conexão do Redis.
                Se não fornecida, lê da variável de ambiente REDIS_URL.
                Se nenhuma existir, usa armazenamento em memória.
        """
        self._redis = None
        self._carrinhos: Dict[str, CarrinhoCompras] = {}
        self._lock = threading.Lock()

        url = redis_url or os.getenv('REDIS_URL')

        if url and REDIS_DISPONIVEL:
            try:
                self._redis = redis.from_url(url, decode_responses=True)
                # Testa a conexão imediatamente
                self._redis.ping()
                print(f"[CarrinhoService] Usando Redis: {url.split('@')[-1]}")
            except Exception as e:
                print(f"[CarrinhoService] Redis indisponível ({e}). Usando memória.")
                self._redis = None
        else:
            print("[CarrinhoService] REDIS_URL não configurada. Usando memória.")

    # ========== SERIALIZAÇÃO (Redis) ==========

    def _chave(self, sessao_id: str) -> str:
        """Monta a chave do Redis para uma sessão."""
        return f"carrinho:{sessao_id}"

    def _serializar(self, carrinho: CarrinhoCompras) -> str:
        """Converte um carrinho em JSON para salvar no Redis."""
        produtos = []
        for p in carrinho.listar_produtos():
            produtos.append({
                'id': p['id'],
                'titulo': p['titulo'],
                'preco': p['preco'],
                'descricao': p.get('descricao', ''),
                'quantidade': p['quantidade'],
            })
        return json.dumps({'produtos': produtos})

    def _desserializar(self, dados: str) -> CarrinhoCompras:
        """Reconstrói um carrinho a partir do JSON do Redis."""
        carrinho = CarrinhoCompras()
        if not dados:
            return carrinho
        obj = json.loads(dados)
        for p in obj.get('produtos', []):
            produto = Produto(
                id=p['id'],
                titulo=p['titulo'],
                preco=p['preco'],
                descricao=p.get('descricao', ''),
                quantidade=p.get('quantidade', 1),
            )
            carrinho.adicionar_produto(produto)
        return carrinho

    def _carregar(self, sessao_id: str) -> CarrinhoCompras:
        """Carrega o carrinho do armazenamento (Redis ou memória)."""
        if self._redis is not None:
            dados = self._redis.get(self._chave(sessao_id))
            return self._desserializar(dados)
        # Memória
        with self._lock:
            if sessao_id not in self._carrinhos:
                self._carrinhos[sessao_id] = CarrinhoCompras()
            return self._carrinhos[sessao_id]

    def _salvar(self, sessao_id: str, carrinho: CarrinhoCompras) -> None:
        """Salva o carrinho no armazenamento (Redis ou memória)."""
        if self._redis is not None:
            self._redis.setex(
                self._chave(sessao_id),
                CARRINHO_TTL,
                self._serializar(carrinho),
            )
        else:
            with self._lock:
                self._carrinhos[sessao_id] = carrinho

    # ========== OPERAÇÕES COM CARRINHOS ==========

    def obter_carrinho(self, sessao_id: str) -> CarrinhoCompras:
        """
        Obtém ou cria um carrinho para uma sessão.

        Args:
            sessao_id (str): ID da sessão

        Returns:
            CarrinhoCompras: Carrinho da sessão

        Raises:
            ValueError: Se sessao_id estiver vazio
        """
        if not sessao_id:
            raise ValueError("Sessão ID não pode estar vazio")
        return self._carregar(sessao_id)

    def existe_sessao(self, sessao_id: str) -> bool:
        """Verifica se uma sessão existe."""
        if self._redis is not None:
            return bool(self._redis.exists(self._chave(sessao_id)))
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
        """
        if not isinstance(produto, Produto):
            raise TypeError("Argumento deve ser um Produto")

        carrinho = self.obter_carrinho(sessao_id)
        resultado = carrinho.adicionar_produto(produto)
        self._salvar(sessao_id, carrinho)
        return resultado

    def remover_produto(self, sessao_id: str, produto_id: str) -> bool:
        """Remove um produto do carrinho."""
        if not self.existe_sessao(sessao_id):
            return False
        carrinho = self.obter_carrinho(sessao_id)
        resultado = carrinho.remover_produto(produto_id)
        self._salvar(sessao_id, carrinho)
        return resultado

    def atualizar_quantidade(
        self,
        sessao_id: str,
        produto_id: str,
        quantidade: int
    ) -> bool:
        """Atualiza a quantidade de um produto."""
        carrinho = self.obter_carrinho(sessao_id)
        resultado = carrinho.atualizar_quantidade(produto_id, quantidade)
        self._salvar(sessao_id, carrinho)
        return resultado

    # ========== OPERAÇÕES DE CONSULTA ==========

    def obter_resumo_carrinho(self, sessao_id: str) -> Dict:
        """Obtém um resumo completo do carrinho."""
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.obter_resumo()

    def listar_produtos(self, sessao_id: str) -> list:
        """Lista todos os produtos do carrinho."""
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.listar_produtos()

    def obter_total(self, sessao_id: str) -> float:
        """Obtém o total do carrinho."""
        carrinho = self.obter_carrinho(sessao_id)
        return carrinho.obter_total()

    # ========== LIMPEZA ==========

    def limpar_carrinho(self, sessao_id: str) -> bool:
        """Limpa todos os produtos de um carrinho."""
        if not self.existe_sessao(sessao_id):
            return False
        carrinho = self.obter_carrinho(sessao_id)
        carrinho.limpar()
        self._salvar(sessao_id, carrinho)
        return True

    def remover_sessao(self, sessao_id: str) -> bool:
        """Remove completamente uma sessão do sistema."""
        if self._redis is not None:
            removido = bool(self._redis.delete(self._chave(sessao_id)))
            return removido
        with self._lock:
            if sessao_id in self._carrinhos:
                del self._carrinhos[sessao_id]
                return True
            return False

    def listar_sessoes(self) -> list:
        """Lista todos os IDs de sessão ativas."""
        if self._redis is not None:
            chaves = self._redis.keys("carrinho:*")
            return [c.replace("carrinho:", "", 1) for c in chaves]
        with self._lock:
            return list(self._carrinhos.keys())

    def obter_quantidade_sessoes(self) -> int:
        """Retorna quantas sessões estão ativas."""
        return len(self.listar_sessoes())

    def __repr__(self) -> str:
        """Representação em string do serviço."""
        modo = "Redis" if self._redis is not None else "Memória"
        return f"CarrinhoService(modo={modo}, {self.obter_quantidade_sessoes()} sessões)"
