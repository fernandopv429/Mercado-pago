"""
Script: run.py
==============

Script para executar a aplicação em modo desenvolvimento.

Uso:
    python run.py
    
A aplicação será executada em: http://localhost:3000
"""

import os
from src import criar_app_debug

if __name__ == '__main__':
    # Criar aplicação com debug
    app = criar_app_debug()
    
    # Executar
    porta = int(os.getenv('PORT', 3000))
    
    print(f"\n{'='*60}")
    print(f"  Iniciando aplicação em modo DEBUG")
    print(f"  Acesso em: http://localhost:{porta}")
    print(f"  API Health: http://localhost:{porta}/api/health")
    print(f"  Info: http://localhost:{porta}/api/info")
    print(f"{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=porta,
        debug=True
    )
