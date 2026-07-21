"""
Módulo: services/webhook_service.py
===================================

Descrição:
    Gerencia a URL de destino para onde os eventos de pagamento aprovado
    serão reenviados (ex.: painel de gestão, n8n, Discord).

    A URL fica salva no Redis (quando disponível) ou em memória, e pode ser
    cadastrada/trocada via API. Quando um pagamento é aprovado, o serviço
    faz um POST para essa URL com os dados do evento.

Exemplo de uso:
    >>> ws = WebhookService()
    >>> ws.definir_url("https://meu-painel.com/webhook")
    >>> ws.reenviar_evento({"tipo": "pagamento.aprovado", ...})
"""

import os
import json
import threading
from typing import Optional, Dict

import requests

try:
    import redis
    REDIS_DISPONIVEL = True
except ImportError:
    redis = None
    REDIS_DISPONIVEL = False


# Chave usada no Redis para guardar a URL de destino
REDIS_KEY = "config:webhook_destino"

# Timeout do POST de reenvio (segundos)
TIMEOUT_REENVIO = 8


class WebhookService:
    """
    Serviço de gerenciamento e reenvio de webhooks.

    Guarda a URL de destino (persistente no Redis) e reenvia os eventos
    de pagamento para ela.
    """

    def __init__(self, redis_url: Optional[str] = None):
        self._redis = None
        self._url_memoria: Optional[str] = None
        self._lock = threading.Lock()

        url = redis_url or os.getenv('REDIS_URL')
        if url and REDIS_DISPONIVEL:
            try:
                self._redis = redis.from_url(url, decode_responses=True)
                self._redis.ping()
            except Exception:
                self._redis = None

    # ---------- Gerenciar a URL ----------

    def definir_url(self, url: str) -> None:
        """Cadastra ou troca a URL de destino do webhook."""
        if self._redis is not None:
            self._redis.set(REDIS_KEY, url)
        else:
            with self._lock:
                self._url_memoria = url

    def obter_url(self) -> Optional[str]:
        """Retorna a URL de destino cadastrada (ou None)."""
        if self._redis is not None:
            return self._redis.get(REDIS_KEY)
        with self._lock:
            return self._url_memoria

    def remover_url(self) -> bool:
        """Remove a URL de destino cadastrada."""
        if self._redis is not None:
            return bool(self._redis.delete(REDIS_KEY))
        with self._lock:
            existia = self._url_memoria is not None
            self._url_memoria = None
            return existia

    # ---------- Reenvio ----------

    def reenviar_evento(self, evento: Dict) -> Dict:
        """
        Faz um POST do evento para a URL de destino cadastrada.

        Args:
            evento (dict): Dados do evento a reenviar.

        Returns:
            dict: {'enviado': bool, 'status_code'|'erro'|'aviso': ...}
        """
        url = self.obter_url()
        if not url:
            return {'enviado': False, 'aviso': 'Nenhuma URL de destino cadastrada'}

        try:
            resp = requests.post(
                url,
                json=evento,
                timeout=TIMEOUT_REENVIO,
                headers={'Content-Type': 'application/json'},
            )
            return {'enviado': True, 'status_code': resp.status_code, 'url': url}
        except Exception as erro:
            return {'enviado': False, 'erro': str(erro), 'url': url}
