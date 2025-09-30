#!/usr/bin/env python3
"""
Script simples para verificar usuários no banco de dados
"""

import sqlite3
import os

def check_users():
    """Verifica usuários existentes no banco"""
    
    # Procurar pelo arquivo do banco
    db_paths = [
        'instance/consultorio.db',
        'consultorio.db',
        'src/database/consultorio.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Banco de dados não encontrado!")
        return
    
    print(f"📁 Usando banco: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Tabela 'users' não encontrada!")
            return
        
        # Buscar todos os usuários
        cursor.execute("SELECT id, email, nome_completo, role FROM users")
        users = cursor.fetchall()
        
        print(f"\n👥 Usuários encontrados ({len(users)}):")
        print("-" * 60)
        
        for user in users:
            user_id, email, nome, role = user
            print(f"ID: {user_id} | Email: {email} | Nome: {nome} | Role: {role}")
        
        conn.close()
        
        if users:
            print(f"\n✅ Use estes emails para teste:")
            for user in users[:2]:  # Mostrar apenas os 2 primeiros
                print(f"   - {user[1]}")
        
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {str(e)}")

if __name__ == "__main__":
    check_users()