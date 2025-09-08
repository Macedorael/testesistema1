#!/bin/bash
# Script de deploy automático para Render
# Este script é executado automaticamente no deploy

echo "[DEPLOY] Iniciando deploy com correções automáticas..."

# Instalar dependências
echo "[DEPLOY] Instalando dependências..."
pip install -r requirements.txt

# Executar correções de isolamento se necessário
echo "[DEPLOY] Verificando e aplicando correções de isolamento..."
python auto_fix_on_startup.py

echo "[DEPLOY] Deploy concluído com sucesso!"
echo "[DEPLOY] Sistema pronto com isolamento correto"