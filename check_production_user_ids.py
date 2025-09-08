#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_production_user_ids():
    """Verifica se os registros em produção têm user_id definido"""
    
    # Usar o mesmo banco que o servidor
    db_path = os.path.join('src', 'database', 'app.db')
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== VERIFICAÇÃO DE USER_ID EM PRODUÇÃO ===")
    
    # Primeiro, verificar quais tabelas existem
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tabelas encontradas: {tables}")
    
    # Verificar especialidades (tentar diferentes nomes)
    esp_table = None
    for table_name in ['especialidades', 'especialidade']:
        if table_name in tables:
            esp_table = table_name
            break
    
    if esp_table:
        cursor.execute(f'SELECT id, nome, user_id FROM {esp_table} WHERE user_id IS NULL OR user_id = 0')
        esp_null = cursor.fetchall()
        
        cursor.execute(f'SELECT id, nome, user_id FROM {esp_table}')
        esp_all = cursor.fetchall()
    else:
        esp_null = []
        esp_all = []
    
    print(f"\n📋 Especialidades:")
    print(f"   Total: {len(esp_all)}")
    print(f"   Sem user_id: {len(esp_null)}")
    
    if esp_all:
        print(f"   Exemplos:")
        for esp in esp_all[:5]:
            print(f"      ID {esp[0]}: '{esp[1]}' (user_id: {esp[2]})")
    
    # Verificar funcionários (tentar diferentes nomes)
    func_table = None
    for table_name in ['funcionarios', 'funcionario']:
        if table_name in tables:
            func_table = table_name
            break
    
    if func_table:
        cursor.execute(f'SELECT id, nome, email, user_id FROM {func_table} WHERE user_id IS NULL OR user_id = 0')
        func_null = cursor.fetchall()
        
        cursor.execute(f'SELECT id, nome, email, user_id FROM {func_table}')
        func_all = cursor.fetchall()
    else:
        func_null = []
        func_all = []
    
    print(f"\n👥 Funcionários:")
    print(f"   Total: {len(func_all)}")
    print(f"   Sem user_id: {len(func_null)}")
    
    if func_all:
        print(f"   Exemplos:")
        for func in func_all[:5]:
            print(f"      ID {func[0]}: '{func[1]}' - {func[2]} (user_id: {func[3]})")
    
    # Verificar usuários
    cursor.execute('SELECT id, email FROM users')
    usuarios = cursor.fetchall()
    
    print(f"\n👤 Usuários disponíveis: {len(usuarios)}")
    for user in usuarios:
        print(f"   ID {user[0]}: {user[1]}")
    
    conn.close()
    
    # Diagnóstico
    print(f"\n=== DIAGNÓSTICO ===")
    if len(esp_null) > 0 or len(func_null) > 0:
        print("\n⚠️  PROBLEMA CONFIRMADO!")
        print(f"   - {len(esp_null)} especialidades sem user_id")
        print(f"   - {len(func_null)} funcionários sem user_id")
        print("\n💡 SOLUÇÃO: Atribuir user_id aos registros órfãos")
        
        if len(usuarios) > 0:
            print(f"\n🔧 Sugestão: Atribuir ao usuário ID {usuarios[0][0]} ({usuarios[0][1]})")
    else:
        print("\n✅ Todos os registros têm user_id definido!")

if __name__ == '__main__':
    check_production_user_ids()