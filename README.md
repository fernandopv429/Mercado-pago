# 🛒 Sistema de Carrinho com Mercado Pago - Modularizado

Projeto profissional e modularizado para integração com Mercado Pago, desenvolvido em Python com Flask.

---

## 📋 Índice

- [Estrutura do Projeto](#estrutura-do-projeto)
- [Começar Rápido](#começar-rápido)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Uso](#uso)
- [API Endpoints](#api-endpoints)
- [Modularização](#modularização)
- [Deploy](#deploy)

---

## 🎯 Estrutura do Projeto

```
projeto_modular/
├── src/                          # Código-fonte
│   ├── __init__.py              # Package principal
│   ├── config.py                # Configurações
│   │
│   ├── models/                  # Modelos de dados
│   │   ├── __init__.py
│   │   ├── produto.py           # Classe Produto
│   │   └── carrinho.py          # Classe CarrinhoCompras
│   │
│   ├── services/                # Serviços de negócio
│   │   ├── __init__.py
│   │   ├── carrinho_service.py  # Gerencia carrinhos por sessão
│   │   └── pagamento_service.py # Integra com Mercado Pago
│   │
│   └── api/                     # Aplicação Flask
│       ├── __init__.py
│       ├── app.py               # Aplicação principal
│       └── routes/              # Blueprints de rotas
│           ├── __init__.py
│           ├── carrinho_routes.py    # Endpoints carrinho
│           ├── pagamento_routes.py   # Endpoints pagamento
│           └── produto_routes.py     # Endpoints produtos
│
├── run.py                       # Script para desenvolvimento
├── wsgi.py                      # Entry point produção
├── requirements.txt             # Dependências Python
├── Dockerfile                   # Contêinerização
├── docker-compose.yml           # Orquestração local
├── .env.example                 # Variáveis de ambiente
├── .gitignore                   # Git ignore
└── README.md                    # Este arquivo
```

---

## ⚡ Começar Rápido

### 1. Clone/Copie o Projeto

```bash
cd projeto_modular
```

### 2. Instale Dependências

```bash
pip install -r requirements.txt
```

### 3. Configure Variáveis de Ambiente

```bash
cp .env.example .env
# Edite .env e adicione seu access token do Mercado Pago
```

### 4. Execute em Desenvolvimento

```bash
python run.py
```

Acesse: `http://localhost:3000/api/health`

---

## 💾 Instalação

### Pré-requisitos

- Python 3.11+
- pip
- Conta Mercado Pago com credenciais de teste

### Passos Detalhados

```bash
# 1. Criar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar ambiente
cp .env.example .env
nano .env  # Editar arquivo

# 4. Testar
python run.py
```

---

## ⚙️ Configuração

### Variáveis de Ambiente Obrigatórias

```bash
MERCADOPAGO_ACCESS_TOKEN=APP_USR-seu-token-aqui
```

### Variáveis Opcionais

```bash
FLASK_ENV=development          # development | production | testing
SECRET_KEY=sua-chave-secreta   # Mude em produção!
PORT=3000                      # Porta padrão
```

---

## 🚀 Uso

### Exemplos Python

#### Usar Modelos Diretamente

```python
from src.models import Produto, CarrinhoCompras

# Criar produto
produto = Produto(
    id="001",
    titulo="Notebook",
    preco=2500.00,
    descricao="Notebook Intel Core i7"
)

# Criar carrinho
carrinho = CarrinhoCompras()
carrinho.adicionar_produto(produto)

# Consultar
print(f"Total: R$ {carrinho.obter_total():.2f}")
print(f"Itens: {carrinho.obter_quantidade_itens()}")
```

#### Usar Serviços

```python
from src.services import CarrinhoService, PagamentoService

# Serviço de carrinho
carrinho_service = CarrinhoService()
carrinho_service.adicionar_produto("sessao_1", produto)

# Serviço de pagamento
pagamento_service = PagamentoService("seu_token")
resultado = pagamento_service.gerar_link_pagamento(carrinho)

if resultado['sucesso']:
    print(resultado['link_pagamento'])
```

#### Usar API Flask

```python
from src import criar_app

app = criar_app()
app.run()
```

---

## 📡 API Endpoints

### Health Check

```bash
GET /api/health
```

**Resposta:**
```json
{
    "status": "OK",
    "versao": "1.0.0",
    "ambiente": "production"
}
```

### Produtos

#### Listar Todos

```bash
GET /api/produtos
```

#### Obter Detalhe

```bash
GET /api/produtos/001
```

#### Listar Por Categoria

```bash
GET /api/produtos/categoria/Eletrônicos
```

---

### Carrinho

#### Obter Carrinho

```bash
GET /api/carrinho/sessao1
```

**Resposta:**
```json
{
    "sucesso": true,
    "produtos": [
        {
            "id": "001",
            "titulo": "Notebook",
            "preco": 2500.0,
            "quantidade": 1,
            "subtotal": 2500.0
        }
    ],
    "total": 2500.0,
    "quantidade_itens": 1
}
```

#### Adicionar Produto

```bash
POST /api/carrinho/sessao1/adicionar
Content-Type: application/json

{
    "id": "001",
    "titulo": "Notebook",
    "preco": 2500.00,
    "descricao": "Notebook Intel Core i7",
    "quantidade": 1
}
```

#### Atualizar Quantidade

```bash
PUT /api/carrinho/sessao1/atualizar-quantidade
Content-Type: application/json

{
    "produto_id": "001",
    "quantidade": 5
}
```

#### Remover Produto

```bash
DELETE /api/carrinho/sessao1/remover/001
```

#### Limpar Carrinho

```bash
DELETE /api/carrinho/sessao1/limpar
```

---

### Pagamento

#### Gerar Link de Pagamento

```bash
POST /api/pagamento/sessao1/gerar-link
Content-Type: application/json

{
    "email": "cliente@email.com",
    "titulo": "Minha Compra"
}
```

**Resposta:**
```json
{
    "sucesso": true,
    "id": "987654321",
    "link_pagamento": "https://www.mercadopago.com.br/checkout/v1/...",
    "total": 2500.0
}
```

---

## 🔧 Modularização

### 1. Models (Modelos de Dados)

Responsáveis por **estrutura e lógica de dados**.

#### `Produto`
- Representa um item individual
- Valida dados no `__post_init__`
- Calcula subtotal automaticamente
- Método: `para_dicionario()` para serialização

#### `CarrinhoCompras`
- Gerencia múltiplos produtos
- Thread-safe (operações com lock)
- Métodos de adição, remoção, atualização
- Cálculos automáticos de total e quantidade

### 2. Services (Serviços de Negócio)

Responsáveis pela **lógica de negócio**.

#### `CarrinhoService`
- Gerencia carrinhos por sessão ID
- Thread-safe para multi-threading
- Isolamento de dados por sessão
- Não conhece Flask ou HTTP

#### `PagamentoService`
- Integra com API Mercado Pago
- Formata dados para API
- Processa respostas
- Isolado da camada HTTP

### 3. API (Aplicação Flask)

Responsável pela **comunicação HTTP**.

#### `app.py`
- Factory pattern para criar aplicação
- Registra blueprints
- Configura CORS e middlewares
- Handlers de erro globais

#### `routes/`
- Blueprints separados por recurso
- Endpoints RESTful
- Validação de entrada
- Respostas JSON padronizadas

### 4. Config (Configurações)

Responsável por **gerenciar ambientes**.

- Classe base `Config`
- Subclasses por ambiente (`Development`, `Production`, `Testing`)
- Factory `obter_config()` para seleção

---

## 🎯 Padrões Implementados

### 1. **Factory Pattern**

```python
# config.py
config = obter_config('production')

# app.py
app = criar_app(config)
```

### 2. **Blueprint Pattern (Flask)**

```python
# Cada recurso é um blueprint independente
carrinho_bp = Blueprint('carrinho', ...)
pagamento_bp = Blueprint('pagamento', ...)

app.register_blueprint(carrinho_bp)
app.register_blueprint(pagamento_bp)
```

### 3. **Separation of Concerns**

```
Models (O QUÊ)
    ↓
Services (COMO fazer)
    ↓
API/Routes (COMO expor via HTTP)
```

### 4. **Dependency Injection**

Services recebem dependências como parâmetros:

```python
def __init__(self, access_token: str):
    self.sdk = mercadopago.SDK(access_token)
```

---

## 🐳 Docker e Deploy

### Desenvolvimento Local

```bash
# Com docker-compose
docker-compose up

# Acessa em: http://localhost:3000
```

### Produção (Coolify)

```bash
# Envie para Git
git push origin main

# Coolify detecta Dockerfile automaticamente
# Deploy automático é acionado
```

---

## 📊 Fluxo de Dados

```
┌─────────────────────────────────────┐
│   Cliente HTTP (REST API)           │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Routes (Validação HTTP)           │
│   - Valida entrada                  │
│   - Chama services                  │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Services (Lógica de Negócio)      │
│   - CarrinhoService                 │
│   - PagamentoService                │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│   Models (Dados)                    │
│   - Produto                         │
│   - CarrinhoCompras                 │
└─────────────────────────────────────┘
```

---

## 🧪 Testes

### Testar com curl

```bash
# Listar produtos
curl http://localhost:3000/api/produtos

# Adicionar ao carrinho
curl -X POST http://localhost:3000/api/carrinho/sessao1/adicionar \
  -H "Content-Type: application/json" \
  -d '{"id":"001","titulo":"Mouse","preco":150}'

# Gerar link
curl -X POST http://localhost:3000/api/pagamento/sessao1/gerar-link \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com"}'
```

---

## 📚 Documentação Adicional

Ver arquivos individuais para documentação detalhada:

- `src/models/produto.py` - Documentação Produto
- `src/models/carrinho.py` - Documentação CarrinhoCompras
- `src/services/carrinho_service.py` - Documentação CarrinhoService
- `src/services/pagamento_service.py` - Documentação PagamentoService
- `src/api/routes/carrinho_routes.py` - Documentação endpoints
- `src/api/routes/pagamento_routes.py` - Documentação pagamento
- `src/config.py` - Documentação configuração

---

## 🚀 Próximos Passos

- [ ] Adicionar banco de dados (SQLite/PostgreSQL)
- [ ] Implementar testes automatizados (pytest)
- [ ] Adicionar logging estruturado
- [ ] Implementar cache (Redis)
- [ ] Adicionar paginação
- [ ] Criar documentação Swagger/OpenAPI
- [ ] Implementar webhooks de pagamento
- [ ] Adicionar autenticação de usuários
- [ ] Implementar desconto/cupons

---

## 📞 Suporte

- [Documentação Mercado Pago](https://www.mercadopago.com.br/developers)
- [Documentação Flask](https://flask.palletsprojects.com)
- [Documentação Docker](https://docs.docker.com)

---

**Desenvolvido com ❤️ para ser profissional, modular e escalável**
