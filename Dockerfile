FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivos da aplicação
COPY mercadopago_payment_system.py .
COPY app_flask.py .
COPY wsgi.py .

# Criar diretório para logs (se necessário)
RUN mkdir -p /app/logs

# Expor porta
EXPOSE 3000

# Variáveis de ambiente padrão
ENV FLASK_APP=app_flask.py
ENV FLASK_ENV=production
ENV PORT=3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/api/health || exit 1

# Comando de inicialização com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
