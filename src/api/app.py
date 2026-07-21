"""
Módulo: src/api/app.py
======================

Descrição:
    Arquivo principal da aplicação Flask.
    
Responsabilidades:
    - Criar e configurar aplicação Flask
    - Registrar blueprints de rotas
    - Definir handlers de erro
    - Middlewares (CORS, etc)
    
Exemplo:
    from src.api.app import criar_app
    app = criar_app()
    app.run()
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os

from .routes import carrinho_bp, pagamento_bp, produto_bp
from .swagger import swagger_bp
from ..config import obter_config


def criar_app(config=None) -> Flask:
    """
    Factory function para criar e configurar a aplicação Flask.
    
    Args:
        config (Config, optional): Objeto de configuração
                                 Se não fornecido, usa variável FLASK_ENV
    
    Returns:
        Flask: Aplicação Flask configurada
    
    Example:
        >>> app = criar_app()
        >>> app.run()
    """
    
    # ========== INICIALIZAR FLASK ==========
    
    app = Flask(__name__)
    
    # Configurar aplicação
    if config is None:
        config = obter_config(os.getenv('FLASK_ENV', 'development'))
    elif isinstance(config, str):
        config = obter_config(config)
    app.config.from_object(config)
    
    # ========== MIDDLEWARE ==========
    
    # Habilitar CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # ========== AUTENTICAÇÃO POR API KEY ==========

    # Chave lida da variável de ambiente. Se não definida, a proteção
    # fica DESLIGADA (útil em desenvolvimento).
    API_KEY = os.getenv('API_KEY', '')

    # Rotas que NÃO exigem API Key (públicas):
    # - /api/pagamento/webhook : o Mercado Pago acessa sem chave
    # - /docs e /openapi.json  : documentação
    # - /api/health            : health check (útil para o Coolify monitorar)
    ROTAS_PUBLICAS = {
        '/api/pagamento/webhook',
        '/docs',
        '/openapi.json',
        '/api/health',
    }

    @app.before_request
    def verificar_api_key():
        """Bloqueia requisições sem API Key válida (exceto rotas públicas)."""
        # Se não há chave configurada, não protege (modo desenvolvimento)
        if not API_KEY:
            return None

        # Libera requisições OPTIONS (preflight CORS)
        if request.method == 'OPTIONS':
            return None

        # Libera rotas públicas
        caminho = request.path.rstrip('/') or '/'
        if caminho in ROTAS_PUBLICAS:
            return None

        # Demais rotas exigem a chave no header X-API-Key
        chave_recebida = request.headers.get('X-API-Key', '')
        if chave_recebida != API_KEY:
            return jsonify({
                'sucesso': False,
                'erro': 'Não autorizado. Forneça uma API Key válida no header X-API-Key.'
            }), 401

        return None

    # ========== BLUEPRINTS ==========
    
    # Registrar rotas de produtos
    app.register_blueprint(produto_bp)
    
    # Registrar rotas de carrinho
    app.register_blueprint(carrinho_bp)
    
    # Registrar rotas de pagamento
    app.register_blueprint(pagamento_bp)

    # Registrar documentação Swagger (/docs e /openapi.json)
    app.register_blueprint(swagger_bp)
    
    # ========== ROTAS GERAIS ==========
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Endpoint: GET /api/health
        
        Verifica se a aplicação está respondendo.
        
        Returns:
            JSON com status
        
        Example Response (200):
            {
                "status": "OK",
                "versao": "1.0.0",
                "ambiente": "production"
            }
        """
        return jsonify({
            "status": "OK",
            "versao": "1.0.0",
            "ambiente": app.config.get('ENV', 'unknown')
        }), 200
    
    # ========== ERROR HANDLERS ==========
    
    @app.errorhandler(404)
    def nao_encontrado(erro):
        """
        Handler para erro 404 - Rota não encontrada.
        
        Args:
            erro: Exceção do Flask
        
        Returns:
            JSON com mensagem de erro
        """
        return jsonify({
            "sucesso": False,
            "erro": "Rota não encontrada",
            "status": 404
        }), 404
    
    @app.errorhandler(405)
    def metodo_nao_permitido(erro):
        """
        Handler para erro 405 - Método HTTP não permitido.
        
        Args:
            erro: Exceção do Flask
        
        Returns:
            JSON com mensagem de erro
        """
        return jsonify({
            "sucesso": False,
            "erro": "Método HTTP não permitido",
            "status": 405
        }), 405
    
    @app.errorhandler(500)
    def erro_interno(erro):
        """
        Handler para erro 500 - Erro interno do servidor.
        
        Args:
            erro: Exceção do Flask
        
        Returns:
            JSON com mensagem de erro
        """
        return jsonify({
            "sucesso": False,
            "erro": "Erro interno do servidor",
            "status": 500,
            "detalhes": str(erro) if app.debug else None
        }), 500
    
    # ========== ROTAS DE DESENVOLVIMENTO ==========
    
    if app.debug:
        @app.route('/api/info', methods=['GET'])
        def info():
            """
            Endpoint: GET /api/info (apenas em debug)
            
            Retorna informações sobre a aplicação.
            
            Returns:
                JSON com informações
            """
            return jsonify({
                "aplicacao": "Sistema de Carrinho com Mercado Pago",
                "versao": "1.0.0",
                "debug": True,
                "routes": [
                    "GET /api/health",
                    "GET /api/info",
                    "GET /api/produtos",
                    "GET /api/produtos/<id>",
                    "GET /api/carrinho/<sessao>",
                    "POST /api/carrinho/<sessao>/adicionar",
                    "DELETE /api/carrinho/<sessao>/remover/<produto>",
                    "PUT /api/carrinho/<sessao>/atualizar-quantidade",
                    "DELETE /api/carrinho/<sessao>/limpar",
                    "POST /api/pagamento/<sessao>/gerar-link",
                    "GET /api/pagamento/health"
                ]
            }), 200
    
    return app


# Função auxiliar para desenvolvimento
def criar_app_debug() -> Flask:
    """
    Cria aplicação com todas as configurações de debug habilitadas.
    
    Útil para testes e desenvolvimento.
    
    Returns:
        Flask: Aplicação configurada para debug
    
    Example:
        >>> app = criar_app_debug()
    """
    from ..config import DevelopmentConfig
    return criar_app(DevelopmentConfig())
