#!/bin/bash

echo "========================================"
echo "  🚀 DEPLOY AUTOMÁTICO LOCAL"
echo "  Sistema Consultório de Psicologia"
echo "========================================"

# Função para log com timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Loop principal
while true; do
    echo
    log "🔍 Verificando novos commits..."
    
    # Fazer fetch do repositório remoto
    if ! git fetch origin master 2>/dev/null; then
        log "❌ Erro ao fazer fetch do repositório"
        sleep 30
        continue
    fi
    
    # Verificar se há novos commits
    NEW_COMMITS=$(git rev-list HEAD..origin/master --count 2>/dev/null)
    
    if [ "$NEW_COMMITS" = "0" ]; then
        log "✅ Nenhum commit novo encontrado"
        sleep 30
        continue
    fi
    
    log "🎉 $NEW_COMMITS novo(s) commit(s) encontrado(s)!"
    log "📥 Fazendo pull das alterações..."
    
    # Fazer pull das alterações
    if ! git pull origin master; then
        log "❌ Erro ao fazer pull das alterações"
        sleep 30
        continue
    fi
    
    log "🛑 Parando containers Docker..."
    if ! docker-compose down; then
        log "⚠️ Aviso: Erro ao parar containers (podem não estar rodando)"
    fi
    
    log "🏗️ Fazendo build local da aplicação (sem Docker Hub)..."
    if ! docker-compose build --no-cache app; then
        log "❌ Erro no build da aplicação"
        sleep 30
        continue
    fi
    
    log "🚀 Iniciando containers atualizados..."
    if ! docker-compose up -d; then
        log "❌ Erro ao iniciar containers"
        sleep 30
        continue
    fi
    
    log "✅ Deploy local concluído com sucesso!"
    log "🌐 Aplicação disponível em: http://localhost:5000"
    log "📊 Para ver logs: docker-compose logs -f app"
    
    # Aguardar um pouco antes de verificar novamente
    sleep 60
done