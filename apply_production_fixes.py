#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para aplicar correções de isolamento em produção
Este script deve ser executado no servidor de produção após o deploy
"""

import os
import sys
import sqlite3
from datetime import datetime

def log_message(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def check_database_exists():
    """Verificar se o banco de dados existe"""
    db_path = os.path.join('src', 'database', 'app.db')
    if not os.path.exists(db_path):
        log_message(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    log_message(f"✅ Banco de dados encontrado: {db_path}")
    return True

def backup_database():
    """Fazer backup do banco antes das correções"""
    db_path = os.path.join('src', 'database', 'app.db')
    backup_path = f"app_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        log_message(f"✅ Backup criado: {backup_path}")
        return backup_path
    except Exception as e:
        log_message(f"❌ Erro ao criar backup: {e}")
        return None

def check_current_state():
    """Verificar estado atual do isolamento"""
    log_message("🔍 Verificando estado atual do isolamento...")
    
    db_path = os.path.join('src', 'database', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar usuários
        cursor.execute('SELECT id, email FROM users ORDER BY id')
        usuarios = cursor.fetchall()
        log_message(f"👤 Usuários encontrados: {len(usuarios)}")
        
        # Verificar distribuição de especialidades
        cursor.execute('SELECT user_id, COUNT(*) FROM especialidades GROUP BY user_id')
        esp_dist = cursor.fetchall()
        
        # Verificar distribuição de funcionários
        cursor.execute('SELECT user_id, COUNT(*) FROM funcionarios GROUP BY user_id')
        func_dist = cursor.fetchall()
        
        log_message("📊 Distribuição atual:")
        for user_id, email in usuarios:
            esp_count = next((count for uid, count in esp_dist if uid == user_id), 0)
            func_count = next((count for uid, count in func_dist if uid == user_id), 0)
            log_message(f"   Usuário {user_id} ({email}): {esp_count} especialidades, {func_count} funcionários")
        
        conn.close()
        return True
        
    except Exception as e:
        log_message(f"❌ Erro ao verificar estado: {e}")
        conn.close()
        return False

def apply_isolation_fixes():
    """Aplicar correções de isolamento"""
    log_message("🔧 Aplicando correções de isolamento...")
    
    # 1. Executar fix_isolation_constraints.py
    log_message("1️⃣ Executando correção de constraints...")
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'fix_isolation_constraints.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log_message("✅ Constraints corrigidas com sucesso")
        else:
            log_message(f"❌ Erro na correção de constraints: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"❌ Erro ao executar fix_isolation_constraints.py: {e}")
        return False
    
    # 2. Executar fix_user_isolation.py
    log_message("2️⃣ Executando redistribuição de dados...")
    try:
        result = subprocess.run([sys.executable, 'fix_user_isolation.py'], 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            log_message("✅ Dados redistribuídos com sucesso")
        else:
            log_message(f"❌ Erro na redistribuição: {result.stderr}")
            return False
            
    except Exception as e:
        log_message(f"❌ Erro ao executar fix_user_isolation.py: {e}")
        return False
    
    return True

def verify_fixes():
    """Verificar se as correções foram aplicadas corretamente"""
    log_message("✅ Verificando correções aplicadas...")
    
    db_path = os.path.join('src', 'database', 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar nova distribuição
        cursor.execute('SELECT user_id, COUNT(*) FROM especialidades GROUP BY user_id')
        esp_dist = cursor.fetchall()
        
        cursor.execute('SELECT user_id, COUNT(*) FROM funcionarios GROUP BY user_id')
        func_dist = cursor.fetchall()
        
        cursor.execute('SELECT id, email FROM users ORDER BY id')
        usuarios = cursor.fetchall()
        
        log_message("📊 Nova distribuição:")
        isolation_working = False
        
        for user_id, email in usuarios:
            esp_count = next((count for uid, count in esp_dist if uid == user_id), 0)
            func_count = next((count for uid, count in func_dist if uid == user_id), 0)
            log_message(f"   Usuário {user_id} ({email}): {esp_count} especialidades, {func_count} funcionários")
            
            # Verificar se há distribuição entre usuários
            if esp_count > 0 or func_count > 0:
                isolation_working = True
        
        # Testar constraints
        log_message("🧪 Testando constraints...")
        try:
            # Tentar criar especialidade duplicada para mesmo usuário
            cursor.execute("INSERT INTO especialidades (user_id, nome, descricao) VALUES (1, 'Teste Constraint', 'Teste')")
            cursor.execute("INSERT INTO especialidades (user_id, nome, descricao) VALUES (1, 'Teste Constraint', 'Teste 2')")
            conn.commit()
            log_message("❌ ERRO: Constraint não está funcionando!")
            return False
        except sqlite3.IntegrityError:
            conn.rollback()
            log_message("✅ Constraints funcionando corretamente")
        
        conn.close()
        
        if isolation_working:
            log_message("✅ Isolamento aplicado com sucesso!")
            return True
        else:
            log_message("❌ Isolamento não foi aplicado corretamente")
            return False
            
    except Exception as e:
        log_message(f"❌ Erro na verificação: {e}")
        conn.close()
        return False

def main():
    """Função principal"""
    log_message("🚀 INICIANDO APLICAÇÃO DE CORREÇÕES EM PRODUÇÃO")
    log_message("=" * 60)
    
    # 1. Verificar se banco existe
    if not check_database_exists():
        log_message("❌ Abortando: banco de dados não encontrado")
        sys.exit(1)
    
    # 2. Fazer backup
    backup_path = backup_database()
    if not backup_path:
        log_message("⚠️  Continuando sem backup (RISCO!)")
    
    # 3. Verificar estado atual
    if not check_current_state():
        log_message("❌ Abortando: erro ao verificar estado atual")
        sys.exit(1)
    
    # 4. Aplicar correções
    if not apply_isolation_fixes():
        log_message("❌ Abortando: erro ao aplicar correções")
        if backup_path:
            log_message(f"💡 Restaure o backup se necessário: {backup_path}")
        sys.exit(1)
    
    # 5. Verificar correções
    if not verify_fixes():
        log_message("❌ Correções não foram aplicadas corretamente")
        if backup_path:
            log_message(f"💡 Restaure o backup se necessário: {backup_path}")
        sys.exit(1)
    
    log_message("=" * 60)
    log_message("🎉 CORREÇÕES APLICADAS COM SUCESSO!")
    log_message("")
    log_message("📋 Próximos passos:")
    log_message("   1. Reiniciar o servidor de produção")
    log_message("   2. Testar login com diferentes usuários")
    log_message("   3. Verificar se cada usuário vê apenas seus dados")
    log_message("")
    if backup_path:
        log_message(f"💾 Backup salvo em: {backup_path}")
    log_message("✅ Isolamento de dados funcionando corretamente!")

if __name__ == '__main__':
    main()