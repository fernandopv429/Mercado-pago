"""
Módulo: wsgi.py
===============

Entry point WSGI para produção.

Usado por servidores WSGI como Gunicorn em ambientes de produção
(Coolify, Heroku, etc).

Exemplo de uso em produção:
    gunicorn wsgi:app
    
Ou com Coolify:
    O Coolify detecta este arquivo automaticamente.
"""

import os
from src import criar_app

# Obter ambiente
ambiente = os.getenv('FLASK_ENV', 'production')

# Criar aplicação
app = criar_app()

if __name__ == '__main__':
    # Nunca rode em modo debug em produção!
    porta = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=porta, debug=False)
