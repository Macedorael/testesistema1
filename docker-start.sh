#!/bin/bash

# Script para inicializar o sistema com Docker
echo "🐳 Iniciando Consultório de Psicologia com Docker..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Parar containers existentes (se houver)
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar os containers
echo "🔨 Construindo e iniciando containers..."
docker-compose up --build -d

# Aguardar alguns segundos para os serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Verificar status dos containers
echo "📊 Status dos containers:"
docker-compose ps

# Mostrar logs da aplicação
echo "📋 Logs da aplicação:"
docker-compose logs app

echo ""
echo "✅ Sistema iniciado com sucesso!"
echo "🌐 Acesse a aplicação em: http://localhost:5000"
echo "🗄️  MySQL disponível em: localhost:3306"
echo ""
echo "📝 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Parar sistema: docker-compose down"
echo "   - Reiniciar: docker-compose restart"
echo "   - Acessar MySQL: docker-compose exec mysql mysql -u consultorio_user -p consultorio_db"