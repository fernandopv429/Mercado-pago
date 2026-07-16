"""
Módulo: api
===========

Contém a aplicação Flask e rotas:
    - app.py: Aplicação principal
    - routes/: Blueprints de rotas
"""

from .app import criar_app, criar_app_debug

__all__ = ['criar_app', 'criar_app_debug']
