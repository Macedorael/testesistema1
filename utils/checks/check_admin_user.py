#!/usr/bin/env python3
"""
Script para verificar se o usuário admin existe
"""

import sqlite3
import os

def main():
    print("=== VERIFICANDO USUÁRIO ADMIN ===")
    
    # Tentar diferentes caminhos do banco de dados
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db'),
        os.path.join(os.path.dirname(__file__), 'instance', 'consultorio.db'),
        os.path.join(os.path.dirname(__file__), 'consultorio.db')
    ]
    
    database_path = None
    for path in possible_paths:
        if os.path.exists(path):
            database_path = path
            print(f"Banco de dados encontrado em: {path}")
            break
    
    if not database_path:
        print("❌ Nenhum banco de dados encontrado nos caminhos:")
        for path in possible_paths:
            print(f"  - {path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Verificar se a tabela users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("❌ Tabela 'users' não encontrada!")
            return
        
        # Verificar todos os usuários
        cursor.execute("SELECT id, email, role FROM users")
        users = cursor.fetchall()
        
        print(f"Total de usuários: {len(users)}")
        for user in users:
            print(f"  - ID: {user[0]}, Email: {user[1]}, Role: {user[2]}")
        
        # Verificar especificamente admin@test.com
        cursor.execute("SELECT id, email, role FROM users WHERE email = 'admin@test.com'")
        admin = cursor.fetchone()
        
        if admin:
            print(f"\n✅ Admin encontrado: ID {admin[0]}, Email: {admin[1]}, Role: {admin[2]}")
        else:
            print("\n❌ Admin não encontrado!")
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()