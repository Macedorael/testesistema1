#!/usr/bin/env python3
"""
Script para verificar as tabelas do banco de dados
"""

import sqlite3
import os

def main():
    print("=== VERIFICANDO TABELAS DO BANCO DE DADOS ===")
    
    # Caminho do banco de dados
    database_path = os.path.join(os.path.dirname(__file__), 'instance', 'consultorio.db')
    
    if not os.path.exists(database_path):
        print(f"Banco de dados não encontrado em: {database_path}")
        return
    
    try:
        # Conectar ao banco
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Listar todas as tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"Tabelas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verificar estrutura da tabela de usuários
        print("\n=== VERIFICANDO ESTRUTURA DA TABELA DE USUÁRIOS ===")
        for table_name in ['users', 'user', 'usuario', 'usuarios']:
            try:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                if columns:
                    print(f"\nTabela '{table_name}' encontrada:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                    
                    # Verificar se existe admin
                    cursor.execute(f"SELECT id, email FROM {table_name} WHERE email LIKE '%admin%';")
                    admin_users = cursor.fetchall()
                    print(f"Usuários admin encontrados: {len(admin_users)}")
                    for user in admin_users:
                        print(f"  - ID: {user[0]}, Email: {user[1]}")
                    break
            except sqlite3.OperationalError:
                continue
        
        # Verificar estrutura da tabela de sessões
        print("\n=== VERIFICANDO ESTRUTURA DA TABELA DE SESSÕES ===")
        for table_name in ['sessions', 'session', 'sessao', 'sessoes']:
            try:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                if columns:
                    print(f"\nTabela '{table_name}' encontrada:")
                    for col in columns:
                        print(f"  - {col[1]} ({col[2]})")
                    
                    # Contar sessões
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    print(f"Total de sessões: {count}")
                    break
            except sqlite3.OperationalError:
                continue
            
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main()