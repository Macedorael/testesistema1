# Use uma imagem base do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema necessárias para MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar driver MySQL para Python
RUN pip install --no-cache-dir mysqlclient

# Copiar código da aplicação
COPY . .

# Criar diretório para banco de dados local (caso necessário)
RUN mkdir -p src/database

# Expor porta da aplicação
EXPOSE 5000

# Definir variáveis de ambiente padrão
ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para iniciar a aplicação
CMD ["python", "src/main.py"]