#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Correção Automática na Inicialização
Executa automaticamente quando a aplicação inicia para garantir isolamento correto
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime

def log_startup(message):
    """Log com prefixo STARTUP"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [STARTUP] {message}")

def check_isolation_needed():
    """Verifica se correções de isolamento são necessárias"""
    db_path = os.path.join('src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        log_startup("Banco de dados não encontrado - primeira execução")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se existem registros sem user_id
        cursor.execute('SELECT COUNT(*) FROM especialidades WHERE user_id IS NULL')
        esp_null = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM funcionarios WHERE user_id IS NULL')
        func_null = cursor.fetchone()[0]
        
        # Verificar se constraints estão corretas
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='especialidades'")
        esp_schema = cursor.fetchone()
        
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='funcionarios'")
        func_schema = cursor.fetchone()
        
        conn.close()
        
        # Verificar se constraints UNIQUE estão corretas
        esp_constraint_ok = esp_schema and 'UNIQUE(user_id, nome)' in esp_schema[0]
        func_constraint_ok = func_schema and 'UNIQUE(user_id, email)' in func_schema[0]
        
        needs_fix = (
            esp_null > 0 or 
            func_null > 0 or 
            not esp_constraint_ok or 
            not func_constraint_ok
        )
        
        if needs_fix:
            log_startup(f"Correções necessárias: esp_null={esp_null}, func_null={func_null}, constraints_ok={esp_constraint_ok and func_constraint_ok}")
        else:
            log_startup("Isolamento OK - nenhuma correção necessária")
        
        return needs_fix
        
    except Exception as e:
        log_startup(f"Erro ao verificar isolamento: {e}")
        return False

def create_backup():
    """Criar backup antes das correções"""
    db_path = os.path.join('src', 'database', 'app.db')
    backup_name = f"backup_startup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        shutil.copy2(db_path, backup_name)
        log_startup(f"Backup criado: {backup_name}")
        return backup_name
    except Exception as e:
        log_startup(f"Erro ao criar backup: {e}")
        return None

def apply_fixes():
    """Aplicar correções de isolamento"""
    log_startup("Aplicando correções automáticas...")
    
    try:
        # Executar fix_isolation_constraints.py
        import subprocess
        
        log_startup("Executando correção de constraints...")
        result1 = subprocess.run(
            [sys.executable, 'fix_isolation_constraints.py'], 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result1.returncode != 0:
            log_startup(f"Erro na correção de constraints: {result1.stderr}")
            return False
        
        log_startup("Executando redistribuição de dados...")
        result2 = subprocess.run(
            [sys.executable, 'fix_user_isolation.py'], 
            capture_output=True, 
            text=True, 
            timeout=300
        )
        
        if result2.returncode != 0:
            log_startup(f"Erro na redistribuição: {result2.stderr}")
            return False
        
        log_startup("Correções aplicadas com sucesso")
        return True
        
    except Exception as e:
        log_startup(f"Erro ao aplicar correções: {e}")
        return False

def verify_isolation():
    """Verificar se isolamento está funcionando após correções"""
    try:
        db_path = os.path.join('src', 'database', 'app.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar distribuição
        cursor.execute('SELECT user_id, COUNT(*) FROM especialidades GROUP BY user_id')
        esp_dist = cursor.fetchall()
        
        cursor.execute('SELECT user_id, COUNT(*) FROM funcionarios GROUP BY user_id')
        func_dist = cursor.fetchall()
        
        conn.close()
        
        # Verificar se há dados distribuídos entre usuários
        users_with_data = set([uid for uid, _ in esp_dist] + [uid for uid, _ in func_dist])
        
        if len(users_with_data) >= 2:
            log_startup(f"Isolamento funcionando - dados distribuídos entre {len(users_with_data)} usuários")
            return True
        else:
            log_startup("Aviso: Dados concentrados em um único usuário")
            return True  # Não é erro, pode ser situação normal
            
    except Exception as e:
        log_startup(f"Erro na verificação: {e}")
        return False

def auto_fix_isolation():
    """Função principal de correção automática"""
    log_startup("=== INICIANDO VERIFICAÇÃO DE ISOLAMENTO ===")
    
    # 1. Verificar se correções são necessárias
    if not check_isolation_needed():
        log_startup("Sistema OK - nenhuma correção necessária")
        return True
    
    # 2. Criar backup
    backup_path = create_backup()
    if not backup_path:
        log_startup("Aviso: Continuando sem backup")
    
    # 3. Aplicar correções
    if not apply_fixes():
        log_startup("Erro ao aplicar correções")
        if backup_path:
            log_startup(f"Restaure o backup se necessário: {backup_path}")
        return False
    
    # 4. Verificar resultado
    if not verify_isolation():
        log_startup("Erro na verificação pós-correção")
        return False
    
    log_startup("=== CORREÇÕES APLICADAS COM SUCESSO ===")
    return True

if __name__ == '__main__':
    # Executar correções automáticas
    success = auto_fix_isolation()
    
    if not success:
        log_startup("ERRO: Falha nas correções automáticas")
        sys.exit(1)
    else:
        log_startup("Sistema pronto com isolamento correto")