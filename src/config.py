"""
Módulo: src/config.py
=====================

Descrição:
    Define as configurações da aplicação Flask.
    
Variáveis:
    - DEBUG: Modo debug (desenvolvimento/produção)
    - TESTING: Modo testes
    - ENV: Ambiente (development/production)
    - Outras configurações Flask
    
Exemplo:
    from src.config import DevelopmentConfig, ProductionConfig
"""

import os


class Config:
    """Configuração base para toda aplicação."""
    
    # ========== FLASK ==========
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    JSON_SORT_KEYS = False
    
    # ========== MERCADO PAGO ==========
    MERCADOPAGO_ACCESS_TOKEN = os.getenv('MERCADOPAGO_ACCESS_TOKEN', '')
    MERCADOPAGO_TIMEOUT = 30  # segundos
    
    # ========== CARRINHO ==========
    CARRINHO_TIMEOUT = 3600  # 1 hora em segundos
    MAX_SESSOES = 10000
    
    # ========== LOGS ==========
    LOG_LEVEL = 'INFO'
    
    def __repr__(self):
        return f"{self.__class__.__name__}()"


class DevelopmentConfig(Config):
    """Configuração para desenvolvimento."""
    
    DEBUG = True
    TESTING = False
    ENV = 'development'
    
    # Mais verbose em desenvolvimento
    JSON_SORT_KEYS = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Configuração para produção."""
    
    DEBUG = False
    TESTING = False
    ENV = 'production'
    
    # Mais seguro em produção
    PROPAGATE_EXCEPTIONS = True


class TestingConfig(Config):
    """Configuração para testes."""
    
    TESTING = True
    DEBUG = True
    
    # Para testes
    CARRINHO_TIMEOUT = 60  # Sessões mais curtas em testes


# ========== SELEÇÃO DE CONFIGURAÇÃO ==========

def obter_config(ambiente: str = None) -> Config:
    """
    Obtém a configuração apropriada baseado no ambiente.
    
    Args:
        ambiente (str): Nome do ambiente (development/production/testing)
    
    Returns:
        Config: Objeto de configuração apropriado
    
    Example:
        >>> config = obter_config('production')
        >>> config.DEBUG
        False
    """
    ambiente = ambiente or os.getenv('FLASK_ENV', 'development')
    
    configuracoes = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    return configuracoes.get(ambiente, DevelopmentConfig)()
