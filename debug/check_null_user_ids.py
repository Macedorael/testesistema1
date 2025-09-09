#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_null_user_ids():
    """Verifica registros sem user_id no banco de produção"""
    
    # Conectar ao banco
    db_path = 'consultorio.db'
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=== VERIFICAÇÃO DE REGISTROS SEM USER_ID ===")
    
    # Verificar especialidades
    cursor.execute('SELECT id, nome, user_id FROM especialidades WHERE user_id IS NULL OR user_id = 0')
    esp_null = cursor.fetchall()
    
    print(f"\n📋 Especialidades sem user_id: {len(esp_null)}")
    for esp in esp_null[:10]:  # Mostrar até 10
        print(f"   ID {esp[0]}: '{esp[1]}' (user_id: {esp[2]})")
    
    if len(esp_null) > 10:
        print(f"   ... e mais {len(esp_null) - 10} registros")
    
    # Verificar funcionários
    cursor.execute('SELECT id, nome, email, user_id FROM funcionarios WHERE user_id IS NULL OR user_id = 0')
    func_null = cursor.fetchall()
    
    print(f"\n👥 Funcionários sem user_id: {len(func_null)}")
    for func in func_null[:10]:  # Mostrar até 10
        print(f"   ID {func[0]}: '{func[1]}' - {func[2]} (user_id: {func[3]})")
    
    if len(func_null) > 10:
        print(f"   ... e mais {len(func_null) - 10} registros")
    
    # Verificar usuários disponíveis
    cursor.execute('SELECT id, email FROM usuarios ORDER BY id')
    usuarios = cursor.fetchall()
    
    print(f"\n👤 Usuários disponíveis: {len(usuarios)}")
    for user in usuarios:
        print(f"   ID {user[0]}: {user[1]}")
    
    conn.close()
    
    # Resumo
    print(f"\n=== RESUMO ===")
    print(f"Especialidades sem user_id: {len(esp_null)}")
    print(f"Funcionários sem user_id: {len(func_null)}")
    print(f"Usuários disponíveis: {len(usuarios)}")
    
    if len(esp_null) > 0 or len(func_null) > 0:
        print("\n⚠️  PROBLEMA IDENTIFICADO: Existem registros sem user_id!")
        print("   Isso causa vazamento de dados entre usuários.")
        print("   É necessário atribuir user_id aos registros órfãos.")
    else:
        print("\n✅ Todos os registros têm user_id definido.")

if __name__ == '__main__':
    check_null_user_ids()