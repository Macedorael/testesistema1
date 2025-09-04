#!/usr/bin/env python3
"""
Script para verificar a estrutura do banco de dados
"""

import sqlite3
import os

def check_database_structure():
    """Verifica a estrutura das tabelas no banco de dados"""
    db_path = os.path.join('src', 'database', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Banco de dados {db_path} não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tabelas encontradas:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Verificar estrutura de cada tabela relevante
    relevant_tables = ['users', 'patients', 'appointments', 'payments']
    
    for table_name in relevant_tables:
        print(f"\nEstrutura da tabela '{table_name}':")
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            if columns:
                for col in columns:
                    print(f"  {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - {'PK' if col[5] else ''}")
            else:
                print(f"  Tabela '{table_name}' não encontrada")
        except Exception as e:
            print(f"  Erro ao verificar tabela '{table_name}': {e}")
    
    conn.close()

if __name__ == '__main__':
    check_database_structure()